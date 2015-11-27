#! /bin/sh
java -Xmx512M -cp .:lib/ECLA.jar:lib/DTNConsoleConnection.jar core.DTNSim $*
a=0
declare -a argslist
for var in "$@"; do
    if [[ $var == *".txt"* ]]
    then
        argslist[$a]=$var;
        let "a += 1"
    fi;
done

python scripts/process_energy_report.py $(echo ${argslist[*]})
