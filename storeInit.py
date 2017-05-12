# -*- coding: utf-8 -*-
from pyexcel_xlsx import get_data
from rdflib import Graph, BNode, URIRef, Literal, RDF

g = Graph()
typePLZ = URIRef("http://dbpedia.org/ontology/zipCode")


data = get_data("VGR_KreisergebnisseBand3.xlsx")
vek = data["VEK je Einwohner"]
for zipCodeArea in vek:
    # there are some descriptive entries, that we can filter out easily
    if len(zipCodeArea) > 5:
        if zipCodeArea[6] == '3':
            #print 'Postleitzahlbereich ' + str(zipCodeArea[2]) + ' Verfügbaren Einkommen pro Einwohner und Jahr in € ' + str(zipCodeArea[27]) + '\n'
            plz = BNode(value=str(zipCodeArea[2]))
            g.add( (plz, RDF.type, typePLZ) )

print g.serialize(format='turtle')