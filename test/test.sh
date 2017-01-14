#!/bin/bash
#
# Test cmpds.py using data generated by gends.py.
#

# ================================================================
#
# Functions
#
# ================================================================
function passed_fct() {
    local tid="$1"
    local ctxt=($(caller 0))
    local ln=$(( ${ctxt[0]} - 2 ))
    (( Total++ ))
    (( Passed++ ))
    printf 'test:%02d:%03d: passed - %s\n' $Total $ln "$tid"
}

function failed_fct() {
    local tid="$1"
    local ctxt=($(caller 0))
    local ln=$(( ${ctxt[0]} - 4 ))
    (( Total++ ))
    (( Failed++ ))
    printf 'test:%02d:%03d: failed - %s\n' $Total $ln "$tid"
}

# ================================================================
# Main.
# ================================================================
Passed=0
Failed=0
Total=0
GenDS=./gends.py
ConfDS=../dsconf.py

# Test 1. Dataset with no interesting values.
tid='all the same'
printf '\n*** test %s\n' "$tid"
echo "2" | awk '{for(i=0;i<50;i++) {printf("%s\n", $1)}}' | $ConfDS | tee $$.tmp
st=$?
if  grep '2\.00000 \.\. 2\.00000' <$$.tmp; then
    passed_fct "$tid"
else
    failed_fct "$tid"
    cat $$.tmp
fi
rm -f $$.tmp

# Test 2. 50 values in the range of 11.5 to 12.5.
tid='50 values in range: [11.5 .. 12.5], 95% CL'
printf '\n*** test %s\n' "$tid"
./gends.py -d 2 50 11.5 12.5 | $ConfDS | tee $$.tmp
st=$?
if  grep '11\.[0-9]* \.\. 12.[0-9]*' <$$.tmp; then
    passed_fct "$tid"
else
    failed_fct "$tid"
    cat $$.tmp
fi
rm -f $$.tmp

# Test 3. 50 values in the range of 11.5 to 12.5, 98%.
tid='50 values in range: [11.5 .. 12.5], 98% CL'
printf '\n*** test %s\n' "$tid"
./gends.py -d 2 50 11.5 12.5 | $ConfDS -c 0.98 | tee $$.tmp
st=$?
if  grep '11\.[0-9]* \.\. 12.[0-9]*' <$$.tmp; then
    passed_fct "$tid"
else
    failed_fct "$tid"
    cat $$.tmp
fi
rm -f $$.tmp

# Test 4. 50 values in the range of 11.5 to 12.5, 99%.
tid='50 values in range: [11.5 .. 12.5], 99% CL'
printf '\n*** test %s\n' "$tid"
./gends.py -d 2 50 11.5 12.5 | $ConfDS -c 0.99 | tee $$.tmp
st=$?
if  egrep '11\.[0-9]* \.\. 12.[0-9]*' <$$.tmp; then
    passed_fct "$tid"
else
    failed_fct "$tid"
    cat $$.tmp
fi
rm -f $$.tmp

# Test 5. 20 values in the range of 11.5 to 12.5, 99%
tid='20 values in range: [11.5 .. 12.5], 99% CL'
printf '\n*** test %s\n' "$tid"
./gends.py -d 2 20 11.5 12.5 | $ConfDS -c 0.99 | tee $$.tmp
st=$?
if  egrep '11\.[0-9]* \.\. 12.[0-9]*' <$$.tmp; then
    passed_fct "$tid"
else
    failed_fct "$tid"
    cat $$.tmp
fi
rm -f $$.tmp

# Summary:
echo
printf "test:summary passed %2d\n" $Passed
printf "test:summary failed %2d\n" $Failed
printf "test:summary total  %2d\n" $Total

if (( $Failed )) ; then
    echo "FAILED"
else
    echo "PASSED"
fi
exit $Failed

