#!/usr/bin/env python
import sys, os, argparse
from argparse import RawTextHelpFormatter

##############################
### 0.1 script description ###
##############################
synopsis1 = "\
  - draw x-y and distribution plot (seaborn.jointplot) for two variables from\n\
     two columns of the input file"
synopsis2 = "detailed description:\n\
 1. Input\n\
  - <input> is a tab-delimited text;\n\
  - <col1> and <col2> are the column numbers to use for the plot;\n\
 2. Options and parameters:\n\
  - '-data_name': name the data, will appear as x and y labels, comma-separated;\n\
     if not specified, the column headers will be used (if available),\n\
  - '-jntp_opt': string of options to be passed to seaborn.jointplot code;\n\
     start with a ',' and put in quotation marks; e.g. "",color='r'""\n\
  * note: xlim and ylim can be passed using '-jntp_opt', e.g.:\n\
      -jntp_opt \",xlim=(0,60), ylim=(0,12)\"\n\
  * other commonly used '-jntp_opt' examples (in addition to xlim and ylim):\n\
      -jntp_opt \",kind='kde',fill=True,n_levels=12,thresh=0.001,cmap='Blues'\"\n\
      -jntp_opt \",kind='hex',gridsize=25,marginal_kws=dict(bins=25)\"\n\
      -jntp_opt \",kind='scatter',color='gray',alpha=0.1,s=5,marginal_kws=dict(bins=50)\"\n\
  - '-o output_name': if not specified, <output_name> = <input> w/o extension\n\
     + '_<col1>' + '_<col2>' + '<data_names>' + '_jntp.png';\n\
  - '-v/--verbose': print line numbers with faulty input (e.g. NaN); [False];\n\
 4. Output:\n\
  - plot the histogram + distribution plot as <output_name>.png\n\
  - print (to stdout) linear regression results between the two columns\n\
by ohdongha@gmail.com 20220419 ver 0.2\n\n"
#version_history
#20220419 ver 0.2 report # of pairs rejected (e.g. NaN); bug fix on linear regression, etc.
#20210713 ver 0.1 python3 compatible; print linear regression results, etc 
#20191111 ver 0.0.1 print the python codes for plots
#20191106 ver 0.0 modified from plot_hist_dist.py 

#############################
### 0.2 parsing arguments ###
#############################
parser = argparse.ArgumentParser(description = synopsis1, epilog = synopsis2, formatter_class = RawTextHelpFormatter)
# positional arguments
parser.add_argument('input', type=argparse.FileType('r'))
parser.add_argument('col1', type=int)
parser.add_argument('col2', type=int)
# options
parser.add_argument('-data_name', dest="xytitle", type=str, default= "x,y") 
parser.add_argument('-jntp_opt', dest="jointplot_opt", type=str, default= "")
parser.add_argument('-o', dest="output_name", type=str, default= "__NA__") 
parser.add_argument('-v', '--verbose', action="store_true", default=False)
 

args = parser.parse_args()

# parsing arguments
col1_index = args.col1
col2_index = args.col2
if args.output_name == "__NA__":
	outfile = os.path.splitext(args.input.name)[0] + "_%d-%d" % (col1_index, col2_index) # later add "_jntp.png" etc,
else:
	outfile = args.output_name

# parsing xytitle
xtitle = ""
ytitle = ""
if args.xytitle != "x,y":
	try:
		xtitle = args.xytitle.split(',')[0].strip()
		ytitle = args.xytitle.split(',')[1].strip()
	except (ValueError, IndexError):
		sys.stderr.write( "Warning: '-data_name' option had an invalid argument... ignored\n" )
		args.xytitle = "x,y"

###########################
### 0.3 importing stuff ###
###########################
try:
	import numpy as np, pandas as pd
	import seaborn as sns
	import matplotlib.pyplot as plt
	plt.switch_backend('agg') 
	import scipy.stats as stats
except ImportError as ErrorMessage:
	sys.stderr.write(str(ErrorMessage) + '\n')
	sys.exit()

#########################################
### 1. reading input and drawing plot ###
#########################################
Value1 = 0.0
Value2 = 0.0
Value1_list = []
Value2_list = []
FaultyLines = 0
num_lines = 0
num_records = 0
clean_pass = False

sys.stderr.write( "## getting the %d and %d (st/nd/th) columns from %s\n" % (col1_index, col2_index, args.input.name) )
for line in args.input:
	clean_pass = False
	try:
		tok = line.split('\t')
		num_lines = num_lines + 1
		Value1 = float(tok[col1_index-1].strip())
		Value2 = float(tok[col2_index-1].strip())
		clean_pass = True
	except (ValueError, IndexError) as err :
		FaultyLines = FaultyLines + 1
		if num_lines == 1 and args.xytitle == "x,y":
			xtitle = tok[col1_index-1].strip()
			ytitle = tok[col2_index-1].strip()
		else:
			if args.verbose:
				sys.stderr.write( "Warning: %s at line %d ...\n" % (err, num_lines) )
		clean_pass = False # just in case
		pass
	
	if clean_pass: # add only if both columns have float numbers
		Value1_list.append(Value1)
		Value2_list.append(Value2)
		
if len(Value1_list) == len(Value2_list):
	num_records = len(Value1_list)
else:
	sys.stderr.write( "Warning: number of x and y records not equal (#x: %d, #y: %d)\n" % (len(Value1_list), len(Value2_list) ) )
args.input.close()

# process xytitle (e.g. adding xytitle to the output file name)
Value1_series = pd.Series(Value1_list, name=xtitle)
Value2_series = pd.Series(Value2_list, name=ytitle)
if args.output_name == "__NA__":
	if args.xytitle == "x,y":
		outfile = outfile + "_jntp.png"	
	else:
		outfile = outfile + '_%s-%s' % ( xtitle.replace(' ', '_'), ytitle.replace(' ', '_') ) + "_jntp.png"

sys.stderr.write( "## done reading %d lines, %d rejected (e.g. header, NaN, etc.); plotting remaining %d pairs to %s\n" \
		% (num_lines, FaultyLines, num_records, outfile) )

if args.jointplot_opt != "":
	if args.jointplot_opt[0] != ',': 
		args.jointplot_opt = ',' + args.jointplot_opt
jntplot_code = "sns.jointplot(x=Value1_series, y=Value2_series" + args.jointplot_opt + ")"
savefig_code = "plt.savefig(outfile, dpi = 600)"

exec( jntplot_code )
exec( savefig_code )
plt.close()

sys.stderr.write( "\n## python jointplot codes used: " )
sys.stderr.write( jntplot_code + '\n' )
#sys.stderr.write( savefig_code + '\n' )
#sys.stderr.write( "plt.close()\n" )

###############################################################################
### 2. also, print linear regression and Spearman's correlation bcs why not ###
###############################################################################
sys.stderr.write( "\n## printing (to stdout) linear regression and Spearman's correlation, bcs why not\n" )

Value1_array = np.array(Value1_list)
Value2_array = np.array(Value2_list) 
mask = ~np.isnan(Value1_array) & ~np.isnan(Value2_array) # suppress NaN (see https://stackoverflow.com/a/13643460/6283377 )
slope, intercept, r, p, stderr = stats.linregress( Value1_array[mask], Value2_array[mask] )

if intercept >= 0: 
	print( "Linear regression: y = %s x + %s ( r = %s, p = %s, stderr = %f )" % \
		( "{:0.3f}".format(slope), "{:0.3f}".format(intercept), "{:0.3f}".format(r), "{:.3e}".format(p), stderr ) )
else:
	print( "Linear regression: y = %s x - %s ( r = %s, p = %s, stderr = %f )" % \
		( "{:0.3f}".format(slope), "{:0.3f}".format(intercept * -1), "{:0.3f}".format(r), "{:.3e}".format(p), stderr ) )

rho, p_Scorr = stats.spearmanr( Value1_array[mask], Value2_array[mask] )
print( "Spearman's corr: rho = %s, p_Scorr = %s" % ( "{:0.3f}".format(rho), "{:.3e}".format(p_Scorr) ) )
sys.stderr.write( "## all done.\n" )
