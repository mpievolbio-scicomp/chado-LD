import re
import codecs
import sys
import optparse
import logging
import string
import simplejson as json
import rdflib
from rdflib import RDF, RDFS

OWL = rdflib.Namespace("http://www.w3.org/2002/07/owl#")

def allValuesFrom(args):
    print "output allValuesFrom test for "+args["cls"]+" on "+args["prop"]+" to "+args["val"]
    if args["val"].startswith("http://www.w3.org/2001/XMLSchema#"):
        return allValuesFromDatatype(args)
    else:
        return [] # TODO ???

def allValuesFromDatatype(args):
    query = """ASK { ?x a <%(cls)s> ; <%(prop)s> ?y . FILTER ( datatype(?y) != <%(val)s> ) }""" % args
    expect = False
    name = "test class [%(cls)s] on [%(prop)s] datatype range [%(val)s]" % args
    message = "expected all values for property [%(prop)s] at [%(cls)s] to have datatype [%(val)s]" % args
    print query
    return [{"name":name, "expect":expect, "query":query, "message":message}]
    
    
def cardinality(args):
    print "output exact cardinality test for "+args["cls"]+" on "+args["prop"]+" to "+args["val"]
    if int(args["val"]) == 1:
        return cardinalityOne(args)
    else:
        return [] # TODO ???

def cardinalityOne(args):
    print "output exact cardinality one test for "+args["cls"]+" on "+args["prop"]
    a = minCardinalityOne(args)
    b = maxCardinalityOne(args)
    a.extend(b)
    return a

def maxCardinalityOne(args):
    print "output maximum cardinality one test for "+args["cls"]+" on "+args["prop"]
    query = """ASK { ?x a <%(cls)s> ; <%(prop)s> ?y1, ?y2 . } FILTER ( ?y1 != ?y2 ) }""" % args
    expect = False
    name = "test class [%(cls)s] on [%(prop)s] max cardinality one" % args
    message = "expected at most one value for property [%(prop)s] at [%(cls)s]" % args
    print query
    return [{"name":name, "expect":expect, "query":query, "message":message}]

def minCardinalityOne(args):
    print "output minimum cardinality one test for "+args["cls"]+" on "+args["prop"]
    query = """ASK { ?x a <%(cls)s> . OPTIONAL { ?x <%(prop)s> ?y } FILTER ( !bound(?y) ) }""" % args
    expect = False
    name = "test class [%(cls)s] on [%(prop)s] min cardinality one" % args
    message = "expected at least one value for property [%(prop)s] at [%(cls)s]" % args
    print query
    return [{"name":name, "expect":expect, "query":query, "message":message}]
        
def maxCardinality(args):
    print "output max cardinality test for "+args["cls"]+" on "+args["prop"]+" to "+args["val"]
    if int(args["val"]) == 1:
        return maxCardinalityOne(args)
    else:
        return [] # TODO ???

def init(prog, argv):

    # create a parser for the command line options
    parser = optparse.OptionParser(
                usage="%prog [options]\n\n",
                version="%prog $Rev: 344 $")

    # input option
    parser.add_option("-i", "--input", 
                      dest="input", 
                      default="",
                      help="Input file name")

    # output option
    parser.add_option("-o", "--output", 
                      dest="output", 
                      default="",
                      help="Output file name")
    
    # format option
    parser.add_option("-f", "--format", 
                      dest="format", 
                      default="xml",
                      help="Input file format")

    # parse command line now
    (options, args) = parser.parse_args(argv)

#    if len(args) > 4: parser.error("Too many arguments")

    if not options.input:
        parser.error("Expected -i or --input")

    if not options.output:
        parser.error("Expected -o or --output")

    return options


def run(options):

    print "open input file"
    ontology = rdflib.ConjunctiveGraph()
    ontology.load(options.input, format=options.format)
    
    tests = []

    print "open output file"
    output_file = codecs.open(options.output, mode='w', encoding='UTF-8')
    
    for t1 in ontology.triples((None, RDF.type, OWL["Class"])):
        cls = t1[0]
        print "found class: " + str(cls)
        for t2 in ontology.triples((cls, RDFS.subClassOf, None)):
            super = t2[2]
            print "found super: " + str(super)
            for t3 in ontology.triples((super, OWL["allValuesFrom"], None)):
                range = t3[2]
                print "found allValuesFrom: " + str(range)
                for t4 in ontology.triples((super, OWL["onProperty"], None)):
                    prop = t4[2]
                    print "found onProperty: " + str(prop)
                    tests.append(("allValuesFrom", str(cls), str(prop), str(range)))
            for t3 in ontology.triples((super, OWL["cardinality"], None)):
                card = t3[2]
                print "found cardinality: " + str(card)
                for t4 in ontology.triples((super, OWL["onProperty"], None)):
                    prop = t4[2]
                    print "found onProperty: " + str(prop)
                    tests.append(("cardinality", str(cls), str(prop), str(card)))
            for t3 in ontology.triples((super, OWL["maxCardinality"], None)):
                card = t3[2]
                print "found max cardinality: " + str(card)
                for t4 in ontology.triples((super, OWL["onProperty"], None)):
                    prop = t4[2]
                    print "found onProperty: " + str(prop)
                    tests.append(("maxCardinality", str(cls), str(prop), str(card)))
            
    testcase = []
    
    for test in tests:
        type = test[0]
        args = {"cls":test[1], "prop":test[2], "val":test[3]}
        t = None
        if type == "allValuesFrom":
            t = allValuesFrom(args)
        elif type == "cardinality":
            t = cardinality(args)
        elif type == "maxCardinality":
            t = maxCardinality(args)
        if t != None:
            testcase.extend(t)
        
    testcase.sort(testcompare)
    print "dump test case to output file"
    json.dump(testcase, output_file, indent=4)
#    output_file.write(json.dumps(testcase, indent=4, ))
    print "flush and close output file"
    output_file.flush()
    output_file.close()

    print "all done"
    return 0

def testcompare(x, y):
    if x["name"] > y["name"]:
        return 1
    else:
        return -1

# Program run from command line
if __name__ == "__main__":
    options = init("OWL2SPARQL", sys.argv)
    status = 1
    if options:
        status  = run(options)
    sys.exit(status)


# $Id: SQL2OWL.py 344 2009-02-24 11:54:42Z alistair.miles@zoo.ox.ac.uk $, end.