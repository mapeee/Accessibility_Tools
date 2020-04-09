# -*- coding: cp1252 -*-
#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:        Modul, um in einem Shape Geschwindigkeiten anzupassen
# Purpose:
#
# Author:      mape
#
# Created:     22/12/2015
# Copyright:   (c) mape 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import arcpy
from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Netzaufbereitung','Zeiten_Wegenetz.txt')
f = path.read_text()
f = f.split('\n')

File = "D:"+f[0]

#--Parameter--#
maxRad = 28 #Schneller fährt der durchschnittliche Radler auch bei Gefälle nicht (Annahme)
minRad = 6
sRad = 1.5
maxFuss = 6
minFuss = 2
sFuss = 0.15
dFuss = 4 ##Durchschnittliches Gehtempo

#--vDurchschnitt Radverkehr--#
v_schnitt = [(u'tertiary',18,maxRad,minRad),
(u'secondary',18,maxRad,minRad),
(u'residential',18,maxRad,minRad),
(u'primary',18,maxRad,minRad),
(u'unclassified',16,24,minRad),
(u'primary_link',14,20,minRad),
(u'pedestrian',10,15,minRad),
(u'track',16,24,minRad),
(u'living_street',16,24,minRad),
(u'footway',10,15,minRad),
(u'cycleway',20,30,minRad),
(u'path',18,maxRad,minRad),
(u'service',16,24,minRad),
(u'road',16,24,minRad),
(u'steps',1,1,1),
(u'construction',10,15,minRad),
(u'tertiary_link',14,20,minRad),
(u'secondary_link',14,20,minRad),
(u'elevator',1,1,1),
(u'services',16,maxRad,minRad)]




#--Ausgabe alle Feldnamen--#
desc = arcpy.Describe(File)
fields =  desc.fields
for field in fields:
    print field.name


"""Radverkehr"""

#--Berechnung der Geschwindigkeiten--#
with arcpy.da.UpdateCursor(File, ['Hoehe','First','Last','vRadHin','vRadRueck','STEIGUNG','type']) as cursor:
    for row in cursor:

        vRad = v_schnitt[map(lambda o : row[6] not in o,v_schnitt).index(False)][1]
        maxRad = v_schnitt[map(lambda o : row[6] not in o,v_schnitt).index(False)][2] #maxRad ergibt sich auch aus dem Streckentyp
        minRad = v_schnitt[map(lambda o : row[6] not in o,v_schnitt).index(False)][3] #minRad ergibt sich auch aus dem Streckentyp

        if (row[1] == row[2]) and row[0] >2: #Steigung über 2 in beide Richtungen.
            row[3:5] = [vRad,vRad]
        elif row[0]==0: #keine Steigung
            row[3:5] = [vRad,vRad]
        elif row[0] <= 2: #Höhe kleiner gleich zwei, keine Steigung
            row[3:5] = [vRad,vRad]
        elif row[1] < row[2]: #Steigung Richtung Last (nach Rechts)
            row[3:5] = [vRad+(row[5]*sRad),vRad-(row[5]*sRad)]
        elif row[1] > row[2]: #Steigung Richtung First (nach Links)
            row[3:5] = [vRad-(row[5]*sRad),vRad+(row[5]*sRad)]

        cursor.updateRow(row)

#--Geschwindigkeitskorrektur--#
with arcpy.da.UpdateCursor(File, ['vRadHin','vRadRueck']) as cursor:
    for row in cursor:
        if row[0] < minRad:
            row[0] = minRad
        if row [0] > maxRad:
            row[0] = maxRad
        if row[1] < minRad:
            row[1] = minRad
        if row [1] > maxRad:
            row[1] = maxRad


        cursor.updateRow(row)

#--Geschwindigkeit in Zeit--#
with arcpy.da.UpdateCursor(File, ['vRadHin','vRadRueck','tRadHin','tRadRueck','Shape_Length']) as cursor:
    for row in cursor:
        row[2:4] = [(row[4]/(row[0]/3.6))/60,(row[4]/(row[1]/3.6))/60]

        cursor.updateRow(row)

del cursor

"""Fussverkehr"""

maxRad = maxFuss
minRad = minFuss
sRad = sFuss

#--Berechnung der Geschwindigkeiten--#
with arcpy.da.UpdateCursor(File, ['Hoehe','First','Last','vFussHin','vFussRueck','STEIGUNG']) as cursor:
    for row in cursor:
        vRad = dFuss
        if (row[1] == row[2]) and row[0] >2: #Steigung über 2 in beide Richtungen.
            row[3:5] = [vRad,vRad]
        elif row[0]==0: #keine Steigung
            row[3:5] = [vRad,vRad]
        elif row[0] <= 2: #Höhe kleiner gleich zwei, keine Steigung
            row[3:5] = [vRad,vRad]
        elif row[1] < row[2]: #Steigung Richtung Last (nach Rechts)
            row[3:5] = [vRad+(row[5]*sRad),vRad-(row[5]*sRad)]
        elif row[1] > row[2]: #Steigung Richtung First (nach Links)
            row[3:5] = [vRad-(row[5]*sRad),vRad+(row[5]*sRad)]

        cursor.updateRow(row)

#--Geschwindigkeitskorrektur--#
with arcpy.da.UpdateCursor(File, ['vFussHin','vFussRueck']) as cursor:
    for row in cursor:
        if row[0] < minRad:
            row[0] = minRad
        if row [0] > maxRad:
            row[0] = maxRad
        if row[1] < minRad:
            row[1] = minRad
        if row [1] > maxRad:
            row[1] = maxRad

        cursor.updateRow(row)

#--Geschwindigkeit in Zeit--#
with arcpy.da.UpdateCursor(File, ['vFussHin','vFussRueck','tFussHin','tFussRueck','Shape_Length']) as cursor:
    for row in cursor:
        row[2:4] = [(row[4]/(row[0]/3.6))/60,(row[4]/(row[1]/3.6))/60]

        cursor.updateRow(row)