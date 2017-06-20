from rdflib import Graph, RDF, URIRef, Literal, RDFS, Namespace
from rdflib.util import date_time
from torrequest import TorRequest
from bs4 import BeautifulSoup
from datetime import datetime
from requests.exceptions import ConnectionError
import time
import re


def crawl(zipCodeSearchString, tr, adsGraph):

        payload = {'keywords':'iPhone','locationStr':zipCodeSearchString,'categoryId':'173','adType':'OFFER'}
        response = tr.get('https://www.ebay-kleinanzeigen.de/s-suchanfrage.html', params=payload)

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

            if  price > 50 and 'Gestern' in time and "reparatur " not in title.lower() and "defekt" not in title.lower():

                # finding out which iphone is in the ad:
                # and iphoneModelString.lower() in title.lower()
                for tuple in modelList:
                    if tuple[0].lower() in title.lower():
                        foundiPhoneModelResource = tuple[1]
                        break
                else:
                    # no model could be detected, i.e. old model
                    break

                adRessource = URIRef("ad:" + adId)
                zipCodeURI = URIRef("zipCode:"+zipCode)
                priceLiteral = Literal(price)
                adTime = Literal(date_time())

                adsGraph.add((adRessource, containsModel, foundiPhoneModelResource))
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

modelList = []

# iterateing over the iphone models
for iPhoneModelResource,p,o in backgroundInfo.triples((None, RDF.type , typeiPhoneModel)):
    # getting the name of the iphone model
    for s,p,iPhoneLabelString in backgroundInfo.triples((iPhoneModelResource, RDFS.label, None)):
        #  and saving result into triples
        tuple = (str(iPhoneLabelString),iPhoneModelResource)
        # making shure that the plus models come before the regular ones, this makes it easier to distinguis plus and non plus models
        if "Plus" in str(iPhoneLabelString):
            modelList.insert(0,tuple)
        else:
            modelList.append(tuple)


with TorRequest(proxy_port=9050, ctrl_port=9051, password=None) as tr:
    i=0
    d=0
    print str(datetime.now())
    # iterateing over the zip codes
    for zipCode,p,o in backgroundInfo.triples((None, RDF.type, typePLZ)):
        i = i+1
        d = d+1
        print d
        zipCode = zipCode.split(':')[1]
        try:
            adsGraph = crawl(zipCode, tr, adsGraph)
        except ConnectionError:
            print ("Connection reset error")
            time.sleep(600)
            continue


        #Reset the tor identity after i zip codes
        if i == 3:
            i = 0
            tr.reset_identity()
    print str(datetime.now())

f = open('ads' + str(datetime.now()) + '.ttl','w')
f.write(adsGraph.serialize(format='turtle'))
f.close()