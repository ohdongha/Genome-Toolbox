#!/usr/bin/env python
#version_history
#20170603 ver 0.0
#20170529 started writing

import sys
import argparse
from argparse import RawTextHelpFormatter

###################################################
### 0. script description and parsing arguments ###
###################################################

synopsis1 = "\
 remove genomic regions from a .gff file, splitting a scaffold when needed.\n"
synopsis2 = "detailed description:\n\
 1. Input files and parameters\n\
  - <list_length>: scfID (scaffoldID) and length, one per line;\n\
  - <list_2bRemoved>: scfID, start, and end, positions, one per line;\n\
     regions should not overlap with others and be SORTED by start positions \n\
     within a scaffold, if multiple regions to be removed in a scaffold;\n\
  *** DON'T FORGET TO SORT <list_2bRemoved>!! For example, use:\n\
       sort -k1,1 -k2,2n list_2bRemoved > tmp; mv tmp list_2bRemoved\n\
  - <input_gff>: genome annotation to be edited, in .gff format;\n\
  - all input should be tab-delimited text files.\n\
 2. Editing <input_gff>\n\
  - removes all features included in or overlapping with genomic regions listed\n\
     in <list_2bRemoved>;\n\
  - renames scaffolds numerically as scaffodID_01, scaffodID_02, etc., when \n\
     a scaffold cut in the middle into pieces;\n\
  - changes coordinates for features in renamed scaffolds accordingly; \n\
  - discards scaffolds shorter than MIN_SCAFFOLD_LEN (default=1000) after split;\n\
  - keeps all scaffolds not listed in <list_2bRemoved> unchanged.\n\
 3. Output\n\
  - writes edited genome annotation to <output_gff>;\n\
  - writes coordinates of newly split scaffolds to <output_gff>.list; this list\n\
     can be used to cut genome sequences using 'extract_seq.py'.\n\
 4. Misc. note\n\
  - keeps only features complete included in new scaffolds, without considering\n\
     parent-child relationship among features.\n\
 by ohdongha@gmail.com 20190527 ver 0.0.1\n"

#version_history
#20190527 ver 0.0.1 # the <output_gff>.list column order modified to have the new scaffold ID as the first column (so that it can be directly used by 'extract_seq.py'
#20170603 ver 0.0

# arguments and parameters
parser = argparse.ArgumentParser(description = synopsis1, epilog = synopsis2, formatter_class = RawTextHelpFormatter)

parser.add_argument('list_length', type=argparse.FileType('r'), help="list of chromosome/scaffolds length")
parser.add_argument('list_2bRemoved', type=argparse.FileType('r'), help="coordinates of genomic regions to be removed")
parser.add_argument('input_gff', type=argparse.FileType('r'), help=".gff file to be edited")
parser.add_argument('output_gff', type=argparse.FileType('w'), help="output file; see below for details")

parser.add_argument('-c', '--min_scaffold_len', type=int, default=1000, help="default=1000; see below") # 

args = parser.parse_args()
min_scf_len = args.min_scaffold_len

########################
### 1. reading lists ###
########################

# 1.1 reading <list_length>
scf_len_dict = dict() # dict with key=scfID, value=length
num_line = 0 # line counter

for line in args.list_length:
	num_line += 1
	tok = line.split('\t')
	try:
		scf_len_dict[tok[0]] = int(tok[1].strip())
	except (ValueError, IndexError) :
		print "Line %d is not valid in %s." % (num_line, args.list_length.name)

args.list_length.close()

# 1.2 reading <list_2bRemoved>
num_line = 0 # line counter
num_regions_2bRemoved = 0 # region_2bRemoved counter, also act as regionID
region_2bRemoved_scfID_dict = dict()	# dict with key=regionID (num_regions_2bRemoved), value=scfID
region_2bRemoved_start_dict = dict() # dict with key=regionID (num_regions_2bRemoved), value=start_position
region_2bRemoved_end_dict = dict() # dict with key=regionID (num_regio s_2bRemoved), value=end_position

for line in args.list_2bRemoved:
	num_line += 1
	num_regions_2bRemoved += 1
	tok = line.split('\t')
	try:
		region_2bRemoved_scfID_dict[num_regions_2bRemoved] = tok[0].strip()
		region_2bRemoved_start_dict[num_regions_2bRemoved] = int(tok[1].strip())
		region_2bRemoved_end_dict[num_regions_2bRemoved] = int(tok[2].strip())
	except (ValueError, IndexError) :
		print "Line %d is not valid in %s." % (num_line, args.list_2bRemoved.name)
		num_regions_2bRemoved -= 1 # so that the wrong entries can be re-written with the next line

args.list_2bRemoved.close()

#####################################################
### 2. editing <input_gff> and write <output_gff> ###
#####################################################
num_subscf = 0
scf_2modify_set = set() # set of scaffolds that need to be modified
scf_2discard_set = set() # set of scaffolds that can be completely thrown away
subscf_2keep_set = set() # set of all sub-scaffolds not shorter than the min_scaffold_len
scan_position = 0

new_scfID = ""
new_scf_start = 0
new_scf_end = 0
new_scf_len = 0

new_scf_start_dict = dict() # dict with key=new_scfID, value=start_position
new_scf_end_dict = dict() # dict with key=new_scfID, value=end_position
new_scf_offset_dict = dict() # dict with key=new_scfID, value=offset


# 2.1 create updated scfIDs and offset values for updated feature coordinates, and <output_gff>.list
fout_chop_list = open(args.output_gff.name + ".list", "w")
 
for scfID in sorted(scf_len_dict, key=scf_len_dict.get, reverse = True):

	# initializing scan for new scaffold
	scan_position = 0
	num_subscf = 0 
	num_subscf_2keep = 0
	
	# start scanning; at first, keep all split sub-scaffolds regardless of the length
	for	regionID in sorted(region_2bRemoved_scfID_dict): 
		if region_2bRemoved_scfID_dict[regionID] == scfID:
			num_subscf += 1		
			new_scf_start = min(scan_position + 1, scf_len_dict[scfID])
			new_scf_end = max(region_2bRemoved_start_dict[regionID] - 1, 1)
			new_scf_len = new_scf_end - new_scf_start + 1
			scan_position = region_2bRemoved_end_dict[regionID]

			# now determine whether to keep the sub-scaffold
			if new_scf_len >= min_scf_len :
				num_subscf_2keep += 1
				new_scfID = scfID + "_" + str(num_subscf_2keep).zfill(2)
				new_scf_start_dict[new_scfID] = new_scf_start
				new_scf_end_dict[new_scfID] = new_scf_end
				new_scf_offset_dict[new_scfID] = new_scf_start - 1 
				# when modifying feature coordinates, subtract offset value from original coordinates
				scf_2modify_set.add(scfID)
				subscf_2keep_set.add(new_scfID)
				print "%s: %d ~ %d to be kept as %s (len %d >= %d)" \
					% (scfID, new_scf_start, new_scf_end, new_scfID, new_scf_len, min_scf_len)
#				fout_chop_list.write("%s\t%d\t%d\t%s\n" % (scfID, new_scf_start, new_scf_end, new_scfID))
				fout_chop_list.write("%s\t%s\t%d\t%d\n" % (new_scfID, scfID, new_scf_start, new_scf_end)) # v0.1
			elif new_scf_len > 1:
				print "%s: %d ~ %d to be discarded (len %d < %d)" \
					% (scfID, new_scf_start, new_scf_end, new_scf_len, min_scf_len)
		
			
	# after scan, deal with the end of the scaffold
	if num_subscf == 0:
		print "%s is unchanged." % scfID
#		fout_chop_list.write("%s\t%d\t%d\t%s\n" % (scfID, 1, scf_len_dict[scfID], scfID))
		fout_chop_list.write("%s\t%s\t%d\t%d\n" % (scfID, scfID, 1, scf_len_dict[scfID]))
	else:
		num_subscf += 1
		new_scf_start = min(scan_position + 1, scf_len_dict[scfID])
		new_scf_end = scf_len_dict[scfID]
		new_scf_len = new_scf_end - new_scf_start + 1
		
		if new_scf_len >= min_scf_len :
			num_subscf_2keep += 1
			new_scfID = scfID + "_" + str(num_subscf_2keep).zfill(2)
			new_scf_start_dict[new_scfID] = new_scf_start
			new_scf_end_dict[new_scfID] = new_scf_end
			new_scf_offset_dict[new_scfID] = new_scf_start - 1 
			scf_2modify_set.add(scfID)
			subscf_2keep_set.add(new_scfID)
			print "%s: %d ~ %d to be kept as %s (len %d >= %d)" \
				% (scfID, new_scf_start, new_scf_end, new_scfID, new_scf_len, min_scf_len)
#			fout_chop_list.write("%s\t%d\t%d\t%s\n" % (scfID, new_scf_start, new_scf_end, new_scfID))
			fout_chop_list.write("%s\t%s\t%d\t%d\n" % (new_scfID, scfID, new_scf_start, new_scf_end)) # v0.1
		elif new_scf_len > 1:
			print "%s: %d ~ %d to be discarded (len %d < %d)" \
				% (scfID, new_scf_start, new_scf_end, new_scf_len, min_scf_len)
		
		# check whether the scaffold can be safely discarded
		if num_subscf_2keep == 0:
			print "%s can be safely discarded; no regions left longer than %d." \
				% (scfID, min_scf_len)
			scf_2discard_set.add(scfID)
			
fout_chop_list.close()


# 2.2 process the <input_gff> and write <output_gff>
num_line = 0

for line in args.input_gff:
	num_line += 1
	tok = line.split('\t')
	scfID = tok[0].strip()
	
	# decision tree to process each line
	if len(tok) != 9:
		print "line %d contains only %d fields; print without processing," % (num_line, len(tok))
		args.output_gff.write(line)
	elif scfID in scf_2modify_set :
		i = 1
		while ( scfID + "_" + str(i).zfill(2) ) in subscf_2keep_set:
			new_scfID = scfID + "_" + str(i).zfill(2)
			try:
				# keep only features that completely included in the new_scf 
				if new_scf_start_dict[new_scfID] <= int(tok[3]) and \
						new_scf_end_dict[new_scfID] >= int(tok[4]):
					tok[0] = new_scfID
					tok[3] = str( int(tok[3]) - new_scf_offset_dict[new_scfID] )
					tok[4] = str( int(tok[4]) - new_scf_offset_dict[new_scfID] )
					args.output_gff.write('\t'.join(tok) + '\n')
			except (ValueError, IndexError) :	
				print "unable to process line %d due to invalud fields," % num_line
			i += 1
	elif scfID not in scf_2discard_set :
		args.output_gff.write(line)

args.output_gff.close()
print "\ndone"