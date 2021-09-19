import re
import codecs
import sys
import optparse
import logging
import string

preamble = """
# $Id: SQL2D2RQ.py 503 2009-03-09 11:57:14Z alistair.miles@zoo.ox.ac.uk $

# Standard namespaces
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix : <http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#> .

# Namespaces for this mapping
@prefix map: <http://openflydata.org/d2r-mapping/flybase/> . # The namespace for this mapping
@prefix chado: <http://purl.org/net/chado/schema/> . # The CHADO in OWL schema

# ---------------------------------
# database configuration
# ---------------------------------
map:storage a :Database;
    :jdbcDriver "org.postgresql.Driver"; 
    :jdbcDSN "jdbc:postgresql://flybase.org/flybase";
    :username "flybase";
    # :resultSizeLimit 100 ; # Temporary fix to stop pulling all records
.

#map:storage a :Database;
#    :jdbcDriver "org.postgresql.Driver"; 
#    :jdbcDSN "jdbc:postgresql://db.genedb.org/snapshot";
#    :username "genedb_ro";
#    # :resultSizeLimit 100 ; # Temporary fix to stop pulling all records
#.

"""

re_entity = re.compile("\s*create\s+table\s+(\S+)\s*\(\s*--.*@ENTITY", re.IGNORECASE)
re_data = re.compile("\s*(\S*)\s+(serial|varchar|text|int|smallint|boolean|character).*--.*@DATA", re.IGNORECASE)
re_link = re.compile("\s*(\S*)_id\s+int.*--.*@LINK", re.IGNORECASE)
re_binary = re.compile("\s*create\s+table\s*(\S+)\s*\(\s*--.*@BINARY", re.IGNORECASE)
re_source = re.compile("\s*(\S*)_id.*--.*@SOURCE", re.IGNORECASE)
re_target = re.compile("\s*(\S*)_id.*--.*@TARGET", re.IGNORECASE)
re_nary = re.compile("\s*create\s+table\s+(\S+)\s*\(\s*--.*@NARY", re.IGNORECASE)
re_notnull = re.compile("not\s+null", re.IGNORECASE)
re_pk = re.compile("primary\s+key\s*\((\S+)\)", re.IGNORECASE)
re_fk = re.compile("foreign\s+key\s+\((\S+)_id\)\s+references\s+(\S+)\s*\((\S+)\)", re.IGNORECASE)
re_close = re.compile("\);", re.IGNORECASE)


def init(prog, argv):

    # create a parser for the command line options
    parser = optparse.OptionParser(
                usage="%prog [options]\n\n",
                version="%prog $Rev: 503 $")

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
    
    
    
def firstpass(input, out):
    
    # set up class maps for entity and nary association classes
    current_entity = None
    current_nary = None

    for line in input:

        prog_entity = re_entity.search(line)
        prog_nary = re_nary.search(line)
        prog_pk = re_pk.search(line)
        prog_close = re_close.search(line)
        
        if (prog_entity != None or prog_nary != None or prog_pk != None):
            pass
            #out.write("# "+line) 
            
        if (current_entity != None and prog_pk != None):
            sqlname = prog_pk.group(1)
            print "found primary key ["+sqlname+"]"
            out.write("    :uriPattern \""+current_entity.lower()+"/@@"+current_entity.lower()+"."+sqlname+"@@\" ;\n")
        elif (current_nary != None and prog_pk != None):
            sqlname = prog_pk.group(1)
            print "found primary key ["+sqlname+"]"
            out.write("    :uriPattern \""+current_nary.lower()+"/@@"+current_nary.lower()+"."+sqlname+"@@\" ;\n")

        if (prog_entity != None):
            sqlname = prog_entity.group(1)
            name = tocaps(sqlname)
            print "found entity ["+name+"]"
            current_entity = name
            out.write("\n# ---------------------------------\n")
            out.write("# "+sqlname+" entity class map\n")
            out.write("# ---------------------------------\n")
            out.write("map:"+sqlname+" a :ClassMap ;\n    :dataStorage map:storage ;\n    :class chado:"+name+" ;\n")
            
        elif (prog_nary != None):
            sqlname = prog_nary.group(1)
            name = tocaps(sqlname)
            print "found n-ary ["+name+"]"
            current_nary = name
            out.write("\n# ---------------------------------\n")
            out.write("# "+sqlname+" n-ary association class map\n")
            out.write("# ---------------------------------\n")
            out.write("map:"+sqlname+" a :ClassMap ;\n    :dataStorage map:storage ;\n    :class chado:"+name+" ;\n")
        
        elif (current_entity != None and prog_close != None):
            current_entity = None
            out.write(".\n\n")
            
        elif (current_nary != None and prog_close != None):
            current_nary = None
            out.write(".\n\n")
            
#        elif (prog_comment != None):
#            reltype = prog_comment.group(1)
#            element = prog_comment.group(2)
#            value = prog_comment.group(3)
#            print "found comment on "+reltype+" ["+element+"]: "+value


def secondpass(input, out):
    current_entity = None
    current_binary = None
    current_nary = None
    last_link = None
    last_source = None
    last_target = None
    in_comment = False
    
    for line in input:

        prog_entity = re_entity.search(line)
        prog_data = re_data.search(line)
        prog_link = re_link.search(line)
        prog_binary = re_binary.search(line)
        prog_source = re_source.search(line)
        prog_target = re_target.search(line)
        prog_nary = re_nary.search(line)
        prog_pk = re_pk.search(line)
        prog_fk = re_fk.search(line)
        prog_close = re_close.search(line)
        
        if (prog_entity != None or prog_data != None or prog_link != None or prog_binary != None or prog_source != None or prog_target != None or prog_nary != None or prog_fk != None or prog_pk != None):
            # out.write("\n# "+line) 
            pass
            
        if (current_entity != None and prog_pk != None):
            sqlname = prog_pk.group(1)
            print "found primary key ["+sqlname+"]"
        elif (current_nary != None and prog_pk != None):
            sqlname = prog_pk.group(1)
            print "found primary key ["+sqlname+"]"
            

        if (prog_entity != None):
            sqlname = prog_entity.group(1)
            name = tocaps(sqlname)
            print "found entity ["+name+"]"
            current_entity = name
            
        elif (prog_nary != None):
            sqlname = prog_nary.group(1)
            name = tocaps(sqlname)
            print "found n-ary ["+name+"]"
            current_nary = name
        
        elif (current_entity != None and prog_data != None):
            sqlname = prog_data.group(1)
            column = current_entity.lower() + "." + sqlname
            print "found data ["+sqlname+"] on entity ["+current_entity.lower()+"]"
            datatype = mapdatatype(prog_data.group(2))
            print "found ["+sqlname+"] all values from ["+datatype+"] on ["+current_entity.lower()+"]"
            out.write("\n# ---------------------------------\n")
            out.write("# "+column+" data property bridge\n")
            out.write("# ---------------------------------\n")
            out.write("map:"+column+" a :PropertyBridge ;\n    :belongsToClassMap map:"+current_entity.lower()+" ;\n    :column \""+column+"\" ;\n    :property chado:"+sqlname+" ;\n    :datatype xsd:"+datatype+" ;\n.\n\n")

            prog_notnull = re_notnull.search(line)
            if (prog_notnull != None):
                print "found ["+name+"] cardinality exactly one on ["+current_entity+"]"
            else:
                print "found ["+name+"] cardinality at most one on ["+current_entity+"]"
                        
        elif (current_entity != None and prog_link != None):
            name = prog_link.group(1)
            print "found link ["+name+"]"
            last_link = name
            if (prog_notnull != None):
                print "found ["+name+"] cardinality exactly one on ["+current_entity+"]"
            else:
                print "found ["+name+"] cardinality at most one on ["+current_entity+"]"
            
        elif (current_nary != None and prog_data != None):
            sqlname = prog_data.group(1)
            column = current_nary.lower() + "." + sqlname
            print "found data ["+sqlname+"] on n-ary ["+current_nary.lower()+"]"
            datatype = mapdatatype(prog_data.group(2))
            print "found ["+sqlname+"] all values from ["+datatype+"] on ["+current_nary.lower()+"]"
            out.write("\n# ---------------------------------\n")
            out.write("# "+column+" data property bridge\n")
            out.write("# ---------------------------------\n")
            out.write("map:"+column+" a :PropertyBridge ;\n    :belongsToClassMap map:"+current_nary.lower()+" ;\n    :column \""+column+"\" ;\n    :property chado:"+sqlname+" ;\n    :datatype xsd:"+datatype+" ;\n.\n\n")

            prog_notnull = re_notnull.search(line)
            if (prog_notnull != None):
                print "found ["+name+"] cardinality exactly one on ["+current_nary+"]"
            else:
                print "found ["+name+"] cardinality at most one on ["+current_nary+"]"

        elif (current_nary != None and prog_link != None):
            name = prog_link.group(1)
            print "found link ["+name+"]"
            last_link = name
            if (prog_notnull != None):
                print "found ["+name+"] cardinality exactly one on ["+current_nary+"]"
            else:
                print "found ["+name+"] cardinality at most one on ["+current_nary+"]"
            
        elif (prog_binary != None):
            sqlname = prog_binary.group(1)
            print "found binary ["+sqlname+"]"
            current_binary = sqlname
            out.write("\n# ---------------------------------\n")
            out.write("# "+sqlname+" object property bridge\n")
            out.write("# ---------------------------------\n")
            out.write("map:"+sqlname+" a :PropertyBridge ;\n    :property chado:"+sqlname+" ;\n")
            
        elif (current_binary != None and prog_source != None):
            name = prog_source.group(1)
            print "found source ["+name+"] on ["+current_binary+"]"
            last_source = name
            
        elif (current_binary != None and prog_target != None):
            name = prog_target.group(1)
            print "found target ["+name+"] on ["+current_binary+"]"
            last_target = name
        
        elif (current_binary != None and prog_fk != None):
            attr = prog_fk.group(1)
            type = tocaps(prog_fk.group(2))
            ref = prog_fk.group(3)
            if attr == last_source:
                print "found domain ["+type+"] on ["+current_binary+"]"
                out.write("    :belongsToClassMap map:"+type.lower()+" ;\n")
                out.write("    :join \""+type.lower()+"."+ref+" = "+current_binary+"."+attr+"_id\" ;\n")
            elif attr == last_target:
                print "found range ["+type+"] on ["+current_binary+"]"
                out.write("    :join \""+current_binary+"."+attr+"_id = "+type.lower()+"."+ref+"\" ;\n")
                out.write("    :uriPattern \""+type.lower()+"/@@"+type.lower()+"."+ref+"@@\" ;\n")
        
        elif (current_entity != None and prog_fk != None):
            attr = prog_fk.group(1)
            range = tocaps(prog_fk.group(2))
            ref = prog_fk.group(3)
            if attr == last_link:
                print "found link ["+attr+"] range ["+range+"] on entity ["+current_entity+"]"
                out.write("\n# ---------------------------------\n")
                out.write("# "+current_entity.lower()+"."+attr+"_id object property bridge\n")
                out.write("# ---------------------------------\n")
                out.write("map:"+current_entity.lower()+"."+attr+" a :PropertyBridge ;\n")
                out.write("    :property chado:"+attr+" ;\n")
                out.write("    :belongsToClassMap map:"+current_entity.lower()+" ;\n")
#                out.write("    :refersToClassMap map:"+range.lower()+" ;\n")
                out.write("    :uriPattern \""+range.lower()+"/@@"+range.lower()+"."+ref+"@@\" ;\n")
                out.write("    :join \""+current_entity.lower()+"."+attr+"_id = "+range.lower()+"."+ref+"\" ;\n.\n\n")

        elif (current_nary != None and prog_fk != None):
            attr = prog_fk.group(1)
            range = tocaps(prog_fk.group(2))
            ref = prog_fk.group(3)
            if attr == last_link:
                print "found link ["+attr+"] range ["+range+"] on n-ary ["+current_nary+"]"
                out.write("\n# ---------------------------------\n")
                out.write("# "+current_nary.lower()+"."+attr+"_id object property bridge\n")
                out.write("# ---------------------------------\n")
                out.write("map:"+current_nary.lower()+"."+attr+" a :PropertyBridge ;\n")
                out.write("    :property chado:"+attr+" ;\n")
                out.write("    :belongsToClassMap map:"+current_nary.lower()+" ;\n")
#                out.write("    :refersToClassMap map:"+range.lower()+" ;\n")
                out.write("    :uriPattern \""+range.lower()+"/@@"+range.lower()+"."+ref+"@@\" ;\n")
                out.write("    :join \""+current_nary.lower()+"."+attr+"_id = "+range.lower()+"."+ref+"\" ;\n.\n\n")

        elif (current_binary != None and prog_close != None):
            current_binary = None
            out.write(".\n\n")
            
        elif (prog_close != None):
            current_entity = None
            current_binary = None
            current_nary = None
            
#        elif (prog_comment != None):
#            reltype = prog_comment.group(1)
#            element = prog_comment.group(2)
#            value = prog_comment.group(3)
#            print "found comment on "+reltype+" ["+element+"]: "+value
            
def run(options):

    print "open input file"
    input_file = open(options.input,mode="r")

    print "open output file"
    output_file = codecs.open(options.output, mode='w', encoding='UTF-8')
    
    print "write preamble"
    output_file.write(preamble)

    print "first pass..."
    firstpass(input_file, output_file)

    input_file.close()
    print "open input file"
    input_file = open(options.input,mode="r")
    
    print "second pass..."
    secondpass(input_file, output_file)
    
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


# $Id: SQL2D2RQ.py 503 2009-03-09 11:57:14Z alistair.miles@zoo.ox.ac.uk $, end.