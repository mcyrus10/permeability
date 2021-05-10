# Palabos Permeability

## Clone this repository with git

In a terminal navigate to the directory where you want permeability to exist then type (note the $ is not part of the command, just to indicate that this is a shell command):

```shell
$ git clone https://github.com/mcyrus10/permeability.git
```

---

## Compiling

This will download all the contents of this repository into a directory called *permeability.* 
If you have the old makefile, it should work exactly the same in this directory and you can delete *Cmakelist.txt*. If you want to use this program in an arbitrary directory all you need to do is open *CmakeList.txt*, navigate to line 98 and give it the path to palabos on your computer (also do this for line 99,100,102 and 103). Then:

```shell
$ mkdir build
$ cd build
$ cmake ..
$ make
$ cd ..
```

Now you should be able to execute permeability with:
 
```shell
$ mpiexec -n 4 ./permeability
```

---

## params.xml

This file now has the additional parameters :

| parameter | description |
| --- | --- |
| composite | (0 **or** 1) toggles composite domain  in *generate_domain.py*
| cyl_proportion | (0-1) defines how much of the solid phase is composed of fibers
| C         | Forcheimer coefficient |


When you run the program, now it will tell you the permeability calculated with the forcheimer coefficient as well as the dary permeability.

---

## generate_domain.py

This python script is used to generate the porous media for the palabos
simulation. To recover the domain of fibers, toggle *composite* in *params.xml*
to 0.  
**Note** 
- the function 'composite_domain' is defined in *header.py* if you want to
modify this, also the last line of generate_domain.py is *plt.show()*, which you
can comment out if you want to suppress the figure.

- *blobiness* can be passed as a paramter to 'composite_domain' (default value is 1)