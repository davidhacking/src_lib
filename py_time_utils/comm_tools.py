import datetime
import time

TIME_FORMAT_COMMON = '%Y-%m-%d %H:%M:%S'


def formatTime(date, formatStr):
	return datetime.datetime.fromtimestamp(date).strftime(formatStr)


def datetime2time(t):
	return time.mktime(t.timetuple()) + t.microsecond / 1E6


def str2time(t):
	return datetime2time(datetime.datetime.strptime(t, TIME_FORMAT_COMMON))


def allTime2time(t):
	if type(t) is datetime.datetime:
		t = datetime2time(t)
	elif type(t) is str:
		if t.find('.') != -1:
			t = t[:t.rfind('.')]
		t = str2time(t)
	return t


if __name__ == "__main__":
	print(formatTime(1543279875.57, TIME_FORMAT_COMMON))
	# start_time = "2018-11-13 12:46:50"
	# end_time = "2018-10-02	13:56:30.578000"
	# print allTime2time(start_time)
	pass
