# -*- coding: utf-8 -*-

from pyexcel_xlsx import get_data
import json
data = get_data("VGR_KreisergebnisseBand3.xlsx")
vek = data["VEK je Einwohner"]
for zipCodeArea in vek:
    # there are some descriptive entries, that we can filter out easily
    if len(zipCodeArea) > 5:
        if zipCodeArea[6] == '3':
            print 'Postleitzahlbereich ' + str(zipCodeArea[2]) + ' Verfügbaren Einkommen pro Einwohner und Jahr in € ' + str(zipCodeArea[27]) + '\n'
