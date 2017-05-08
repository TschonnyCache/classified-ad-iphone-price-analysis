import requests

payload = {'keywords':'iPhone','locationStr':'04103','categoryId':'173'}
r = requests.get('https://www.ebay-kleinanzeigen.de/s-suchanfrage.html',params=payload)
#r.encoding = 'utf-8'
print(r.text)
#f = open('index.html','w')
#f.write(r.text)
#f.close()
