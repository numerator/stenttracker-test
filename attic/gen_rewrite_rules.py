# parse story rewrite rules

import csv
import json

story_rewrite_rules = {}

with open('stories.csv') as csvfile:
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

print(json.dumps(story_rewrite_rules, indent=2))

# 	for line in f:

# story_rewrite_rules = {
# 	'u1':{
# 		'63893069':{'ts':'0'},				 # inv depletion
# 		'63893295':{'ts':'0', 'appt':'40'},  # schedule appt
# 		'63893445':{'ts':'40', 'appt':'40'}, # arrival at appt
# 		'63893665':{'ts':'40', 'appt':'40'}  # discharge
# 		}
#}