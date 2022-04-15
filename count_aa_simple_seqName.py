#!/usr/bin/env python
#count_nt.py input.txt output.txt
import sys

fin = open(sys.argv[1], 'r')
#fout = open(sys.argv[2], 'w')
fout2 = open(sys.argv[2]+".simple_seqName.count", 'w')

seq_size = 0
head = ''
seq = list()
AminoAcids = set('ARNDBCEQZGHILKMFPSTWYVXarndbceqzghilkmfpstwyvx')

for line in fin:
    if line[0] == '>':     # beginning of a sequence
        # before processing, the last sequence must be written
        if(head != ''):
#            new_head = '>' + head[:-1] + '\t' + str(len(seq)) + '\n' 
#            new_head = '>' + head.strip() + '\t' + str(len(seq)) + '\n' 
            new_head = head[:-1].split()[0] + '\t' + str(len(seq)) + '\n' # print only the first potion of seq header, plus length
#            fout.write(new_head)
            fout2.write(new_head)
#            fout.write("".join(seq)+ '\n')
        # start a new sequence
        seq = list()
        head = line[1:]
    else: # in the middle of sequence
        for c in line:
            if(c in AminoAcids):
                seq.append(c)

# write the last seq
#new_head = '>' + head[:-1] + '\t' + str(len(seq)) + '\n' 
new_head = head[:-1].split()[0] + '\t' + str(len(seq)) + '\n' # print only the first potion of seq header, plus length
#fout.write(new_head)
fout2.write(new_head)
#fout.write("".join(seq)+ '\n')


