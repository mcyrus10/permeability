#!/home/cyrus/miniconda3/bin/python3
from mpl_toolkits.mplot3d import Axes3D
from sys import argv
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import porespy as ps
#==============================================================================
def parse_input_file(   fname): # {{{
    retDict = {}
    with open(fname,'r') as f:
        text = list(filter(None,f.read().split("\n")))
    for line in text:
        if "#------" not in line:
            temp = line.split(" ")
            retDict[temp[0]] = temp[2]
    return(retDict) # }}}
def z_map(  array_2d,k): # {{{
    temp = array_2d-1
    temp[temp == -1]*= -k
    return(temp) # }}}
def render_scatter_3D(  im): # {{{
    #--------------------------------------------------------------------------
    # this function renders xs,ys, and zs to use in
    # mpl_toolkits.mplot3d.Axes3D.scatter it creates an array of xs and ys such
    # that xs goes from 0 to nx for each y-value. eg:
    #       xs = [0,1,2,3,0,1,2,3,0,1,2,3]
    #       ys = [0,0,0,0,1,1,1,1,2,2,2,2]
    #       zs = [0,0,0,0,1,1,1,1,0,0,0,0]
    # note that the zeros for zs are actually 'nans' so they are rendered as
    # void space
    #--------------------------------------------------------------------------
    nx,ny,nz = im.shape
    numel = np.prod(im.shape)
    xs = np.array(list(range(nx))*ny*nz).astype(np.int)
    ys = np.array([np.ones(nx)*j for j in range(ny)]*nz).astype(np.int).flatten()
    zs = np.zeros((nx,ny,nz))
    for k in range(nz):
        temp = z_map(im[:,:,k],k)
        zs[:,:,k] = temp
    zs = zs.flatten(order = 'F')
    zs[zs==0] = np.nan
    return xs,ys,zs # }}}
def read_xml(f_name,fields):# {{{
    retDict = {}
    with open(f_name,'r') as f:
        text = f.read().split("\n")
    for line in text:
        for field in fields:
            if "<{}>".format(field[0]) in line:
                temp = list(filter(None,line.split(" ")))
                retDict[field[0]] = field[1](temp[1])
    return(retDict)
    # }}}
def batch_csv_read(path): # {{{
    #--------------------------------------------------------------------------
    # this is for reading the csv data with arbitrary headers, etc. so that you
    # don't have to keep rewriting this function for all different batch sweeps
    #--------------------------------------------------------------------------
    with open(path,'r') as f:
        names = f.readlines()[2][1:].split(",")
    names = [name[1:] for name in names]
    names[-1] = names[-1].split("\n")[0]
    return pd.read_csv(path,delimiter = ',', skiprows = 4, names = names) # }}}
def composite_domain(input_params, thresh = 0.01, blobiness = 1): # {{{
    #--------------------------------------------------------------------------
    # this generates a domain that is a composite of blobs and cylinders the
    # cyl_proportion parameter (0-1) controls how much of the porosity is
    # composed of cylinders
    # it uses a 2nd order polynomial fit to estimate the number of cylinders to
    # achieve the target porosity (since the cylinders generator does not have
    # a porosity argument, but only the number of cylinders)
    #--------------------------------------------------------------------------
    nx = input_params['nx']
    ny = input_params['ny']
    nz = input_params['nz']
    shape = [nx,ny,nz]
    composite = bool(input_params['composite'])
    cyl_proportion = input_params['cyl_proportion']
    phi_max = input_params['phi_max']
    theta_max = input_params['theta_max']
    target_porosity = input_params['target_porosity']
    radius = input_params['radius']
    ncylinders = input_params['ncylinders']
    actual_porosity = 0.0                               # starting value for while loop
    big_step = 10
    j=0
    cylinders = []
    porosity = []
    cyl = np.ones(shape).astype(bool)
    im = np.ones(shape).astype(bool)
    blob = np.ones(shape).astype(bool)
    if composite:
        blob_porosity = (1-target_porosity)*cyl_proportion + target_porosity

        blob = ps.generators.blobs(     shape=shape,
                                        porosity = blob_porosity,
                                        blobiness = blobiness)
        blob_p = ps.metrics.porosity(blob)

        while abs(blob_p - blob_porosity) > thresh:
            blob = ps.generators.blobs(     shape=shape,
                                            porosity = blob_porosity,
                                            blobiness = blobiness)
            blob_p = ps.metrics.porosity(blob)
            print("target_blob = {}; blob porosity = {}".format(blob_porosity, blob_p))

        actual_porosity = blob_p.copy()
        im = blob.copy()
    while abs(actual_porosity-target_porosity)>thresh:
        cyl = ps.generators.cylinders(  shape = shape,
                                        radius = radius,
                                        ncylinders = ncylinders,
                                        theta_max = theta_max,
                                        phi_max = phi_max)

        cyl_p = ps.metrics.porosity(cyl)
        im = ~(~blob+~cyl) if composite else cyl
        #==========================================================================
        actual_porosity = ps.metrics.porosity(im)
        print('Iteration:{}; Porosity = {}; cyl = {}; n_cylinders = {}'.format(j,actual_porosity,cyl_p,ncylinders))
        diff = actual_porosity-target_porosity
        cylinders.append(ncylinders)
        porosity.append(actual_porosity)
        if j == 0:
            ncylinders+=100
        else:
            fit = np.polyfit(porosity,cylinders,2)
            ncylinders = int(np.polyval(fit,target_porosity))
        j+=1
    return im, cyl, blob, ncylinders # }}}
