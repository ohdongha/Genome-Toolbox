#!/usr/bin/env python
import sys, subprocess, argparse
from argparse import RawTextHelpFormatter

###################################################
### 0. script description and parsing arguments ###
###################################################
synopsis1 = "synopsis:\n\
 - rename the 'transcript_id' field in the 9th column of a .gtf file, given a tab-delimited list of old and new transcript IDs.\n\
 - with '-e' option, can extract subset of transcripts.\n\
 - with '-g' option, can also rename 'gene_id' and 'gene_name' fields.\n"
synopsis2 = "detailed description:\n\
 - based on <2bRenamed_list>, replace names of transcripts in <input_gtf> and and write to <output_gtf>.\n\
 - tab-delimited <2bRenamed_list> includes old and new transcript IDs; assume the transcript id not to be changed if no new ID given.\n\
 - from the 9th column of <input_gtf>, only 'transcript_id' field will be renamed and written to <output_gtf>\n\
 - '-e'|'--extract': extract and rename only those transcripts included in <2bRenamed_list>; default behavior is to print all without renaming those not included.\n\
 - '-x'|'--exclude': extract only those transcripts NOT included in <2bRenamed_list>; does not perform renaming; [False]\n\
 - '-g'|'--gene_id': rename also 'gene_id' and 'gene_name' fields; <2bRenamed_list> should contain old and new transcript IDs, plus the new gene ID and gene name, tab-delimited and one entry per line.\n\n\
by ohdongha@gmail.com 20211204 ver 0.4\n\n"

#version_history
#20211204 ver 0.4 # added '-g' option to rename also gene_id and gene_name fields
#20211122 ver 0.3.1 # minimal modification to make it work with python 3
#20180624 ver 0.3 # added an option to exclude transcripts in the list
#20171017 ver 0.2 # added an option to extract transcripts in the list only
#20160328 ver 0.1 # if new transcript ID is not given, old transcript ID will be retained.
#20151129 ver 0.0 

#### Example: lines in a <input_gtf> file
##ch1-1	transdecoder	exon	933	2176	.	+	.	transcript_id "TCONS_00000001|m.1"; gene_id "TCONS_00000001|g.1"; gene_name "ORF";
##ch1-1	transdecoder	exon	2564	2651	.	+	.	transcript_id "TCONS_00000001|m.1"; gene_id "TCONS_00000001|g.1"; gene_name "ORF";
##ch1-1	transdecoder	exon	2763	3532	.	+	.	transcript_id "TCONS_00000001|m.1"; gene_id "TCONS_00000001|g.1"; gene_name "ORF";
##ch1-1	transdecoder	exon	3729	4716	.	+	.	transcript_id "TCONS_00000001|m.1"; gene_id "TCONS_00000001|g.1"; gene_name "ORF";
##ch1-1	transdecoder	exon	4895	4983	.	+	.	transcript_id "TCONS_00000001|m.1"; gene_id "TCONS_00000001|g.1"; gene_name "ORF";
##ch1-1	transdecoder	exon	5068	6122	.	+	.	transcript_id "TCONS_00000001|m.1"; gene_id "TCONS_00000001|g.1"; gene_name "ORF";
##ch1-1	transdecoder	CDS	2166	2176	.	+	0	transcript_id "TCONS_00000001|m.1"; gene_id "TCONS_00000001|g.1"; gene_name "ORF";
##ch1-1	transdecoder	CDS	2564	2651	.	+	1	transcript_id "TCONS_00000001|m.1"; gene_id "TCONS_00000001|g.1"; gene_name "ORF";
##ch1-1	transdecoder	CDS	2763	3532	.	+	0	transcript_id "TCONS_00000001|m.1"; gene_id "TCONS_00000001|g.1"; gene_name "ORF";
##ch1-1	transdecoder	CDS	3729	3822	.	+	1	transcript_id "TCONS_00000001|m.1"; gene_id "TCONS_00000001|g.1"; gene_name "ORF";
##...

#### Example: lines in a <2bRenamed_list> file
##TCONS_00065516|m.58617	Tp7g37420.a
##TCONS_00066150|m.58581	Tp7g37350.a
##TCONS_00066146|m.58566	Tp7g37340.a
##TCONS_00065459|m.58443	Tp7g36860.a
##TCONS_00066071|m.58420	Tp7g36760.a
##TCONS_00065432|m.58405	Tp7g36700.a
##TCONS_00065427|m.58394	Tp7g36680.a
##TCONS_00065425|m.58392	Tp7g36670.a
##TCONS_00066055|m.58380	Tp7g36630.a
##TCONS_00066053|m.58376	Tp7g36620.a
##TCONS_00066035|m.58344	Tp7g36470.a
##...

parser = argparse.ArgumentParser(description = synopsis1, epilog = synopsis2, formatter_class = RawTextHelpFormatter)

# positional parameters
parser.add_argument('_2bRenamed_list', type=argparse.FileType('r'))
parser.add_argument('input_gtf', type=argparse.FileType('r'))
parser.add_argument('output_gtf', type=argparse.FileType('w'))

# options
parser.add_argument('-e', '--extract', action="store_true", default=False)
parser.add_argument('-x', '--exclude', action="store_true", default=False)
parser.add_argument('-g', '--gene_id', action="store_true", default=False)

args = parser.parse_args()


#######################################
### 1. reading in <_2bRenamed_list> ###
#######################################
transcriptID_dict = dict() # k = old transcript_id; v = new transcript_id
if args.gene_id:
	geneID_dict = dict()  # k = old transcript_id; v = new gene_id
	geneName_dict = dict() # k = old transcript_id; v = new gene_name

print( "reading %s as the <_2bRenamed_list>:" % args._2bRenamed_list.name )	
num_line = 0

for line in args._2bRenamed_list:
	tok = line.split('\t')
	if args.gene_id:
		try:
			transcriptID_dict[tok[0].strip()] = tok[1].strip()
			geneID_dict[tok[0].strip()] = tok[2].strip()
			geneName_dict[tok[0].strip()] = tok[3].strip()
			num_line += 1
		except (IndexError) :
			print("## Warning: with '-g' option, <2bRenamed_list> should have 4 columns; line ignored.")
	else:
		num_line += 1
		try:
			transcriptID_dict[tok[0].strip()] = tok[1].strip()
		except (IndexError) :
			transcriptID_dict[tok[0].strip()] = tok[0].strip()
args._2bRenamed_list.close()
print( "read %d entries." % num_line )

##########################################################
### 2. renaming <input_gtf> and writing to <output_gtf>###
##########################################################
ninthColumn_records = ""
ninthColumn_transcriptID = ""
num_line = 0
num_line_renamed = 0
num_line_kept = 0

print( "reading %s as the <input_gtf>:" % args.input_gtf.name )

for line in args.input_gtf:
	num_line += 1
	tok = line.replace('\"','').split('\t')
	if not args.exclude:
		try:
			ninthColumn_records = tok[8].split(';')
			ninthColumn_transcriptID = "NA"
			for record in ninthColumn_records:
				if record.strip().split(' ')[0] == 'transcript_id':
					ninthColumn_transcriptID = record.strip().split(' ')[1]
			if ninthColumn_transcriptID in transcriptID_dict:
				if args.gene_id:
					tok[8] = 'transcript_id "' + transcriptID_dict[ninthColumn_transcriptID] + '";' \
						+ 'gene_id "' + geneID_dict[ninthColumn_transcriptID] + '";' \
						+ 'gene_name "' + geneName_dict[ninthColumn_transcriptID] + '"\n'
				else:
					tok[8] = 'transcript_id "' + transcriptID_dict[ninthColumn_transcriptID] + '";\n'
				args.output_gtf.write('\t'.join(tok))
				num_line_renamed += 1
			elif args.extract == False:
				args.output_gtf.write(line)
				num_line_kept += 1
		except (ValueError, IndexError) :
			print( line.strip() + "\t:invalid_line_%d" % num_line )
	else:
		try:
			ninthColumn_records = tok[8].split(';')
			ninthColumn_transcriptID = "NA"
			for record in ninthColumn_records:
				if record.strip().split(' ')[0] == 'transcript_id':
					ninthColumn_transcriptID = record.strip().split(' ')[1]
			if ninthColumn_transcriptID not in transcriptID_dict:
				args.output_gtf.write(line)
				num_line_kept += 1
		except (ValueError, IndexError) :
			print( line.strip() + "\t:invalid_line_%d" % num_line )

print( "out of %d lines, %d renamed/extracted, %d untouched/kept." % (num_line, num_line_renamed, num_line_kept) )
print( "done\n" )
args.input_gtf.close()
args.output_gtf.close()
