import simplejson as json
import httplib
import urllib
from time import time

def sparql(host, port, path, query):
    start = time()
    params = urllib.urlencode({"query": query})
    headers = { 
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "application/sparql-results+json"}
    conn = httplib.HTTPConnection(host, port)
    conn.request('POST', path, params, headers)
    res = conn.getresponse()
    if (res.status != 200):
        print res.status
        print res.reason
        print res.read()
        conn.close()
        return None
    else:
        end = time()
        return end - start

test_query = """
PREFIX chado: <http://purl.org/net/chado/schema/>
PREFIX so: <http://purl.org/obo/owl/SO#>
SELECT * WHERE {
  ?feature a chado:Feature , so:SO_0000704 ;
    chado:uniquename ?uniquename ;
    chado:name ?name ; 
    chado:organism ?organism ;
  .
  
  ?organism a chado:Organism ;
    chado:genus ?genus ;
    chado:species ?species ;
  .
}
LIMIT 10
"""

query1 = """
# flybase benchmark query 1 (SPARQL)

PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>    
PREFIX chado: <http://purl.org/net/chado/schema/>
PREFIX so: <http://purl.org/obo/owl/SO#>
PREFIX syntype: <http://purl.org/net/flybase/synonym-types/>

SELECT DISTINCT ?flybaseid ?annotationsymbol ?fullname WHERE {

  ?feature chado:name "schuy"^^xsd:string ; 
    a so:SO_0000704 ;
    chado:organism  [
      chado:genus "Drosophila"^^xsd:string ;
      chado:species "melanogaster"^^xsd:string ;
    ] ;
    chado:is_analysis "false"^^xsd:boolean ;
    chado:is_obsolete "false"^^xsd:boolean;
    chado:uniquename ?flybaseid ;
    chado:feature_dbxref [ 
      chado:accession ?annotationsymbol ; 
      chado:db <http://openflydata.org/id/flybase/db/FlyBase_Annotation_IDs> 
    ] .

  ?feature_fullname 
    chado:feature ?feature ; 
    chado:is_current "true"^^xsd:boolean ;
    a chado:Feature_Synonym ;
    chado:synonym [ 
      a syntype:FullName ;
      chado:name ?fullname ; 
    ] ;
  .

}
"""

query2 = """
# flybase benchmark query 2 (SPARQL)

PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX chado: <http://purl.org/net/chado/schema/>
PREFIX so: <http://purl.org/obo/owl/SO#>

SELECT DISTINCT ?pubid ?title ?pyear ?pages ?volume ?issue ?miniref WHERE {
  
  ?feature 
    chado:uniquename "FBgn0004644"^^xsd:string ;
    a so:SO_0000704 ;
    chado:organism  [
      chado:genus "Drosophila"^^xsd:string ;
      chado:species "melanogaster"^^xsd:string ;
    ] ;
    chado:is_analysis "false"^^xsd:boolean ;
    chado:is_obsolete "false"^^xsd:boolean;
    chado:feature_pub ?pub .

  ?pub a chado:Pub ;
    chado:uniquename ?pubid .
  
  OPTIONAL { ?pub chado:title ?title }
  OPTIONAL { ?pub chado:pyear ?pyear }
  OPTIONAL { ?pub chado:pages ?pages }
  OPTIONAL { ?pub chado:volume ?volume }
  OPTIONAL { ?pub chado:issue ?issue }
  OPTIONAL { ?pub chado:miniref ?miniref }

}
""" 

for i in range(1):
    t = sparql("openflydata.org", 80, "/query/flybase-FB2009_02", query2)
    print t
