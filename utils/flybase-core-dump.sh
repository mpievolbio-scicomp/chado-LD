#!/bin/bash

echo "---------------------------------------------------"
echo "== flybase core dump =="
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

echo "=== general module ==="
dump general general-vanilla

echo "=== organism module ==="
dump organism organism-vanilla

echo "=== sequence module ==="
dump sequence sequence-vanilla-features
dump sequence sequence-vanilla-featurelocs
dump sequence sequence-vanilla-synonyms
dump sequence sequence-feature-type
dump sequence sequence-synonym-type
dump sequence sequence-feature-label

endall=$(date)
echo "all done at $endall"
echo "---------------------------------------------------"