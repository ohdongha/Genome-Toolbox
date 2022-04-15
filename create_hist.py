#!/usr/bin/env python
import sys, math

# functions for median and mean (from StackOverflow comments by A.J. Uppal, NPE, and Quentin Pradet)
def median(numbers):
    n = len(numbers)
    if n < 1:
            return None
    if n % 2 == 1:
            return sorted(numbers)[n//2]
    else:
            return sum(sorted(numbers)[n//2-1:n//2+1])/2.0
			
def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def stddev(lst):
    """returns the standard deviation of lst"""
    mn = mean(lst)
    variance = sum([(e-mn)**2 for e in lst]) / len(lst)
    return math.sqrt(variance)

###################################################
### 0. script description and parsing arguments ###
###################################################

synopsis = "\n\
create_hist.py <table.txt> <N> <bin_size> <output.hist>\n\n\
 - print histogram of values in the <N>st/nd/th column of <table.txt>;\n\
 - <N> == 1 indicate the 1st column; \n\
 - <bin_size> should be a positive float number, larger than 0.0001; \n\
 - ignore non-numerical values from the input.\n\
by ohdongha@gmail.com ver0.2.4 20200904\n"

#version_history
#20200904 ver 0.2.4 # modified to work with python 3 + minor bug fixes
#20181204 ver 0.2.3 # 1st column of the output modified,
#20171112 ver 0.2.2 # print standard deviation
#20171112 ver 0.2.1 # fixed an issue with ZeroDivisionError; also use output file name as the column header,
#20170313 ver 0.2 # now accept bin size as a positive float, print median and average on the screen
#20170221 ver 0.1 # print average on the screen
#20141026 ver 0.0 

# parameters
report_progress_interval = 5000 # report progress on the screen at this interval

try: 
	fin = open(sys.argv[1], "r")
	col_index = int(sys.argv[2].strip())
	if col_index <= 1 :
		col_index = 1
		print( "col_index is set to 1.\n" )
	bin_size = float(sys.argv[3].strip())
	if bin_size <= 0.0 :
		bin_size = 1.0
		print( "bin_size is set to 1.\n" )
	fout = open(sys.argv[4], "w")
except (IndexError, ValueError) :
	print( synopsis )
	sys.exit(0)

	
###############
### 1. main ###
###############

Value_dict = dict()
Value_list = []
num_lines = 0
FaultyLines = 0
Sum = 0

for line in fin:
	try:
		num_lines = num_lines + 1
		tok = line.split('\t')
		Value = float(tok[col_index-1].strip())
		Value_dict[int(Value / bin_size)] = Value_dict.get(int(Value / bin_size), 0) + 1 
		Sum = Sum + Value
		Value_list.append(Value)
		if ( num_lines % report_progress_interval == 0):
			sys.stdout.write("\r   counted %d lines" % num_lines)
			sys.stdout.flush()
	except (ValueError, IndexError) as err :
		print( "%s at line %d ...\n" % (err, num_lines) )
		FaultyLines = FaultyLines + 1
		pass

try:
	print( "\n%s : Total %d values counted." % (sys.argv[1].strip(), len(Value_list)) )
	print( "%s : There were %d faulty lines." % (sys.argv[1].strip(), FaultyLines) )
	print( "%s : median, mean, and stdev of %d values == %f, %f, %f" % \
			(sys.argv[1].strip(), len(Value_list), median(Value_list), mean(Value_list), stddev(Value_list) ) )
except ZeroDivisionError:
	print( "a ZeroDivisionError - the input might be empty or all zero." )
fin.close()

fout.write('Bin_range\tBin_label\t' + sys.argv[4].strip() + '\n')
for key in sorted(Value_dict):
	fout.write(str(round(key*bin_size,5)) + '<=x<' +str(round((key +1)*bin_size,5)) + '\t' + str(round(key*bin_size,5)) + '\t' + str(Value_dict[key]) + '\n') 
print( "done" )
fout.close()
