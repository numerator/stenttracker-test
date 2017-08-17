#new-stories.py

import csv
import json

def get_story_from_msg_id(msg_id):
	global msg_to_story_id
	return msg_to_story_id[msg_id]

#CSV CONSTANTS
story_idx = 0
new_msg_idx = 3

story_to_msg_id = {}
msg_to_story_id = {}
story_msgs = {}

with open('stories-v2.csv') as csvfile:
	reader = csv.reader(csvfile)
	for line in reader:
		story_id = line[story_idx].strip()
		if story_id not in story_to_msg_id:
			story_to_msg_id[story_id] = []
		story_to_msg_id[story_id].append(line[new_msg_idx])
		msg_id = line[new_msg_idx]
		print(type(msg_id))
		msg_to_story_id[msg_id] = story_id

print(msg_to_story_id)

with open('testmessages.json') as f:
	for line in f:
		msg = json.loads(line)
		msg_id = msg["Meta"]["Message"]["ID"]
		print(type(msg_id))
		story_id = msg_to_story_id[str(msg_id)]
		if story_id not in story_msgs:
			story_msgs[story_id] = []
		story_msgs[story_id].append(msg)

story_dir = 'new_stories/'
for story_id in story_msgs:
	fname = story_dir + str(story_id) + '.json'
	with open(fname, 'w') as f:
		for m in story_msgs[story_id]:
			f.write(json.dumps(m) + '\n')


