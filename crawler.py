from rdflib import Graph, RDF, URIRef, Literal, RDFS, Namespace
from torrequest import TorRequest
from bs4 import BeautifulSoup
import re


def crawl(iphoneModelString,iPhoneModelResource, zipCode,tr,g):

        payload = {'keywords':iphoneModelString,'locationStr':zipCode,'categoryId':'173','adType':'OFFER'}
        response = tr.get('https://www.ebay-kleinanzeigen.de/s-suchanfrage.html', params=payload)
        #r.encoding = 'utf-8'
        #print(r.text)
        #f = open('index.html','w')
        #f.write(r.text)
        #f.close()
        soup = BeautifulSoup(response.text, 'html.parser')
        for ad in soup.find_all("article", class_="aditem"):

            if int(re.sub("\D", "", ad.contents[5].contents[1].contents[0])) > 40:
                print 'Id'
                print ad.attrs['data-adid']
                print 'Titel'
                print ad.contents[3].contents[1].contents[0].contents[0]
                print 'Preis'
                print re.sub("\D", "", ad.contents[5].contents[1].contents[0])
                print 'PLZ'
                print ad.contents[5].contents[4].replace(" ", "").strip()
                print 'Zeit'
                print ad.contents[7].contents[0].replace(" ", "").strip()

                adRessource = URIRef("ad:" + ad.attrs['data-adid'])
                zipCode = URIRef("zipCode:"+ad.contents[5].contents[4].replace(" ", "").strip())
                price = Literal(re.sub("\D", "", ad.contents[5].contents[1].contents[0]))

                g.add( (adRessource, containsModel, iPhoneModelResource) )
                g.add( (adRessource, isInZipCode, zipCode) )
                g.add( (adRessource, hasPrice, price) )

        return g



#TODO load iPhones.json, query for all iphones, load vek-store, query for all zipCodes, call crawl

ns = Namespace("sw-kreusch")
containsModel = URIRef("containsModel")
isInZipCode = URIRef("isInZipCode")
hasPrice = URIRef("hasPrice")
typePLZ = URIRef("http://dbpedia.org/ontology/zipCode")
typeiPhoneModel = URIRef("https://www.wikidata.org/wiki/Q2766")

g = Graph()
g.parse("tripels.ttl", format="turtle")

adsGraph = Graph()
try:
    adsGraph.parse('ads.ttl', format="turtle")
except IOError:
    pass

with TorRequest(proxy_port=9050, ctrl_port=9051, password=None) as tr:
    i = 0
    for zipCode,p,o in g.triples((None, RDF.type, typePLZ)):
        i = i+1
        zipCode = zipCode.split(':')[1]

        for iPhoneModelResource,p,o in g.triples((None, RDF.type , typeiPhoneModel)):

            for s,p,iPhoneLabelString in g.triples((iPhoneModelResource,RDFS.label,None)):

                g = crawl(iPhoneLabelString, iPhoneModelResource, zipCode,tr,adsGraph)

        if i == 2:
            break;
        if i == 15:
            i = 1
            tr.reset_identity()

f = open('ads.ttl','w')
f.write(adsGraph.serialize(format='turtle'))
f.close()