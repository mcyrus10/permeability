#!/Users/cyrus/miniconda3/bin/python3
from header import *

def read_xml(   f_name,
                fields):
    # {{{
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

fields = [
            ('nx',int),
            ('ny',int),
            ('nz',int),
            ('radius',float),
            ('ncylinders',int),
            ('target_porosity',float),
            ('phi_max',float),
            ('theta_max',float),
        ]

params_path = "params.xml"
# read in params from 'params.xml'
inputParams = read_xml(params_path,fields)
nx = inputParams['nx']
ny = inputParams['ny']
nz = inputParams['nz']
shape = [nx,ny,nz]
target_porosity = inputParams['target_porosity']
theta_max = inputParams['theta_max']
phi_max = inputParams['phi_max']
radius = inputParams['radius']
ncylinders = inputParams['ncylinders']

actual_porosity = 0
thresh = .01
#==============================================================================
# Domain Parameters
#inputs = parse_input_file('input.dat')
#nx = int(inputs['nx'])
#ny = int(inputs['ny'])
#nz = int(inputs['nz'])
#shape = [nx,ny,nz]
#target_porosity = float(inputs['target_porosity'])
#radius = float(inputs['radius'])
#ncylinders = int(inputs['ncylinders'])
#phi_max = float(inputs['phi_max'])
#theta_max = float(inputs['theta_max'])
#==============================================================================
# Generator
big_step = 10
j=0
cylinders = []
porosity = []

while abs(actual_porosity-target_porosity)>thresh:
    im = ps.generators.cylinders(   shape=shape,
                                    radius = radius,
                                    ncylinders = ncylinders,
                                    theta_max = theta_max,
                                    phi_max = phi_max)
    #==========================================================================
    actual_porosity = ps.metrics.porosity(im)
    print('Iteration:{}; Porosity = {}'.format(j,actual_porosity))
    diff = actual_porosity-target_porosity
    cylinders.append(ncylinders)
    porosity.append(actual_porosity)
    plt.plot(ncylinders,actual_porosity,'kx')
    if j == 0:
        ncylinders-=20
    else:
        fit = np.polyfit(porosity,cylinders,1)
        ncylinders = int(np.polyval(fit,target_porosity))
    j+=1

plt.show()
target = 'porespy_palabos_geometry'

with open('.{}.info'.format(target),'w') as f:
    f.write("nx = {}\n".format(nx))
    f.write("ny = {}\n".format(ny))
    f.write("nz = {}\n".format(nz))
    f.write("radius = {}\n".format(radius))
    f.write("ncylinders = {}\n".format(ncylinders))
    f.write("porosity (calcualted) = {}\n".format(actual_porosity))
    f.write("porosity (target) = {}\n".format(target_porosity))
    f.write("theta_max = {}\n".format(theta_max))
    f.write("phi_max = {}\n".format(phi_max))
print('-'*80)
ps.io.to_palabos(   im,
                    '{}.dat'.format(target),
                    solid = 0)
ps.io.to_vtk(   im,
                path = 'tmp/domain')
print('File written successfully ({})'.format(target))
print('target porosity = ',target_porosity)
print('porosity = ', actual_porosity)
print('ncylinders = ', ncylinders)
print('diff porosity = ',abs(ps.metrics.porosity(im)-target_porosity))
print('Visualize with paraview. File is in tmp/domain')
print('-'*80)
#input("Press enter")
#==============================================================================
# Visualization
#fs = (9,9)
#plt.figure(0, figsize = fs)
#plt.imshow(ps.visualization.show_3D(im))
#plt.figure(1, figsize = fs)
#plt.imshow(ps.visualization.sem(im))
#xs,ys,zs = render_scatter_3D(im)
#fig = plt.figure(2, figsize = fs)
#ax = fig.add_subplot(111, projection = '3d')
#ax.scatter(xs,ys,zs, marker= '.', color = 'k')
#plt.show()



