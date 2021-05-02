#!/usr/local/bin/python3
#-------------------------------------------------------------------------------
#   I JUST COULDN'T TAKE IT ANY MORE
#-------------------------------------------------------------------------------
from os import system

def write_write_log(integers,
                    doubles,
                    handle):
    # {{{
    #---------------------------------------------------------------------------
    # This writes the 'writeLogFile' function so that it includes all of the OG
    # stuff + the new class and all of its members for debugging
    #---------------------------------------------------------------------------
    integer_names = integers['assigned']+list(integers['calculated'].keys())
    double_names = doubles['assigned']+list(doubles['calculated'].keys())
    all_names = integer_names+double_names
    handle.write("template<typename T>\n")
    handle.write("void writeLogFile(  IncomprFlowParam<T> const& parameters,\n")
    handle.write("\t\tSimulationParams<T> const& simParams,\n")
    handle.write("\t\tstd::string const& title)\n")
    handle.write("{\n")
    handle.write('\tstd::string fullName = global::directories().getLogOutDir() + "plbLog.dat";\n')
    handle.write("\tplb_ofstream ofile(fullName.c_str());\n")
    handle.write('\tofile << title << "\\n\\n";\n')
    handle.write('\tofile << "Velocity in lattice units: u=" << parameters.getLatticeU() << "\\n";\n')
    handle.write('\tofile << "Reynolds number:           Re=" << parameters.getRe() << "\\n";\n')
    handle.write('\tofile << "Lattice resolution:        N=" << parameters.getResolution() << "\\n";\n')
    handle.write('\tofile << "Relaxation frequency:      omega=" << parameters.getOmega() << "\\n";\n')
    handle.write('\tofile << "LatticeViscosity:          nu=" << parameters.getLatticeNu() << "\\n";\n')
    handle.write('\tofile << "Extent of the system:      lx=" << parameters.getLx() << "\\n";\n')
    handle.write('\tofile << "nx:                        nx=" << parameters.getNx() << "\\n";\n')
    handle.write('\tofile << "ny:                        ny=" << parameters.getNy() << "\\n";\n')
    handle.write('\tofile << "Extent of the system:      ly=" << parameters.getLy() << "\\n";\n')
    handle.write('\tofile << "Extent of the system:      lz=" << parameters.getLz() << "\\n";\n')
    handle.write('\tofile << "Grid spacing deltaX:       dx=" << parameters.getDeltaX() << "\\n";\n')
    handle.write('\tofile << "Time step deltaT:          dt=" << parameters.getDeltaT() << "\\n";\n')
    handle.write('\tofile << "==============================" << "\\n";\n')
    for name in all_names:
        handle.write('\tofile << "{}\t\t\t{} = " << simParams.get{}{}() << "\\n";\n'.format(name,name,name[0].upper(),name[1:]))
    handle.write("}\n")
    # }}}

def write_assign_params(    integers,
                            doubles,
                            handle):
    # {{{
    #---------------------------------------------------------------------------
    # This function writes the assign_params function which parses the
    # 'params.xml' input file and assigns the inputs to the (returned)
    # SimulationParams class
    #---------------------------------------------------------------------------
    integer_names = integers['assigned']
    double_names = doubles['assigned']
    all_names = integer_names+double_names
    handle.write("SimulationParams<T> assign_params(string f_name)\n")
    handle.write("{\n")
    handle.write("\tplint {};\n".format(", ".join(integer_names)))
    handle.write("\tT {};\n".format(", ".join(double_names)))
    handle.write("\ttry{\n")
    handle.write("\t\tXMLreader xmlFile(f_name);\n")
    handle.write('\t\tpcout << "CONFIGURATION" << endl;\n')
    handle.write('\t\tpcout << "=============" << endl;\n')
    handle.write("\t\txmlFile.print(0);\n")
    for val in all_names:
        handle.write('\t\txmlFile["inputs"]["{}"].read({});\n'.format(val,val))
    handle.write('\t\tpcout << "=============" << endl << endl;\n')
    handle.write("\t\t} catch (PlbIOException& exception) { \n")
    handle.write("\t\t    pcout << exception.what() << endl;\n")
    handle.write("\t\t}\n")
    handle.write("\t\treturn SimulationParams<T> (\n")
    for i,val in enumerate(all_names):
        if i < len(all_names)-1:
            handle.write("\t\t\t\t\t{},\n".format(val))
        else:
            handle.write("\t\t\t\t\t{});\n".format(val))
    handle.write("};\n")
    # }}}

def write_params_class( integers, 
                        doubles,
                        handle):
    # {{{
    #---------------------------------------------------------------------------
    #   This function writes the generic SimulationParams<T> class with
    #   corresponding 'get__' methods for each parameter
    #---------------------------------------------------------------------------
    integer_names = integers['assigned']+list(integers['calculated'])
    double_names = doubles['assigned']+list(doubles['calculated'])
    lines = [   
                "template<typename T>",
                "class SimulationParams",
                "{",
                "\tprivate:",
                "plint",
                "T",
                "\tpublic:",
                "\t\tSimulationParams<T>("]
    #---------------------------------------------------------------------------
    # Top of the Class and instatiate member types
    #---------------------------------------------------------------------------
    for line in lines:
        if line == "plint":
            handle.write("\t\tplint {};\n".format(", ".join(integer_names)))
        elif line == "T":
            handle.write("\t\tT {};\n".format(", ".join(double_names)))
        else:
            handle.write("{}\n".format(line))
    #---------------------------------------------------------------------------
    # Constructor Arguments
    #---------------------------------------------------------------------------
    for integer in integers['assigned']:
        handle.write("\t\t\t\t\tplint {}_,\n".format(integer))
    for i,double in enumerate(doubles['assigned']):
        if i < len(doubles['assigned'])-1:
            handle.write("\t\t\t\t\tT {}_,\n".format(double))
        else:
            handle.write("\t\t\t\t\tT {}_\n".format(double))
    handle.write("\t\t\t\t\t):\n")
    #---------------------------------------------------------------------------
    # Instantiating Assigned Members 
    #---------------------------------------------------------------------------
    for integer in integers['assigned']:
        handle.write("\t\t\t{}({}_),\n".format(integer,integer))
    for i,double in enumerate(doubles['assigned']):
        if i < len(doubles['assigned'])-1:
            handle.write("\t\t\t{}({}_),\n".format(double,double))
        else:
            handle.write("\t\t\t{}({}_)\n".format(double,double))
    #---------------------------------------------------------------------------
    # Calculated Members 
    #---------------------------------------------------------------------------
    handle.write("\t\t{\n")
    handle.write("\t\t\t//Calculated values\n")
    for dct in [integers,doubles]:
        for key in dct['calculated']:
            handle.write("\t\t\t{} = {};\n".format(key,dct['calculated'][key]))
    handle.write("\t\t}\n")
    #---------------------------------------------------------------------------
    # Methods 
    #---------------------------------------------------------------------------
    handle.write("\t\t//Methods\n")
    for integer in integer_names:
        handle.write("\t\tplint\tget{}{}() const {{ return {}; }}\n".format(integer[0].upper(),integer[1:],integer))
    for double in double_names:
        handle.write("\t\tT\t\tget{}{}() const {{ return {}; }}\n".format(double[0].upper(),double[1:],double))
    handle.write("};\n")
    # }}}

def overwrite_base(   f_name,
                    tag,
                    function,
                    integers,
                    doubles):
    # {{{
    #---------------------------------------------------------------------------
    # This function replaces the text in 'f_name' with the text from the
    # different functions defined in this file. It first reads the file and
    # identifies the 'bounds' of the replacement text. It then opens the file
    # in write mode and rewrites the text up to bounds[0], calls a 'function'
    # to write new text, then writes the rest of the file back
    #---------------------------------------------------------------------------
    with open(f_name,'r') as f:
        text = f.read().split("\n")
    bounds = []
    for i,line in enumerate(text):
        if ('start {}'.format(tag[0]) in line) or ('end {}'.format(tag) in line):
            bounds.append(i)
    with open(f_name,'w') as f:
        #                   This includes the line 'start' line
        #                        |
        #                        v
        for i in range(bounds[0]+1):
            f.write("{}\n".format(text[i]))
        function(integers,doubles,f)
        for i in range(bounds[1],len(text)):
            f.write("{}\n".format(text[i]))
    # }}}

    
if __name__ == "__main__":
    # {{{
    #--------------------------------------------------------------------------
    #   Implementation
    #--------------------------------------------------------------------------
    #   The integer and double (T) arguments are either assigned by the params.xml or
    #   calculated by the class. Each data type has a dictionary with two keys: the
    #   'assigned' parameters is a list with strings for the parameters, and the
    #   'calculated' values which are held in a dictionary whose keys are the
    #   parameter names and entries are strings that represent the calculation
    #--------------------------------------------------------------------------
    integers =  {
                'assigned':[
                            "nx",
                            "ny",
                            "nz",
                            "max_iter",
                            ],
                'calculated':   {
                                }
                }

    doubles = {
                'assigned':[
                            "deltaP",
                            "tau",
                            ],
                'calculated':{
                            }
                    }

    #--------------------------------------------------------------------------
    # The last line of defense
    #--------------------------------------------------------------------------
    input("Save and close base.h then press enter")
    #--------------------------------------------------------------------------
    # Backup the old io.h file
    #--------------------------------------------------------------------------
    system("cp base.h .old_base.h")
    #--------------------------------------------------------------------------
    # These strings are matched in 'io.h' as 'start <string>', and 'end <string>'
    # so that overwrite_base can identify where the replacement text will go (i.e.
    # they correspond with the same order as funcs)
    #--------------------------------------------------------------------------
    strings = ['SimulationParams','assign_params','writeLogFile']
    funcs = [write_params_class,write_assign_params,write_write_log]
    for i,func in enumerate(funcs):
        overwrite_base(   'base.h',
                        strings[i],
                        func,
                        integers,
                        doubles)
    # }}}
