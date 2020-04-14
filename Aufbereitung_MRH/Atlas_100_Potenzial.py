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

MXDS = [[r"V:"+f[0]+"Atlas_100_AP.mxd","Arbeitsplätze","Arbeitsplaetze",u'Arbeitsplätze:\r\nNexiga Gmbh 2017','(Montag zwischen 6 und 8 Uhr)'],\
[r"V:"+f[0]+"Atlas_100_EK.mxd","\r\nEinkaufsgelegenheiten (aperiodisch)","Einkauf_aperiodisch",u'Einkaufsgelegenheiten:\r\nOSM / TUHH 2017','(Montag zwischen 9 und 12 Uhr)'],\
[r"V:"+f[0]+"Atlas_100_FZ.mxd","\r\nFreizeitgelegenheiten","Freizeit",u'Freizeitgelegenheiten:\r\nOSM / TUHH 2017','(Montag zwischen 9 und 12 Uhr)'],\
[r"V:"+f[0]+"Atlas_100_EW.mxd","\r\nEinwohner","Einwohner",u'Einwohner:\r\nNexiga GmbH / TUHH 2017','(Montag zwischen 9 und 12 Uhr)']]


for m in MXDS:
    mxd = arcpy.mapping.MapDocument(m[0])

    #--Ziele--#
    fc =[[7,'Mit dem Pkw erreichbare '+m[1]+'\r\nin 30 Minuten (in Tsd.)',m[3],'Pkw_'+m[2]+'_30Min'],\
    [8,'Mit dem Pkw erreichbare '+m[1]+'\r\nin 60 Minuten (in Tsd.)',m[3],'Pkw_'+m[2]+'_60Min'],\
    [9,'Zu Fuß erreichbare '+m[1]+'\r\nin 15 Minuten (in Tsd.)',m[3],'Fuss_'+m[2]+'_15Min'],\
    [10,'Zu Fuß erreichbare '+m[1]+'\r\nin 30 Minuten (in Tsd.)',m[3],'Fuss_'+m[2]+'_30Min'],\
    [11,'Mit dem Rad erreichbare '+m[1]+'\r\nin 15 Minuten (in Tsd.)',m[3],'Rad_'+m[2]+'_15Min'],\
    [12,'Mit dem Rad erreichbare '+m[1]+'\r\nin 30 Minuten (in Tsd.)',m[3],'Rad_'+m[2]+'_30Min'],\
    [13,'Mit dem ÖV erreichbare '+m[1]+'\r\nin 30 Minuten (in Tsd.)',m[3],'OEV_'+m[2]+'_30Min'],\
    [14,'Mit dem ÖV erreichbare '+m[1]+'\r\nin 60 Minuten (in Tsd.)',m[3],'OEV_'+m[2]+'_60Min'],\
    [15,'Mit dem ÖV ohne Umstieg erreichbare '+m[1]+'\r\n (in Tsd.)',m[3],'OEV_'+m[2]+'_UH0'],\
    ]


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
        print("Beginne mit: "+g[0])
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
            elm[2].text = i[2]


            #####################################
            #Alle#
            #####################################
            layer[3].visible = True ##Autobahn
            layer[4].visible = False ##Bundesstraße
            layer[5].visible = True ##Bahnstrecke
            layer[i[0]].visible = True
            if ("aperiodisch" or "Freizeit") in i[3]: a = i[1].replace(" (in Tsd.)","")
            else:  a = i[1]
            if "OEV" in i[3]:elm[0].text = "Indikator:\r\n\r\n"+a+"\r\n"+m[4]
            else:elm[0].text = "Indikator:\r\n\r\n"+a

            #--Export--#
            arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\"+i[3]+".pdf")
            layer[i[0]].visible = False


            #####################################
            #Ende#
            #####################################

        del df,layer
    del mxd

#--ENDE-#
print "--Fertig--"
