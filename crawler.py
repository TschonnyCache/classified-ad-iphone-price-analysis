import requests
from bs4 import BeautifulSoup
import re

payload = {'keywords':'iPhone','locationStr':'04103','categoryId':'173','adType':'OFFER'}
r = requests.get('https://www.ebay-kleinanzeigen.de/s-suchanfrage.html',params=payload)
#r.encoding = 'utf-8'
#print(r.text)
#f = open('index.html','w')
#f.write(r.text)
#f.close()
soup = BeautifulSoup(r.text, 'html.parser')
for add in soup.find_all("article", class_="aditem"):
    print 'Id'
    print add.attrs['data-adid']
    print 'Titel'
    print add.contents[3].contents[1].contents[0].contents[0]
    print 'Preis'
    print re.sub("\D", "", add.contents[5].contents[1].contents[0])
    print 'PLZ'
    print add.contents[5].contents[4].replace(" ", "").strip()
    print 'Zeit'
    print add.contents[7].contents[0].replace(" ", "").strip()