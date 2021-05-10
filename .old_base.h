#include "palabos3D.h"
#include "palabos3D.hh"

#include <vector>
#include <cmath>
#include <cstdlib>

#include <fstream>
#include <string>
#include <iostream>
#include <sstream>
#include <iomanip>

using namespace std;
using namespace plb;

typedef double T;

// Uncomment next two lines for Single-Relaxation time
#define DESCRIPTOR descriptors::D3Q19Descriptor
typedef BGKdynamics<T,DESCRIPTOR> BackgroundDynamics;

// Uncomment next two lines for Multi-Relaxation time
//#define DESCRIPTOR descriptors::MRTD3Q19Descriptor
//typedef MRTdynamics<T,DESCRIPTOR> BackgroundDynamics;

//------------------------------------------------------------------------------
// Essentially All the methods need SimulationParams so it is defined at the top
// of the stream as well as its I/O functions
//------------------------------------------------------------------------------
// {{{ start SimulationParams
template<typename T>
class SimulationParams
{
	private:
		plint nx, ny, nz, max_iter;
		T deltaP, tau;
	public:
		SimulationParams<T>(
					plint nx_,
					plint ny_,
					plint nz_,
					plint max_iter_,
					T deltaP_,
					T tau_
					):
			nx(nx_),
			ny(ny_),
			nz(nz_),
			max_iter(max_iter_),
			deltaP(deltaP_),
			tau(tau_)
		{
			//Calculated values
		}
		//Methods
		plint	getNx() const { return nx; }
		plint	getNy() const { return ny; }
		plint	getNz() const { return nz; }
		plint	getMax_iter() const { return max_iter; }
		T		getDeltaP() const { return deltaP; }
		T		getTau() const { return tau; }
};
// }}} end SimulationParams
// {{{ start assign_params
SimulationParams<T> assign_params(string f_name)
{
	plint nx, ny, nz, max_iter;
	T deltaP, tau;
	try{
		XMLreader xmlFile(f_name);
		pcout << "CONFIGURATION" << endl;
		pcout << "=============" << endl;
		xmlFile.print(0);
		xmlFile["inputs"]["nx"].read(nx);
		xmlFile["inputs"]["ny"].read(ny);
		xmlFile["inputs"]["nz"].read(nz);
		xmlFile["inputs"]["max_iter"].read(max_iter);
		xmlFile["inputs"]["deltaP"].read(deltaP);
		xmlFile["inputs"]["tau"].read(tau);
		pcout << "=============" << endl << endl;
		} catch (PlbIOException& exception) { 
		    pcout << exception.what() << endl;
		}
        pcout << "assign params --> tau = " << tau << std::endl;
        pcout << "assign params --> deltaP = " << deltaP << std::endl;
        pcout << "assign params --> nx = " << nx << std::endl;
        pcout << "assign params --> ny = " << ny << std::endl;
		return SimulationParams<T> (
					nx,
					ny,
					nz,
					max_iter,
					deltaP,
					tau);
};
//}}} end assign_params
// {{{ start writeLogFile
template<typename T>
void writeLogFile(  IncomprFlowParam<T> const& parameters,
		SimulationParams<T> const& simParams,
		std::string const& title)
{
	std::string fullName = global::directories().getLogOutDir() + "plbLog.dat";
	plb_ofstream ofile(fullName.c_str());
	ofile << title << "\n\n";
	ofile << "Velocity in lattice units: u=" << parameters.getLatticeU() << "\n";
	ofile << "Reynolds number:           Re=" << parameters.getRe() << "\n";
	ofile << "Lattice resolution:        N=" << parameters.getResolution() << "\n";
	ofile << "Relaxation frequency:      omega=" << parameters.getOmega() << "\n";
	ofile << "LatticeViscosity:          nu=" << parameters.getLatticeNu() << "\n";
	ofile << "Extent of the system:      lx=" << parameters.getLx() << "\n";
	ofile << "nx:                        nx=" << parameters.getNx() << "\n";
	ofile << "ny:                        ny=" << parameters.getNy() << "\n";
	ofile << "Extent of the system:      ly=" << parameters.getLy() << "\n";
	ofile << "Extent of the system:      lz=" << parameters.getLz() << "\n";
	ofile << "Grid spacing deltaX:       dx=" << parameters.getDeltaX() << "\n";
	ofile << "Time step deltaT:          dt=" << parameters.getDeltaT() << "\n";
	ofile << "==============================" << "\n";
	ofile << "nx			nx = " << simParams.getNx() << "\n";
	ofile << "ny			ny = " << simParams.getNy() << "\n";
	ofile << "nz			nz = " << simParams.getNz() << "\n";
	ofile << "max_iter			max_iter = " << simParams.getMax_iter() << "\n";
	ofile << "deltaP			deltaP = " << simParams.getDeltaP() << "\n";
	ofile << "tau			tau = " << simParams.getTau() << "\n";
}
// }}} end writeLogFile
