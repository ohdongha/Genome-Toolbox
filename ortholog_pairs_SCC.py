#!/usr/bin/env python
import sys, os, argparse
from argparse import RawTextHelpFormatter

##############################
### 0.1 script description ###
##############################
synopsis1 = "\
  - given gene expression matrix for two species and ortholog pairs, add\n\
  Spearman's correlation coefficient (SCC) or Euclidean/cosine distance (DIS)\n\
  similarity to the ortholog pair file.\n"
  
synopsis2 = "detailed description:\n\
 0. Pre-requisite:\n\
  - scipy\n\
 1. Input files and options\n\
  - <input_ortholog_pair>: tab-delimited, with ortholog pair ID, followed by geneIDs\n\
     from species 1 and 2; must have a header; can have additional columns\n\
  - <input_species1>: tab-delimited, with gene ID, followed by expression values\n\
     for N samples, for species 1;\n\
  - <input_species2>: tab-delimited, with gene ID, followed by expression values\n\
     for N samples, for species 2;\n\
  - '-d'|'--distance': : instead of SCC (and p-value), add Euclidean and cosine \n\
     distances (EucDis and CosDis) and similarities (EucSim and CosSim) as separate\n\
     columns; EucSim = 1/(1 + EucDis) and CosSim = 1 - CosDis ; by default [False];\n\
  - '-N N': assumes there are N samples in the expression matrix; by default,\n\
     sample numbers (i.e. columns after gene ID) for species 1 will be used;\n\
  - if either of geneIDs in <input_ortholog_pair> does not have expression values,\n\
     print a warning to stderr (if '--print_warning' on) and skip the pair.\n\
 2. Output and options\n\
  - add as additional columns to <input_ortholog_pair> the Spearman's correlation\n\
     coefficients and p-values\n\
  - '--print_exp': print expression matrix from species 1 and species 2\n\
     as additional columns, comma-separated; (formerly '--print_matrix')\n\
  - output will be written to STDOUT (lazy ...)\n\
by ohdongha@gmail.com 20220308 ver 0.0\n\n"
#version_history
#20220321 ver 0.1 -d option to print Euclidean/cosine distances (DIS) instead of SCC
#20220319 ver 0.0.1 print warning and ignore (instead of error and stop) when the expression matrix does not have the gene
#20220308 ver 0.0 modified from pairplot_correlation_matrix_pairwise_orthologs_basal.py

#############################
### 0.2 parsing arguments ###
#############################
parser = argparse.ArgumentParser(description = synopsis1, epilog = synopsis2, formatter_class = RawTextHelpFormatter)
# positional arguments
parser.add_argument('input_ortholog_pair', type=argparse.FileType('r'))
parser.add_argument('input_species1', type=argparse.FileType('r'))
parser.add_argument('input_species2', type=argparse.FileType('r'))
# options
parser.add_argument('-d', '--distance', action="store_true", default=False) 
parser.add_argument('-N', dest="N", type=int, default= 0) 
parser.add_argument('--print_exp', action="store_true", default=False) 
parser.add_argument('--print_matrix', action="store_true", default=False) #depricated 
parser.add_argument('--print_warning', action="store_true", default=False) 
args = parser.parse_args()

# parsing arguments
if args.N < 3 and args.N != 0:
	sys.stderr.write("## To calculate SCC meaningfully, min 3 samples required, exiting\n")
	sys.exit()
else:
	num_samples = args.N

if args.print_matrix:
	args.print_exp = True
	
	
###########################
### 0.3 importing stuff ###
###########################
try:
	import numpy as np #, pandas as pd
	import scipy.stats as ss
	from scipy.spatial import distance
except ImportError as ErrorMessage:
	sys.stderr.write(str(ErrorMessage)+'\n')
	sys.exit()


###########################
### 1. read input files ###
###########################
## 1.1 reading expression matrix for species1
sys.stderr.write("## Reading %s as expression matrix file for the 1st species \n" % args.input_species1.name )
species1_dict = dict() # key = gene ID, value = list of expression values
get_N = False

if num_samples == 0:
	sys.stderr.write("## Number of samples will be obtained from the 1st line of %s. \n" % args.input_species1.name )
	get_N = True
	
for line in args.input_species1:
	tok = line.strip().split('\t')
	if get_N:
		num_samples = len(tok) - 1
		get_N = False
		sys.stderr.write("## Number of samples = %d. \n" % num_samples )
	try:
		species1_dict[ tok[0] ] = tok[1:num_samples+1]
	except IndexError:
		sys.stderr.write("## Warning: ignored a line without correct number of samples: %s\n" % line )
		
sys.stderr.write("## Read total %d genes (may include the header line) with %d samples.\n" % (len( species1_dict ), num_samples) )
args.input_species1.close()

## 1.2 reading expression matrix for species2
sys.stderr.write("## Reading %s as expression matrix file for the 2nd species \n" % args.input_species2.name )
species2_dict = dict() # key = gene ID, value = list of expression values
for line in args.input_species2:
	tok = line.strip().split('\t')
	try:
		species2_dict[ tok[0] ] = tok[1:num_samples+1]
	except IndexError:
		sys.stderr.write("## Warning: ignored a line without correct number of samples: %s\n" % line )
		
sys.stderr.write("## Read total %d genes (may include the header line) with %d samples.\n" % (len( species2_dict ), num_samples) )
args.input_species2.close()


########################################
### 2. print ortholog pair + SCC/DIS ###
########################################
sys.stderr.write("## Reading %s as <input_ortholog_pair> file, \n" % args.input_ortholog_pair.name )
exp1 = []; exp2 = [] # 1D-array of gene expression for species 1 and 2 
if args.distance:
	EucDis = 0.0; EucSim = 0.0; CosDis = 0.0; CosSim = 0.0
else:
	Sr = 0.0; Sp = 0.0
newline = ""
skippedError = False
zeroExp = False; num_zeroExp = 0; num_line = 0
header = True

sys.stderr.write("## Printing SCC, etc. to STDOUT \n")
for line in args.input_ortholog_pair:
	tok = line.strip().split('\t')
	newline = ""
	zeroExp = False
	if header:
		if args.distance:
			newline = line.strip() + '\tEucDis\tEucSim\tCosDis\tCosSim'		
		else:
			newline = line.strip() + '\tSCC\tp'
		if args.print_exp:
			newline = newline + '\texp1\texp2'
		header = False
	else:
		try:
			exp1 = np.array( species1_dict[tok[1]], float )
			exp2 = np.array( species2_dict[tok[2]], float )
			if ( not np.any(exp1) ) or ( not np.any(exp2) ): # check whether either is an array of zeroes.
				zeroExp = True
				num_zeroExp += 1
			num_line +=1
		except IndexError:
			if args.print_warning:
				sys.stderr.write("## Warning: ignored a line without pair of gene IDs: %s\n" % line )
			skippedError = True
		except KeyError:
			if args.print_warning:
				sys.stderr.write("## Warning: ignored a pair without expression values: %s\n" % tok[0:3] )
			skippedError = True
		
		if args.distance:
#			EucDis = distance.euclidean(exp1, exp2) # for some reason this gives an error ...
			if not zeroExp:
				EucDis = np.linalg.norm(exp1-exp2)
				EucSim = 1.0 / (1.0 + EucDis)
				CosDis = distance.cosine(exp1, exp2)			
				CosSim = 1.0 - CosDis
				newline = line.strip() + '\t%.4f\t%.4f\t%.4f\t%.4f' % (EucDis, EucSim, CosDis, CosSim)
			else:
				newline = line.strip() + "\tNaN" * 4 # don't calculate Dis/Sim if either exp1 or exp2 zeros
		else:
			if not zeroExp:
				Sr, Sp = ss.spearmanr(exp1, exp2)
				newline = line.strip() + '\t%.4f\t%.2E' % (Sr, Sp)
			else:
				newline = line.strip() + "\tNaN" * 4 # don't calculate Sr/Sp if either exp1 or exp2 zeros
		if args.print_exp:		
			newline = newline + '\t%s\t%s' % \
				(','.join( list( map(str, exp1)) ), ','.join( list( map(str, exp2)) ) )
	if newline != "":
		print(newline)

if not args.print_warning and skippedError:
	sys.stderr.write("## Some pairs in %s were skipped; run with '--print_warning' option to view details.\n" % args.input_ortholog_pair.name ) 

sys.stderr.write("## Total %d valid pairs, %d were skipped for one or both of the pair having zero expression values\n" % (num_line, num_zeroExp ) )
sys.stderr.write("## All done?\n" )
