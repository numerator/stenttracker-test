#new_inv.py

import json

filename = 'inv-w-provider.json'

# write messages to a file indicating relevant user story, or at least MRN

'''
	  "Patient": {
    "Identifiers": [
      {
        "ID": "400143891",
        "IDType": "MRN"
      },
'''

def extract_mrn(json_str):
	json_obj = json.loads(json_str)
	ids = json_obj['Patient']['Identifiers']
	for id in ids:
		if id['IDType'] == 'MRN':
			return id['ID']
	return "No MRN"

def extract_id(json_str):
	json_obj = json.loads(json_str)
	return json_obj['Meta']['Message']['ID']

with open (filename) as f:
	for line in f:
		j = json.loads(line)
		mrn = extract_mrn(line)
		message_id = extract_id(line)
		print('message', message_id, '; mrn', mrn)
		print()
		print(line)
		print()
