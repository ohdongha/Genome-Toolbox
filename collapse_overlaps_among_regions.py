#!/usr/bin/env python
synopsis = "\ncollapse_overlaps_among_regions.py <region_table.list> <N> <output.txt>\n\n\
# from a <region_table.list> sorted based on start positions, print out new coordinates with overlap collapsed to <output.txt>;\n\
# <region_table.list> should have the chromosome ID, start, and end positions at the <N>, (<N>+1), and (<N>+2)th columns, tab-delimited;\n\
# <region_table.list> should be sorted ascending according to <start_pos> and <chromosome_ID>;\n\
# for each line in <region_table.list>, the larger between <end_position> of the previous line and <start_pos>, will be kept as <new_start_pos> ...  ;\n\
# and the larger between <end_position> of the previous line and <end_pos>, will be kept as <new_end_pos> ;\n\
# if <new_end_pos> is larger than <new_start_pos>, <new_len_region> will be <new_end_pos> - <new_start_pos> + 1 ;\n\
# if <new_end_pos> == <new_start_pos>, <new_len_region> will be 0  ;\n\
# <output.txt>: will contain all lines from <region_table.list> plus 4 new columns for <chrID>, <new_start_pos>, <new_end_pos>, and <new_len_region>, tab-delimited. \n\n\
## 20170713 script name changed, previously 'remove_overlaps_among_regions.py'\n\
## 20151022 ver 1.2 ## bug fix\n\
## 20150811 ver 1.1\n\
## 20150801 ver 1.0\n\
## copyleft by ohdongha@gmail.com\n"

import sys
import re

try: 
	fin_list = open(sys.argv[1], "rU")
	chromosome_column_index = int(sys.argv[2])
	fout = open(sys.argv[3], "w")
except ValueError :
	print synopsis
	sys.exit(0)
except IndexError :
	print synopsis
	sys.exit(0)


### reading and processing lines in <region_table.list> and print to <output.txt>
Lines = 1
LinesWithOverlap = 0
LinesWithError = 0
ChrID = ""
start_position = 0
end_position = 0
previous_ChrID = ""
previous_start_position = 0
previous_end_position = 0

for line in fin_list:
	try :
		tok = re.split('\t', line)
		ChrID = tok[chromosome_column_index - 1].strip()
		start_position = int( tok[chromosome_column_index].strip() )
		end_position = int( tok[chromosome_column_index + 1].strip() )
		if ( (ChrID == previous_ChrID) and (start_position < previous_start_position) ):
			print "\n The input file appears not properly sorted at line number", str(Lines), "\n"
			print "\n Exiting, without further processing.\n"
			break				
		if ( end_position <= start_position ):
			raise ValueError()
		if ( ChrID != previous_ChrID):  ## dealing with the first line of each chromosome
			previous_start_position = start_position
			previous_end_position = end_position
			previous_ChrID = ChrID
			fout.write(line.strip()  + '\t' + ChrID + '\t' + str( start_position ) + '\t' + str( end_position ) + '\t' + str( end_position - start_position + 1 ) + '\n')
		else:
			if( start_position < previous_end_position):
				LinesWithOverlap = LinesWithOverlap + 1				
			previous_start_position = start_position
			start_position = max(start_position, previous_end_position)
			end_position = max(end_position, previous_end_position)
			previous_end_position = end_position
			previous_ChrID = ChrID
			if ( start_position != end_position): 
				fout.write(line.strip() + '\t' + ChrID + '\t' + str( start_position ) + '\t' + str( end_position ) + '\t' + str( end_position - start_position + 1 ) + '\n')
			else:
				fout.write(line.strip() + '\t' + ChrID + '\t' + "0" + '\t' + "0" + '\t' + "0" + '\n')
		Lines = Lines + 1
		if ( Lines % 10000 == 0):
			sys.stdout.write("\r   processing %d+ lines" % (Lines))
			sys.stdout.flush()
	except (ValueError, IndexError):
		fout.write(line)
		print "\n", str(Lines), "st \ nd \ th line contain non-processable values.  Keeping without processing." 
		LinesWithError = LinesWithError + 1
fin_list.close()
fout.close()

print "\nOut of ", str(Lines), " lines, ", str(LinesWithOverlap), " overlapped with previous lines and ", str(LinesWithError), " lines were excluded from processing due to unexpected column values.\n"
print "done\n"
