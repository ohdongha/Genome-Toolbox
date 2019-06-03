#!/usr/bin/env python
synopsis = "\n\n###usage: mark_positions_overlapping_with_other_regions.py <region_table.list> <N> <n> <position_table_ToBeMarked.txt> <output.txt>\n\
###mark regions in <position_table_ToBeMarked.txt> that overlap within <n> of any region specified in <region_table.list>;\n\
###<region_table.list>: should contain <region_ID> + '\\t' + <chromosome_ID> + '\\t' + <start_pos> + '\\t' + <end_pos>;\n\
###<region_table.list>: genomic regions in <region_table.list> may overlap, but <region_ID> should be unique;\n\
###<region_table.list>: requires no header;\n\n\
###<position_table_ToBeMarked.txt> should have the chromosome ID and position at the <N> and (<N>+1)th columns, tab-delimited. e.g. a .tab file.;\n\
###<output.txt> contains entire lines from <region_table_ToBeMarked.txt>, with overlapping positions marked by adding <region_ID> from <region_table.list>\n\n\
###copyleft by ohdongha@gmail.com 20180824 ver 1.1.1, bug fix\n\
###copyleft by ohdongha@gmail.com 20180818 ver 1.1, temparory modification\n\
###copyleft by ohdongha@gmail.com 20151223 ver 1.0, modified from collect_regions_overlapping_with_other_regions.py.\n\
###copyleft by ohdongha@gmail.com 20150814 ver 1.3\n\
###copyleft by ohdongha@gmail.com 20150728 ver 1.2\n\
###copyleft by ohdongha@gmail.com 20150724 ver 1.1\n\
###copyleft by ohdongha@gmail.com 20150419 ver 1.0\n\n"

import sys

try: 
	fin_list = open(sys.argv[1], "rU")
	chromosome_column_index = int(sys.argv[2])
	length_expanded = int(sys.argv[3])
	fin_ToBeFiltered = open(sys.argv[4], "rU")
	fout = open(sys.argv[5], "w")
except (ValueError, IndexError, IOError) :
	print synopsis
	sys.exit(0)

### reading in <region_table.list>
lines_in_region_table = 0
faultyLines_in_region_table = 0
regionID = ""
chrID = ""
regionStart = 0
regionEnd = 0
regionNum = 0

regionID_dict = dict() # key = chrID, value = dictionary of regionID in chrID
start_dict = dict()
end_dict = dict()

for line in fin_list:
	tok = line.split('\t')
	lines_in_region_table = lines_in_region_table + 1
	try:
		regionID = tok[0].strip()
		chrID = tok[1].strip()	
		regionStart = int(tok[2].strip())
		regionEnd = int(tok[3].strip())
		if regionEnd >= regionStart :
			if chrID not in regionID_dict:
				regionID_dict[chrID] = dict()
				start_dict[chrID] = dict()
				end_dict[chrID] = dict()
			regionID_dict[chrID][regionNum] = regionID
			start_dict[chrID][regionNum] = regionStart
			end_dict[chrID][regionNum] = regionEnd
			regionNum = regionNum + 1
		else:
			faultyLines_in_region_table = faultyLines_in_region_table +1			
	except IndexError :
		faultyLines_in_region_table = faultyLines_in_region_table +1
	except ValueError :
		faultyLines_in_region_table = faultyLines_in_region_table +1

print "Out of total ", lines_in_region_table, " lines in ", sys.argv[1].strip(), ", ", faultyLines_in_region_table, " lines were rejected."
print "Now collecting regions in ", sys.argv[4].strip(), ": \n"
fin_list.close()


### collecting lines in <position_table_ToBeMarked.txt> and print to <output.txt>
Lines = 0
collectedLines = 0
ChrID = ""
start_pos = 0
end_pos = 0
counted = False

overlap = 0
max_overlap = 0
rID_maxOvrlp = 0

for line in fin_ToBeFiltered:
	overlap = 0
	max_overlap = 0
	rID_maxOvrlp = 0
	counted = False

	try :
		tok = line.split('\t')
		ChrID = tok[chromosome_column_index - 1].strip()
		start_pos = int( tok[chromosome_column_index].strip() )-length_expanded
		end_pos = int( tok[chromosome_column_index + 1].strip() )+length_expanded
		if ChrID in regionID_dict:	
			for i in regionID_dict[ChrID] : 
				#if  (chrID_dict[i] == ChrID) and (start_dict[i] <= start_pos) and (end_dict[i] >= end_pos) : 
	#			if  (chrID_dict[i] == ChrID):
	#				if ((start_dict[i] <= start_pos) and (end_dict[i] >= end_pos)):					
	#					fout.write(regionID_dict[i] + '\toverlap:\t' + ChrID + '\t' + str(start_pos) + '\t' + str(end_pos) + '\t' + str(end_pos - start_pos +1) + '\t' + line)
	#					counted = True
	#				elif ((start_dict[i] < start_pos) and (end_dict[i] > start_pos)):
	#					fout.write(regionID_dict[i] + '\toverlap:\t' + ChrID + '\t' + str(start_pos) + '\t' + str(min(end_pos, end_dict[i])) + '\t' + str( min(end_pos, end_dict[i]) - start_pos +1) + '\t' + line)
	#					counted = True
	#				elif ((start_dict[i] < end_pos) and (end_dict[i] > end_pos)):
	#					fout.write(regionID_dict[i] + '\toverlap:\t' + ChrID + '\t' + str(max(start_dict[i], start_pos)) + '\t' + str(end_pos) + '\t' + str( end_pos -  max(start_dict[i], start_pos) +1) + '\t' + line)
	#					counted = True
	#				elif ((start_dict[i] >= start_pos) and (end_dict[i] <= end_pos)):
	#					fout.write(regionID_dict[i] + '\toverlap:\t' + ChrID + '\t' + str(start_dict[i]) + '\t' + str(end_dict[i])  + '\t' + str( end_dict[i] - start_dict[i] +1) + '\t' + line)
	#					counted = True
		#		if (((start_dict[ChrID][i] <= start_pos) and (end_dict[ChrID][i] >= start_pos))) or \
		#				(((start_dict[ChrID][i] <= end_pos) and (end_dict[ChrID][i] >= end_pos))):
				if (start_dict[ChrID][i] > end_pos) or (end_dict[ChrID][i] < start_pos):
					pass
				else:
					overlap = min( end_dict[ChrID][i], end_pos ) - max( start_dict[ChrID][i], start_pos ) + 1
					if overlap > max_overlap:
						max_overlap = overlap
						rID_maxOvrlp = i
					counted = True
			if counted:
				collectedLines = collectedLines + 1
				fout.write(line.strip() + '\t' + regionID_dict[ChrID][rID_maxOvrlp] + '\t' \
							+ str(max_overlap) + "\t%.2f\n" \
							% ( (1.0 * max_overlap) / ( end_pos - start_pos + 1) ) )
#							% ( (1.0 * max_overlap) / min ( end_pos - start_pos + 1, \
#							end_dict[ChrID][rID_maxOvrlp] - start_dict[ChrID][rID_maxOvrlp] + 1 ) ) # the proportion is printed for the smaller of the two regions
				counted = False
			else:
				fout.write(line)
		else:
#			print "chromosome %s was not in %s," % (ChrID, sys.argv[1])
			fout.write(line)
			
		Lines = Lines + 1
		if ( Lines % 1000 == 0):
			sys.stdout.write("\r   collecting %d regions out of %d" % (collectedLines, Lines))
			sys.stdout.flush()

	except (ValueError, IndexError):
		print "faulty line, perhaps header?: %s" % line.strip()
		fout.write(line)
		pass

print "\n\nFor total ", Lines, " regions in ", sys.argv[4].strip(), ", ", collectedLines, " were marked."
print "Printing to ", sys.argv[5].strip(), ": \n"
fin_ToBeFiltered.close()
fout.close()

print "done"
