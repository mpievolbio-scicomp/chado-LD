import re
import codecs
import sys
import optparse
import logging
import string


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

    # parse command line now
    (options, args) = parser.parse_args(argv)

#    if len(args) > 4: parser.error("Too many arguments")

    if not options.input:
        parser.error("Expected -i or --input")

    if not options.output:
        parser.error("Expected -o or --output")

    return options

def tocaps(s):
    l = map(string.capitalize, s.split("_"))
    return string.join(l, "_")
    

# TODO comments

def run(options):

    print "open input file"
    input_file = open(options.input,mode="r")

    print "open output file"
    output_file = codecs.open(options.output, mode='w', encoding='UTF-8')
    
    re_entity = re.compile("\s*create\s+table\s+(\S+)\s*\(\s*--.*@ENTITY", re.IGNORECASE)
    re_data = re.compile("\s*(\S*)\s+(serial|varchar|text|int|smallint|boolean|character).*--.*@DATA", re.IGNORECASE)
    re_link = re.compile("\s*(\S*)_id\s+int.*--.*@LINK", re.IGNORECASE)
    re_binary = re.compile("\s*create\s+table\s*(\S+)\s*\(\s*--.*@BINARY", re.IGNORECASE)
    re_source = re.compile("\s*(\S*)_id.*--.*@SOURCE", re.IGNORECASE)
    re_target = re.compile("\s*(\S*)_id.*--.*@TARGET", re.IGNORECASE)
    re_nary = re.compile("\s*create\s+table\s+(\S+)\s*\(\s*--.*@NARY", re.IGNORECASE)
    re_notnull = re.compile("not\s+null", re.IGNORECASE)
    re_fk = re.compile("foreign\s+key\s+\((\S+)_id\)\s+references\s+(\S+)", re.IGNORECASE)
    re_close = re.compile("\);", re.IGNORECASE)
#    re_comment = re.compile("COMMENT\sON\s(TABLE|COLUMN)\s(\S*)\sIS\s'([^']*)';")
#    re_comment_open = re.compile("COMMENT\sON\s(TABLE|COLUMN)\s(\S*)\sIS\s'([^']*)$")
#    re_comment_line = re.compile("^([^']*)$")
#    re_comment_close = re.compile("^([^']*)';")
    
    current_entity = None
    current_binary = None
    current_nary = None
    last_link = None
    last_source = None
    last_target = None
    in_comment = False
    
    for line in input_file:

        prog_entity = re_entity.search(line)
        prog_data = re_data.search(line)
        prog_link = re_link.search(line)
        prog_binary = re_binary.search(line)
        prog_source = re_source.search(line)
        prog_target = re_target.search(line)
        prog_nary = re_nary.search(line)
        prog_fk = re_fk.search(line)
        prog_close = re_close.search(line)
#        prog_comment = re_comment.search(line)
#        prog_comment_open = re_comment_open.search(line)
#        prog_comment_line = re_comment_line.search(line)
#        prog_comment_close = re_comment_close.search(line)
        
        used = set()

        if (prog_entity != None or prog_data != None or prog_link != None or prog_binary != None or prog_source != None or prog_target != None or prog_nary != None or prog_fk != None):
            output_file.write("\n# "+line) 

        if (prog_entity != None):
            name = prog_entity.group(1)
            used.add(name)
            name = tocaps(name)
            print "found entity ["+name+"]"
            current_entity = name
            # output class
            output_file.write("chado:"+name+" rdf:type owl:Class .\n")
            
        elif (prog_nary != None):
            name = prog_nary.group(1)
            used.add(name)
            name = tocaps(name)
#            ns = map(string.capitalize, name.split("_"))
#            name = string.join(ns, "_")
            print "found n-ary ["+name+"]"
            current_nary = name
            # output class
            output_file.write("chado:"+name+" rdf:type owl:Class .\n")
        
        elif (current_entity != None and prog_data != None):
            name = prog_data.group(1)
            used.add(current_entity.lower()+"."+name)
            print "found data ["+name+"]"
            output_file.write("chado:"+name+" rdf:type owl:DatatypeProperty .\n")
            prog_notnull = re_notnull.search(line)
            if (prog_notnull != None):
                print "found ["+name+"] cardinality exactly one on ["+current_entity+"]"
                # output restriction
                output_file.write("chado:"+current_entity+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+name+"; owl:cardinality \"1\"^^xsd:integer ] .\n")
            else:
                print "found ["+name+"] cardinality at most one on ["+current_entity+"]"
                # output restriction
                output_file.write("chado:"+current_entity+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+name+"; owl:maxCardinality \"1\"^^xsd:integer ] .\n")
            range = mapdatatype(prog_data.group(2))
            print "found ["+name+"] all values from ["+range+"] on ["+current_entity+"]"
            # output range restriction
            output_file.write("chado:"+current_entity+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+name+"; owl:allValuesFrom xsd:"+range+" ] .\n")
                        
        elif (current_entity != None and prog_link != None):
            name = prog_link.group(1)
            used.add(current_entity.lower()+"."+name)
            print "found link ["+name+"]"
            last_link = name
            output_file.write("chado:"+name+" rdf:type owl:ObjectProperty .\n")
            if (prog_notnull != None):
                print "found ["+name+"] cardinality exactly one on ["+current_entity+"]"
                # output restriction
                output_file.write("chado:"+current_entity+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+name+"; owl:cardinality \"1\"^^xsd:integer ] .\n")
            else:
                print "found ["+name+"] cardinality at most one on ["+current_entity+"]"
                # output restriction
                output_file.write("chado:"+current_entity+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+name+"; owl:maxCardinality \"1\"^^xsd:integer ] .\n")
            
        elif (current_nary != None and prog_data != None):
            name = prog_data.group(1)
            used.add(current_nary.lower()+"."+name)
            print "found data ["+name+"]"
            output_file.write("chado:"+name+" rdf:type owl:DatatypeProperty .\n")
            prog_notnull = re_notnull.search(line)
            if (prog_notnull != None):
                print "found ["+name+"] cardinality exactly one on ["+current_nary+"]"
                # output restriction
                output_file.write("chado:"+current_nary+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+name+"; owl:cardinality \"1\"^^xsd:integer ] .\n")
            else:
                print "found ["+name+"] cardinality at most one on ["+current_nary+"]"
                # output restriction
                output_file.write("chado:"+current_nary+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+name+"; owl:maxCardinality \"1\"^^xsd:integer ] .\n")
            range = mapdatatype(prog_data.group(2))
            print "found ["+name+"] all values from ["+range+"] on ["+current_nary+"]"
            # output range restriction
            output_file.write("chado:"+current_nary+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+name+"; owl:allValuesFrom xsd:"+range+" ] .\n")
                        
        elif (current_nary != None and prog_link != None):
            name = prog_link.group(1)
            used.add(current_nary.lower()+"."+name)
            print "found link ["+name+"]"
            last_link = name
            output_file.write("chado:"+name+" rdf:type owl:ObjectProperty .\n")
            if (prog_notnull != None):
                print "found ["+name+"] cardinality exactly one on ["+current_nary+"]"
                # output restriction
                output_file.write("chado:"+current_nary+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+name+"; owl:cardinality \"1\"^^xsd:integer ] .\n")
            else:
                print "found ["+name+"] cardinality at most one on ["+current_nary+"]"
                # output restriction
                output_file.write("chado:"+current_nary+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+name+"; owl:maxCardinality \"1\"^^xsd:integer ] .\n")
            
        elif (prog_binary != None):
            name = prog_binary.group(1)
            used.add(name)
            print "found binary ["+name+"]"
            current_binary = name
            # output object property
            output_file.write("chado:"+name+" rdf:type owl:ObjectProperty .\n")
            
        elif (prog_source != None):
            name = prog_source.group(1)
            print "found source ["+name+"] on ["+current_binary+"]"
            last_source = name
            
        elif (prog_target != None):
            name = prog_target.group(1)
            print "found target ["+name+"] on ["+current_binary+"]"
            last_target = name
        
        elif (current_binary != None and prog_fk != None):
            attr = prog_fk.group(1)
            type = tocaps(prog_fk.group(2))
            if attr == last_source:
                print "found domain ["+type+"] on ["+current_binary+"]"
                # output domain
                output_file.write("chado:"+current_binary+" rdfs:domain chado:"+type+" .\n")
            elif attr == last_target:
                print "found range ["+type+"] on ["+current_binary+"]"
                # output range
                output_file.write("chado:"+current_binary+" rdfs:range chado:"+type+" .\n")
        
        elif (current_entity != None and prog_fk != None):
            attr = prog_fk.group(1)
            range = tocaps(prog_fk.group(2))
            if attr == last_link:
                print "found link ["+attr+"] range ["+range+"] on entity ["+current_entity+"]"
                # output local range
                output_file.write("chado:"+current_entity+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+attr+"; owl:allValuesFrom chado:"+range+" ] .\n")

        elif (current_nary != None and prog_fk != None):
            attr = prog_fk.group(1)
            range = tocaps(prog_fk.group(2))
            if attr == last_link:
                print "found link ["+attr+"] range ["+range+"] on n-ary ["+current_nary+"]"
                # output local range
                output_file.write("chado:"+current_nary+" rdfs:subClassOf [a owl:Restriction; owl:onProperty chado:"+attr+"; owl:allValuesFrom chado:"+range+" ] .\n")

        elif (prog_close != None):
            current_entity = None
            current_binary = None
            current_nary = None
            
#        elif (prog_comment != None):
#            reltype = prog_comment.group(1)
#            element = prog_comment.group(2)
#            value = prog_comment.group(3)
#            print "found comment on "+reltype+" ["+element+"]: "+value
            
    input_file.close()
    output_file.flush()
    output_file.close()

    print "all done"
    return 0

def mapdatatype(sqltype):
    re_stringtype = re.compile("(text|varchar|character)", re.IGNORECASE)
    re_inttype = re.compile("(serial|int|smallint)", re.IGNORECASE)
    re_booleantype = re.compile("boolean", re.IGNORECASE) 
    re_dateTime = re.compile("timestampe", re.IGNORECASE)
    re_double = re.compile("double", re.IGNORECASE)
    re_float = re.compile("float", re.IGNORECASE)
    if (re_stringtype.match(sqltype) != None):
        return "string"
    elif (re_inttype.match(sqltype) != None):
        return "integer"
    elif (re_booleantype.match(sqltype) != None):
        return "boolean"
    elif (re_dateTime.match(sqlType) != None):
        return "dateTime"
    elif (re_double.match(sqlType) != None):
        return "double"
    elif (re_float.match(sqlType) != None):
        return "float"
    else:
        return None

# Program run from command line
if __name__ == "__main__":
    options = init("SQL2OWL", sys.argv)
    status = 1
    if options:
        status  = run(options)
    sys.exit(status)


# $Id: SQL2OWL.py 344 2009-02-24 11:54:42Z alistair.miles@zoo.ox.ac.uk $, end.