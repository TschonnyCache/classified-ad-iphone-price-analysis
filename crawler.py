from rdflib import Graph, RDF, URIRef, Literal, RDFS, Namespace
from rdflib.util import date_time
from torrequest import TorRequest
from bs4 import BeautifulSoup
from datetime import datetime
import re


def crawl(iphoneModelString, iPhoneModelResource, zipCodeSearchString, tr, adsGraph):

        # print "Searching for " + iphoneModelString + " in " + zipCodeSearchString + "\n"

        payload = {'keywords':iphoneModelString,'locationStr':zipCodeSearchString,'categoryId':'173','adType':'OFFER'}
        response = tr.get('https://www.ebay-kleinanzeigen.de/s-suchanfrage.html', params=payload)
        #r.encoding = 'utf-8'
        #print(r.text)
        #f = open('index.html','w')
        #f.write(r.text)
        #f.close()
        soup = BeautifulSoup(response.text, 'html.parser')
        for ad in soup.find_all("article", class_="aditem"):
            adId = ad.attrs['data-adid']
            title = ad.contents[3].contents[1].contents[0].contents[0]
            try:
                zipCode = ad.contents[5].contents[4].replace(" ", "").strip()
            except IndexError:
                continue
            try:
                time = ad.contents[7].contents[0].replace(" ", "").strip()
            except IndexError:
                continue
            priceRaw = re.sub("\D", "", ad.contents[5].contents[1].contents[0])
            try:
                price = int(re.sub("\D", "", ad.contents[5].contents[1].contents[0]))
            except ValueError:
                # filtering "VB Preise"
                continue

            # print 'Id ' + adId
            # print 'Titel ' + title
            # print 'Preis ' + str(price)
            # print 'PLZ ' + zipCode
            # print 'Zeit ' + time + "\n"

            if  price > 50 and 'Gestern' in time and iphoneModelString.lower() in title.lower() and "reparatur " not in title.lower() and "defekt" not in title.lower():
                adRessource = URIRef("ad:" + ad.attrs['data-adid'])
                zipCodeURI = URIRef("zipCode:"+zipCode)
                priceLiteral = Literal(price)
                adTime = Literal(date_time())

                adsGraph.add((adRessource, containsModel, iPhoneModelResource))
                adsGraph.add((adRessource, isInZipCode, zipCodeURI))
                adsGraph.add((adRessource, hasPrice, priceLiteral))
                adsGraph.add((adRessource, postedOn, adTime))

        return adsGraph

ns = Namespace("sw-kreusch")
containsModel = URIRef("containsModel")
isInZipCode = URIRef("isInZipCode")
hasPrice = URIRef("hasPrice")
postedOn = URIRef("postedOn")
typePLZ = URIRef("http://dbpedia.org/ontology/zipCode")
typeiPhoneModel = URIRef("https://www.wikidata.org/wiki/Q2766")

backgroundInfo = Graph()
backgroundInfo.parse("tripels.ttl", format="turtle")

adsGraph = Graph()
# try:
#     adsGraph.parse('ads.ttl', format="turtle")
# except IOError:
#     pass

with TorRequest(proxy_port=9050, ctrl_port=9051, password=None) as tr:
    i=0
    print str(datetime.now())
    # iterateing over the zip codes
    for zipCode,p,o in backgroundInfo.triples((None, RDF.type, typePLZ)):
        i = i+1
        zipCode = zipCode.split(':')[1]

        # iterateing over the iphone models
        for iPhoneModelResource,p,o in backgroundInfo.triples((None, RDF.type , typeiPhoneModel)):
            # getting the name of the iphone model
            for s,p,iPhoneLabelString in backgroundInfo.triples((iPhoneModelResource, RDFS.label, None)):

                adsGraph = crawl(str(iPhoneLabelString), iPhoneModelResource, zipCode,tr,adsGraph)

        #Debug
        # if i == 10:
        #     break;
        #Reset the tor identity after i zip codes
        if i == 3:
            i = 0
            tr.reset_identity()
    print str(datetime.now())
f = open('ads' + str(datetime.now()) + '.ttl','w')
f.write(adsGraph.serialize(format='turtle'))
f.close()