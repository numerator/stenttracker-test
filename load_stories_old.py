#load_story.py

import json
import sys
import os
import csv
import requests
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from dateutil.parser import *

class Episode:
	pass

class UserStory:

class Message:
	def __init__(self, json):
		self.timestamp = parse(json["Meta"]["EventDateTime"])
		self.data_model = json["Meta"]["DataModel"]
		self.event_type = msg['Meta']['EventType']
		self.id = json['Meta']['Message']['ID']

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

def get_data_model(msg):
	return msg["Meta"]["DataModel"]

def get_event_type(msg):
	return msg['Meta']['EventType']

def get_msg_time(msg):
	return parse(msg["Meta"]["EventDateTime"])

def get_appt_time(msg):
	if 'Visit' in msg:
		return parse(msg['Visit']['VisitDateTime'])
	else:
		return None
def print_inv_depletions():
	for fname in os.listdir(STORY_PATH):
		print('\n\nDoing story:', fname, '\n\n')
		with open (STORY_PATH + fname) as f:
			for line in f:
				msg = json.loads(line)
				if get_data_model(msg) == 'Inventory':
					print (get_msg_id(msg))
					#print(json.dumps(msg, indent=2))

# not used - for debugging
def send_story_summaries(story_id):
	json_path = 'stories/' + story_id + '.json'
	with open(json_path) as f:
		for msg in f:
			msg_obj = json.loads(msg)

			print_inventory_depletions(msg)
			# msg = json.dumps(msg_obj, indent=2)
			timestamp = msg_obj["Meta"]["EventDateTime"]
			data_model = msg_obj['Meta']['DataModel']		
			event_type = msg_obj['Meta']['EventType']
			msg_id = msg_obj['Meta']['Message']['ID']
			ids = msg_obj['Patient']['Identifiers']
			for id in ids:
				if id['IDType'] == 'MRN':
					mrn = id['ID']
			first_name = msg_obj['Patient']['Demographics']['FirstName']
			last_name = msg_obj['Patient']['Demographics']['LastName']
			visit_number = ''
			visit_date_time = ''
			visit_status = ''

			if 'Visit' in msg_obj:
				visit_number = msg_obj['Visit']['VisitNumber']
				visit_date_time = msg_obj['Visit']['VisitDateTime']
				visit_status = msg_obj['Visit']['Status']

			print(story_id, timestamp, msg_id, data_model, event_type, mrn, 
				first_name, last_name, visit_number, visit_status, 
				visit_date_time, sep=',')

			r = requests.post(post_url, headers=ct_headers, data=msg)
			print(r)
			print (json.dumps(msg_obj, indent=2))

def get_story_ids_and_offsets(args, story_path):
	story_offsets = []
	for a in sys.argv:
		if a.startswith('u') or a.startswith('c'):
			story_offsets.append((a.split(':')[0], a.split(':')[1]))
	return story_offsets

def load_rewrite_rules(rule_file):
	story_rewrite_rules = {}

	with open(rule_file) as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			story = row[0]
			msg_id = row[2]
			ts_offset = row[-2]
			appt_offset = row[-1]
			story_rules = {}
			if story in story_rewrite_rules:
				story_rules = story_rewrite_rules[story]
			story_rules[msg_id] = {}
			story_rules[msg_id]['ts'] = ts_offset
			if appt_offset != '':
				story_rules[msg_id]['appt'] = appt_offset
			story_rewrite_rules[story] = story_rules

	return story_rewrite_rules

def load_stories(story_offset_list, story_path):
	stories = {}
	for u, off in story_offset_list:
		stories[u] = {}
		with (open(story_path + u + '.json')) as f:
			stories[u]['offset'] = off
			stories[u]['messages'] = []
			for line in f:
				msg = json.loads(line)
				stories[u]['messages'].append(msg)
	return stories

def rewrite_msg_timestamp(story, msg, date_zero, rewrite_rules):
	rewrite_rule = rewrite_rules[story]
	msg_id = get_msg_id(msg)
	creation_time = date_zero + timedelta(days=int(rewrite_rule[str(msg_id)]['ts']))
	msg['Meta']['EventDateTime'] = format_date_time_redox_json(creation_time)
	if 'appt' in rewrite_rule:
		appt_time = date_zero + timedelta(days=int(rewrite_rule['appt']))
		msg['Visit']['VisitDateTime'] = format_date_time_redox_json(appt_time)
	return msg

def rewrite_timestamps(story_dict, rewrite_rules):
	for story in story_dict:
		date_zero = get_date_zero(story_dict[story]['offset'])
		story_messages = story_dict[story]['messages']
		for i in range(len(story_messages)):
			m = story_messages[i]
			shifted_msg = rewrite_msg_timestamp(story, m, date_zero, rewrite_rules)
			story_messages[i] = shifted_msg

#original curl command
#curl -H "Content-Type: application/json" -X POST --data-binary @depletion.json http://app-4429.on-aptible.com/redox
def send_story_message(msg, url):
	print('sending message', get_msg_id(msg), get_data_model(msg), get_event_type(msg), get_msg_time(msg), get_appt_time(msg))
	headers = {'Content-Type': 'application/json'}
	r = requests.post(url, headers=headers, data=json.dumps(msg).encode())
	print(r)
	
def send_story_messages(stories, url):
	for s in stories:
		messages = stories[s]['messages']
		for m in messages:
			if get_msg_time(m) < datetime.now(timezone.utc):
				send_story_message(m, url)
			else:
				print('ignoring future message:', get_msg_time(m))

def print_messages_for_story(story_id, stories):
	print("\n\nStory: " + story_id)
	if story_id in stories:
		for msg in stories[story_id]['messages']:
			print_message(msg)

def print_message(msg):
	msg_id = get_msg_id(msg)
	patient_name = msg['Patient']['Demographics']['FirstName'] + ' ' + msg['Patient']['Demographics']['LastName']
	event_date = msg['Meta']['EventDateTime'] 
	if 'Visit' in msg:
		appt_date = msg['Visit']['VisitDateTime']
		appt_status = msg['Visit']['Status']
	else:
		appt_date = ''
		appt_status = ''
	data_model = msg['Meta']['DataModel']
	event_type = msg['Meta']['EventType']

	print('Message:', msg_id)
	print('\t Patient:', patient_name)
	print('\t TS:', event_date)
	print('\t Event: ', data_model, "-", event_type)
	if 'Visit' in msg:
		print('\t Appt:', appt_date, appt_status)

	print()

####### MAIN FLOW #######

STORY_PATH = 'stories/'
REWRITE_RULES_FILENAME = 'stories.csv'
ST_URL = 'http://app-4429.on-aptible.com/redox'

#print_inv_depletions()

story_ids_and_offsets = get_story_ids_and_offsets(sys.argv, STORY_PATH)
rewrite_rules = load_rewrite_rules(REWRITE_RULES_FILENAME)
stories = load_stories(story_ids_and_offsets, STORY_PATH)
rewrite_timestamps(stories, rewrite_rules)
# for story in stories:
# 	print_messages_for_story(story, stories)
# 	print(json.dumps(stories[story], indent=2))
send_story_messages(stories, ST_URL)

