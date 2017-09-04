#!/bin/bash

# Purpose:
#   Use CDO to do some quick preliminary analysis of the p17d simulations
#
# Usage:
#   To be run on local machine:
#     ./cdo_analysis_prelim_p17d.sh
#
# Author:
#   Benjamin S. Grandey, 2017

IN_DIR=$HOME/data/projects/p17d_sulphur_eas_eqm/output_timeseries/
OUT_DIR=$HOME/data/projects/p17d_sulphur_eas_eqm/cdo_analysis_prelim/

# 0. Delete all NetCDF files in output directory
rm -f $OUT_DIR/*.nc

# 1. Calculatime means across time for all input files
# 1a. Prescribed-SST simulations - use years 3-32
for IN_FILE in $IN_DIR/p17d_f_*.nc
do
    OUT_FILE="$OUT_DIR/s1.tm.${IN_FILE##*/}"
    cdo timmean -selyear,3/32 $IN_FILE $OUT_FILE
done

# 1b. Coupled atmosphere-ocean simulations - use years 41-100
for IN_FILE in $IN_DIR/p17d_b_*.nc
do
    OUT_FILE="$OUT_DIR/s1.tm.${IN_FILE##*/}"
    cdo timmean -selyear,41/100 $IN_FILE $OUT_FILE
done

# 2. Prescribed-SST simulation differences
# 2a. 2D fields
CASENAME1="p17d_f_2000"
VARIABLE_LIST="FSNTOA FSNTOA_d1 FSNTOAC_d1 SWCF_d1 LWCF LWCF_d1 H2SO4_SRF"

for CASENAME2 in p17d_f_eas0 p17d_f_eas0b p17d_f_eas0c
do
    for VARIABLE in $VARIABLE_LIST
    do
	IN_FILE1="$OUT_DIR/s1.tm.$CASENAME1.cam.h0.$VARIABLE.nc"
	IN_FILE2="$OUT_DIR/s1.tm.$CASENAME2.cam.h0.$VARIABLE.nc"
	OUT_FILE="$OUT_DIR/s2.tm.$CASENAME1-$CASENAME2.cam.h0.$VARIABLE.nc"
	cdo sub $IN_FILE1 $IN_FILE2 $OUT_FILE
    done
done

# 2b. Derived fields
# Net RFP
CASENAME1="p17d_f_2000"
for CASENAME2 in p17d_f_eas0 p17d_f_eas0b p17d_f_eas0c
do
    IN_FILE1="$OUT_DIR/s2.tm.$CASENAME1-$CASENAME2.cam.h0.FSNTOA.nc"
    IN_FILE2="$OUT_DIR/s2.tm.$CASENAME1-$CASENAME2.cam.h0.LWCF_d1.nc"
    TEMP_FILE="$OUT_DIR/temp.nc"
    OUT_FILE="$OUT_DIR/s2.tm.$CASENAME1-$CASENAME2.cam.h0.cFNTOA.nc"
    cdo merge $IN_FILE1 $IN_FILE2 $TEMP_FILE
    cdo expr,'cFNTOA=FSNTOA+LWCF_d1' $TEMP_FILE $OUT_FILE
    rm -f $TEMP_FILE
done

# 2c. Area-weighted means
for IN_FILE in $OUT_DIR/s2.*.nc
do
    OUT_FILE=${IN_FILE%nc}fm.nc
    cdo fldmean $IN_FILE $OUT_FILE
done

# 3. Atmosphere-ocean simulation differences
# 3a. 2D fields
CASENAME1="p17d_b_2000"
VARIABLE_LIST="TS PRECC PRECL H2SO4_SRF"
for CASENAME2 in p17d_b_eas0 p17d_b_eas0b p17d_b_eas0c
do
    for VARIABLE in $VARIABLE_LIST
    do
	IN_FILE1="$OUT_DIR/s1.tm.$CASENAME1.cam.h0.$VARIABLE.nc"
	IN_FILE2="$OUT_DIR/s1.tm.$CASENAME2.cam.h0.$VARIABLE.nc"
	OUT_FILE="$OUT_DIR/s3.tm.$CASENAME1-$CASENAME2.cam.h0.$VARIABLE.nc"
	cdo sub $IN_FILE1 $IN_FILE2 $OUT_FILE
    done
done

# 3b. Derived fields
# Total precipitation
CASENAME1="p17d_b_2000"
for CASENAME2 in p17d_b_eas0 p17d_b_eas0b p17d_b_eas0c
do
    IN_FILE1="$OUT_DIR/s3.tm.$CASENAME1-$CASENAME2.cam.h0.PRECC.nc"
    IN_FILE2="$OUT_DIR/s3.tm.$CASENAME1-$CASENAME2.cam.h0.PRECL.nc"
    TEMP_FILE="$OUT_DIR/temp.nc"
    OUT_FILE="$OUT_DIR/s3.tm.$CASENAME1-$CASENAME2.cam.h0.cPRECT.nc"
    cdo merge $IN_FILE1 $IN_FILE2 $TEMP_FILE
    cdo expr,'cPRECT=PRECC+PRECL' $TEMP_FILE $OUT_FILE
    rm -f $TEMP_FILE
done

# 3c. Area-weighted means
for IN_FILE in $OUT_DIR/s3.*.nc
do
    OUT_FILE=${IN_FILE%nc}fm.nc
    cdo fldmean $IN_FILE $OUT_FILE
done

echo "Finished analysis"

# Print area-weighted means
for IN_FILE in $OUT_DIR/*.fm.nc
do
    echo ${IN_FILE##*/}
    cdo infov $IN_FILE 2>/dev/null | grep -v '0.0000\|nan\|2.1475\|Mean'
done

echo "Finished"
