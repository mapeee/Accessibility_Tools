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

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Aufbereitung_MRH','Atlas_100.txt')
f = path.read_text()
f = f.split('\n')

#--Verbindung zur mxd--#
mxd = arcpy.mapping.MapDocument(r"V:"+f[0]+"Atlas_500.mxd")

#--Ziele--#
arcpy.env.workspace = "C:"+f[1]+"Standortqualitaet.gdb"
fc =[['E_Apotheken_500','zur nächsten\r\nApotheke (in Minuten)',u'Apotheken:\r\nOSM 2017','(Montag zwischen 9 und 12 Uhr)'],\
 ['E_Bahnhof_500','zum nächsten\r\nBahnhof (in Minuten)',u'Bahnhöfe:\r\nTUHH 2017','(Montag zwischen 9 und 12 Uhr)'],\
 ['E_Grundschulen_500','zur nächsten\r\nGrundschule (in Minuten)',u'Grundschulen:\r\nLandeskultusministerien 2017','(Montag zwischen 6 und 8 Uhr)'],\
 ['E_Hausarzt_500','zum nächsten\r\nHausarzt (in Minuten)',u'Hausärzte:\r\nKassenärztliche Vereinigungen, \r\nGelbe Seiten 2017','(Montag zwischen 9 und 12 Uhr)'],\
 ['E_Oberstufe_500','zur nächsten\r\nOberstufe (in Minuten)',u'Oberstufen:\r\nLandeskultusministerien 2017','(Montag zwischen 6 und 8 Uhr)'],\
 ['E_Supermarkt_500','zum nächsten\r\nSupermarkt (in Minuten)',u'Supermärkte:\r\nOSM 2017','(Montag zwischen 9 und 12 Uhr)'],\
 ['E_OZ_500','zum nächsten\r\nOberzentrum (in Minuten)',u'Oberzentren:\r\nLGV 2017','(Montag zwischen 9 und 12 Uhr)'],\
 ['E_MZ_500','zum nächsten\r\nMittelzentrum (in Minuten)',u'Mittelzentren:\r\nLGV 2017','(Montag zwischen 9 und 12 Uhr)'],\
 ['E_Freizeit_Potenziale_500','',u'',''],\
 ['E_Supermarkt_Potenziale_500','',u'',''],\
 ['E_Arbeitsplaetze_Potenziale_500','',u'','']]

for i in fc:
    if "Potenzial" in i[0]: continue
    #--Fuege Layer mit Ergebnissen hinzu--#
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    addLayer = arcpy.mapping.Layer("C:"+f[1]+"Standortqualitaet.gdb\\"+i[0])
    arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
    #--Bearbeite Layer und Textelder--#
    layer = arcpy.mapping.ListLayers(mxd, "*", df)
    elm = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")
    elm[1].text = i[2]

    #####################################
    #Fuss#
    #####################################
    layer[4].visible = False ##Autobahn
    layer[5].visible = False ##Bahnstrecke
    layer[7].visible = False
    elm[0].text = "Gehzeit "+i[1]
    arcpy.ApplySymbologyFromLayer_management(layer[15],layer[7])
    #--Export--#
    arcpy.mapping.ExportToPDF(mxd, r"V:"+f[3]+"Fuss_"+i[0].replace("E_","")+".pdf")

    #####################################
    #Meter#
    #####################################
    layer[4].visible = False ##Autobahn
    layer[5].visible = True ##Bahnstrecke
    layer[7].visible = False
    elm[0].text = "Entfernung "+i[1].replace("Minuten","Metern")
    arcpy.ApplySymbologyFromLayer_management(layer[15],layer[11])
    arcpy.ApplySymbologyFromLayer_management(layer[7],layer[11])
    #--Export--#
    arcpy.mapping.ExportToPDF(mxd, r"V:"+f[3]+"Meter_"+i[0].replace("E_","")+".pdf")
    arcpy.ApplySymbologyFromLayer_management(layer[7],layer[14])

    #####################################
    #Rad#
    #####################################
    layer[4].visible = False ##Autobahn
    layer[5].visible = False ##Bahnstrecke
    layer[7].visible = False
    elm[0].text = "Reisezeit mit dem Rad "+i[1]
    arcpy.ApplySymbologyFromLayer_management(layer[15],layer[8])
    #--Export--#
    arcpy.mapping.ExportToPDF(mxd, r"V:"+f[3]+"Rad_"+i[0].replace("E_","")+".pdf")

    #####################################
    #Pkw#
    #####################################
    layer[4].visible = True ##Autobahn
    layer[5].visible = False ##Bahnstrecke
    layer[7].visible = False
    elm[0].text = "Reisezeit mit dem Pkw "+i[1]
    arcpy.ApplySymbologyFromLayer_management(layer[15],layer[9])
    #--Export--#
    arcpy.mapping.ExportToPDF(mxd, r"V:"+f[3]+"Pkw_"+i[0].replace("E_","")+".pdf")

    #####################################
    #OEV#
    #####################################
    layer[4].visible = False ##Autobahn
    layer[5].visible = True ##Bahnstrecke
    layer[7].visible = False
    elm[0].text = "Reisezeit mit dem ÖV "+i[1]+"\r\n"+i[3]
    arcpy.ApplySymbologyFromLayer_management(layer[15],layer[10])
    #--Export--#
    arcpy.mapping.ExportToPDF(mxd, r"V:"+f[3]+"OEV_"+i[0].replace("E_","")+".pdf")

    #####################################
    #Umstiege#
    #####################################
    layer[4].visible = False ##Autobahn
    layer[5].visible = True ##Bahnstrecke
    layer[7].visible = False
    elm[0].text = "Umstiege im ÖV "+i[1].replace("(in Minuten)","")+"\r\n"+i[3]
    arcpy.ApplySymbologyFromLayer_management(layer[15],layer[12])
    arcpy.ApplySymbologyFromLayer_management(layer[7],layer[12])
    #--Export--#
    arcpy.mapping.ExportToPDF(mxd, r"V:"+f[3]+"Umstiege_"+i[0].replace("E_","")+".pdf")
    arcpy.ApplySymbologyFromLayer_management(layer[7],layer[14])

    #####################################
    #Verbindungen#
    #####################################
    layer[4].visible = False ##Autobahn
    layer[5].visible = True ##Bahnstrecke
    layer[7].visible = False
    elm[0].text = "Fahrten des ÖV "+i[1].replace("(in Minuten)","")+"\r\n"+i[3]
    arcpy.ApplySymbologyFromLayer_management(layer[15],layer[13])
    arcpy.ApplySymbologyFromLayer_management(layer[7],layer[13])
    #--Export--#
    arcpy.mapping.ExportToPDF(mxd, r"V:"+f[3]+"Verbindungen_"+i[0].replace("E_","")+".pdf")
    arcpy.ApplySymbologyFromLayer_management(layer[7],layer[14])

    #####################################
    #Ende#
    #####################################
    #--Loesche Layer mit Ergebnissen--#
    arcpy.mapping.RemoveLayer(df, layer[15])

    del df,layer

#--ENDE-#
print("--Fertig--")
del mxd

#--Verschiedenes--#
##layer[2].visible = False
##bkmk = arcpy.mapping.ListBookmarks(mxd, "", df)
##df[0].extent = bkmk[0].extent
##layer[8].definitionQuery = "Minuten_OEV <200" ##statt 999