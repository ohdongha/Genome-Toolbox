#!/usr/bin/env python

synopsis = "\n\n### usage: extract_seq.py <input.fa> <region.list> <output.txt> <output_mode>\n\
### extract sequences from <input.fa> for the regions described in <region.list> and write to <output.txt>.\n\
### <input.fa> should be fasta file with nucleotide sequences.\n\
### <region.list> contains 'SeqID', 'chromosome/contig', 'start', and 'end position', tab-delimited.\n\
### if <output_mode> is '0', extracted sequences will be added as the 4th column, in each line of ...\n\
### ... <region.list>, and printed to <output.txt>.\n\
### if <output_mode> is '1', <output.txt> will be a fasta file, with each line of ...\n\
### ... <region.list> as the sequence header.\n\
### copyleft by ohdongha@gmail.com 20151104 ver 1.0\n\n"
	
#function to get nucleotides from a string
def get_nucleotide(str1):
		return "".join(re.findall('[ATGCNatgcnRYSWKMBDHVryswkmbdhv]',str1))	

import sys, re, os

try:
	fin_fasta = open(sys.argv[1], 'r')
	fin_list = open(sys.argv[2], 'r')
	fout = open(sys.argv[3], 'w')
	output_mode = int(sys.argv[4])
except (ValueError, IndexError) :
	print synopsis
	sys.exit(0)

## reading in <input.fa>
print "\nreading %s" % sys.argv[1]
seq_in_fasta_dict=dict()
chrID=""
seq_in_line = ""
collected_seq = ""

seq_count = 0
nt_count = 0
collect = 0

for line in fin_fasta:
	if(line[0] == '>'):
		if chrID != "":
			seq_in_fasta_dict[chrID] = collected_seq
		chrID = line[1:-1].split()[0]
		print chrID
		collected_seq = ""
		seq_in_line = ""
		seq_count = seq_count + 1
		collect = 1
	elif collect :
#		seq_in_line = get_nucleotide(line)  ## use this if you expect dirty fasta file, will slow substantially
		seq_in_line = line.strip()
		nt_count = nt_count + len(seq_in_line)
		collected_seq = collected_seq + seq_in_line
		
seq_in_fasta_dict[chrID] = collected_seq ## writing the last sequence
print "total %d sequences, %d nucleotides were read from %s ... " % (seq_count, nt_count, sys.argv[1])
fin_fasta.close()


## reading in <region.list>, extract sequences, and output.	
print "\nreading %s" % sys.argv[2]

chrID = ""
start = 0 
end = 0
seq_extracted = ""
line_number = 0
line_extracted = 0
		
for line in fin_list:
	tok = line.strip().split('\t')
	line_number = line_number + 1
	try:
		if (len(tok)==4 and int(tok[2]) <= int(tok[3])):
			chrID = tok[1].strip()
			start = int(tok[2].strip())
			end = int(tok[3].strip())
			if chrID in seq_in_fasta_dict:
				if (start >= 0 and end <= len(seq_in_fasta_dict[chrID])):
					seq_extracted = seq_in_fasta_dict[chrID][start-1:end]
					line_extracted = line_extracted + 1
					if output_mode == 0:
						fout.write(line.strip() + '\t' + seq_extracted + '\n')
					else:
						fout.write('>' + line.strip() + '\n' + seq_extracted + '\n')					
				else:
					print "Line %d in %s: start and/or end positions out of range: %s" % (line_number, sys.argv[2], line.strip())
			else:
				print "Line %d in %s: chr/contig not exist in %s: %s" % (line_number, sys.argv[2], sys.argv[1], line.strip())
		else:
			print "Line %d in %s: invalid: %s" % (line_number, sys.argv[2], line.strip())
	except (ValueError, IndexError):
		print "Line %d in %s: invalid: %s" % (line_number, sys.argv[2], line.strip())
		pass

print "for regions descriged in %s, %d were successfully extracted from %s, while %d failed.\n" % (sys.argv[2], line_extracted, sys.argv[1], line_number - line_extracted)
print "extracted sequences written to %s ..." % sys.argv[3]	
fin_list.close()
fout.close()