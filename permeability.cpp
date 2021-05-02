#include "base.h"

// This function object returns a zero velocity, and a pressure which decreases
//   linearly in x-direction. It is used to initialize the particle populations.
class PressureGradient {
public:
    PressureGradient(T deltaP_, plint nx_) : deltaP(deltaP_), nx(nx_)
    { }
    void operator() (plint iX, plint iY, plint iZ, T& density, Array<T,3>& velocity) const
    {
        velocity.resetToZero();
        density = (T)1 - deltaP*DESCRIPTOR<T>::invCs2 / (T)(nx-1) * (T)iX;

    }
private:
    T deltaP;
    plint nx;
};

void readGeometry(  std::string fNameIn,
                    std::string fNameOut,
                    MultiScalarField3D<int>& geometry)
{
    const plint nx = geometry.getNx();
    const plint ny = geometry.getNy();
    const plint nz = geometry.getNz();

    Box3D sliceBox(0,0, 0,ny-1, 0,nz-1);
    std::unique_ptr<MultiScalarField3D<int> > slice = generateMultiScalarField<int>(geometry, sliceBox);
    plb_ifstream geometryFile(fNameIn.c_str());
    for (plint iX=0; iX<nx-1; ++iX) {
        if (!geometryFile.is_open()) {
            pcout << "Error: could not open geometry file " << fNameIn << std::endl;
            exit(EXIT_FAILURE);
        }
        geometryFile >> *slice;
        copy(*slice, slice->getBoundingBox(), geometry, Box3D(iX,iX, 0,ny-1, 0,nz-1));
    }

    {
        VtkImageOutput3D<T> vtkOut("porousMedium", 1.0);
        vtkOut.writeData<float>(*copyConvert<int,T>(geometry, geometry.getBoundingBox()), "tag", 1.0);
    }

    {
        std::unique_ptr<MultiScalarField3D<T> > floatTags = copyConvert<int,T>(geometry, geometry.getBoundingBox());
        std::vector<T> isoLevels;
        isoLevels.push_back(0.5);
        typedef TriangleSet<T>::Triangle Triangle;
        std::vector<Triangle> triangles;
        Box3D domain = floatTags->getBoundingBox().enlarge(-1);
        domain.x0++;
        domain.x1--;
        isoSurfaceMarchingCube(triangles, *floatTags, isoLevels, domain);
        TriangleSet<T> set(triangles);
        std::string outDir = fNameOut + "/";
        set.writeBinarySTL(outDir + "porousMedium.stl");
    }
}

void porousMediaSetup(MultiBlockLattice3D<T,DESCRIPTOR>& lattice,
        OnLatticeBoundaryCondition3D<T,DESCRIPTOR>* boundaryCondition,
        MultiScalarField3D<int>& geometry, T deltaP)
{
    const plint nx = lattice.getNx();
    const plint ny = lattice.getNy();
    const plint nz = lattice.getNz();

    pcout << "Definition of inlet/outlet." << std::endl;
    Box3D inlet (0,0, 1,ny-2, 1,nz-2);
    boundaryCondition->addPressureBoundary0N(inlet, lattice);
    setBoundaryDensity(lattice, inlet, (T) 1.);

    Box3D outlet(nx-1,nx-1, 1,ny-2, 1,nz-2);
    boundaryCondition->addPressureBoundary0P(outlet, lattice);
    setBoundaryDensity(lattice, outlet, (T) 1. - deltaP*DESCRIPTOR<T>::invCs2);

    pcout << "Definition of the geometry." << std::endl;
    // Where "geometry" evaluates to 1, use bounce-back.
    defineDynamics(lattice, geometry, new BounceBack<T,DESCRIPTOR>(), 1);
    // Where "geometry" evaluates to 2, use no-dynamics (which does nothing).
    defineDynamics(lattice, geometry, new NoDynamics<T,DESCRIPTOR>(), 2);

    pcout << "Initilization of rho and u." << std::endl;
    initializeAtEquilibrium( lattice, lattice.getBoundingBox(), PressureGradient(deltaP, nx) );

    lattice.initialize();
    delete boundaryCondition;
}

void writeGifs(MultiBlockLattice3D<T,DESCRIPTOR>& lattice, plint iter)
{
    const plint nx = lattice.getNx();
    const plint ny = lattice.getNy();
    const plint nz = lattice.getNz();

    const plint imSize = 600;
    ImageWriter<T> imageWriter("leeloo");

    // Write velocity-norm at x=0.
    imageWriter.writeScaledGif(createFileName("ux_inlet", iter, 6),
            *computeVelocityNorm(lattice, Box3D(0,0, 0,ny-1, 0,nz-1)),
            imSize, imSize );

    // Write velocity-norm at x=nx/2.
    imageWriter.writeScaledGif(createFileName("ux_half", iter, 6),
            *computeVelocityNorm(lattice, Box3D(nx/2,nx/2, 0,ny-1, 0,nz-1)),
            imSize, imSize );
}

void writeVTK(MultiBlockLattice3D<T,DESCRIPTOR>& lattice, plint iter)
{
    VtkImageOutput3D<T> vtkOut(createFileName("vtk", iter, 6), 1.);
    vtkOut.writeData<float>(*computeVelocityNorm(lattice), "velocityNorm", 1.);
    vtkOut.writeData<3,float>(*computeVelocity(lattice), "velocity", 1.);
}

T computePermeability(MultiBlockLattice3D<T,DESCRIPTOR>& lattice, T nu, T deltaP, Box3D domain )
{
    pcout << "Computing the permeability." << std::endl;

    // Compute only the x-direction of the velocity (direction of the flow).
    plint xComponent = 0;
    plint nx = lattice.getNx();

    T meanU = computeAverage(*computeVelocityComponent(lattice, domain, xComponent));

    pcout << "Average velocity     = " << meanU                         << std::endl;
    pcout << "Lattice viscosity nu = " << nu                            << std::endl;
    pcout << "Grad P               = " << deltaP/(T)(nx-1)              << std::endl;
    pcout << "Permeability         = " << nu*meanU / (deltaP/(T)(nx-1)) << std::endl;

    return meanU;
}

int main(int argc, char **argv)
{
    plbInit(&argc, &argv);
    pcout << "start" << endl;

    SimulationParams<T> simParams = assign_params("params.xml");
    plint nx = simParams.getNx();       
    plint ny = simParams.getNy();
    plint nz = simParams.getNz();


    global::directories().setOutputDir("tmp/");

    const T omega   = 1.0/simParams.getTau();
    const T nu      = ((T)1/omega- (T)0.5)/DESCRIPTOR<T>::invCs2;
    const T deltaP  = simParams.getDeltaP();

    pcout << "Creation of the lattice." << std::endl;
    MultiBlockLattice3D<T,DESCRIPTOR> lattice(
                                            simParams.getNx(),
                                            simParams.getNy(),
                                            simParams.getNz(),
                                            new BackgroundDynamics(omega));
    // Switch off periodicity.
    lattice.periodicity().toggleAll(false);

    pcout << "Reading the geometry file." << std::endl;
    MultiScalarField3D<int> geometry(nx,ny,nz);
    readGeometry("porespy_palabos_geometry.dat", "tmp", geometry);

    pcout << "nu = " << nu << std::endl;
    pcout << "deltaP = " << deltaP << std::endl;
    pcout << "omega = " << omega << std::endl;
    pcout << "nx = " << lattice.getNx() << std::endl;
    pcout << "ny = " << lattice.getNy() << std::endl;
    pcout << "nz = " << lattice.getNz() << std::endl;

    porousMediaSetup(   lattice,
                        createLocalBoundaryCondition3D<T,DESCRIPTOR>(),
                        geometry,
                        deltaP);

    // The value-tracer is used to stop the simulation once is has converged.
    // 1st parameter:velocity
    // 2nd parameter:size
    // 3rd parameters:threshold
    // 1st and second parameters ae used for the length of the time average (size/velocity)
    util::ValueTracer<T> converge(1.0,1000.0,1.0e-4);

    pcout << "Simulation begins" << std::endl;
    plint iT=0;

    const plint maxT = simParams.getMax_iter();
    for (;iT<maxT; ++iT) {
        if (iT % 100 == 0) {
            pcout << "Iteration " << iT << std::endl;
        }

        lattice.collideAndStream();
        converge.takeValue(getStoredAverageEnergy(lattice),true);

        if (converge.hasConverged()) {
            break;
        }
    }

    pcout << "End of simulation at iteration " << iT << std::endl;

    pcout << "Permeability:" << std::endl << std::endl;
    computePermeability(lattice, nu, deltaP, lattice.getBoundingBox());
    pcout << std::endl;

    pcout << "Writing VTK file ..." << std::endl << std::endl;
    writeVTK(lattice,iT);
    pcout << "Finished!" << std::endl << std::endl;

    return 0;
}
