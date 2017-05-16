# -*- coding: utf-8 -*-
from pyexcel_xlsx import get_data
from rdflib import Graph, URIRef, Literal, RDF, RDFS, XSD, Namespace
from rdflib.plugins.sparql import prepareQuery

ns = Namespace("sw-kreusch")
g = Graph()
typePLZ = URIRef("http://dbpedia.org/ontology/zipCode")
typeCounty = URIRef("http://dbpedia.org/ontology/county")
hasVEK = URIRef("hasVEK")
isInCounty = URIRef("isInisInCounty")
g.add( (hasVEK,RDF.type,RDF.Property ) )
g.add( (hasVEK,RDFS.range,XSD.onNegativeInteger) )

#Parsing the zipCode to county mapping
data = get_data("AuszugGV1QAktuell.xlsx")
counties = data["Onlineprodukt_Gemeinden_310317"]
for community in counties:
    if len(community) > 13:
        #Testing if the current row contains a string or not
        try:
            regCode = int(str(community[2]))
        except UnicodeEncodeError:
            continue
        except ValueError:
            continue
        regCode = str(community[2])+str(community[3])+str(community[4])
        if community[3] is not None:
            if community[14] is not None:
                #print regCode + " " + community[14]
                zipCode = URIRef(str(community[14]))
                county = URIRef(regCode)
                g.add((zipCode,RDF.type, typePLZ))
                g.add((zipCode, isInCounty, county))

#Parsing the VEK
data = get_data("VGR_KreisergebnisseBand3.xlsx")
vek = data["VEK je Einwohner"]
for countyEntry in vek:
    # there are some descriptive entries, that we can filter out easily
    if len(countyEntry) > 5:
        if countyEntry[6] == '3':
            if len(str(countyEntry[2])) == 5:
                #print 'Postleitzahlbereich ' + str(countyEntry[2]) + ' Verfügbaren Einkommen pro Einwohner und Jahr in € ' + str(countyEntry[27]) + '\n'
                county = URIRef(str(countyEntry[2]))
                for zipCode,p,o in g.triples((None, isInCounty, county)):
                    g.add((zipCode, hasVEK, Literal(countyEntry[27])))

                # g.add((county, RDF.type, typeCounty))
                # g.add((county, hasVEK, Literal(countyEntry[27])))

print g.serialize(format='turtle')