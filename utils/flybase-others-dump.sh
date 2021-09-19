#!/bin/bash

echo "---------------------------------------------------"
echo "== flybase other modules dump =="
beginall=$(date)
echo "begin all at $beginall"
echo "D2RQROOT: $D2RQROOT"
echo "CHADOROOT: $CHADOROOT"
dumploc=$1
uribase=http://openflydata.org/id/flybase/
echo "dump location: $dumploc"
echo "URI base: $uribase"

function dump {
    mod=$1
    fname=$2
    begin=$(date)
    echo "begin dump $mod/$fname at $begin"
    cmd="$D2RQROOT/dump-rdf -m $CHADOROOT/modules/$mod/flybase/$fname.d2rq.ttl -b $uribase -f N-TRIPLES -o $dumploc/flybase-$fname.nt"
    echo "$cmd"
    $cmd
    end=$(date)
    echo "dump $mod/$fname complete at $end"
    echo "launch async postprocess"
    cmd2="sed --in-place --file=$CHADOROOT/modules/flybase-postprocess.sed $dumploc/flybase-$fname.nt"
    echo "$cmd2"
    ( $cmd2 ) &
}

echo "=== contact module ==="
dump contact contact-vanilla

echo "=== cv module ==="
dump cv cv-vanilla

# tables are empty in FB2009_02...
# echo "=== expression module ==="
# dump expression expression-vanilla

# done in core...
# echo "=== general module ==="
# dump general general-vanilla

echo "=== genetic module ==="
dump genetic genetic-vanilla

echo "=== library module ==="
dump library library-vanilla

# tables are empty in FB2009_02...
# echo "=== map module ==="
# dump map map-vanilla

# done in core...
# echo "=== organism module ==="
# dump organism organism-vanilla

echo "=== phenotype module ==="
dump phenotype phenotype-vanilla

# tables not present in FB2009_02...
# echo "=== phylogeny module ==="
# dump phylogeny phylogeny-vanilla

echo "=== pub module ==="
dump pub pub-vanilla

echo "=== sequence module ==="
dump sequence sequence-feature_cvterm-go
dump sequence sequence-feature_cvterm-so
# done in core...
# dump sequence sequence-feature-label
dump sequence sequence-featurelocs-padded
dump sequence sequence-featureprop-expression
dump sequence sequence-feature-relationships
# done in core but redo here because of SO problems
dump sequence sequence-feature-type
# done in core...
# dump sequence sequence-synonym-type
# dump sequence sequence-vanilla-features
# dump sequence sequence-vanilla-featurelocs
# dump sequence sequence-vanilla-synonyms

echo "=== stock module ==="
dump stock stock-vanilla

# ignore this for now...
# echo "=== companalysis module ==="
# dump companalysis companalysis-vanilla

endall=$(date)
echo "all done at $endall"
echo "---------------------------------------------------"