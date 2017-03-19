
import json
import datetime
from dateutil.parser import parse
import sys

these_stories = sys.argv[1:]
print (these_stories)

# Inventory Depletion timestamp
# "Meta": {
#   "DataModel": "Inventory",
#   "EventType": "Deplete",
#   "EventDateTime": "2017-02-10T15:16:13.000Z",... }

# Appointment 
# "Meta": {
#   "DataModel": "Scheduling",
#   "EventType": "Modification" | "New" | 
#   "EventDateTime": "2017-02-10T14:21:28.000Z", ... 
# }
# "Visit": {
#   "VisitDateTime": "2017-03-24T08:30:00.000Z",
#   "Status": "Comp",
# }

def handle_scheduling(appt_record):
	appt_dt = parse(appt_record['Visit']['VisitDateTime'])
	print('\t\t\tAppt:', appt_dt, 'Status:' , appt_record['Visit']['Status'])

story_to_mrn = {'u1': '400144142', # Jake
			'u2': '400144144', # Sam
			'u3': '400144634', # Suzy
			'u4': '400144641', # Tim
			'u5': '0000', 	   	# Jennifer
			'c1': '400144635', # Jim
			'c2': '400144636', # Stan
			'c3': '400144637', # Bob
			'c4': '400144638', # Tom
			'c5': '400144639', # Alice
			'c6': '400144640', # Liz
			'c7': '400144644'  # Penelope
 			}

mrn_to_story = {v: k for k, v in story_to_mrn.items()}

print (datetime.datetime.now() + datetime.timedelta(40))

fhand = open ('2-10-17-Testing.json')

msgcount = 0
mrncount = 0
stories = {}


for line in fhand:
	line = line.strip()[1:-1]
	msg = json.loads(line)

	ids = msg['Patient']['Identifiers']
	for id in ids:
		if id['IDType'] == 'MRN':
			mrn = id['ID']
			if mrn in stories:
				story_msgs = stories[mrn]
			else:
				story_msgs = []
			story_msgs.append(msg)
			stories[mrn] = story_msgs

# one time, write out each user story
for k, v in stories.items():
	if (k in mrn_to_story):
		with open(mrn_to_story[k] + '.json', 'w') as f:
			for msg in v:
				f.write(json.dumps(msg) + '\n')






