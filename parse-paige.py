import json

# look for {
# if found, create a stack where the first { is the bottom
# then for each { found, append and for each } found, pop. When len = 0, we've completed one.

in_json = False
curr_json_string = ""
stack = []
json_objs = []

fhand = open('paige.json')

line_no = 0
for line in fhand:
	s = line.strip()
	line_no += 1
	if not in_json:
		if s == '{':
			print("\nstarting JSON object at line: ", line_no)
			in_json = True
			stack.append(s)
			curr_json_string = s
	else:
		if '{' in s and '}'  in s:
			print("Warning, assumption violated at line", line_no, ": ", line)
		if '{' in s:
			print("found { at line", line_no)
			stack.append(s)
		if '}' in s:
			print("found } at line", line_no)
			stack.pop()
		# append to the current string no matter what
		curr_json_string += s
		if len(stack) == 0:
			json_objs.append(json.loads(curr_json_string))

			print("\nending JSON object at line: ", line_no)
			print("\njson obj: \n\t", json_objs[-1])

			curr_json_string = ""
			in_json = False

fhand.close()

fhand = open('testmessages.json', 'w')
for j in json_objs:
	fhand.write(json.dumps(j) + '\n')
fhand.close()



