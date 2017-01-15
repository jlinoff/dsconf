# dsconf
Aanalyzes a dataset for the interval associated with a specified confidence level.

There are many uses for a tool like this. For example, you can use it
to determine whether min or max values are in the range. Or, you could
use it to visually compare two datasets to see if their intervals
overlap.

You can input the z-value for the confidence level manually. If you don't
it will try to use the ztables tool to figure it out.

Note that for sample sizes smaller than about 30 it will use t-distributions
automatically unless you specify -z.

Here is an example use. Note that I used expr to make it compatible with
bash 3.x.
```bash
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
```
By default the result is displayed with 5 digits of precision but it was
changed to 2 digits using the -p option.

Note that ztables was copied over from https://github.com/jlinoff/ztables.

It has been tested using python 2.7 and 3.6.

## Example 2. Parsing multiple columns of data.
This example shows how to process a file with multiple columns of data.

```bash
$ cat ds.txt
# Sample data
 98  98  98  98  98  98  98  98  98  98
 98  98  99  99  99  99  99  99  99  99
 99  99  99  99  99  99  99  99  99  99
 99  99  99  99  99  99  99  99 100 100
100 100 100 100 100 100 100 100 100 100
100 100 100 100 100 100 100 100 100 100
100 101 101 101 101 101 101 101 101 101
101 101 101 101 101 101 101 101 101 101
101 101 101 101 101 101 101 101 101 101
102 102 102 102 102 102 102 102 102 102

$ # Ignore blank lines and lines that start with '#'.
$ egrep -v '^$|^ *#' <ds.txt | awk '{for(i=1;i<=NF;i++){print $i}}' | ./dsconf.py -p 2

dataset          = stdin
confidence level = 95.0%
z-value          = 1.96
size             = 100
mean             = 99.99 (arithmetic)
median           = 100.0
min              = 98.0
max              = 102.0
above mean       = 62 62.0%
below mean       = 38 38.0%
stddev           = 1.20180840168
bound factor     = 0.235554446729
lower bound      = 99.7544455533
upper bound      = 100.225554447
bound diff       = 0.471108893458
null hypothesis  = rejected

The interval about the mean 99.99 for a confidence level of
95.0% is in the range [99.75 .. 100.23].

The interval does not include 0 which means that the null
hypothesis can be rejected. The interval is meaningful.

```

## Calculation details
From page 210 in [1].

### Step 1. Compute the sample means

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://cloud.githubusercontent.com/assets/2991242/21951651/c22f8e9a-d9be-11e6-83d5-ab59b99dd9a7.png" width="128" alt="sample mean">

### Step 2. Compute the sample standard deviation

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://cloud.githubusercontent.com/assets/2991242/21951652/d12a5a10-d9be-11e6-9cf9-c19fb561c245.png" width="256" alt="sample stand deviation">

### Step 3. Compute the confidence interval

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://cloud.githubusercontent.com/assets/2991242/21951666/df247646-d9be-11e6-85bd-e54a05846dc4.png" width="196" alt="confidence interval">
