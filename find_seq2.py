#!/usr/bin/env python
#synopsis : find_seq <list.txt> <fasta.txt> <output.txt>
#find sequences of genes in list.txt from fasta.txt and print to output.txt

import sys
#import re

f1 = open(sys.argv[1], 'r')
contigSet = set();

for line in f1:
    contigSet.add(line)

# Demanded contigs have been collected in contigSet    

f2 = open(sys.argv[2], 'r')
fout = open(sys.argv[3], 'w')

collect = False

for line in f2:
    if line[0] == '>':
    	tok = line[1:].split()
    	if (tok[0]+'\n' in contigSet) or (tok[0] in contigSet) or (line[1:-1] in contigSet) or (line[1:] in contigSet):
    	#if (line[1:] in contigSet):
    		collect = True
    		fout.write(line);
    	else:
    		collect = False
    else:
        if collect:
            fout.write(line);
