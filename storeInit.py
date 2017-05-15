# -*- coding: utf-8 -*-
from pyexcel_xlsx import get_data
from rdflib import Graph, BNode, URIRef, Literal, RDF, RDFS, XSD, Namespace

ns = Namespace("sw-kreusch")
g = Graph()
typePLZ = URIRef("http://dbpedia.org/ontology/zipCode")
typeCounty = URIRef("http://dbpedia.org/ontology/county")
hasVEK = URIRef("hasVEK")
g.add( (hasVEK,RDF.type,RDF.Property ) )
g.add( (hasVEK,RDFS.range,XSD.onNegativeInteger) )

data = get_data("VGR_KreisergebnisseBand3.xlsx")
vek = data["VEK je Einwohner"]
# for countyEntry in vek:
#     # there are some descriptive entries, that we can filter out easily
#     if len(countyEntry) > 5:
#         if countyEntry[6] == '3':
#             if len(str(countyEntry[2])) == 5:
#                 #print 'Postleitzahlbereich ' + str(countyEntry[2]) + ' Verfügbaren Einkommen pro Einwohner und Jahr in € ' + str(countyEntry[27]) + '\n'
#                 county = URIRef(str(countyEntry[2]))
#                 g.add( (county, RDF.type, typeCounty) )
#                 g.add((county, hasVEK, Literal(countyEntry[27])))

#print g.serialize(format='turtle')

data = get_data("AuszugGV1QAktuell.xlsx")
counties = data["Onlineprodukt_Gemeinden_310317"]
for community in counties:
    if len(community) > 5:
        #error parsing "Regionalcode" cus its unicode
        regCode = str(community[2])+str(community[3])+str(community[4])
        if community[14] is not None:
            print regCode + " " + community