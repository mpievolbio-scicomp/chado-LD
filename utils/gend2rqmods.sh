for mod in companalysis contact cv expression general genetic library mage map organism phenotype phylogeny pub sequence stock
do
python utils/SQL2D2RQ.py --input modules/$mod/$mod.sql --output modules/$mod/$mod-vanilla.d2rq.ttl
done
