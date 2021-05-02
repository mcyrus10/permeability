Permeability testing
====================

convert to word

figures to make:

- function of delta p
- function of delta tau

---

Note: to toggle between Single and Multi-Relaxation time the lines in base.h are commented out for one or the other. The generic defition *BackgroundDynamics* is then used to to make the distinction generic.
The MRT matrix, weights and diagonal of the **S** vector can be seen in the file 

    <palabos root>/src/latticeBoltzmann/mrtLattices.hh 
  
If you want to modifiy these values you should make a copy of this file in the local directory and include it with your new values.

# REMEMBER! 

CHANGE COMPILER FLAGS AND PYTHON PATH ON MAKEFILE WHEN THIS IS UPLOADED TO ACF!

This directory is for testing out the permeability tutorial with porespy generated domains. It is a copy of the *permeability* tutorial with some modifications.


## To Do:

  * ~~create an input file (and readers for *generate_domain.py* and
    *permeability.cpp*). probably can just use the ones from the boolean mask
    directory~~
  * ~~create a minimal-working-example to demonstrate how it works for cylinders.
    Some good dimensions might be:~~
    * ~~dim = 40~~
    * ~~radius = 5~~
    * ~~ncylinders = 5~~
  * might want to lower the number of iterations or make it a controllable
    parameter from the 'input.dat' surface
  * look at examples/codesByTopics/couplings to understand data processors
  * ~~modify *generate_domain.py* to write a hidden text file with the geometric
    simulation paramters (including the calculated porosity)~~

## Questions:

  * **hypothesis -> size of the geometric domain multiplied by nodes must be less
    than pvmem x nodes**
    * this is not exactly true - tried 4 nodes with 32 processors and memory failed
  * ~~is the call to ps.io.to_palabos correct? (should solid be 1 or 0?)~~
  * look at nu and omega (frequency of relaxation from palabos coursera
    tutorial this is the term that is in the collision step and is the inverse
    of tau?) calculations in *permeability.cpp* to see how it is calculating
    the time constant (is nu == tau in Dr. Ekici's Code?)
