#!/bin/sh
#------------------------------------------------------------------------------
#       Script for sweeping tau in Palabos program
#
#   outline:
#       - write parameters file
#       - generate new lattice
#       - execute c++
#       - extract parameters to .csv file
#------------------------------------------------------------------------------

write_params() { 
echo '<?xml version="1.0" ?>' > $1
echo "<inputs>" >> $1
echo "    <!--====================================================================-->" >> $1
echo "    <!--Geometric paramters (these parameters are for generators.cylinders!)-->" >> $1
echo "    <!--====================================================================-->" >> $1
echo "    <nx>                200      </nx>               <!--  number in x-->" >> $1
echo "    <ny>                200      </ny>               <!--  number in y-->" >> $1
echo "    <nz>                200      </nz>               <!--  number in z-->" >> $1
echo "    <radius>            2     </radius>           <!--  radius of cylinders-->" >> $1
echo "    <ncylinders>        2260     </ncylinders>       <!--  number of cylinders in the domain-->" >> $1
echo "    <target_porosity>  .697       </target_porosity>  <!--  porosity is not controlled directly in cylinders-->" >> $1
echo "    <phi_max>           90      </phi_max>          <!--  angle <- [0,phi_max] in the Z-direction-->" >> $1
echo "    <theta_max>         90      </theta_max>        <!--  angle <- [0,theta_max] in the X-Y plane-->" >> $1
echo "    <!-- =============================================================== -->" >> $1
echo "    <!--            Fluid           -->" >> $1
echo "    <!-- =============================================================== -->" >> $1
echo "    <Re>                1      </Re>               <!-- Reynolds Number -->" >> $1
echo "    <tau>               $2  </tau>           <!-- Presure Gradient -->" >> $1
echo "    <deltaP>            .16    </deltaP>           <!-- Presure Gradient -->" >> $1
echo "    <!-- ================================================================ -->" >> $1
echo "    <!--            IO              -->" >> $1
echo "    <!-- ================================================================ -->" >> $1
echo "    <fNameIn>  porespy_palabos_geometry.dat </fNameIn>" >> $1
echo "    <fNameOut> tmp                          </fNameOut>" >> $1
echo "</inputs>" >> $1
}

extract() { grep $1 $2 | awk '{print $NF}'; }

# These are the tau values to sweep through
taus=( '2.0' '1.5' '1.25' '1' '0.8' '0.75' '0.6')

# Output directory
output=batch

[ -d $output ] && rm -r $output 
mkdir $output && echo "Creating New Batch Directory - $output"

echo "tau   permeability"
echo "------------------"
for t in ${taus[*]}; do
    write_params params.xml $t
    mpiexec -n 4 ./permeability  > tmp/palabos_out.dat
    permeability=$(extract "Permeability.*=" tmp/palabos_out.dat)
    echo "$t\t$permeability"
    mv tmp $output/tau_${t}
    mv params.xml $output/tau_${t}
    mkdir tmp
done


