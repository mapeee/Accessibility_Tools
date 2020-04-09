# -*- coding: cp1252 -*-
#-------------------------------------------------------------------------------
# Name:        OSM_Import_Tags
# Purpose:
#
# Author:      mape
#
# Created:     07/04/2015
# Copyright:   (c) mape 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

##Module##
import overpy
import arcpy

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Netzaufbereitung','OSM_Import_Tags.txt')
f = path.read_text()
f = f.split('\n')

##Verzeichnisse##
Shape = "D:"+f[0]
fields = ["osm_id","Lanes"]

##Feld hinzufügen##
arcpy.AddField_management(Shape,"Lanes","SHORT")

##Abfrage##
api = overpy.Overpass()
result = api.query("[out:json];area[admin_level='4']['de:amtlicher_gemeindeschluessel'='12'];way(area)[highway]['lanes'~'2|3|4|5|6'];out;")
print("--Abfrage erfolgreich--")
print(len(result.ways))
##Join##
with arcpy.da.UpdateCursor(Shape, fields) as cursor:
    for row in cursor:
        ID = int(row[0])
        for way in result.ways:
            if ID == int(way.id):
                lanes = way.tags.get("lanes")
                try:
                    row[1] = int(lanes.split(".")[0])  ##manchmal gibt es halbe Fahrspuren...
                except:
                    row[1] = int(lanes.split(";")[0])  ##manchmal gibt es halbe Fahrspuren...
                cursor.updateRow(row)
del cursor
