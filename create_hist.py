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
by ohdongha@gmail.com ver0.2.9 20220914\n"

#version_history
#20220914 ver 0.2.9 # to be used in wrapper scripts, make sure nothing printed to stdout
#20220907 ver 0.2.8 # show the sum and the column number at the end
#20220809 ver 0.2.7 # show max and min values (instead of stdev) at the end
#20220427 ver 0.2.6 # skips inf values + messages printed to stderr insead of stdout
#20201216 ver 0.2.5 # add # of faulty lines, mean, median, etc, at the end of the output file
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
		sys.stderr.write( "col_index is set to 1.\n" )
	bin_size = float(sys.argv[3].strip())
	if bin_size <= 0.0 :
		bin_size = 1.0
		sys.stderr.write( "bin_size is set to 1.\n" )
	fout = open(sys.argv[4], "w")
except (IndexError, ValueError) :
	sys.stderr.write( synopsis )
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
			sys.stderr.write("\r   counted %d lines\r" % num_lines)
			sys.stderr.flush()
	except (ValueError, IndexError, OverflowError) as err :
#		sys.stderr.write( "%s at line %d ...\n" % (err, num_lines) ) # for debuggin purpose
		FaultyLines = FaultyLines + 1
		pass

try:
	sys.stderr.write( "\n%s : Total %d values counted from column %d.\n" % (sys.argv[1].strip(), num_lines, col_index) )
	sys.stderr.write( "%s : There were %d faulty lines.\n" % (sys.argv[1].strip(), FaultyLines) )
	sys.stderr.write( "%s : median, mean, min., max., and sum. of %d values == %.3f, %.3f, %.3f, %.3f, and %.3f\n" % \
			(sys.argv[1].strip(), len(Value_list), median(Value_list), mean(Value_list), min(Value_list), max(Value_list), sum(Value_list) ) )
#	sys.stderr.write( "%s : median, mean, and stdev of %d values == %f, %f, %f\n" % \
#			(sys.argv[1].strip(), len(Value_list), median(Value_list), mean(Value_list), stddev(Value_list) ) )
except ZeroDivisionError:
	sys.stderr.write( "a ZeroDivisionError - the input might be empty or all zero.\n" )
fin.close()

fout.write('Bin_range\tBin_label\t' + sys.argv[4].strip() + '\n')
for key in sorted(Value_dict):
	fout.write(str(round(key*bin_size,5)) + '<=x<' +str(round((key +1)*bin_size,5)) + '\t' + str(round(key*bin_size,5)) + '\t' + str(Value_dict[key]) + '\n') 
try:
	fout.write( "### %s : Total %d values counted from column %d.\n" % (sys.argv[1].strip(), num_lines, col_index) )
	fout.write( "### %s : There were %d faulty lines.\n" % (sys.argv[1].strip(), FaultyLines) )
	fout.write( "### %s : median, mean, min., max., and sum. of %d values == %.3f, %.3f, %.3f, %.3f, and %.3f\n" % \
			(sys.argv[1].strip(), len(Value_list), median(Value_list), mean(Value_list), min(Value_list), max(Value_list), sum(Value_list) ) )
#	fout.write( "### %s : median, mean, and stdev of %d values == %f, %f, %f\n" % \
#			(sys.argv[1].strip(), len(Value_list), median(Value_list), mean(Value_list), stddev(Value_list) ) )
except ZeroDivisionError:
	sys.stderr.write( "a ZeroDivisionError - the input might be empty or all zero.\n" )

sys.stderr.write( "done" )
fout.close()
