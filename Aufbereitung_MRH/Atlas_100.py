# -*- coding: cp1252 -*-
#!/usr/bin/python
#Skript, mit dem Potenziale von bestimmten Einrichtungen aus berechnet werden.
#Marcus September 2015
#f�r Python 2.7.5
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
mxd = arcpy.mapping.MapDocument(r"V:"+f[0]+"Atlas_100.mxd")

#--Ziele--#
fc =[['Gesundheit.gdb\\E_Apotheken','zur n�chsten\r\nApotheke (in Minuten)',u'Apotheken:\r\nOSM 2017','(Montag zwischen 9 und 12 Uhr)','Apotheken'],\
 ['Gesundheit.gdb\\E_Hausarzt','zum n�chsten Hausarzt\r\n(in Minuten)',u'Haus�rzte:\r\nKassen�rztliche Vereinigungen, \r\nGelbe Seiten 2017','(Montag zwischen 9 und 12 Uhr)','Hausaerzte'],\
 ['Gesundheit.gdb\\E_Krankenhaus','zum n�chsten Krankenhaus\r\n(in Minuten)',u'Krankenh�user:\r\nOSM 2017, \r\nDKV Deutsches Krankenhausverzeichnis 2017','(Montag zwischen 9 und 12 Uhr)','Krankenhaus'],\
 ['Bildung.gdb\\E_Foerderschule','zur n�chsten\r\nF�rderschule (in Minuten)',u'F�rderschulen:\r\nKultusministerien der\r\nL�nder 2017','(Montag zwischen 6 und 8 Uhr)','Foerderschulen'],\
 ['Bildung.gdb\\E_Grundschulen','zur n�chsten\r\nGrundschule (in Minuten)',u'Grundschulen:\r\nKultusministerien der\r\nL�nder 2017','(Montag zwischen 6 und 8 Uhr)','Grundschulen'],\
 ['Bildung.gdb\\E_Hochschule','zur n�chsten Hochschule\r\n(in Minuten)',u'Hochschulen:\r\nKultusministerien der\r\nL�nder 2017','(Montag zwischen 9 und 12 Uhr)','Hochschulen'],\
 ['Bildung.gdb\\E_Oberstufe','zur n�chsten Oberstufe\r\n(in Minuten)',u'Oberstufen:\r\nKultusministerien der\r\nL�nder 2017','(Montag zwischen 6 und 8 Uhr)','Oberstufen'],\
 ['Bildung.gdb\\E_Weitf_Schule','zur n�chsten\r\nweiterf�hrenden Schule (in Minuten)',u'Weiterf�hrende Schulen:\r\nKultusministerien der\r\nL�nder 2017','(Montag zwischen 6 und 8 Uhr)','Weiterf_Schulen'],\
 ['Einzelhandel.gdb\\E_Supermarkt','zum n�chsten\r\nSupermarkt (in Minuten)',u'Superm�rkte:\r\nOSM / TUHH 2017','(Montag zwischen 9 und 12 Uhr)','Supermarkt'],\
 ['Freizeit.gdb\\E_Kino','vom n�chsten Kino\r\nnach Hause am Abend (in Minuten)',u'Kinos:\r\nOSM 2017','(Samstag zwischen 22 und 24 Uhr)','Kino'],\
 ['Freizeit.gdb\\E_Schwimmen','zur n�chsten\r\nSchwimmgelegenheit (in Minuten)',u'Schwimmgelegenheiten:\r\nOSM 2017','(Montag zwischen 9 und 12 Uhr)','Schwimmen'],\
 ['Raumplanung.gdb\\E_MZ','zum n�chsten\r\nMittelzentrum (in Minuten)',u'Mittelzentren:\r\nLGV 2017','(Montag zwischen 9 und 12 Uhr)','Mittelzentren'],\
 ['Raumplanung.gdb\\E_OZ','zum n�chsten\r\nOberzentrum (in Minuten)',u'Oberzentren:\r\nLGV 2017','(Montag zwischen 9 und 12 Uhr)','Oberzentren'],\
 ['Soziales.gdb\\E_Arbeitsamt','zum(r) n�chsten\r\nJobcenter / Arbeitsagentur (in Minuten)',u'Jobcenter / Arbeitsagenturen:\r\nOSM / TUHH  2017','(Montag zwischen 9 und 12 Uhr)','Jobcenter'],\
 ['Soziales.gdb\\E_Kita','zur n�chsten\r\nKindertagesst�tte (in Minuten)',u'Kindertagesst�tten:\r\nLGV / KGeo / OSM / TUHH 2017','(Montag zwischen 6 und 8 Uhr)','Kitas'],\
 ['Soziales.gdb\\E_Rathaeuser','zum n�chsten\r\nVerwaltungssitz (in Minuten)',u'Verwaltungssitze:\r\nOSM / TUHH 2017','(Montag zwischen 9 und 12 Uhr)','Verwaltungen'],\
 ['Verkehrsinfrastruktur.gdb\\E_Bahnhof','zum n�chsten\r\nBahnhof (in Minuten)',u'Bahnh�fe:\r\nTUHH / HAFAS 2017','(Montag zwischen 9 und 12 Uhr)','Bahnhoefe'],\
 ['Verkehrsinfrastruktur.gdb\\E_Fernbahn','zum n�chsten\r\nFernbahnhof (in Minuten)',u'Fernbahnh�fe:\r\nTUHH / HAFAS 2017','(Montag zwischen 9 und 12 Uhr)','Fernbahnhoefe'],\
 ['Verkehrsinfrastruktur.gdb\\E_Flughafen','zum\r\nHamburger Flughafen (in Minuten)',u'Flughafen:\r\nTUHH 2017','(Montag zwischen 9 und 12 Uhr)','Flughafen_Hamburg'],\
 ['Verkehrsinfrastruktur.gdb\\E_Hbf','zum\r\nHamburger Hauptbahnhof (in Minuten)',u'Hamburg Hbf.:\r\nTUHH 2017','(Montag zwischen 6 und 8 Uhr)','Hauptbahnhof_Hamburg'],\
 ['Verkehrsinfrastruktur.gdb\\E_PuR','zur n�chsten\r\nP&R-Station (in Minuten)',u'P&R-Stationen:\r\nHVV 2017','(Montag zwischen 6 und 8 Uhr)','PuR'],\
 ['Verkehrsinfrastruktur.gdb\\Abfahrten_Haltestellen_Montags','',u'Bahnh�fe / Fahrplan:\r\nTUHH / HAFAS 2017','',''],\
 ['Verkehrsinfrastruktur.gdb\\Abfahrten_Haltestellen_Sonntags','',u'Bahnh�fe / Fahrplan:\r\nTUHH / HAFAS 2017','','']]


Gebiete =[["Kreis Stormarn","01Stormarn",129,"Stormarn"],\
["Kreis Segeberg","02Segeberg",291,"Segeberg"],\
["Kreis Dithmarschen","03Dithmarschen",437,"Dithmarschen"],\
["Kreis Steinburg","04Steinburg",338,"Steinburg"],\
["Kreis Pinneberg","05Pinneberg",439,"Pinneberg"],\
["Neum�nster","06Neum�nster",314,"Neum�nster"],\
["Kreis Ostholstein","07Ostholstein",300,"Ostholstein"],\
["L�beck","08L�beck",131,"L�beck"],\
["Herzogtum Lauenburg","09Lauenburg",102,"Herzogtum Lauenburg"],\
["Hamburg","20Hamburg",434,"Hamnburg"],\
["Landkreis\r\nNordwestmecklenburg","30Nordwestmecklenburg",249,"Nordwestmecklenburg"],\
["Landeshauptstadt\r\nSchwerin","31Schwerin",276,"Schwerin"],\
["Landkreis\r\nLudwigslust-Parchim","32LuLu_Parchim",101,"Ludwigslust-Parchim"],\
["Landkreis\r\nL�chow-Dannenberg","40L�chow_Dannenberg",120,"L�chow-Dannenberg"],\
["Landkreis\r\nL�neburg","41L�neburg",112,"L�neburg"],\
["Landkreis\r\nHarburg","42Harburg",113,"Harburg"],\
["Landkreis\r\nStade","43Stade",82,"Stade"],\
["Landkreis\r\nCuxhaven","44Cuxhaven",418,"Cuxhaven"],\
["Landkreis\r\nHeidekreis","45Heidekreis",10,"Heidekreis"],\
["Landkreis\r\nUelzen","46Uelzen",339,"Uelzen"],\
["Landkreis\r\nRotenburg (W�mme)","47Rotenburg",404,"Rotenburg (W�mme)"]]


for g in Gebiete:
    print("Beginne mit: "+g[0])
    elm = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")

    elm[1].text = g[0]
    df_Gebiet = arcpy.mapping.ListDataFrames(mxd)[0]
    layer_Gebiet = arcpy.mapping.ListLayers(mxd, "*", df_Gebiet)
    layer_Gebiet[0].definitionQuery = "Kreis = '"+g[3]+"' and type = 'town'"
    layer_Gebiet[1].definitionQuery = "OBJECTID = "+str(g[2])
    layer_Gebiet[2].definitionQuery = "OBJECTID <> "+str(g[2])
    df_Gebiet.extent = layer_Gebiet[1].getExtent()

    ##if g[2] != 129:continue


    for i in fc:
        #--Fuege Layer mit Ergebnissen hinzu--#
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        addLayer = arcpy.mapping.Layer("C:"+f[1]+i[0])
        arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
        #--Bearbeite Layer und Textelder--#
        layer = arcpy.mapping.ListLayers(mxd, "*", df)
        elm[2].text = i[2]

        #####################################
        #Haltestellen Montag#
        #####################################
        if "Montags" in i[0]:
            layer[3].visible = True ##Autobahn
            layer[4].visible = False ##Bundesstra�e
            layer[5].visible = True ##Bahnstrecke
            layer[7].visible = False
            layer[18].visible = False
            layer[14].visible = True
            elm[0].text = "Indikator:\r\n\r\nAnzahl an Abfahrten an einem Montag\r\nje Haltestelle"
            layer[7].replaceDataSource("C:"+f[1]+"Verkehrsinfrastruktur.gdb","FILEGDB_WORKSPACE", "Abfahrten_Haltestellen_Montags")
            arcpy.ApplySymbologyFromLayer_management(layer[18],layer[14])
            arcpy.ApplySymbologyFromLayer_management(layer[7],layer[14])
            #--Export--#
            arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\Abfahrten_Montags.pdf")
            layer[7].replaceDataSource("C:"+f[1]+"Bildung.gdb","FILEGDB_WORKSPACE", "E_Grundschulen")
            arcpy.ApplySymbologyFromLayer_management(layer[7],layer[17])
            arcpy.mapping.RemoveLayer(df, layer[18])
            layer[14].visible = False
            continue

        #####################################
        #Haltestellen Sonntag#
        #####################################
        if "Sonntags" in i[0]:
            layer[3].visible = True ##Autobahn
            layer[4].visible = False ##Bundesstra�e
            layer[5].visible = True ##Bahnstrecke
            layer[7].visible = False
            layer[18].visible = False
            layer[15].visible = True
            elm[0].text = "Indikator:\r\n\r\nAnzahl an Abfahrten an einem Sonntag\r\nje Haltestelle"
            layer[7].replaceDataSource("C:"+f[1]+"Verkehrsinfrastruktur.gdb","FILEGDB_WORKSPACE", "Abfahrten_Haltestellen_Sonntags")
            arcpy.ApplySymbologyFromLayer_management(layer[18],layer[15])
            arcpy.ApplySymbologyFromLayer_management(layer[7],layer[15])
            #--Export--#
            arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\Abfahrten_Sonntags.pdf")
            layer[15].visible = False

        #####################################
        #Haltestellen Linien#
        #####################################
        if "Sonntags" in i[0]:
            layer[3].visible = True ##Autobahn
            layer[4].visible = False ##Bundesstra�e
            layer[5].visible = True ##Bahnstrecke
            layer[7].visible = False
            layer[18].visible = False
            layer[16].visible = True
            elm[0].text = "Indikator:\r\n\r\nLinien je Haltestelle"
            arcpy.ApplySymbologyFromLayer_management(layer[18],layer[16])
            arcpy.ApplySymbologyFromLayer_management(layer[7],layer[16])
            #--Export--#
            arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\Anzahl_Linien.pdf")
            layer[7].replaceDataSource("C:"+f[1]+"Bildung.gdb","FILEGDB_WORKSPACE", "E_Grundschulen")
            arcpy.ApplySymbologyFromLayer_management(layer[7],layer[17])
            arcpy.mapping.RemoveLayer(df, layer[18])
            layer[16].visible = False
            continue

        #####################################
        #Fuss#
        #####################################
        layer[3].visible = True ##Autobahn
        layer[4].visible = False ##Bundesstra�e
        layer[5].visible = True ##Bahnstrecke
        layer[7].visible = False
        elm[0].text = "Indikator:\r\n\r\nGehzeit "+i[1]
        arcpy.ApplySymbologyFromLayer_management(layer[18],layer[7])
        #--Export--#
        if i[4]!= "PuR":arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\Fuss_"+i[4]+".pdf")

        #####################################
        #Meter#
        #####################################
        layer[3].visible = True ##Autobahn
        layer[4].visible = False ##Bundesstra�e
        layer[5].visible = True ##Bahnstrecke
        layer[7].visible = False
        elm[0].text = "Indikator:\r\n\r\nEntfernung "+i[1].replace("Minuten","Metern")
        arcpy.ApplySymbologyFromLayer_management(layer[18],layer[11])
        arcpy.ApplySymbologyFromLayer_management(layer[7],layer[11])
        #--Export--#
        if i[4]!= "PuR":arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\Meter_"+i[4]+".pdf")
        arcpy.ApplySymbologyFromLayer_management(layer[7],layer[17])

        #####################################
        #Rad#
        #####################################
        layer[3].visible = True ##Autobahn
        layer[4].visible = True ##Bundesstra�e
        layer[5].visible = False ##Bahnstrecke
        layer[7].visible = False
        elm[0].text = "Indikator:\r\n\r\nReisezeit mit dem Rad "+i[1]
        arcpy.ApplySymbologyFromLayer_management(layer[18],layer[8])
        #--Export--#
        arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\Rad_"+i[4]+".pdf")

        #####################################
        #Pkw#
        #####################################
        layer[3].visible = True ##Autobahn
        layer[4].visible = True ##Bundesstra�e
        layer[5].visible = False ##Bahnstrecke
        layer[7].visible = False
        elm[0].text = "Indikator:\r\n\r\nReisezeit mit dem Pkw "+i[1]
        arcpy.ApplySymbologyFromLayer_management(layer[18],layer[9])
        #--Export--#
        arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\Pkw_"+i[4]+".pdf")

        #####################################
        #OEV#
        #####################################
        layer[3].visible = True ##Autobahn
        layer[4].visible = False ##Bundesstra�e
        layer[5].visible = True ##Bahnstrecke
        layer[7].visible = False
        elm[0].text = "Indikator:\r\n\r\nReisezeit mit dem �V "+i[1]+"\r\n"+i[3]
        arcpy.ApplySymbologyFromLayer_management(layer[18],layer[10])
        #--Export--#
        if i[4]!= "PuR":arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\OEV_"+i[4]+".pdf")

        #####################################
        #Umstiege#
        #####################################
        layer[3].visible = True ##Autobahn
        layer[4].visible = False ##Bundesstra�e
        layer[5].visible = True ##Bahnstrecke
        layer[7].visible = False
        elm[0].text = "Indikator:\r\n\r\nUmstiege im �V "+i[1].replace("(in Minuten)","")+"\r\n"+i[3]
        arcpy.ApplySymbologyFromLayer_management(layer[18],layer[12])
        arcpy.ApplySymbologyFromLayer_management(layer[7],layer[12])
        #--Export--#
        if i[4]!= "PuR":arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\Umstiege_"+i[4]+".pdf")
        arcpy.ApplySymbologyFromLayer_management(layer[7],layer[17])

        #####################################
        #Verbindungen#
        #####################################
        layer[3].visible = True ##Autobahn
        layer[4].visible = False ##Bundesstra�e
        layer[5].visible = True ##Bahnstrecke
        layer[7].visible = False
        elm[0].text = "Indikator:\r\n\r\nFahrten des �V "+i[1].replace("(in Minuten)","")+"\r\n"+i[3]
        arcpy.ApplySymbologyFromLayer_management(layer[18],layer[13])
        arcpy.ApplySymbologyFromLayer_management(layer[7],layer[13])
        #--Export--#
        if i[4]!= "PuR":arcpy.mapping.ExportToPDF(mxd, r"V:"+f[2]+g[1]+"\\Verbindungen_"+i[4]+".pdf")
        arcpy.ApplySymbologyFromLayer_management(layer[7],layer[17])

        #####################################
        #Ende#
        #####################################
        #--Loesche Layer mit Ergebnissen--#
        arcpy.mapping.RemoveLayer(df, layer[18])

        del df,layer
    del df_Gebiet, layer_Gebiet

#--ENDE-#
print "--Fertig--"
del mxd