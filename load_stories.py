#load_story.py

import json
import sys
import csv
import requests
from datetime import datetime
from datetime import timedelta

def get_msg_id(message):
	#print(json.dumps(message, indent=2))
	
	return message['Meta']['Message']['ID']

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
	headers = {'Content-Type': 'application/json'}
	requests.post(url, headers=headers, data=json.dumps(msg).encode())

def send_story_messages(stories, url):
	for s in stories:
		messages = stories[s]['messages']
		for m in messages:
			send_story_message(m, url)


####### MAIN FLOW #######

STORY_PATH = 'stories/'
REWRITE_RULES_FILENAME = 'stories.csv'
ST_URL = 'http://app-4429.on-aptible.com/redox'

story_ids_and_offsets = get_story_ids_and_offsets(sys.argv, STORY_PATH)
rewrite_rules = load_rewrite_rules(REWRITE_RULES_FILENAME)
stories = load_stories(story_ids_and_offsets, STORY_PATH)
# print ("Before rewrite")
# print (json.dumps(stories, indent=2))
rewrite_timestamps(stories, rewrite_rules)
# print ("After rewrite")
# print (json.dumps(stories, indent=2))
send_story_messages(stories, ST_URL)

