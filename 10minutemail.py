import requests
import re 
import os
import sys
import time
import html  # Import the html module for unescaping

global file
file = None

def usage():
	print("Usage:")
	print("\tpython %s" % sys.argv[0])
	print("\tpython %s --save/-s Write/Save body,from,subject and date at file\n" % sys.argv[0])
	sys.exit()

def main(path):
	subjects = []
	xc = 0
	path = path
	body = None
	try:
		argv = sys.argv[1]
	except IndexError:
		argv = ""
	email_ = None
	r = requests.get('https://10minutemail.net/')
	email = re.findall(r'class="mailtext" value="(.*\@.+\.\w*)" />', r.content.decode(), re.I)
	print("\033[1;31mYour email:\033[0m \033[3;33m" + email[0] + "\033[0m")
	phps = re.findall(r'PHPSESSID=[a-zA-Z0-9]+', r.headers['Set-Cookie'], re.I)[0]
	header  = "+-----------------------+------------------------+-----------------------+----------------------+\n"
	header += "|\t\033[1;31mFrom\033[0m\t\t|\t\033[1;32mSubject\033[0m\t\t |\t\033[1;33mDate\033[0m\t\t |\t\033[1;34mBody\033[0m\t\t|"
	header += "\n+-----------------------+------------------------+-----------------------+----------------------+"
	print(header)
	# 600 -> 60(seconds) x 10(minutes) 
	for i in range(0, 600):
		a = requests.get('https://10minutemail.net/mailbox.ajax.php', headers={'Cookie': phps})
		fields = re.findall(r'<td>(.*?)</td>', a.content.decode())
		form = html.unescape(fields[0])  # Use html.unescape directly
		subject = re.findall(r'>(.*?)<', fields[1], re.I)[0]
		date = re.findall(r'>(.*?)<', fields[2], re.I)[0]
		url = 'https://10minutemail.net/' + re.findall(r'href="(.+?)"', fields[1], re.I)[0]
		# find body	
		def sender(url):
			aa = requests.get(url, headers={'Cookie': phps})
			b = re.findall(r'class="break-all mailinhtml">(.+?)<', aa.content.decode(), re.I)[0]
			return b

		# write body
		if 'welcome' not in url and argv in ('--save', '-s'):
			body = html.unescape(sender(url))
			email_ = re.findall(r'([a-zA-Z0-9._-]+@[a-zA-Z.-_]+)', form, re.I)[0].replace('>', '').replace('<', '').replace('@', '_') + '.txt'
			if os.path.exists(email_ if path == None else path):
				with open(email_ if path == None else path, 'r+') as file:
					data = file.read()
					file.seek(0)
					file.write('%s\nFrom: %s\nSubject: %s\nDate: %s\nBody: %s\n' % ("-"*50, form, subject, time.strftime("%H:%M:%S"), body))
					file.truncate()
			file = open('%s' % email_ if path == None else path, 'w')
			file.write('%s\nFrom: %s\nSubject: %s\nDate: %s\nBody: %s\n' % ("-"*50, form, subject, time.strftime("%H:%M:%S"), body))
		
		# print subject one time
		if subject not in subjects:
			subjects.append(subject)
			print('| \033[1;31m%s | \033[1;32m%s | \033[1;33m%s | \033[1;34m%s\033[0m\n' % (form, subject, date, email_ if path == None else path))
		
		# wait 10 seconds 
		time.sleep(10)
	
	if file != None:
		file.close()

if __name__ == "__main__":
	try:
		try:
			if '--save' in sys.argv[1] or '-s' in sys.argv[1]:
				if sys.argv[1-2] in ('-s', '--save'):
					usage()
				main(sys.argv[1-2])
		except IndexError:
			main(path=None)
	except Exception as error:
		if file != None:
			file.close()
		sys.exit("[ERROR]: %s" % str(error))
	except KeyboardInterrupt:
		if file != None:
			file.close()
		sys.exit("[USER EXIT]: CTRL+c!!!")
