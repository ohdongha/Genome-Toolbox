#!/usr/bin/env python
import sys, os, argparse
from argparse import RawTextHelpFormatter

##############################
### 0.1 script description ###
##############################
synopsis1 = "\
  - plot histogram (seaborn.histplot) for values in a column of the input file\n\
  * to print histogram as a tab-delimited text, use 'create_hist.py'\n\
  * to plot density plot (kde, etc) use 'plot_hist_dist.py'"
synopsis2 = "detailed description:\n\
 0. Pre-requisite:\n\
  - python 3; numpy (np), scipy, pandas (pd), and matplotlib.pyplot (plt);\n\
  - seaborn (sns; script tested with v0.11.2);\n\
 1. Input\n\
  - <input> is a tab-delimited text;\n\
  - <col> is the column number to use for the plot;\n\
 2. Options and parameters:\n\
  - '-x': x-axis label; default: the column header (if available),\n\
  - '-y': y-axis label; default: 'Count',\n\
  - '-ylim': y_max; set max value (a positive integer) at y-axis; basically \n\
   add 'plt.ylim(0,y_max)' to the plot command; default = not set;\n\
  - '-o output_name': output file name will be <output_name> + '_hist.png';\n\
   if not specified, <input> w/o extension + '_<col>' + '_<xtitle>_hist.png';\n\
  - '-hist_opt': string of options to be passed to seaborn.histplot code;\n\
   start with a ',' and in quotation marks:\n\
      e.g. -hist_opt \",binwidth=0.1,binrange=(0.0,1.0)\"\n\
 4. Output:\n\
  - print the histogram plot as <output_name>_hist.png\n\
by ohdongha@gmail.com 20220412 ver 0.1\n\n"
#version_history
#20220412 ver 0.1 add option to set y-axis max range 
#20220219 ver 0.0 modified from plot_hist_dist.py ver 0.2 

#############################
### 0.2 parsing arguments ###
#############################
parser = argparse.ArgumentParser(description = synopsis1, epilog = synopsis2, formatter_class = RawTextHelpFormatter)
# positional arguments
parser.add_argument('input', type=argparse.FileType('r'))
parser.add_argument('col', type=int)
# options
parser.add_argument('-o', dest="output_name", type=str, default= "__NA__") 
parser.add_argument('-x', dest="xtitle", type=str, default= "x variable") 
parser.add_argument('-y', dest="ytitle", type=str, default= "__NA__") 
parser.add_argument('-ylim', dest="y_max", type=int, default=0) 
parser.add_argument('-hist_opt', dest="histplot_opt", type=str, default= "") 

args = parser.parse_args()

# parsing arguments
col_index = args.col
y_max = args.y_max
if args.output_name == "__NA__":
	outfile = os.path.splitext(args.input.name)[0] + '_' + str(col_index) # later add "_dist.png" etc,
else:
	outfile = args.output_name # if outfile is explicitly specified, don't add col index
#	outfile = args.output_name + '_' + str(col_index)


###########################
### 0.3 importing stuff ###
###########################
try:
	import numpy as np, pandas as pd
	import seaborn as sns
	import matplotlib.pyplot as plt
	plt.switch_backend('agg') 
	from scipy import stats
except ImportError as ErrorMessage:
	print(str(ErrorMessage))
	sys.exit()


#########################################
### 1. reading input and drawing plot ###
#########################################
Value_list = []
FaultyLines = 0
num_lines = 0

print("getting the %d (st/nd/th) column from %s" % (col_index, args.input.name))
for line in args.input:
	try:
		tok = line.split('\t')
		num_lines = num_lines + 1
		Value_list.append(float(tok[col_index-1].strip()))
	except (ValueError, IndexError) as err :
		if num_lines == 1 and args.xtitle == "x variable":
			args.xtitle = tok[col_index-1].strip()
#			print "use %s as the data name (i.e. x-axis title)" % args.xtitle
		else:
			print("Warning: %s at line %d ..." % (err, num_lines))
			FaultyLines = FaultyLines + 1
		pass
args.input.close()

# process xtitle (e.g. adding xtitle to the output file name)
Value_series = pd.Series(Value_list, name=args.xtitle)
if args.output_name == "__NA__" and args.xtitle != "x_variable":
	outfile = outfile + '_' + args.xtitle.replace(' ', '_') # add <data_name> to outfile name
else:
	outfile = outfile + "_hist.png"
print('## done reading %d values as "%s", now plotting to %s' % (len(Value_list), args.xtitle, outfile)) 

if args.histplot_opt != "":
	if args.histplot_opt[0] != ',':
		args.histplot_opt = ',' + args.histplot_opt
		
distplot_code = "sns.histplot(x=Value_series" + args.histplot_opt + ")"
if y_max > 0:
	distplot_code = distplot_code + "; plt.ylim(0,%d)" % y_max
savefig_code = 'plt.savefig("%s", dpi = 600)' % outfile

#distplot = exec( distplot_code )
exec( distplot_code )
print("\npython codes used:")
print( distplot_code )

if args.ytitle != "__NA__":
	plt.ylabel(args.ytitle)
	print("plt.ylabel('%s')" % args.ytitle)

exec( savefig_code )
print( savefig_code )

plt.close()
print("plt.close()\n")