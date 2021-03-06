"""
Functions for p17d-sulphur-eas-eqm/analysis_draft2018a/.

Warning:
    The complete functionality of these functions has not been extensively tested.
    They have only been tested for the specific purposes used in the draft2018a analysis.

Dependencies:
    - climapy (https://github.com/grandey/climapy, https://doi.org/10.5281/zenodo.1053020)
    - pandas
    - xarray

Data requirements:
    - Default MAM3 emissions data (available from the CESM input data repository).
    - Modified MAM3 emissions data (https://doi.org/10.6084/m9.figshare.6072887).
    - CESM output data in timeseries format (https://doi.org/10.6084/m9.figshare.6072887).
    - Data from G16 (Grandey et al., JClim, 2016) (http://doi.org/10.6084/m9.figshare.2067084).
    - GPCP v2.3 1981-2010 mean monthly data
      (https://www.esrl.noaa.gov/psd/data/gridded/data.gpcp.html, accessed 2018-07-18).

Author:
    Benjamin S. Grandey, 2018
"""

import climapy  # https://doi.org/10.5281/zenodo.1053020
import os
import pandas as pd
import re
import xarray as xr


# Directories holding data
# Modified emissions, https://doi.org/10.6084/m9.figshare.6072887
p17d_emis_dir = os.path.expandvars('$HOME/data/figshare/figshare6072887/input_data_p17d/')
# Default MAM3 emissions
mam_emis_dir = os.path.expandvars('$HOME/data/inputdataCESM/trop_mozart_aero/emis/')
# CESM output data in timeseries format, https://doi.org/10.6084/m9.figshare.6072887
output_dir = os.path.expandvars('$HOME/data/figshare/figshare6072887/')
# G16 CESM output data, https://doi.org/10.6084/m9.figshare.2067084
g16_dir = os.path.expandvars('$HOME/data/figshare/figshare2067084/')
# GPCP v2.3 1981-2010 mean monthly climatology file
gpcp_filename = os.path.expandvars('$HOME/data/datasets/gpcp/precip.mon.ltm.nc')


def dependency_versions():
    """
    Get versions of dependencies.
    """
    version_dict = {}
    for package in [climapy, os, pd, xr]:
        try:
            version_dict[package.__name__] = package.__version__
        except AttributeError:
            pass
    return version_dict


def load_region_bounds_dict():
    """
    Load dictionary containing region short names (keys) and bounds (values).
    The bounds are in the order [longitude tuple, latitude tuple].
    """
    region_bounds_dict = {'ESEAs': [(94, 161), (-10, 65)],  # modified emissions regions
                          'EAs': [(100, 130), (20, 45)],  # as in Grandey et al. (2016)
                          'SAs': [(65, 90), (5, 30)],
                          'Aus': [(110, 155), (-45, -10)],
                          'Sah': [(-20, 10), (10, 20)],
                          'WAWJ': [(-25, -15), (8.4, 10.6)],
                          'NH': [None, (0, 90)],
                          'SH': [None, (-90, 0)],
                          'Globe': [None, None]}
    return region_bounds_dict


def load_region_long_dict():
    """
    Load dictionary containing region short names (keys) and long names (values).
    """
    region_long_dict = {'ESEAs': 'East and Southeast Asia',  # modified emissions regions
                        'EAs': 'East Asia',
                        'SAs': 'South Asia',
                        'Aus': 'Australia',
                        'Sah': 'Sahel',
                        'WAWJ': 'West African Westerly Jet',
                        'NH': 'Northern Hemisphere',
                        'SH': 'Southern Hemisphere',
                        'Globe': 'globe'}
    return region_long_dict


def load_scenario_name_dict():
    """
    Load dictionary containing scenarios and the names used to refer to the scenarios.
    """
    scenario_name_dict = {'2000': 'Ref',
                          'eas0b': 'Exp1',
                          'eas0c': 'Exp2',
                          'R45': 'RCP4.5',
                          'A2x': 'A2x',
                          'pR45': 'pRCP4.5',
                          'pA2x': 'pA2x'}
    return scenario_name_dict


def load_variable_long_dict():
    """
    Load dictionary containing variable long names of CESM output variables of potential interest,
    assuming one is primarily looking at differences between scenarios.
    """
    variable_long_dict = {'FSNTOA+LWCF': 'Net effective radiative forcing',
                          'SWCF_d1': r'$\Delta$ clean-sky shortwave cloud radiative effect',
                          'LWCF': r'$\Delta$ longwave cloud radiative effect',
                          'FSNTOA-FSNTOA_d1': r'$\Delta$ direct radiative effect',
                          'FSNTOAC_d1': r'$\Delta$ surface albedo radiative effect',
                          'CLDHGH': r'$\Delta$ high cloud fraction',
                          'TGCLDIWP': r'$\Delta$ ice water path',
                          'TS': r'$\Delta$ surface temperature',
                          'PRECC+PRECL': r'$\Delta$ total precipitation rate',
                          'OMEGA_ml19': r'$\Delta$ vertical velocity at level $19$ ' +
                                        '($\approx 525$hPa})',
                          'U_ml27': r'$\Delta$ zonal wind at level $27$ ($\approx 936$hPa})'
                          }
    return variable_long_dict


def load_variable_symbol_dict():
    """
    Load dictionary containing variable symbols, for differences between scenarios.
    """
    variable_symbol_dict = {'FSNTOA+LWCF': r'$\Delta ERF_\mathrm{SW+LW}$',
                            'SWCF_d1': r'$\Delta CRE_\mathrm{SW}$',
                            'LWCF': r'$\Delta CRE_\mathrm{LW}$',
                            'FSNTOA-FSNTOA_d1': r'$\Delta DRE_\mathrm{SW}$',
                            'FSNTOAC_d1': r'$\Delta SRE_\mathrm{SW}$',
                            'CLDHGH': r'$\Delta$ high cloud fraction',
                            'TGCLDIWP': r'$\Delta$ ice water path',
                            'TS': r'$\Delta T$',
                            'PRECC+PRECL': r'$\Delta R$',
                            'OMEGA_ml19': r'$\Delta \omega$',
                            'U_ml27': r'$\Delta u$',
                            }
    return variable_symbol_dict


def load_variable_units_dict():
    """
    Load dictionary containing variable units - after scale factors have been applied.
    """
    variable_units_dict = {'FSNTOA+LWCF': r'W m$^{-2}$',
                           'SWCF_d1': r'W m$^{-2}$',
                           'LWCF': r'W m$^{-2}$',
                           'FSNTOA-FSNTOA_d1': r'W m$^{-2}$',
                           'FSNTOAC_d1': r'W m$^{-2}$',
                           'CLDHGH': r'$\times 10^{-3}$',
                           'TGCLDIWP': r'g m$^{-2}$',
                           'TS': r'$^{\circ}$C',
                           'PRECC+PRECL': r'mm year$^{-1}$',
                           'OMEGA_ml19': r'$\times 10^{-3}$ Pa s$^{-1}$',
                           'U_ml27': r'm s$^{-1}$',
                           }
    return variable_units_dict


def load_variable_sf_dict():
    """
    Load dictionary containing scale-factors to apply to variables.
    """
    variable_sf_dict = {'CLDHGH': 1e3,  # -> x10^-3
                        'TGCLDIWP': 1e3,  # kg/m2 -> g/m2
                        'PRECC+PRECL': 1e3*60*60*24*365,  # m/s -> mm/year
                        'OMEGA_ml19': 1000,  # Pa/s -> mPa/s
                        }
    return variable_sf_dict


def load_variable_g16_dict():
    """
    Load dictionary containing equivalent variables in the G16 data.
    """
    variable_g16_dict = {'FSNTOA+LWCF': 'cFNTOA',
                         'SWCF_d1': 'SWCF_d1',
                         'LWCF': 'LWCF_d1',  # clean-sky LWCF similar to normal LWCF
                         'FSNTOA-FSNTOA_d1': 'cDRE',
                         'FSNTOAC_d1': 'FSNTOAC_d1',
                         'TS': 'TS',
                         'PRECC+PRECL': 'PRECT'
                         }
    return variable_g16_dict


def load_species_sf_dict():
    """
    Load dictionary of scale factors for molecules/cm2/s -> g/m2/yr and
    particles/cm2/s*6.022e26 -> particles/m2/yr for different emitted species
    """
    species_sf_dict = {'so2': (365*24*60*60)*(100*100)*(64/6.02214e23),  # g(SO2)/m2/yr
                       'oc': (365*24*60*60)*(100*100)*(12/6.02214e23),
                       'bc': (365*24*60*60)*(100*100)*(12/6.02214e23),
                       'so4_a1': (365*24*60*60)*(100*100)*(64/6.02214e23),  # g(SO2)/m2/yr
                       'num_a1': (365*24*60*60)*(100*100)*(1/6.022e26),  # particles/m2/yr
                       'so4_a2': (365*24*60*60)*(100*100)*(64/6.02214e23),
                       'num_a2': (365*24*60*60)*(100*100)*(1/6.022e26),  # particles/m2/yr
                       }
    return species_sf_dict


def load_emissions(species='so2', surf_or_elev='both', scenario='eas0c', season='annual'):
    """
    Load annual/seasonal emissions for a specific species and scenario.

    Args:
        species: species name (default 'so2')
        surf_or_elev: 'surf' (surface), 'elev' (elevated), or 'both' (sum; default)
        scenario: scenario name (default 'eas0c')
        season: 'annual' (default) or name of season (e.g 'DJF')

    Returns:
        xarray DataArray
    """
    # If 'both', call function recursively
    if surf_or_elev == 'both':
        surf_data = load_emissions(species=species, surf_or_elev='surf', scenario=scenario,
                                   season=season)
        elev_data = load_emissions(species=species, surf_or_elev='elev', scenario=scenario,
                                   season=season)
        data = surf_data + elev_data
    else:
        # Read data
        try:  # if emissions modified use modified emissions...
            filename = '{}/{}_{}_p17d_{}.nc'.format(p17d_emis_dir, species, surf_or_elev, scenario)
            ds = xr.open_dataset(filename, decode_times=False, drop_variables=['date', ])
        except FileNotFoundError:  # ... otherwise use default MAM3 emissions
            filename = '{}/ar5_mam3_{}_{}_2000_c090726.nc'.format(mam_emis_dir, species,
                                                                  surf_or_elev, scenario)
            ds = xr.open_dataset(filename, decode_times=False, drop_variables=['date', ])
        # If emissions are 3D, convert to 2D
        if surf_or_elev == 'elev':
            alt_deltas = (ds['altitude_int'].values[1:] -
                          ds['altitude_int'].values[:-1]) * 100 * 1000  # depth of levels in cm
            alt_deltas = xr.DataArray(alt_deltas, coords={'altitude': ds['altitude'].values},
                                      dims=['altitude', ])  # set coordinates to altitude
            ds = (ds * alt_deltas).sum(dim='altitude').drop('altitude_int')
        # Add time coord; use 2000 as year
        ds['time'] = pd.date_range('2000-01-01', '2000-12-31', freq='MS') + pd.Timedelta('14 days')
        # Calculate annual/seasonal mean, using arithmetic mean across months
        if season == 'annual':
            ds = ds.mean(dim='time')
        else:
            ds = ds.groupby('time.season').mean(dim='time').sel(season=season)
        # Convert to g/m2/yr
        ds = ds * load_species_sf_dict()[species]
        # Sum across categories
        for var_name in ds.data_vars.keys():
            try:
                ds[species+'_'+surf_or_elev] += ds[var_name]
            except KeyError:
                ds[species+'_'+surf_or_elev] = ds[var_name]
        data = ds[species+'_'+surf_or_elev].load()
    return data


def load_output(variable='TS', scenario='eas0c', f_or_b='b', season='annual', apply_sf=True):
    """
    Load annual/seasonal data for a specific variable and scenario.

    Args:
        variable: string of variable name to load (default 'TS')
        scenario: string scenario name (default 'eas0c')
        f_or_b: 'f' (prescribed-SST) or 'b' (coupled atmosphere-ocean; default)
        season: 'annual' (default) or name of season (e.g 'DJF')
        apply_sf: apply scale factor? (default True)

    Returns:
        xarray DataArray
    """
    # If + or - in variable and the scenario is not a G16 scenario, call function recursively
    if ('+' in variable or '-' in variable) and scenario in ['2000', 'eas0b', 'eas0c']:
        variable1, variable2 = re.split('[+\-]', variable)
        data1 = load_output(variable1, scenario=scenario, f_or_b=f_or_b, season=season,
                            apply_sf=apply_sf)
        data2 = load_output(variable2, scenario=scenario, f_or_b=f_or_b, season=season,
                            apply_sf=apply_sf)
        if '+' in variable:
            data = data1 + data2
        elif '-' in variable:
            data = data1 - data2
    elif scenario in ['2000', 'eas0b', 'eas0c']:  # p17d simulations
        # Read data
        in_filename = '{}/p17d_{}_{}.cam.h0.{}.nc'.format(output_dir, f_or_b, scenario, variable)
        ds = xr.open_dataset(in_filename, decode_times=False)
        # Convert time coordinates
        ds = climapy.cesm_time_from_bnds(ds, min_year=1701)
        # Calculate annual/seasonal mean for each year (Jan-Dec), using arithmetic mean
        if season == 'annual':
            data = ds[variable].groupby('time.year').mean(dim='time')
        else:
            data = ds[variable].where(ds['time.season'] == season,
                                      drop=True).groupby('time.year').mean(dim='time')
        # Discard spin-up
        if f_or_b == 'f':  # discard two years for 'f' simulations
            data = data.where(data['year'] >= 1703, drop=True)
        elif f_or_b == 'b':  # discard 40 years for 'b' simulations
            data = data.where(data['year'] >= 1741, drop=True)
    elif scenario in ['pA2x', 'pR45']:  # G16 prescribed-SST simulations
        # Get G16 equivalent variable name
        variable_g16 = load_variable_g16_dict()[variable]
        # Read data
        in_filename = '{}/{}.nc'.format(g16_dir, scenario)
        ds = xr.open_dataset(in_filename, decode_times=False)
        # Convert time coordinates
        ds = climapy.cesm_time_from_bnds(ds, min_year=1701)
        # Calculate annual/seasonal mean for each year (Jan-Dec), using arithmetic mean
        if season == 'annual':
            data = ds[variable_g16].groupby('time.year').mean(dim='time')
        else:
            data = ds[variable_g16].where(ds['time.season'] == season,
                                      drop=True).groupby('time.year').mean(dim='time')
        # Discard two years spin-up (diff from G16, where 2 years 11 months were discarded)
        data = data.where(data['year'] >= 1703, drop=True)
    else:  # G16 transient simulations
        # Get G16 equivalent variable name
        variable_g16 = load_variable_g16_dict()[variable]
        # Get data for three ensemble members
        da_list = []
        for ic in ['f1', 'h1', 'h2']:
            # Read data
            in_filename = '{}/{}_{}.nc'.format(g16_dir, scenario, ic)
            ds = xr.open_dataset(in_filename, decode_times=False)
            # Convert time coordinates
            ds = climapy.cesm_time_from_bnds(ds, min_year=1701)
            # Calculate annual/seasonal mean for each year (Jan-Dec), using arithmetic mean
            if season == 'annual':
                da = ds[variable_g16].groupby('time.year').mean(dim='time')
            else:
                da = ds[variable_g16].where(ds['time.season'] == season,
                                            drop=True).groupby('time.year').mean(dim='time')
            # Select 2080-2099
            da = da.where(da['year'] >= 2080, drop=True)
            # Shift time dimension to facilitate concatenation
            if ic == 'h1':
                da['year'] += 20
            elif ic == 'h2':
                da['year'] += 40
            # Append to list
            da_list.append(da)
        # Concatenate data from three ensemble members
        data = xr.concat(da_list, dim='year')
    # Apply scale factor?
    if apply_sf:
        try:
            data = data * load_variable_sf_dict()[variable]
        except KeyError:
            pass
    return data


_output_monthly_dict = {}  # dictionary to hold results from load_output_monthly()


def load_output_monthly(variable='TS', scenario='eas0c', f_or_b='b', apply_sf=True):
    """
    Load monthly data for a specific variable and scenario.

    Args:
        variable: string of variable name to load (default 'TS')
        scenario: string scenario name (default 'eas0c')
        f_or_b: 'f' (prescribed-SST) or 'b' (coupled atmosphere-ocean; default)
        apply_sf: apply scale factor? (default True)

    Returns:
        xarray DataArray
    """
    # Check if monthly outout has been loaded previously
    try:
        data = _output_monthly_dict[(variable, scenario, f_or_b, apply_sf)]
    except KeyError:
        # If + or - in variable and the scenario is not a G16 scenario, call function recursively
        if ('+' in variable or '-' in variable) and scenario in ['2000', 'eas0b', 'eas0c']:
            variable1, variable2 = re.split('[+\-]', variable)
            data1 = load_output_monthly(variable1, scenario=scenario, f_or_b=f_or_b,
                                        apply_sf=apply_sf)
            data2 = load_output_monthly(variable2, scenario=scenario, f_or_b=f_or_b,
                                        apply_sf=apply_sf)
            if '+' in variable:
                data = data1 + data2
            elif '-' in variable:
                data = data1 - data2
        elif scenario in ['2000', 'eas0b', 'eas0c']:  # p17d simulations
            # Read data
            in_filename = '{}/p17d_{}_{}.cam.h0.{}.nc'.format(output_dir, f_or_b, scenario, variable)
            ds = xr.open_dataset(in_filename, decode_times=False)
            # Convert time coordinates
            ds = climapy.cesm_time_from_bnds(ds, min_year=1701)
            # Select variable
            data = ds[variable]
            # Split time into separate year and month dimensions
            d_list = []
            for m in range(1, 13):  # loop over months
                d = data.where(data['time.month'] == m,
                               drop=True).groupby('time.year').mean(dim='time')
                d['month'] = m  # add month coordinate
                d_list.append(d)
            data = xr.concat(d_list, dim='month')
            # Discard spin-up
            if f_or_b == 'f':  # discard two years for 'f' simulations
                data = data.where(data['year'] >= 1703, drop=True)
            elif f_or_b == 'b':  # discard 40 years for 'b' simulations
                data = data.where(data['year'] >= 1741, drop=True)
        elif scenario in ['pA2x', 'pR45']:  # G16 prescribed-SST simulations
            raise NotImplementedError('G16 prescribed-SST simulations not supported')
        else:  # G16 transient simulations
            # Get G16 equivalent variable name
            variable_g16 = load_variable_g16_dict()[variable]
            # Get data for three ensemble members
            da_list = []
            for ic in ['f1', 'h1', 'h2']:
                # Read data
                in_filename = '{}/{}_{}.nc'.format(g16_dir, scenario, ic)
                ds = xr.open_dataset(in_filename, decode_times=False)
                # Convert time coordinates
                ds = climapy.cesm_time_from_bnds(ds, min_year=1701)
                # Select variable
                da = ds[variable_g16]
                # Split time into separate year and month dimensions
                d_list = []
                for m in range(1, 13):  # loop over months
                    d = da.where(da['time.month'] == m,
                                 drop=True).groupby('time.year').mean(dim='time')
                    d['month'] = m  # add month coordinate
                    d_list.append(d)
                da = xr.concat(d_list, dim='month')
                # Select 2080-2099
                da = da.where(da['year'] >= 2080, drop=True)
                # Shift time dimension to facilitate concatenation
                if ic == 'h1':
                    da['year'] += 20
                elif ic == 'h2':
                    da['year'] += 40
                # Append to list
                da_list.append(da)
            # Concatenate data from three ensemble members
            data = xr.concat(da_list, dim='year')
        # Apply scale factor?
        if apply_sf:
            try:
                data = data * load_variable_sf_dict()[variable]
            except KeyError:
                pass
        # Save result for future reference
        _output_monthly_dict[(variable, scenario, f_or_b, apply_sf)] = data
    return data


def load_landfrac():
    """
    Load land fraction (LANDFRAC).
    LANDFRAC is invariant across time and scenarios.

    Returns:
        xarray DataArray
    """
    # Read data
    in_filename = '{}/LANDFRAC/p17d_f_000.cam.h0.LANDFRAC.nc'.format(output_dir)
    ds = xr.open_dataset(in_filename, decode_times=False)
    # Convert time coordinates
    ds = climapy.cesm_time_from_bnds(ds, min_year=1701)
    # Collapse time dimension (by calculating mean across time)
    data = ds['LANDFRAC'].mean(dim='time')
    return data
