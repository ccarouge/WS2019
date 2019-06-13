#!/Users/ccc/miniconda3/envs/analight3/bin/python
# coding: utf-8

# How to concatenate several years of ocean outputs from Mk3L.
# 
# There is 1 netcdf file per year. Each file contains all variables. The outputs are monthly so each file contains 12 timesteps.


import glob
import xarray as xr
import pandas as pd
import argparse


def time_coord(ds):
    '''Create a proper time coordinate for the ocean output from Mk3L.
    ds: xarray dataset from reading Mk3L ocean output(s)'''

    year = list(range(ds.sizes['month']//12))
    year = [str(i+1800)+'{:0>2}'.format(m+1) for i in year for m in range(12)]

    time=pd.to_datetime(year, format="%Y%m")

    return time

def concat_ocean(path, file_template):
    file_list = sorted(glob.glob(path+file_template))
    file_list

    ds = xr.open_mfdataset(file_list, concat_dim='month')
    # New time coordinate to include the year. 
    # Arbitrary add 1800 to make it easier to deal with the date! (Calendar issues)
    time=time_coord(ds)
    
    # Replace the month coordinate with these new values and rename to time
    ds = ds.assign_coords(month=time).rename(month='time')
    return ds

if __name__ == '__main__':
    # User inputs:
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',default='./',help='Path with the Mk3L ocean outputs', dest='path')
    parser.add_argument('-r',default='ctl01', help='Name of the experiment', dest='run')

    args = parser.parse_args()
    file_template = f'com.{args.run}.*.nc'
    print(file_template)

    test = concat_ocean(args.path, file_template)
    for var in test.variables:
        test[var].to_netcdf(f'com.ctl01.{var}_all_yr.nc')



