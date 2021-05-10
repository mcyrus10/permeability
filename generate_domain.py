#!/home/cyrus/miniconda3/bin/python3
# this script generates the simulation domain the function composite
from header import *

if __name__=="__main__":
    fields = [
                ('nx',int),
                ('ny',int),
                ('nz',int),
                ('radius',float),
                ('ncylinders',int),
                ('target_porosity',float),
                ('phi_max',float),
                ('theta_max',float),
                ('composite',int),
                ('cyl_proportion',float)
            ]

    plt.rcParams['xtick.bottom'] = False
    plt.rcParams['xtick.labelbottom'] = False
    plt.rcParams['ytick.left'] = False
    plt.rcParams['ytick.labelleft'] = False
    params_path = "params.xml"
    # read in params from 'params.xml'
    input_params = read_xml(params_path,fields)
    nx = input_params['nx']
    ny = input_params['ny']
    nz = input_params['nz']
    composite = bool(input_params['composite'])
    cyl_proportion = input_params['cyl_proportion']
    shape = [nx,ny,nz]
    target_porosity = input_params['target_porosity']
    theta_max = input_params['theta_max']
    phi_max = input_params['phi_max']
    radius = input_params['radius']
    ncylinders = input_params['ncylinders']

    #--------------------------------------------------------------------------
    im,cyl,blob,ncylinders = composite_domain(input_params, thresh = 0.01, blobiness = 1)
    #--------------------------------------------------------------------------

    actual_porosity = ps.metrics.porosity(im)

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
    fs = (20,20)
    fig,ax = plt.subplots(2,3, num = 1, figsize = fs)
    ax = ax.flatten()
    if composite:
        ax[0].imshow(ps.visualization.show_3D(blob))
        ax[3].imshow(ps.visualization.sem(blob))
    ax[1].imshow(ps.visualization.show_3D(cyl))
    ax[2].imshow(ps.visualization.show_3D(im.astype(bool)))
    ax[4].imshow(ps.visualization.sem(cyl))
    ax[5].imshow(ps.visualization.sem(im.astype(bool)))
    ax[0].set_title("Binder Component")
    ax[1].set_title("Fiber Component")
    ax[2].set_title("Composite")
    fig.tight_layout()
    plt.show()
