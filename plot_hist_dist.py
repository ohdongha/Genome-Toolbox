#!/usr/bin/env python
import sys, os, argparse
from argparse import RawTextHelpFormatter

##############################
### 0.1 script description ###
##############################
synopsis1 = "\
  - draw histogram and distribution plot (seaborn.distplot or seaborn.kdeplot)\n\
     for values in a column of the input file"
synopsis2 = "detailed description:\n\
 0. Pre-requisite:\n\
  - python 3; numpy, scipy, panda, and matplotlib.pyplot;\n\
  - seaborn (written under v0.10.x; will gradually move to v0.11.0);\n\
 1. Input\n\
  - <input> is a tab-delimited text;\n\
  - <col> is the column number to use for the plot;\n\
 2. Options and parameters:\n\
  - '-data_name': name the data, will appear as x-axis label; if not specified,\n\
   the column header will be used (if available),\n\
  - '-o output_name': output file name will be <output_name> + '_dist.png';\n\
   if not specified, <input> w/o extension + '_<col>' + '_<data_name>_dist.png';\n\
  - '-xlim=x_min,x_max': x-axis limits as comma-separated float numbers,\n\
  - '-ylim=y_min,y_max': x-axis limits as comma-separated float numbers,\n\
  - '-k'|'--kde': use seaborn.kdeplot instead of seaborn.distplot;\n\
  - '-dist_opt': string of options to be passed to seaborn.displot\n\
   (or seaborn.kdeplot with '-k' or seaborn.histplot with '-H') code;\n\
   start with a ',' and put in quotation marks; e.g. "",kde=True,color='r'"" etc.\n\
 4. Output:\n\
  - print the histogram + distribution plot as <output_name>_dist.png\n\
   (or <output_name>_kde.png with '-k';\n\
by ohdongha@gmail.com 20220218 ver 0.2\n\n"
#version_history
#20220218 ver 0.2 added -H option to use seaborn.histplot for histograms (then what is the use of seaborn.displot?)  
#20210721 ver 0.1.1 seaborn.displot instead of distplot; bug fix for output file names
#20201206 ver 0.1 added -k option to use seaborn.kdeplot for density plots  
#20201202 ver 0.0.3 python 3.0 compatible -_-;;; 
#20191111 ver 0.0.2 print the python codes for plots 
#20191106 ver 0.0.1 minor bug fixes 
#20191028 ver 0.0 modified from create_hist.py 

#############################
### 0.2 parsing arguments ###
#############################
parser = argparse.ArgumentParser(description = synopsis1, epilog = synopsis2, formatter_class = RawTextHelpFormatter)
# positional arguments
parser.add_argument('input', type=argparse.FileType('r'))
parser.add_argument('col', type=int)
# options
parser.add_argument('-o', dest="output_name", type=str, default= "__NA__") 
parser.add_argument('-data_name', dest="xtitle", type=str, default= "x variable") 
parser.add_argument('-xlim', dest="xlim", type=str, default= "__NA__") 
parser.add_argument('-ylim', dest="ylim", type=str, default= "__NA__") 
parser.add_argument('-k', '--kde', action="store_true", default=False)
parser.add_argument('-H', '--hist', action="store_true", default=False)
parser.add_argument('-dist_opt', dest="distplot_opt", type=str, default= "") 

args = parser.parse_args()

# parsing arguments
col_index = args.col
if args.output_name == "__NA__":
	outfile = os.path.splitext(args.input.name)[0] + '_' + str(col_index) # later add "_dist.png" etc,
else:
	outfile = args.output_name # if outfile is explicitly specified, don't add col index
#	outfile = args.output_name + '_' + str(col_index)

# parsing xlim and ylim
xlim_str = args.xlim
if xlim_str != "__NA__":
	try:
		x_min = float( args.xlim.split(',')[0].strip() )
		x_max = float( args.xlim.split(',')[1].strip() )
	except (ValueError, IndexError):
		print("Warning: '-xlim' option had invalid arguments, x-axis limits won't work...")
		xlim_str = "__NA__"

ylim_str = args.ylim
if ylim_str != "__NA__":
	try:
		y_min = float( args.ylim.split(',')[0].strip() )
		y_max = float( args.ylim.split(',')[1].strip() )
	except (ValueError, IndexError):
		print("Warning: '-ylim' option had invalid arguments, x-axis limits won't work...")
		ylim_str = "__NA__"

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
if args.kde:
	outfile = outfile + "_kde.png"
elif args.hist:
	outfile = outfile + "_hist.png"
else:
	outfile = outfile + "_dist.png"

print('## done reading %d values as "%s", now plotting to %s' % (len(Value_list), args.xtitle, outfile)) 

if args.distplot_opt != "":
	if args.distplot_opt[0] != ',':
		args.distplot_opt = ',' + args.distplot_opt
		
if args.kde:
	distplot_code = "sns.kdeplot(x=Value_series" + args.distplot_opt + ", shade=True, color='xkcd:charcoal')"
elif args.hist:
	distplot_code = "sns.histplot(x=Value_series" + args.distplot_opt + ")"
else:
	distplot_code = "sns.displot(x=Value_series" + args.distplot_opt + ")"
savefig_code = 'plt.savefig("%s", dpi = 600)' % outfile

#distplot = exec( distplot_code )
exec( distplot_code )
print("\npython codes used:")
print( distplot_code )

if xlim_str != "__NA__":
	plt.xlim(x_min, x_max)
	print("plt.xlim(%f, %f)" % (x_min, x_max))
if ylim_str != "__NA__":
	plt.ylim(y_min, y_max)
	print("plt.ylim(%f, %f)" % (y_min, y_max))

exec( savefig_code )
print( savefig_code )

plt.close()
print("plt.close()\n")