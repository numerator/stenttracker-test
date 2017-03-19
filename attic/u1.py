#user story 1 messages


import datetime
from datetime import datetime
from datetime import timedelta

offset = 0

tz = datetime.now()

u1_mapping = [
	{"message_id":63893069, "ts":tz},
	{"message_id":63893295, "ts":tz, "appt": (tz + timedelta(days=40))},
	{"message_id":63893445, "ts":tz + timedelta(days=40, minutes=-5), "appt": (tz + timedelta(days=40))},
	{"message_id":63893665, "ts":tz + timedelta(days=40, minutes=50), "appt": (tz + timedelta(days=40))}
]

# EventDateTime_Key = ["Meta"]["EventDateTime"]
# Appt_DateTime_Key = ["Visit"]["VisitDateTime"]



print (u1_mapping)