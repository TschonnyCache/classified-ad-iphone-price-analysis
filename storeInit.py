# -*- coding: utf-8 -*-
import json
from pyexcel_xlsx import get_data
from rdflib import Graph, URIRef, Literal, RDF, RDFS, XSD, Namespace

ns = Namespace("sw-kreusch")
g = Graph()
typePLZ = URIRef("http://dbpedia.org/ontology/zipCode")
typeCounty = URIRef("http://dbpedia.org/ontology/county")
typeiPhoneModel = URIRef("https://www.wikidata.org/wiki/Q2766")
hasVEK = URIRef("hasVEK")
isInCounty = URIRef("isInisInCounty")
inceptedOn = URIRef("inceptedOn")
g.add( (hasVEK,RDF.type,RDF.Property ) )
g.add( (hasVEK,RDFS.range,XSD.nonNegativeInteger) )

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
        #concatenating the regCode/county code
        regCode = str(community[2])+str(community[3])+str(community[4])
        if community[3] is not None:
            if community[14] is not None:
                zipCode = URIRef("zipCode:"+str(community[14]))
                county = URIRef("countyCode:"+regCode)
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
                county = URIRef("countyCode:"+ str(countyEntry[2]) )
                # getting the zipcodes in the current county and adding the vek of the county to the zipcodes
                for zipCode,p,o in g.triples((None, isInCounty, county)):
                    g.add((zipCode, hasVEK, Literal(countyEntry[27])))

#Paring iPhone models from query dump
with open('iphones.json') as data_file:
    data = json.load(data_file)
    for model in data:
        modelRessource = URIRef(model['item'])
        modelString = Literal(model['itemLabel'])
        inceptionLiteral = Literal(model['inception'])
        g.add( (modelRessource,RDF.type,typeiPhoneModel) )
        g.add( (modelRessource, RDFS.label, modelString) )
        g.add( (modelRessource,inceptedOn,inceptionLiteral) )

#writing out the graph
f = open('tripels.ttl','w')
f.write(g.serialize(format='turtle'))
f.close()