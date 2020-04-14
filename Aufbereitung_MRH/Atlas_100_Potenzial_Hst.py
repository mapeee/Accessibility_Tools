# -*- coding: cp1252 -*-
#!/usr/bin/python
#Skript, mit dem Potenziale von bestimmten Einrichtungen aus berechnet werden.
#Marcus September 2015
#für Python 2.7.5
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      mape
#
# Created:     24/07/2017
# Copyright:   (c) mape 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#---Vorbereitung---#
import sys
sys.path.append('c:\\Program Files (x86)\\ArcGIS\\Desktop10.4\\bin')
sys.path.append('c:\\program files (x86)\\arcgis\\desktop10.4\\arcpy')
import arcpy
import h5py
import numpy as np

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Aufbereitung_MRH','Atlas_100.txt')
f = path.read_text()
f = f.split('\n')

#--Verbindung zur mxd--#

mxd = arcpy.mapping.MapDocument(r"V:"+f[0]+"Atlas_100_Hst.mxd")

#--Ziele--#
fc =[[6,'Arbeitsplätze, für die eine Haltestelle die\r\nnächstgelegene ist (800 Meter Realdistanz)','Haltestelle_AP_800m'],\
[7,'Arbeitsplätze, für die eine Haltestelle die\r\nnächstgelegene ist (350 Meter Realdistanz)','Haltestelle_AP_350m'],\
[8,'Einwohner, für die eine Haltestelle die\r\nnächstgelegene ist (800 Meter Realdistanz)','Haltestelle_EW_800m'],\
[9,'Einwohner, für die eine Haltestelle die\r\nnächstgelegene ist (350 Meter Realdistanz)','Haltestelle_EW_350m'],\
[10,'Arbeitsplätze, die von einer Haltestelle in\r\n30 Minuten erreicht werden können (in Tsd.)\r\n(Montag zwischen 6 und 8 Uhr)','Haltestelle_AP30Minuten'],\
[11,'Arbeitsplätze, die von einer Haltestelle ohne\r\nUmstieg erreicht werden können (in Tsd.)\r\n(Montag zwischen 6 und 8 Uhr)','Haltestelle_APUH0'],\
[12,'Einwohner, die von einer Haltestelle in\r\n30 Minuten erreicht werden können (in Tsd.)\r\n(Montag zwischen 9 und 12 Uhr)','Haltestelle_EW30Minuten'],\
[13,'Einwohner, die von einer Haltestelle ohne\r\nUmstieg erreicht werden können (in Tsd.)\r\n(Montag zwischen 9 und 12 Uhr)','Haltestelle_EWUH0']]


Gebiete =[["Kreis Stormarn","01Stormarn",129,"Stormarn"],\
["Kreis Segeberg","02Segeberg",291,"Segeberg"],\
["Kreis Dithmarschen","03Dithmarschen",437,"Dithmarschen"],\
["Kreis Steinburg","04Steinburg",338,"Steinburg"],\
["Kreis Pinneberg","05Pinneberg",439,"Pinneberg"],\
["Neumünster","06Neumünster",314,"Neumünster"],\
["Kreis Ostholstein","07Ostholstein",300,"Ostholstein"],\
["Lübeck","08Lübeck",131,"Lübeck"],\
["Herzogtum Lauenburg","09Lauenburg",102,"Herzogtum Lauenburg"],\
["Hamburg","20Hamburg",434,"Hamnburg"],\
["Landkreis\r\nNordwestmecklenburg","30Nordwestmecklenburg",249,"Nordwestmecklenburg"],\
["Landeshauptstadt\r\nSchwerin","31Schwerin",276,"Schwerin"],\
["Landkreis\r\nLudwigslust-Parchim","32LuLu_Parchim",101,"Ludwigslust-Parchim"],\
["Landkreis\r\nLüchow-Dannenberg","40Lüchow_Dannenberg",120,"Lüchow-Dannenberg"],\
["Landkreis\r\nLüneburg","41Lüneburg",112,"Lüneburg"],\
["Landkreis\r\nHarburg","42Harburg",113,"Harburg"],\
["Landkreis\r\nStade","43Stade",82,"Stade"],\
["Landkreis\r\nCuxhaven","44Cuxhaven",418,"Cuxhaven"],\
["Landkreis\r\nHeidekreis","45Heidekreis",10,"Heidekreis"],\
["Landkreis\r\nUelzen","46Uelzen",339,"Uelzen"],\
["Landkreis\r\nRotenburg (Wümme)","47Rotenburg",404,"Rotenburg (Wümme)"]]


for g in Gebiete:
    print "Beginne mit: "+g[0]
    elm = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")

    elm[1].text = g[0]
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    layer = arcpy.mapping.ListLayers(mxd, "*", df)
    layer[0].definitionQuery = "Kreis = '"+g[3]+"' and type = 'town'"
    layer[1].definitionQuery = "OBJECTID = "+str(g[2])
    layer[2].definitionQuery = "OBJECTID <> "+str(g[2])
    df.extent = layer[1].getExtent()

    ##if g[2] != 129:continue


    for i in fc:
        #--Bearbeite Layer und Textelder--#
        layer = arcpy.mapping.ListLayers(mxd, "*", df)
        elm[0].text = i[1]


        #####################################
        #Alle#
        #####################################
        layer[3].visible = True ##Autobahn
        layer[4].visible = False ##Bundesstraße
        layer[5].visible = True ##Bahnstrecke
        layer[i[0]].visible = True

        #--Export--#
        arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\"+i[2]+".pdf")
        layer[i[0]].visible = False


        #####################################
        #Ende#
        #####################################

    del df,layer
del mxd

#--ENDE-#
print "--Fertig--"
