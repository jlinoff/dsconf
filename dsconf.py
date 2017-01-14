#!/usr/bin/env python
r'''
This tool analyzes a dataset for the interval associated with a
specified confidence level.

There are many uses for a tool like this. For example, you can use it
to determine whether min or max values are in the range. Or, you could
use it to visually compare two datasets to see if their intervals
overlap.

You can input the z-value for the confidence level manually. If you don't
it will try to use the ztables tool to figure it out.

Note that for sample sizes smaller than 30 it will use t-distributions
automatically unless you specify -z.

Here is an example use. Note that I used expr to make it compatible with
bash 3.x.

   $ for i in $(seq 200) ; \
      do n=$(expr $i % 3); \
         case $n in \
           0) echo 19;; \
           1) echo 20;; \
           2) echo 21;; \
         esac ; \
      done | ./dsconf.py -p 2

   dataset          = stdin
   confidence level = 95.0%
   z-value          = 1.96
   size             = 200
   mean             = 20.005 (arithmetic)
   median           = 20.0
   min              = 19.0
   max              = 21.0
   above mean       = 67 33.5%
   below mean       = 133 66.5%
   stddev           = 0.817506319801
   bound factor     = 0.113300595429
   lower bound      = 19.8916994046
   upper bound      = 20.1183005954
   bound diff       = 0.226601190859
   null hypothesis  = rejected

   The interval about the mean 20.00 for a confidence level of
   95.0% is in the range [19.89 .. 20.12].

   The interval does not include 0 which means that the null
   hypothesis can be rejected. The interval is meaningful.

By default the result is displayed with 5 digits of precision but it was
changed to 2 digits using the -p option.
'''
import argparse
import inspect
import math
import os
import sys
import subprocess


#VERSION = '0.1' # Initial implementation
#VERSION = '0.2' # Added the null hypothesis reporting and above/below
#VERSION = '0.3' # Added -t to define the minimum threshold
VERSION = '0.4' # Updated the help


def runcmd(cmd, show_output=True):
    '''
    Execute a short running shell command with no inputs.
    Capture output and exit status.
    '''
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        status = 0
    except subprocess.CalledProcessError as obj:
        output = obj.output.decode('ascii')
        status = obj.returncode

    output = output.decode('ascii')  # byte --> char in Python 3
    if show_output:
        sys.stdout.write(output)

    return status, output


def infov(opts, msg, lev=1, vl=1):
    '''
    Print an info message.
    '''
    if opts.verbose >= vl:
        print('INFO:{} {}'.format(inspect.stack()[lev][2], msg))


def info(msg, lev=1):
    '''
    Print an info message.
    '''
    print('INFO:{} {}'.format(inspect.stack()[lev][2], msg))


def err(msg, lev=1):
    '''
    Print an error message and exit.
    '''
    ln = inspect.stack()[lev][2]
    sys.stderr.write('\nERROR:{} {}\n'.format(ln, msg))
    sys.exit(1)


def getopts():
    '''
    Get the command line options using argparse.
    '''
    # Make sure that the confidence level is in the proper range.
    def get_conf_level():
        class GetConfLevel(argparse.Action):
            def __call__(self, parser, args, values, option_string=None):
                if 0. < values < 1.0:
                    setattr(args, self.dest, values)
                else:
                    msg = 'argument "{}" out of range (0..1)'.format(self.dest)
                    parser.error(msg)
        return GetConfLevel

    # Trick to capitalize the built-in headers.
    # Unfortunately I can't get rid of the ":" reliably.
    def gettext(s):
        lookup = {
            'usage: ': 'USAGE:',
            'positional arguments': 'POSITIONAL ARGUMENTS',
            'optional arguments': 'OPTIONAL ARGUMENTS',
            'show this help message and exit': 'Show this help message and exit.\n ',
        }
        return lookup.get(s, s)

    argparse._ = gettext  # to capitalize help headers
    base = os.path.basename(sys.argv[0])
    name = os.path.splitext(base)[0]
    usage = '\n  {0} [OPTIONS] <DATASET-1> <DATASET-2>'.format(base)
    desc = 'DESCRIPTION:{0}'.format('\n  '.join(__doc__.split('\n')))
    epilog = r'''
EXAMPLES:
   # Example 1: help
   $ {0} -h

   # Example 2: Analyze a dataset to get the 95% confidence interval (the default).
   $ {0} ds1.txt

   # Example 3. Analyze a dataset from stdin.
   $ {0} <ds1.txt

   # Example 4. Specify the z-value manually to avoid calling z-tables.
   #            For this case we know that ds1.txt has more than 30 data points.
   $ {0} -c 0.95 -z 1.96 <ds1.txt

   # Example 5: Analyze a dataset to get the 95% confidence interval (the default)
   #            with 2 decimal digits of precision.
   $ {0} -p 2 ds1.txt
 '''.format(base)
    afc = argparse.RawTextHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=afc,
                                     description=desc[:-2],
                                     usage=usage,
                                     epilog=epilog)

    parser.add_argument('-c', '--conf',
                        type=float,
                        default=0.95,
                        action=get_conf_level(),
                        metavar=('FLOAT'),
                        help='''The confidence level such that 0 < c < 1.
This is the same as specifying --cmpds-args "-c %(default)s".
The default is %(default)s.
 ''')

    parser.add_argument('-k', '--col',
                        action='store',
                        type=int,
                        default=1,
                        metavar=('COLUMN'),
                        help='''The 1 based column where the value exists.
It assumes that the columns are separated by white space.
If the value in the column is not a floating point
number it is ignored.
The default is column %(default)s.
 ''')

    parser.add_argument('-p', '--precision',
                        action='store',
                        type=int,
                        default=5,
                        metavar=('INTEGER'),
                        help='''Decimal digits of precision for the mean
and the confidence interval bounds.
The default is %(default)s.
 ''')

    parser.add_argument('-t', '--threshold',
                        action='store',
                        type=int,
                        default=5,
                        metavar=('INTEGER'),
                        help='''Minimum number of data points.
If there are fewer data points, an error is reported.
The default is %(default)s.
 ''')

    parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help='''Increase the level of verbosity.
Specify -v to see the steps in detail.
Specify -v -v to see the data.
 ''')

    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s v{0}'.format(VERSION),
                        help="""Show program's version number and exit.
 """)

    # Args to the ztables.py tool.
    parser.add_argument('--ztables-args',
                        action='store',
                        default='',
                        metavar=('OPTIONS'),
                        help='''Extra options to ztables.py.
You normally do not need to change this.
Make sure that you enclose them in quotes and add a leading space.
Here is an example: --ztables-args "-k 2 2 -c 0.99"
 ''')
    
    # Get the default path to ztables.py.
    p = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'ztables.py')
    parser.add_argument('--ztables-path',
                        action='store',
                        default=p,
                        metavar=('PATH'),
                        help='''Path to the ztables.py tool.
Default: "%(default)s".
 ''')

    # specify your own z-value
    parser.add_argument('-z',
                        action='store',
                        type=float,
                        metavar=('FLOAT'),
                        help='''Specify the z-value to avoid calling ztables.py.

If you know the z-value, you can specify it directly.

For example, if you have more than 30 data points and
want the interval for a 95%% confidence level, you would
specify -z 1.9.6.

Here is a list of common z-values for the standard normal
distribtion (SND).

  Probability   SND 
  ===========  =====
    50.00%%     0.674
    80.00%%     1.282
    90.00%%     1.645
    95.00%%     1.960
    98.00%%     2.326
    99.00%%     2.576
    99.90%%     3.288
 ''')

    # Positional arguments at the end.
    parser.add_argument('DATASET_FILES',
                        nargs='*',
                        help='''Text data files.
If no files are specified, stdin is read.
 ''')

    opts = parser.parse_args()
    for fn in opts.DATASET_FILES:
        if os.path.exists(fn) is False:
            err('file does not exist: "{}"'.format(fn))
    if opts.col < 1:
        err('minimum column value is invalid: {}, the minimum value is {}'.format(opts.col, 1))
    return opts


def getz(opts, n):
    '''
    Get the z-value from ztables.

    n is the number of data points in the sample
    '''
    infov(opts, 'getting z value for {} conf level'.format(opts.conf))
    if n < 30:
        cmd = '{} -t {} -p {} {}'.format(opts.ztables_path, n, opts.conf, opts.ztables_args)
    else:
        cmd = '{} -s -p {} {}'.format(opts.ztables_path, opts.conf, opts.ztables_args)
    infov(opts, 'cmd = {}'.format(cmd))

    show = True if opts.verbose > 1 else False
    s, o = runcmd(cmd, show)
    if s:
        err('command failed with status {}: {}'.format(s, cmd))

    z = None
    for line in o.split('\n'):
        line = line.strip()
        if '%' in line:
            if z is not None:
                err('unexpected output, found more than one z value, cannot parse')
            flds = line.split()
            z = flds[1]
    if z is None:
        print(o)
        err('unexpected output, did not find a z value, cannot parse')
    infov(opts, 'z-value = {}'.format(z))
    return float(z)


def rdds(opts, fn, ifp):
    '''
    Read the file contents and return the dataset.
    '''
    ds = []
    ln = 0
    col = opts.col - 1
    for line in ifp.readlines():
        ln += 1
        infov(opts, msg='data = {:>6}  {}'.format(ln, line.rstrip()), vl=2)
        line = line.strip()
        tokens = line.split()
        if len(tokens) < col or len(tokens) == 0:
            infov(opts, 'skipping line {} in {}: too few tokens {}'.format(ln, fn, len(tokens)), vl=2)
            continue
        token = tokens[col-1]
        try:
            f = float(token)
            if f < 0.0001:  # avoid divide by 0 errors
                info(opts, 'skipping line {} in {}: number is too small {}'.format(ln, fn, token), vl=2)
                continue
            ds.append(f)
        except ValueError:
            infov(opts, 'skipping line {} in {}: not a number: {}'.format(ln, fn, token), vl=2)
            continue
    minth = opts.threshold
    if len(ds) < minth:
        err('too few data points at column {} in {}, found {}, need at least {}'.format(col, fn, len(ds), minth))
    return ds


def process(opts, fn, ifp):
    '''
    Process a dataset.
    '''
    infov(opts, 'processing {}'.format(fn))
    ds = rdds(opts, fn, ifp)
    n = len(ds)
    infov(opts, 'size = {}'.format(n))
    z = getz(opts, n)

    # Sort the data to get the min, max and median.
    sds = sorted(ds)
    infov(opts, 'min = {}'.format(sds[0]))
    infov(opts, 'max = {}'.format(sds[-1]))
    h = n // 2
    if (n%2) == 1:
        median = (sds[h] + sds[h+1]) / 2.0
    else:
        median = sds[h]
    infov(opts, 'median = {}'.format(median))

    # Get the arithmetic mean.
    amean = sum(sds) / float(n)
    infov(opts, 'mean = {}'.format(amean))

    # Get the variance.
    # correct variance (N-1) vs (N).
    var = sum([ (v - amean)**2 for v in sds]) / float(n - 1.0)
    infov(opts, 'variance = {}'.format(var))

    # Get the standard deviation.
    stddev = math.sqrt(var)
    infov(opts, 'stddev = {}'.format(stddev))

    # Calculate the confidence interval.
    fac = z * (stddev / math.sqrt(n))
    lb = amean - fac
    ub = amean + fac
    cl = opts.conf * 100.

    # Compute the above and below numbers.
    above = sum(val > amean for val in sds)
    below = sum(val < amean for val in sds)
    pabove = 100. * (above / float(n))
    pbelow = 100. * (below / float(n))
    
    # Format the output data.
    fs = '{:,.' + str(opts.precision) + 'f}'
    ams = fs.format(amean)
    lbs = fs.format(lb)
    ubs = fs.format(ub)
    infov(opts, 'precision = {}'.format(opts.precision))

    # Check the null hypothesis.
    nh = 'accepted' if lb <= 0 and ub >= 0 else 'rejected'
                        
    print('')
    print('dataset          = {}'.format(fn))
    print('confidence level = {:.1f}%'.format(cl))
    print('z-value          = {}'.format(z))
    print('size             = {:,}'.format(n))
    print('mean             = {} (arithmetic)'.format(amean))
    print('median           = {}'.format(median))
    print('min              = {}'.format(sds[0]))
    print('max              = {}'.format(sds[-1]))
    print('above mean       = {:,} {:.1f}%'.format(above, pabove))
    print('below mean       = {:,} {:.1f}%'.format(below, pbelow))
    print('stddev           = {}'.format(stddev))
    print('bound factor     = {}'.format(fac))
    print('lower bound      = {}'.format(lb))
    print('upper bound      = {}'.format(ub))
    print('bound diff       = {}'.format(ub - lb))
    print('null hypothesis  = {}'.format(nh))
    print('')
    print('The interval about the mean {} for a confidence level of'.format(ams))
    print('{:.1f}% is in the range [{} .. {}].'.format(cl, lbs, ubs))
    print('')
    if nh == 'accepted':
        print('The interval includes 0 which means that null hypothesis cannot')
        print('be rejected. The interval is not meaningful.')
    else:
        print('The interval does not include 0 which means that the null')
        print('hypothesis can be rejected. The interval is meaningful.')
    print('')


def main():
    '''
    Main.
    '''
    opts = getopts()
    infov(opts, 'dataset col = {}'.format(opts.col))
    
    if len(opts.DATASET_FILES):
        for fn in opts.DATASET_FILES:
            try:
                with open(fn, 'r') as ifp:
                    process(opts, fn, ifp)
            except IOError as e:
                err('unable to read {}: {}'.format(fn, e))
    else:
        process(opts, 'stdin', sys.stdin)


if __name__ == '__main__':
    main()
