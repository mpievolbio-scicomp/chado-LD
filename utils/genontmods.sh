for mod in companalysis contact cv expression general genetic library mage map organism phenotype phylogeny pub sequence stock
do
cat modules/chado-preamble.ttl modules/$mod/$mod.ttl > modules/$mod/chado-$mod-in-owl.ttl
done
