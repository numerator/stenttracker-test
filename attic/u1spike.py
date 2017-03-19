#load_story.py

import json
import sys
import requests
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
import pytz

story_rewrite_rules = {
	'u1':{
		'63893069':{'ts':'0'},				 # inv depletion
		'63893295':{'ts':'0', 'appt':'40'},  # schedule appt
		'63893445':{'ts':'40', 'appt':'40'}, # arrival at appt
		'63893665':{'ts':'40', 'appt':'40'}  # discharge
		}
}

def get_msg_id(message):
	return message['Meta']['Message']['ID']

def make_tz_aware(dt):
	try:
		utc=pytz.UTC
		return utc.localize(dt)
	except:

		return dt

def get_date_zero(offset):
	return datetime.now() - timedelta(days=(int(offset)))

def get_date_for_day_in_story(date_zero, day_in_story):
	return date_zero + timedelta(days=(int(day_in_story)))	

def format_date_time_redox_json(dt):
	zone = dt.strftime('%z')
	if zone == "":
		zone = "000"
	r_date_str = dt.strftime('%Y-%m-%dT%H:%M:%S.'+zone+'Z')
	return r_date_str

def get_msg_timestamp(msg):
	return parse(msg['Meta']['EventDateTime'])

def set_msg_timestamp(msg, timestamp):
	msg['Meta']['EventDateTime'] = format_date_time_redox_json(timestamp)

def get_msg_appt_time(msg):
	if 'Visit' in msg and 'VisitDateTime' in msg['Visit']:
		return msg['Visit']['VisitDateTime']
	else:
		return None

def set_msg_appt_time(msg, appt_time):
	msg['Visit']['VisitDateTime'] = format_date_time_redox_json(appt_time)

def rewrite_msg_times(msg, date_zero, rewrite_rule):
	ts_offset = rewrite_rule['ts']
	set_msg_timestamp(msg, get_date_for_day_in_story(date_zero, ts_offset))
	if 'appt' in rewrite_rule:
		appt_offset = rewrite_rule['appt']
		set_msg_appt_time(msg, get_date_for_day_in_story(date_zero, appt_offset))

def rewrite_story_times(story_messages, day_in_story):
	for m in story_messages:
		rewrite_rule = story_rewrite_rules['u1'][str(get_msg_id(m))]
		date_zero = get_date_zero(day_in_story)
		rewrite_msg_times(m, date_zero, rewrite_rule)

def send_message(msg, url, headers):
	msg_json = json.dumps(msg)
	print(msg, '\n\n')

	r = requests.post(post_url, headers=ct_headers, data=msg_json)
	print(r)

def send_messages(message_list, url, headers):
	for m in message_list:
		ts = make_tz_aware(get_msg_timestamp(m))
		now = make_tz_aware(datetime.now())
		if (ts <= now):
			send_message(m, url, headers)
			
####### MAIN FLOW #######

story_path = 'stories/'
story = 'u1'
story_day = 20

post_url = 'http://app-4429.on-aptible.com/redox'
ct_headers = {'Content-Type': 'application/json',}

story_messages = []
with (open(story_path + story + '.json')) as f:
	for line in f:
		msg = json.loads(line)
		print(get_msg_id(msg))
		story_messages.append(msg)
	rewrite_story_times(story_messages, story_day)
	send_messages(story_messages, post_url, ct_headers)




#		send_messages(story_messages, post_url, ct_headers)
