#load_story.py

import json
import sys
import os
import csv
import requests
import glob
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from dateutil.parser import *

class Episode:
	pass

class UserStory:
	def __init__(self, id):
		self.story_id = id
		self.load_messages()
	
	def load_messages(self):
		global STORY_PATH
		self.messages = []
		file_name = STORY_PATH + self.story_id + '.json'
		with open(file_name) as f:
			for line in f:
				json_obj = json.loads(line)
				self.messages.append(Message(json_obj))

	def get_msg_by_id(self, id):
		for m in self.messages:
			if str(m.id) == str(id):
				return m
		return None

	def apply_offsets(self, date_zero):
		story_rewrite_rules = {}
		global REWRITE_RULES_FILENAME

		with open(REWRITE_RULES_FILENAME) as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				story = row[0]
				if story == self.story_id:
					msg_id = row[2]
					ts_offset = row[-2]
					appt_offset = row[-1]
					msg = self.get_msg_by_id(msg_id)
					creation_time = date_zero + timedelta(days=int(ts_offset))
					msg.set_timestamp(creation_time)
					print('updated', msg.id, 'with creation time', msg.timestamp)
					if appt_offset is not None and appt_offset != '':
						print('updating', msg.id, 'with date zero', date_zero, 'offset', appt_offset)
						appt_time = date_zero + timedelta(days=int(appt_offset))
						msg.set_appt_time(appt_time)
						print('updated', msg.id, 'with appt time', msg.appt.visit_date)

	def rewrite_timestamps(self):
		pass

	def send_story(self):
		global ST_URL
		url = ST_URL

		for m in self.messages:
			if m.timestamp < datetime.now():
				m.send_message(url)
			else:
				print('ignoring future message:', m)
	
	def print_json(self, pretty=True):
		indent = 0
		if pretty:
			indent = 2
		for m in self.messages:
			print (json.dumps(m.json_obj, indent=indent))

	def __repr__(self):
		repr = self.story_id
		for m in self.messages:
			repr += "\n\t" + m.__repr__()
		return repr

class Appt:
	def __init__(self, json_obj):
		self.visit_date = parse(json_obj['Visit']['VisitDateTime'])
		self.status = json_obj['Visit']['Status']

	def __repr__(self):
		repr = format_date_time_simple(self.visit_date) + ", " + self.status
		return repr

class Patient:
	def __init__(self, json_obj):
		self.first_name = json_obj['Patient']['Demographics']['FirstName']
		self.last_name = json_obj['Patient']['Demographics']['LastName']
		ids = json_obj['Patient']['Identifiers']
		for id in ids:
			if id['IDType'] == 'MRN':
				self.mrn = id['ID']
	def __repr__(self):
		repr = self.first_name + " " + self.last_name + "(" + self.mrn + ")"
		return repr

class Message:
	def __init__(self, json_obj):
		self.timestamp = parse(json_obj["Meta"]["EventDateTime"])
		self.data_model = json_obj["Meta"]["DataModel"]
		self.event_type = json_obj['Meta']['EventType']
		self.id = json_obj['Meta']['Message']['ID']
		self.patient = Patient(json_obj)
		if 'Visit' in json_obj:
			self.appt = Appt(json_obj)
		else:
			self.appt = None
		self.json_obj = json_obj

	def __repr__(self):
		repr = str(self.id) + " " + format_date_time_simple(self.timestamp) + \
			", " + self.data_model + ", " + \
			self.event_type + ", " + self.patient.__repr__() + ", " + \
			self.appt.__repr__()
		return repr

	def set_timestamp(self, timestamp):
		self.timestamp = timestamp
		self.json_obj["Meta"]["EventDateTime"] = format_date_time_redox_json(timestamp)

	def set_appt_time(self, appt_time):
		self.appt.visit_date = appt_time
		self.json_obj["Visit"]["VisitDateTime"] = format_date_time_redox_json(appt_time)
	
	def send_message(self, url):
		# print('sending message', self)
		headers = {'Content-Type': 'application/json'}
		r = requests.post(url, headers=headers, data=json.dumps(self.json_obj).encode())
		print('sent message', self.id, format_date_time_simple(self.timestamp), 
			'response:', r)
		print(json.dumps(self.json_obj, indent=2))


### UTILITY FUNCTIONS
def get_date_zero(offset):
	date_zero = datetime.now() - timedelta(days=(int(offset)))
	return date_zero

def get_time_delta(offset_str):
	off = int(offset_str[0:2])
	print(off)

def format_date_time_redox_json(dt):
	zone = dt.strftime('%z')
	if zone == "":
		zone = "000"
	r_date_str = dt.strftime('%Y-%m-%dT%H:%M:%S.'+zone+'Z')
	return r_date_str

def format_date_time_simple(dt):
	r_date_str = dt.strftime('%Y-%m-%d %H:%M')
	return r_date_str

def print_inv_depletions():
	for fname in os.listdir(STORY_PATH):
		print('\n\nDoing story:', fname, '\n\n')
		with open (STORY_PATH + fname) as f:
			for line in f:
				msg = json.loads(line)
				if get_data_model(msg) == 'Inventory':
					print (get_msg_id(msg))
					#print(json.dumps(msg, indent=2))


#original curl command
#curl -H "Content-Type: application/json" -X POST --data-binary @depletion.json http://app-4429.on-aptible.com/redox

def test_story_load(story_list, offset):
	global stories

	if story_list is None or len(story_list) == 0:
		load_all_stories()
	else:
		for s in story_list:
			stories.append(UserStory(s))

	dz = get_date_zero(offset)

	for s in stories:
		s.apply_offsets(dz)

	for s in stories:
		print(s)

def load_all_stories():
	global STORY_PATH
	global stories	
	dir_contents = glob.glob(STORY_PATH + '*.json') # returns list
	for fname in dir_contents:
		print (fname)
		stories.append(UserStory(fname.split('.')[0].split('/')[1]))


####### MAIN FLOW #######

STORY_PATH = 'stories/'
REWRITE_RULES_FILENAME = 'stories.csv'
ST_URL = 'http://app-4429.on-aptible.com/redox'
stories = []

# test_story_load(['u1', 'u2', 'u3', 'u4', 'c1'], 0)
# test_story_load(None, 0)

story_offsets = []
for a in sys.argv:
	if a.startswith('u') or a.startswith('c'):
		story_offsets.append((a.split(':')[0], a.split(':')[1]))

for so in story_offsets:
	story = UserStory(so[0])
	stories.append(story)
	dz = get_date_zero(so[1])
	story.apply_offsets(dz)

for s in stories:
	s.send_story()
	# s.print_json()

