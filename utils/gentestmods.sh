for mod in companalysis contact cv expression general genetic library mage map organism phenotype phylogeny pub sequence stock
do
python utils/OWL2SPARQL.py --input modules/$mod/chado-$mod-in-owl.ttl --output modules/$mod/$mod-testcase.json --format n3
done
