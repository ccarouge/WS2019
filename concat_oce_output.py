#!/usr/bin/env python
# # coding: utf-8

# How to concatenate several years of ocean outputs from Mk3L.
# 
# There is 1 netcdf file per year. Each file contains all variables. The outputs are monthly so each file contains 12 timesteps.


import glob
import os.path
import xarray as xr
import pandas as pd
import argparse


def concat_ocean(path, file_template):
    fname = os.path.join(path, file_template)
    file_list = sorted(glob.glob(fname))

    ds = xr.open_mfdataset(file_list, concat_dim='month')
    # New time coordinate to include the year. 
    time=xr.cftime_range(start='0001', periods=600, freq='MS', calendar='noleap')
    
    # Replace the month coordinate with these new values and rename to time
    ds = ds.assign_coords(month=time).rename(month='time')
    return ds


if __name__ == '__main__':
    # User inputs:
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',default='./',help='Path with the Mk3L ocean outputs', dest='path')
    parser.add_argument('-r',default='ctl01', help='Name of the experiment', dest='run')

    args = parser.parse_args()
    file_template = f'com.{args.run}.[0-9]*.nc'


    test = concat_ocean(args.path, file_template)
    clim = test.groupby('time.year').mean(dim='time')  # Annual mean
    dd = {var: var+"_clim" for var in clim.data_vars}  # Rename clim variables
    clim = clim.rename(dd)
    for var in test.data_vars:
        fname = os.path.join(args.path,f'com.ctl01.{var}_all_yr.nc')
        ds = xr.merge([test[var], clim[var+"_clim"]])
        ds.to_netcdf(fname)



