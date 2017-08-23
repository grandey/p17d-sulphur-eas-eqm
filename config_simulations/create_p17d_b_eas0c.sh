#!/bin/bash

CASENAME=p17d_b_eas0c

cd ~/models/cesm1_2_2_1/scripts/
./create_newcase -case ~/cesm1_2_2_1_cases/$CASENAME -res f19_g16 -compset BC5CN -mach cheyenne -pes_file pes/a720o128n24.xml

cd ~/cesm1_2_2_1_cases/$CASENAME
./cesm_setup
wget https://raw.githubusercontent.com/grandey/p17d-sulphur-eas-eqm/master/user_nl_cam/user_nl_cam_$CASENAME
mv user_nl_cam_$CASENAME user_nl_cam
wget https://raw.githubusercontent.com/grandey/p17d-sulphur-eas-eqm/master/user_nl_cam/user_nl_clm_p17d_b
mv user_nl_clm_p17d_b user_nl_clm
./$CASENAME.build
ln -s /glade/scratch/bgrandey/$CASENAME/run/ scratch_run
./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=10
./xmlchange RESUBMIT=9
sed -i 's/regular/economy/g' $CASENAME.run
./$CASENAME.submit
