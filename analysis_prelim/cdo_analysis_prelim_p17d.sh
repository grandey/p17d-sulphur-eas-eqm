#!/bin/bash

# Purpose:
#   Use CDO to do some quick preliminary analysis of the p17d simulations
#
# Usage:
#   To be run on local machine:
#     ./cdo_analysis_prelim_p17c.sh
#
# Author:
#   Benjamin S. Grandey, 2017

IN_DIR=$HOME/data/projects/p17d_sulphur_eas_eqm/output_timeseries/
OUT_DIR=$HOME/data/projects/p17d_sulphur_eas_eqm/cdo_analysis_prelim/

# 0. Delete all NetCDF files in output directory
rm -f $OUT_DIR/*.nc

# 1. Calculatime means across time for years 3-32 for all input files
for IN_FILE in $IN_DIR/*.nc
do
    OUT_FILE="$OUT_DIR/s1.tm.${IN_FILE##*/}"
    cdo timmean -selyear,3/32 $IN_FILE $OUT_FILE
done

# 2. Calculate RFPs using prescribed-SST simulations
# 2a. Radiation fields
CASENAME1="p17d_f_2000"
CASENAME2="p17d_f_eas0"
VARIABLE_LIST="FSNTOA FSNTOA_d1 FSNTOAC_d1 SWCF_d1 LWCF LWCF_d1"

for VARIABLE in $VARIABLE_LIST
do
    IN_FILE1="$OUT_DIR/s1.tm.$CASENAME1.cam.h0.$VARIABLE.nc"
    IN_FILE2="$OUT_DIR/s1.tm.$CASENAME2.cam.h0.$VARIABLE.nc"
    OUT_FILE="$OUT_DIR/s2.tm.$CASENAME1-$CASENAME2.cam.h0.$VARIABLE.nc"
    cdo sub $IN_FILE1 $IN_FILE2 $OUT_FILE
done

# 2b. Derived RFPs
# Net RFP
IN_FILE1="$OUT_DIR/s2.tm.p17d_f_2000-p17d_f_eas0.cam.h0.FSNTOA.nc"
IN_FILE2="$OUT_DIR/s2.tm.p17d_f_2000-p17d_f_eas0.cam.h0.LWCF_d1.nc"
TEMP_FILE="$OUT_DIR/temp.nc"
OUT_FILE="$OUT_DIR/s2.tm.p17d_f_2000-p17d_f_eas0.cam.h0.cFNTOA.nc"
cdo merge $IN_FILE1 $IN_FILE2 $TEMP_FILE
cdo expr,'cFNTOA=FSNTOA+LWCF_d1' $TEMP_FILE $OUT_FILE
rm -f $TEMP_FILE

# 2c. Area-weighted means of RFPs
for IN_FILE in $OUT_DIR/s2.*.nc
do
    OUT_FILE=${IN_FILE%nc}fm.nc
    cdo fldmean $IN_FILE $OUT_FILE
done

echo "Finished"
