#!/bin/bash
cat modules/chado-preamble.ttl > modules/chado-in-owl.ttl
for mod in companalysis contact cv expression general genetic library mage map organism phenotype phylogeny pub sequence stock
do
cat modules/$mod/$mod.ttl >> modules/chado-in-owl.ttl
done
