#!/bin/bash

start_time=`date +%s`

sh neighbor-districts-modified.sh ; 
sh edge-generator.sh ;
sh case-generator.sh ; 
sh peaks-generator.sh;
sh vaccinated-count-generator.sh;
sh vaccination-population-ratio-generator.sh;
sh vaccine-type-ratio-generator.sh;
sh vaccinated-ratio-generator.sh;
sh complete-vaccination-generator.sh; 

end_time=`date +%s`

echo execution time was `expr $end_time - $start_time` seconds.
