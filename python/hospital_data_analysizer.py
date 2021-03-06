import sys
import datetime
import glob
import database as DB
import os

def two_digit_number(number):
	number = int(number)
	if number < 10:
		return '0' + str(number)
	return str(number)

def transfer_minute(second):
	out_sec = second%60
	second = second/60
	out_min = second%60
	out_hr = second/60
	return '%s:%s:%s' % (two_digit_number(out_hr), two_digit_number(out_min), two_digit_number(out_sec))

# === database doctor structure ===
# { 
# 	datetime 	[string], 
# 	name 		[string], 
# 	dept		[string], 
# 	room		[string], 
# 	interval	[string], 
# 	curNumber 	[int], 
# 	start 		[int], 
# 	end 		[int], 
# 	duration 	[int]
# }

if len(sys.argv)!=2:
	print 'Usage: %s [directory path]' % (__file__)
	print '       parse all the files in the directory and generate database'
	sys.exit()


filePath = sys.argv[1]
save_done_path = filePath+'/../row_data_done/%s' %filePath.split('/')[-1]

dirFileList = glob.glob(filePath + '/*')
DB.setDBFile(filePath + '.db')

for input_file in dirFileList:
	input_file_ptr = open(input_file, 'r')
	print "%s is starting..." % (input_file)

	doctorData_list = {}
	checkPointCount = 0
	for line in input_file_ptr:
		line = line.strip('\n')
		token = line.split(' ')
		timeStamp 	= token[0]
		date 		= datetime.datetime.fromtimestamp( int(timeStamp) ).strftime('%Y-%m-%d')
		interval 	= token[1]
		dept 		= token[2]
		room 		= token[3]
		doctor 		= token[4]
		curNumber 	= token[5]

		key = '%s %s %s %s' % (date, dept, doctor, interval)
		if key in doctorData_list:
			doctorData = doctorData_list[key]
			if (curNumber == doctorData['number']) :#or (int(curNumber.split('(')[0]) < int(doctorData['number'].split('(')[0])):
				continue
			else:
				data = {}
				data['datetime'] 	= date
				data['name'] 		= doctor
				data['dept'] 		= dept
				data['room'] 		= room
				data['interval'] 	= interval
				if -1 != doctorData['number'].find('('):
					tempString = doctorData['number'].split('(')[0]
					if tempString.isdigit() == True :
						data['curnumber'] 	= int(tempString)
						data['comment'] 	= '{"over":true}'
					else:
						continue
				else:
					if doctorData['number'].isdigit() == True :
						data['curnumber'] 	= int(doctorData['number'])
						data['comment'] 	= '{"over":false}'
					else:
						continue
				data['start'] 		= int(doctorData['start_time'])
				data['end'] 		= int(timeStamp)
				data['duration'] 	= data['end'] - data['start']
				#DB.insert(data)

				checkPointCount += 1
				if checkPointCount == 100:
					DB.checkPoint()
					checkPoint = 0

				doctorData['start_time'] = timeStamp
				doctorData['number'] = curNumber
		else:
			doctorData_list[key]={'number':curNumber, 'start_time':timeStamp}

	startpath = str(input_file)
	finalpath = save_done_path+'/'+str(input_file).split('/')[-1]
	os.system('mv '+startpath+' '+finalpath)
	print('mv '+startpath+' '+finalpath)
	print "%s is completed!" % (input_file)
	doctorData_list.clear()
	input_file_ptr.close()
	DB.checkPoint()
DB.close()