#!/bin/sh
#------------------------------------------------------------------------------
# this script is for controlling the interactions with the ACF server such as:
#   copying solutions to the local directory 
#   sending files to the server
#   plotting acf solutions
#   the sshpass commands are used to automatically supply the password to the
#   server
#------------------------------------------------------------------------------

acf=mdaughe5@acf-login.acf.utk.edu
ext=Scratch/palabos/cyrus_experimentation/permeability_sweep
direc=$(pwd)
echo $direc
#------------------------------------------------------------------------------
# this is the shorthand for all of the sshpass scp statements JESUS FN CHRIST
alias extr="scp $acf:$ext"
#------------------------------------------------------------------------------

while [ -n $1 ]
do
echo $1
    case "$1" in
        -extract)
            echo "copying $2 from acf"
            # {{{
            # copies the first file argument to the second argument 
            scp $acf:$ext/$2 $3
            shift;;
            # }}}
        -h)
            echo "available arguments:"
            # {{{
            echo "-extract  -> copy a single file off of acf (specify file and desination)"
            echo "\t =============="
            echo "\t acf --> LOCAL"
            echo "\t =============="
            echo "-h -> (help) : print these lines"
            echo "-send -> send a file to acf"
            echo "\t =============="
            echo "\t LOCAL --> acf"
            echo "\t =============="
            shift;;
            # }}}
        -send)
            echo "sending $2 to $acf:$ext/$3"
            # {{{
            scp $2 $acf:$ext/$3
            shift;;
            # }}}
        *) break;;
    esac
    shift
done
