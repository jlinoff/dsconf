# dsconf
Aanalyzes datasets for the interval associated with a specified confidence level.

There are many uses for a tool like this. For example, you can use it
to determine whether min or max values are in the range. Or, you could
use it to visually compare two datasets to see if their intervals
overlap.

You can input the z-value for the confidence level manually. If you don't
it will try to use the ztables tool to figure it out.

Note that for sample sizes smaller than 30 it will use t-distributions
automatically unless you specify -z.

Here is an example use.
```bash
   $ echo -e '2.1\n1.9\n1.9\n2.0\n2.0\n2.1\n2.0\n1.9\n2.1\n2.0\n1.9\n2.0\n2.1\n2.0\n2.0\n2.1\n2.0\n2.0\n2.0\n1.9\n2.1\n2.0\n2.0\n2.0\n2.1\n2.0\n2.1\n1.9\n2.0\n2.1\n2.1\n2.1\n2.0\n1.9\n2.0\n2.0\n1.9\n2.1\n2.0\n2.0' | \
       ./dsconf.py -k 1 -z 1.96 -c 0.95 -p 2

   confidence level = 95.0%
   z-value          = 1.96
   size             = 40
   mean             = 2.01 (arithmetic)
   bound factor     = 0.0219695827021
   lower bound      = 1.9880304173
   upper bound      = 2.0319695827
   bound diff       = 0.0439391654041

   The confidence interval about the mean 2.01 for a confidence level of
   95.0% is in the range [1.99 .. 2.03].
```
By default the result is displayed with 5 digits of precision but it was
changed to 2 digits using the -p option.

Note that ztables was copied over from https://github.com/jlinoff/ztables.

## Calculation details
From page 210 in [1].

### Step 1. Compute the sample means

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://cloud.githubusercontent.com/assets/2991242/21951651/c22f8e9a-d9be-11e6-83d5-ab59b99dd9a7.png" width="128" alt="sample mean">

### Step 2. Compute the sample standard deviation

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://cloud.githubusercontent.com/assets/2991242/21951652/d12a5a10-d9be-11e6-9cf9-c19fb561c245.png" width="256" alt="sample stand deviation">

### Step 3. Compute the confidence interval

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://cloud.githubusercontent.com/assets/2991242/21951666/df247646-d9be-11e6-85bd-e54a05846dc4.png" width="196" alt="confidence interval">
