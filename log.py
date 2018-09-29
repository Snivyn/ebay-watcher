import datetime

def log(tag, text):
	# Info tag
	if(tag == 'i'):
		print("[" + str(datetime.datetime.now()) + " - INFO] " + text)
	# Error tag
	elif(tag == 'e'):
		print("[" + str(datetime.datetime.now()) + " - ERROR] " + text)
	# Success tag
	elif(tag == 's'):
		print("[" + str(datetime.datetime.now()) + " - SUCCESS] " + text)
