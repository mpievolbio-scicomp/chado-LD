for mod in companalysis contact cv expression general genetic library map organism phenotype phylogeny pub sequence stock
do
sed --in-place --file=modules/flybase-uripatterns-nojoins.sed modules/$mod/flybase/*.d2rq.ttl 
done
