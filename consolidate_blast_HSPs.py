#!/usr/bin/env python
import os, sys, argparse
from argparse import RawTextHelpFormatter

###################################################
### 0. script description and parsing arguments ###
###################################################

synopsis1 = "\
  convert a BLAST tabular output into a table of one query-subject pair per line\n\
  by consolidating HSPs and calculate proportion of query and subject covered by\n\
  HSPs (COV) and approximate proportion of identical sequences within HSPs (IDN).\n"

synopsis2 = "detailed description:\n\
 1. Input:\n\
  - <input> is a tabulated blast+ output using -outfmt '6 std qlen slen'\n\
 2. Output:\n\
  - <output> contains the following for each query-subject pair, tab-delimited:\n\
     query(q), subject(s), num_HSPs, total_score, qHSP_nt, qHSP_ovl, qIDN_nt,\n\
     qHSP_cov, qHSP_idn, sHSP_nt, sHSP_ovl, sIDN_nt, sIDN_cov, and sHSP_idn\n\
  - total_sc == sum of blast hit scores for all HSPs,\n\
  - HSP_nt == total nucleotides (nt) in HSPs,\n\
  - IDN_nt == approximate identical nt, i.e., HSP_nt * average%IDN / 100,\n\
  - HSP_ovl == length of overlap among HSPs,\n\
  - qHSP_cov == qHSP_nt / qlen; sHSP_cov == sHSP_nt / slen,\n\
  - HSP_idn == IDN_nt / HSP_nt,\n\
 3. Options:\n\
  - '-H/--header': include a header line in the output; default==False\n\
  - '-s/--stitle': expect blast output with -outfmt '6 std qlen slen stitle'\n\
     stitle is added as an additional last column; default==False\n\
  - '-p/--blastp': input is from blastp/mmseqs; default==False\n\
  - '--min_qHSP_cov': minimum qHSP_cov to keep (0.0~1.0), default==0.0,\n\
  - '--min_sHSP_cov': minimum sHSP_cov to keep (0.0~1.0), default==0.0,\n\
  - '--min_qHSP_idn': minimum qHSP_idn to keep (0.0~1.0), default==0.0,\n\
  - '--min_sHSP_idn': minimum sHSP_idn to keep (0.0~1.0), default==0.0,\n\
  - '--max_evalue': ignore alignment with e-value larger than this value,\n\
     default==1e-05,\n\
 4. Misc:\n\
  - for BLASTP results, '_nt' becomes '_aa (amino acids)',\n\
  - ignores strands of HSPs and calculates just the total coverages.\n\
 by ohdongha@gmail.com 20220309 ver 0.1.7\n"


output_header_list = ["q", "s", "num_HSPs", "total_sc", "qHSP_nt", "qHSP_ovl", "qIDN_nt", "qHSP_cov", "qHSP_idn", "sHSP_nt", "sHSP_ovl", "sIDN_nt", "sHSP_cov", "sHSP_idn"]
 
#version_history
#20220309 ver 0.1.7 made compatible with python3
#20201201 ver 0.1.6 print _cov and _idn values to 3 digits ... because of reasons ...
#20190331 ver 0.1.5 added evalue cutoff '--max_evalue'; added a progression counter 
#20180417 ver 0.1.4 deals with mmseqs2 output, where percent_idn is actually proportion_idn < 1.0 
#20180404 ver 0.1.3 deals with cases when qlen == 0 
#20180306 ver 0.1.2 deals with -outfmt '6 std qlen slen stitle' # 0312 bug fixed
#20180103 ver 0.1 added total_sc, qHSP_ovl, sHSP_ovl; deal with HSPs in reverse strand of subject,
#20180102 ver 0.0

parser = argparse.ArgumentParser(description = synopsis1, epilog = synopsis2, formatter_class = RawTextHelpFormatter)

## positional arguments
parser.add_argument('input', type=argparse.FileType('r'))
parser.add_argument('output', type=argparse.FileType('w'))

## options to filter results
parser.add_argument('-H', '--header', action="store_true", default=False, help="see below")
parser.add_argument('-s', '--stitle', action="store_true", default=False, help="see below")
parser.add_argument('-p', '--blastp', action="store_true", default=False, help="see below")
parser.add_argument('--min_qHSP_cov', dest="min_qHSP_cov", type=float, default=0.0)
parser.add_argument('--min_sHSP_cov', dest="min_sHSP_cov", type=float, default=0.0)
parser.add_argument('--min_qHSP_idn', dest="min_qHSP_idn", type=float, default=0.0)
parser.add_argument('--min_sHSP_idn', dest="min_sHSP_idn", type=float, default=0.0)
parser.add_argument('--max_evalue', dest="max_evalue", type=float, default=1e-05)

args = parser.parse_args()

min_qHSP_cov = args.min_qHSP_cov
min_sHSP_cov = args.min_sHSP_cov
min_qHSP_idn = args.min_qHSP_idn
min_sHSP_idn = args.min_sHSP_idn
max_evalue = args.max_evalue


##############################################
### 1. reading, consolidating, and writing ###
##############################################
first_line = True
output_line = list()

# print header
if args.blastp:
	output_header_list = ["q", "s", "num_HSPs", "total_sc", "qHSP_aa", "qHSP_ovl", "qIDN_aa", "qHSP_cov", "qHSP_idn", "sHSP_aa", "sHSP_ovl", "sIDN_aa", "sHSP_cov", "sHSP_idn"]
else:
	output_header_list = ["q", "s", "num_HSPs", "total_sc", "qHSP_nt", "qHSP_ovl", "qIDN_nt", "qHSP_cov", "qHSP_idn", "sHSP_nt", "sHSP_ovl", "sIDN_nt", "sHSP_cov", "sHSP_idn"]
if args.stitle:
	output_header_list.append("stitle")
if args.header:
	args.output.write('\t'.join(output_header_list) + '\n')
	
query = ""
subject = ""
percent_idn = 0.0
idn_in_proportion = False
qS = 0
qE = 0
sS = 0 
sE = 0
ev = 0.0
sc = 0.0
qlen = 0
slen = 0

num_HSPs = 0
total_sc = 0.0

qHSP_coords = list()
qHSP_nt = 0
qHSP_nt_2bAdded = 0
qHSP_ovl = 0
qIDN_nt = 0
qHSP_cov = 0.0
qHSP_idn = 0.0

sHSP_coords = list()
sHSP_nt = 0
sHSP_nt_2bAdded = 0
sHSP_ovl = 0
sIDN_nt = 0
sHSP_cov = 0.0
sHSP_idn = 0.0

num_lines_total = sum(1 for line in args.input)
num_line = 0
args.input.seek(0)

for line in args.input:
	# counter display
	num_line += 1
	if ( num_line % 10000 == 0):
		sys.stdout.write("\r   processed %d / %d lines " % (num_line, num_lines_total) )
		sys.stdout.flush()
		
	# start
	tok = line.split('\t')
	try:
		ev = float(tok[10])
	except ValueError:
		sys.stderr.write( "invalid e-value?  skipping: %s" % line )
		ev = 9999.0
		
	if ev <= max_evalue:	# lines with e-value larger than the cutoff is ignored
		if tok[0] != query or tok[1] != subject:
			# print the previous query-species pair, if it is not the first line (don't forget to also print the last line later)
			if first_line == False:
				try:
					qHSP_cov = float(qHSP_nt) / qlen
					qHSP_idn = float(qIDN_nt) / qHSP_nt
					sHSP_cov = float(sHSP_nt) / slen
					sHSP_idn = float(sIDN_nt) / sHSP_nt
				except ZeroDivisionError:
					sys.stderr.write( "ZeroDivisionError in line: %s" % line.strip() )
					qHSP_cov = 0.0 ; qHSP_idn = 0.0 ; sHSP_cov = 0.0; sHSP_idn = 0.0
					
				if qHSP_cov >= min_qHSP_cov and qHSP_idn >= min_qHSP_idn and \
						sHSP_cov >= min_sHSP_cov and sHSP_idn >= min_sHSP_idn:
					output_line = [query, subject, '%d'%num_HSPs, '%.1f'%total_sc,\
							'%d'%qHSP_nt, '%d'%qHSP_ovl, '%d'%qIDN_nt, '%.3f'%qHSP_cov, '%.3f'%qHSP_idn,\
							'%d'%sHSP_nt, '%d'%sHSP_ovl, '%d'%sIDN_nt, '%.3f'%sHSP_cov, '%.3f'%sHSP_idn ]
					if args.stitle:
						output_line.append(stitle)				
					args.output.write('\t'.join(output_line) + '\n')				
			# refreshing stitle
				if args.stitle:
					stitle = tok[-1].strip()
	
			else:
				first_line = False
				# initializing stitle
				if args.stitle:
					stitle = tok[-1].strip()
	
			# initializing
			query = tok[0]
			subject = tok[1]
			qlen = int(tok[12])
			slen = int(tok[13])
			qHSP_coords = [0] * qlen
			sHSP_coords = [0] * slen
			
			num_HSPs = 0
			total_sc = 0.0
			qHSP_nt = 0
			qHSP_ovl = 0
			qIDN_nt = 0
			qHSP_cov = 0.0
			qHSP_idn = 0.0
			sHSP_nt = 0
			sHSP_ovl = 0
			sIDN_nt = 0
			sHSP_cov = 0.0
			sHSP_idn = 0.0
			
		# now process each HSP ...			
		percent_idn = float(tok[2])
		if percent_idn < 1.0 or idn_in_proportion:
			if not idn_in_proportion:
				idn_in_proportion = True
				sys.stderr.write( "identity/similarity values appear to be proportions, rather than percentages," )
			percent_idn = percent_idn * 100.0
		qs = int(tok[6])
		qe = int(tok[7]) 
		ss = int(tok[8])
		se = int(tok[9])
		sc = float(tok[11])
		
		num_HSPs += 1
		total_sc += sc
		
		qHSP_nt_2bAdded = 0
		for i in range (qs - 1, qe):
			if qHSP_coords[i] == 0:
				qHSP_coords[i] = 1
				qHSP_nt_2bAdded += 1
			else:
				qHSP_ovl += 1
		qHSP_nt += qHSP_nt_2bAdded
		qIDN_nt += int( qHSP_nt_2bAdded * percent_idn / 100.0 )
	
		sHSP_nt_2bAdded = 0
		for i in range ( min(ss, se) - 1, max(ss, se)): # subject HSP coords can be in reverse direction ...
			if sHSP_coords[i] == 0:
				sHSP_coords[i] = 1
				sHSP_nt_2bAdded += 1
			else:
				sHSP_ovl += 1
		sHSP_nt += sHSP_nt_2bAdded
		sIDN_nt += int( sHSP_nt_2bAdded * percent_idn / 100.0 )
	
# process the last HSP:
try:
	ev = float(tok[10])
except ValueError:
	sys.stderr.write( "invalid e-value?  skipping: %s" % line )
	ev = 9999.0
	
if ev <= max_evalue: # lines with e-value larger than the cutoff is ignored
	try:
		qHSP_cov = float(qHSP_nt) / qlen
		qHSP_idn = float(qIDN_nt) / qHSP_nt
		sHSP_cov = float(sHSP_nt) / slen
		sHSP_idn = float(sIDN_nt) / sHSP_nt
	except ZeroDivisionError:
		sys.stderr.write( "ZeroDivisionError in the last line!" ) 
		qHSP_cov = 0.0 ; qHSP_idn = 0.0 ; sHSP_cov = 0.0; sHSP_idn = 0.0
	
	if qHSP_cov >= min_qHSP_cov and qHSP_idn >= min_qHSP_idn and \
			sHSP_cov >= min_sHSP_cov and sHSP_idn >= min_sHSP_idn:
		output_line = [query, subject, '%d'%num_HSPs, '%.1f'%total_sc,\
				'%d'%qHSP_nt, '%d'%qHSP_ovl, '%d'%qIDN_nt, '%.3f'%qHSP_cov, '%.3f'%qHSP_idn,\
				'%d'%sHSP_nt, '%d'%sHSP_ovl, '%d'%sIDN_nt, '%.3f'%sHSP_cov, '%.3f'%sHSP_idn ]
		if args.stitle:
			output_line.append(stitle)
		args.output.write('\t'.join(output_line) + '\n')
	
args.input.close()
args.output.close()	
sys.stderr.write( "\ndone\n" )