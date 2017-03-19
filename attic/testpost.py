#testpost.py

import requests
import json
import datetime
from dateutil.parser import parse


from datetime import datetime
from datetime import timedelta

ct_headers = {'Content-Type': 'application/json',}
post_url = 'http://app-4429.on-aptible.com/redox'
# with open('messages/depletion.json', 'r') as f:
# 	first_msg = f.read()
# 	r = requests.post(post_url, headers=ct_headers, data=first_msg)
# 	print(r)
# 	print (first_msg)

def print_inventory_depletions(message):
	if message['Meta']['DataModel'] == 'Inventory'

def send_story_summaries(story_id):
	json_path = 'stories/' + story_id + '.json'
	with open(json_path) as f:
		for msg in f:
			msg_obj = json.loads(msg)

			#ts = parse(msg_obj["Meta"]["EventDateTime"])
			# replace_date = datetime.now() - timedelta(days=7)		
			# zone = replace_date.strftime('%z')
			# if zone == "":
			# 	zone = "000"
			# r_date_str = replace_date.strftime('%Y-%m-%dT%H:%M:%S.'+zone+'Z')
			# msg_obj["Meta"]["EventDateTime"] = r_date_str

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

stories = ['u1', 'u2', 'u3', 'u4', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7']

# for story in stories:
# 	print_story_summaries(story)
send_story_summaries('u2')
