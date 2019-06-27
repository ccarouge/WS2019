#!/usr/bin/env python

import glob
import argparse
import os
import numpy as np
import xarray as xr


if __name__ == '__main__':

    # User id
    user = os.environ['USER']
    # User inputs:
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',default='/g/data/hh5/WS2019/'+user,help='Base path for experiment (/g/data/hh5/WS2019/$USER normally)', dest='path')
    parser.add_argument('-r',default='ctl01', help='Name of the experiment', dest='run')
    parser.add_argument('-v',default='t', help='Name of variable to be processed', dest='var')
    parser.add_argument('-l',default='pressure', help='Type of vertical levels', dest='lev')

    args = parser.parse_args()
    args.path = os.path.join(args.path,args.run)
    file_template = f's{args.var}[0-9][0-9]_{args.run}.nc'

    path = os.path.join(args.path,file_template)
    files=sorted(glob.glob(path))

    print("Reading files: ", path)
    # Rename temperature variable from t to temp
    if args.var == 't':
        args.var = 'temp'

    # Parameters:
    #--------------
    # Vertical coordinate in pressure and height
    pressure = xr.DataArray(np.asarray([1000,925,850,700,600,500,400,300,250,200,150,100,70,50,30,20,10,5],dtype=np.int32),dims=('lev',),attrs={'units':'hPa'})
    height = xr.DataArray(np.asarray([165,300,575,990,1535,2215,3025,3970,5070,6335,7780,9440,11360,13650,16550,20600,27360,36355],dtype=np.int32), dims=('lev',),attrs={'units':'m'})


    # Choose vert. coordinate depending on input argument
    if args.lev == 'pressure':
        lev = pressure
    else:
        lev = height
    
    # Read file and deal with missing values
    ds= xr.open_mfdataset(files)
    ds = ds.where(ds < 9.e36)

    out=xr.concat([ds[dd] for dd in ds.data_vars],dim='lev')
    out.coords['lev']=lev

    # Number of days per month
    days=xr.DataArray([31,28,31,30,31,30,31,31,30,31,30,31],dims=('month',),coords={'month':out['month']})/365

    # Compute annual mean (weighted by number of days in each month)
    print("Calculate annual mean")
    clim = out *days
    clim1 = clim.sum(dim='month')

    # Deal with missing values and leftover dimensions
    clim1 = clim1.where(out < 9.e36)
    clim1 = clim1.sel(month=1).drop('month')

    # Rename variable using name given as argument
    clim1 = clim1.rename(args.var)

    # New long name and units
    clim1.assign_attrs({'long_name': f'Annual-mean atmosphere {args.var}','units':out.units})

    # Write to netcdf
    print("Write output")
    fname = os.path.join(args.path,f's{args.var}_{args.run}_all_atm.nc')
    clim1.to_netcdf(fname)


