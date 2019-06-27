#!/usr/bin/env python

import glob
import os.path
import xarray as xr
import pandas as pd
import argparse
import cftime
import os

def concat_ocean(path, file_template):
    fname = os.path.join(path, file_template)
    file_list = sorted(glob.glob(fname))

    ds = xr.open_mfdataset(file_list, concat_dim='month',decode_cf=False)
    # New time coordinate to include the year. 
    # Arbitrary add 1800 to make it easier to deal with the date! (Calendar issues)
    #ds.load()
    time=xr.cftime_range(start='0001', periods=600, freq='MS', calendar='noleap')
    
    # Replace the month coordinate with these new values and rename to time
    ds = ds.where(ds > -1.e34)
    ds = ds.assign_coords(month=time).rename(month='time')
    return ds


if __name__ == '__main__':
    user = os.environ['USER']

    # User inputs:
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',default='/g/data/hh5/WS2019/'+user,help='Base path for experiment (/g/data/hh5/WS2019/$USER normally)', dest='path')
    parser.add_argument('-r',default='ctl01', help='Name of the experiment', dest='run')

    args = parser.parse_args()
    args.path = os.path.join(args.path,args.run)
    file_template = f'com.{args.run}.[0-9]*.nc'
    print(f"Reading all files: {file_template} from {args.path}")

    test = concat_ocean(args.path, file_template)
    print("Data loaded")
    clim = test.groupby('time.year').mean(dim='time')  # Annual mean
    dd = {var: var+"_mean" for var in clim.data_vars}  # Rename clim variables
    clim = clim.rename(dd)
    print("Mean calculated")
    for var in test.data_vars:
        fname = os.path.join(args.path,f'com.ctl01.{var}_all_yr.nc')
        print(f"Writing {var}")
        ds = xr.merge([test[var], clim[var+"_mean"]])
        ds.to_netcdf(fname)

