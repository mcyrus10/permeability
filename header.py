#!/Users/cyrus/miniconda3/bin/python3
import os
from sys import argv
from numpy import array,flipud,concatenate,zeros,ones,hstack,vstack,fliplr
import numpy as np
import porespy as ps
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#==============================================================================
def parse_input_file(   fname):
    retDict = {}
    with open(fname,'r') as f:
        text = list(filter(None,f.read().split("\n")))
    for line in text:
        if "#------" not in line:
            temp = line.split(" ")
            retDict[temp[0]] = temp[2]
    return(retDict)

def z_map(  array_2d,k):
    temp = array_2d-1
    temp[temp == -1]*= -k
    return(temp)

def render_scatter_3D(  im):
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
    return xs,ys,zs
