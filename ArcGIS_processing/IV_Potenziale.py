# -*- coding: cp1252 -*-
#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:        Berechnung von Potenzialen auf Basis von OD-Linien
# Purpose:
#
# Author:      mape
#
# Created:     18/08/2017
# Copyright:   (c) mape 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#---Vorbereitung---#
import arcpy
import time
import h5py
import numpy as np
import pandas
import gc
start_time = time.clock() ##Ziel: am Ende die Berechnungsdauer ausgeben

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','ArcGIS_processing','IV_Schleife.txt')
f = path.read_text()
f = f.split('\n')

print "--Dieses Skript ermöglicht die Potenzialberechnung im IV von ausgewählten Standorten.--"
print "--Beginne mit der Berechnung!--"


##############################
####--Eingabe-Parameter--#####
MIV = False ##Für NMIV berechnen?
R500 = True
#############################
if R500 == True:
    Raster = "C:"+f[1]+"Raster\MRH_500_EW_gew"
    Raster_ID = "ID_500"
else:
    Raster = "C:"+f[1]+"Raster\MRH_100_EW"
    Raster_ID = "ID"

if MIV==True:
    if R500 == True: Tabelle_E = "E_Potenzial_MIV_500"
    else: Tabelle_E = "E_Potenzial_MIV_100"
if MIV==False:
    if R500 == True: Tabelle_E = "E_Potenzial_NMIV_500"
    else: Tabelle_E = "E_Potenzial_NMIV_100"
#############################

Potenzial_Raster_Layer = "C:"+f[1]+"Raster\MRH_Potenzial_500"
Potenzial_ID = "ID"
if MIV == True: Network = "C:"+f[1]+"MRH_Strassen\MRH_Strassen"
else: Network = "C:"+f[1]+"Wegenetz\Wegenetz"
if MIV == True: Kosten = "tAkt"
else: Kosten = "tRad"
if MIV == True: Max_Kosten = 60
else: Max_Kosten = 30
if MIV == True: loop = 100
else: loop = 1000
Datenbank = "C:"+f[0]+"MRH_IV_2019.h5"
Group_Erg = "Potenziale"
##############################


#--OD-Layer erstellen--#
arcpy.Delete_management("ODMATRIX")
if MIV == True: ODLayer = arcpy.MakeODCostMatrixLayer_na(Network,"ODMATRIX",Kosten,Max_Kosten,"",[Kosten,"Meter"],"","","","","NO_LINES")
else: ODLayer = arcpy.MakeODCostMatrixLayer_na(Network,"ODMATRIX",Kosten,Max_Kosten,"",[Kosten,"tFuss","Meter"],"","","","","NO_LINES")
r = []
desc = arcpy.Describe(Network)
attributes = desc.attributes
for i in attributes:
    if i.usageType =='Restriction':
        r.append(i.name)
o = arcpy.mapping.Layer("ODMATRIX")
p = arcpy.na.GetSolverProperties(o)
p.restrictions = r

#--HDF5-Datenbank und Ergebnis-Tabelle--#
file5 = h5py.File(Datenbank,'r+') ##HDF5-File
group5_Ergebnisse = file5[Group_Erg]

Ergebnis_array = []
if MIV:
    Spalten = [('Start_ID', 'int32'),\
               ('EW30', 'int32'),('EW60', 'int32'),('EW02', 'int32'),('EW05', 'int32'),\
               ('AP30', 'int32'),('AP60', 'int32'),('AP02', 'int32'),('AP05', 'int32'),\
               ('EK30', 'int32'),('EK60', 'int32'),('EK02', 'int32'),('EK05', 'int32'),\
               ('FZ30', 'int32'),('FZ60', 'int32'),('FZ02', 'int32'),('FZ05', 'int32'),\
               ('EW5000', 'int32'),('EW30000', 'int32'),\
               ('AP5000', 'int32'),('AP30000', 'int32'),\
               ('EK5000', 'int32'),('EK30000', 'int32'),\
               ('FZ5000', 'int32'),('FZ30000', 'int32')]
else:
    Spalten = [('Start_ID', 'int32'),\
               ('EW30rad', 'int32'),('EW15rad', 'int32'),('EW02rad', 'int32'),('EW05rad', 'int32'),\
               ('AP30rad', 'int32'),('AP15rad', 'int32'),('AP02rad', 'int32'),('AP05rad', 'int32'),\
               ('EK30rad', 'int32'),('EK15rad', 'int32'),('EK02rad', 'int32'),('EK05rad', 'int32'),\
               ('FZ30rad', 'int32'),('FZ15rad', 'int32'),('FZ02rad', 'int32'),('FZ05rad', 'int32'),\
               ('EW30fuss', 'int32'),('EW15fuss', 'int32'),('EW02fuss', 'int32'),('EW05fuss', 'int32'),\
               ('AP30fuss', 'int32'),('AP15fuss', 'int32'),('AP02fuss', 'int32'),('AP05fuss', 'int32'),\
               ('EK30fuss', 'int32'),('EK15fuss', 'int32'),('EK02fuss', 'int32'),('EK05fuss', 'int32'),\
               ('FZ30fuss', 'int32'),('FZ15fuss', 'int32'),('FZ02fuss', 'int32'),('FZ05fuss', 'int32'),\
               ('EW1000', 'int32'),('EW5000', 'int32'),\
               ('AP1000', 'int32'),('AP5000', 'int32'),\
               ('EK1000', 'int32'),('EK5000', 'int32'),\
               ('FZ1000', 'int32'),('FZ5000', 'int32')]

Spalten = np.dtype(Spalten) ##Wandle Spalten-Tuple in dtype um
data = np.array(Ergebnis_array,Spalten)
#if Tabelle_E in group5_Ergebnisse.keys():
#    del group5_Ergebnisse[Tabelle_E] ##Ergebnisliste wird gelöscht falls schon vorhanden
group5_Ergebnisse.create_dataset(Tabelle_E, data=data, dtype=Spalten, maxshape = (None,))
Ergebnis_T = group5_Ergebnisse[Tabelle_E]
file5.flush()


#--Potenzial-Raster adden--#
arcpy.Delete_management("Potenziale")
arcpy.Delete_management("Raster")
arcpy.MakeFeatureLayer_management(Potenzial_Raster_Layer, "Potenziale")
arcpy.MakeFeatureLayer_management(Raster, "Raster")

if MIV == False: field_mappings = "Name "+Potenzial_ID+" 0; SourceID SourceID_NMIV 0;SourceOID SourceOID_NMIV 0;PosAlong PosAlong_NMIV 0;SideOfEdge SideOfEdge_NMIV 0"
else: field_mappings = "Name "+Potenzial_ID+" 0; SourceID SourceID_MIV 0;SourceOID SourceOID_MIV 0;PosAlong PosAlong_MIV 0;SideOfEdge SideOfEdge_MIV 0; Attr_tAkt tAb 1"

if MIV == False: arcpy.AddLocations_na(ODLayer,"Destinations","Potenziale",field_mappings,"","","","","","","","EXCLUDE")
else: arcpy.AddLocations_na(ODLayer,"Destinations","Potenziale",field_mappings,"","","","","","","","EXCLUDE")


Potenzial_Raster = arcpy.da.FeatureClassToNumPyArray("Potenziale",[Potenzial_ID,"EW_Zensus","AP","Freizeit","Versorgung"])
arcpy.Delete_management("Potenziale")
Potenzial_Raster = pandas.DataFrame(Potenzial_Raster)


#--Schleife über Rasterzellen--#
Schleifen = (int(arcpy.GetCount_management("Raster").getOutput(0))/loop)+1
print Schleifen

for i in range(Schleifen):
    print "Schleife: "+str(i+1)
    print "Vergangene Minuten: "+str(int((time.clock()-start_time)/60))
    Schleifenstart = i*loop
    Schleifenziel = Schleifenstart+loop


    arcpy.Delete_management("Raster")
    arcpy.MakeFeatureLayer_management(Raster, "Raster","OBJECTID >"+str(Schleifenstart)+" and OBJECTID <="+str(Schleifenziel))

    if MIV == False: field_mappings = "Name "+Raster_ID+" 0; SourceID SourceID_NMIV 0;SourceOID SourceOID_NMIV 0;PosAlong PosAlong_NMIV 0;SideOfEdge SideOfEdge_NMIV 0"
    else: field_mappings = "Name "+Raster_ID+" 0; SourceID SourceID_MIV 0;SourceOID SourceOID_MIV 0;PosAlong PosAlong_MIV 0;SideOfEdge SideOfEdge_MIV 0; Attr_tAkt tZu 1"

    if MIV == False: arcpy.AddLocations_na(ODLayer,"Origins","Raster",field_mappings,"","","","","CLEAR","","","EXCLUDE")
    else: arcpy.AddLocations_na(ODLayer,"Origins","Raster",field_mappings,"","","","","CLEAR","","","EXCLUDE")

    arcpy.CheckOutExtension("Network")
    arcpy.na.Solve(ODLayer)

    ##arcpy.GetCount_management("ODMATRIX\Lines").getOutput(0)
    try:
        if MIV == True:Linien = arcpy.da.FeatureClassToNumPyArray("ODMATRIX\Lines",["Name","Total_"+Kosten,"Total_Meter"])
        else: Linien = arcpy.da.FeatureClassToNumPyArray("ODMATRIX\Lines",["Name","Total_"+Kosten,"Total_tFuss","Total_Meter"])

    except: continue

    Linien = pandas.DataFrame(Linien)
    a = pandas.DataFrame(Linien.Name.str.split(' - ').tolist(), columns = "Start Ziel".split())
    Linien = pandas.DataFrame.reset_index(Linien)
    Linien["Start"] = a["Start"]
    Linien["Ziel"] = a["Ziel"]
    Linien[["Start","Ziel"]] = Linien[["Start","Ziel"]].astype(int) ##Sonst klappt das Mergen später nicht
    del a, Linien["Name"]

    Linien = pandas.merge(Linien,Potenzial_Raster,left_on="Ziel", right_on=Potenzial_ID)
    Start = pandas.unique(Linien["Start"])

    for n in Start:
        Ergebnis = []
        Ergebnis.append(n)
        Indi = Linien[Linien["Start"]==n]

        #Einwohner#
        Ergebnis.append(int(Indi[Indi["Total_"+Kosten]<=30]["EW_Zensus"].sum()))
        if MIV: Ergebnis.append(int(Indi["EW_Zensus"].sum()))
        else: Ergebnis.append(int(Indi[Indi["Total_"+Kosten]<=15]["EW_Zensus"].sum()))
        Ergebnis.append(int(round(sum(np.exp(Indi["Total_"+Kosten]*-0.02) * Indi["EW_Zensus"]))))
        Ergebnis.append(int(round(sum(np.exp(Indi["Total_"+Kosten]*-0.05) * Indi["EW_Zensus"]))))

        #Arbeit#
        Ergebnis.append(int(Indi[Indi["Total_"+Kosten]<=30]["AP"].sum()))
        if MIV: Ergebnis.append(int(Indi["AP"].sum()))
        else: Ergebnis.append(int(Indi[Indi["Total_"+Kosten]<=15]["AP"].sum()))
        Ergebnis.append(int(round(sum(np.exp(Indi["Total_"+Kosten]*-0.02) * Indi["AP"]))))
        Ergebnis.append(int(round(sum(np.exp(Indi["Total_"+Kosten]*-0.05) * Indi["AP"]))))

        #Einkauf#
        Ergebnis.append(int(Indi[Indi["Total_"+Kosten]<=30]["Versorgung"].sum()))
        if MIV: Ergebnis.append(int(Indi["Versorgung"].sum()))
        else: Ergebnis.append(int(Indi[Indi["Total_"+Kosten]<=15]["Versorgung"].sum()))
        Ergebnis.append(int(round(sum(np.exp(Indi["Total_"+Kosten]*-0.02) * Indi["Versorgung"]))))
        Ergebnis.append(int(round(sum(np.exp(Indi["Total_"+Kosten]*-0.05) * Indi["Versorgung"]))))

        #Freizeit#
        Ergebnis.append(int(Indi[Indi["Total_"+Kosten]<=30]["Freizeit"].sum()))
        if MIV: Ergebnis.append(int(Indi["Freizeit"].sum()))
        else: Ergebnis.append(int(Indi[Indi["Total_"+Kosten]<=15]["Freizeit"].sum()))
        Ergebnis.append(int(round(sum(np.exp(Indi["Total_"+Kosten]*-0.02) * Indi["Freizeit"]))))
        Ergebnis.append(int(round(sum(np.exp(Indi["Total_"+Kosten]*-0.05) * Indi["Freizeit"]))))

        if MIV == False:
            Ergebnis.append(int(Indi[Indi["Total_tFuss"]<=30]["EW_Zensus"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_tFuss"]<=15]["EW_Zensus"].sum()))
            Ergebnis.append(int(round(sum(np.exp(Indi["Total_tFuss"]*-0.02) * Indi["EW_Zensus"]))))
            Ergebnis.append(int(round(sum(np.exp(Indi["Total_tFuss"]*-0.05) * Indi["EW_Zensus"]))))

            #Arbeit#
            Ergebnis.append(int(Indi[Indi["Total_tFuss"]<=30]["AP"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_tFuss"]<=15]["AP"].sum()))
            Ergebnis.append(int(round(sum(np.exp(Indi["Total_tFuss"]*-0.02) * Indi["AP"]))))
            Ergebnis.append(int(round(sum(np.exp(Indi["Total_tFuss"]*-0.05) * Indi["AP"]))))

            #Einkauf#
            Ergebnis.append(int(Indi[Indi["Total_tFuss"]<=30]["Versorgung"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_tFuss"]<=15]["Versorgung"].sum()))
            Ergebnis.append(int(round(sum(np.exp(Indi["Total_tFuss"]*-0.02) * Indi["Versorgung"]))))
            Ergebnis.append(int(round(sum(np.exp(Indi["Total_tFuss"]*-0.05) * Indi["Versorgung"]))))

            #Freizeit#
            Ergebnis.append(int(Indi[Indi["Total_tFuss"]<=30]["Freizeit"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_tFuss"]<=15]["Freizeit"].sum()))
            Ergebnis.append(int(round(sum(np.exp(Indi["Total_tFuss"]*-0.02) * Indi["Freizeit"]))))
            Ergebnis.append(int(round(sum(np.exp(Indi["Total_tFuss"]*-0.05) * Indi["Freizeit"]))))

            #Meter
            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=1000]["EW_Zensus"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=5000]["EW_Zensus"].sum()))

            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=1000]["AP"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=5000]["AP"].sum()))

            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=1000]["Versorgung"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=5000]["Versorgung"].sum()))

            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=1000]["Freizeit"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=5000]["Freizeit"].sum()))

        else:
            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=5000]["EW_Zensus"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=30000]["EW_Zensus"].sum()))

            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=5000]["AP"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=30000]["AP"].sum()))

            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=5000]["Versorgung"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=30000]["Versorgung"].sum()))

            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=5000]["Freizeit"].sum()))
            Ergebnis.append(int(Indi[Indi["Total_Meter"]<=30000]["Freizeit"].sum()))




        #--Speichern der Ergebnisse--#
        Ergebnis =[tuple(Ergebnis)]
        size = len(Ergebnis_T)
        Ergebnis_T.resize((size+1,))
        Ergebnis_T[size:(size+1)] = Ergebnis
        file5.flush()

    del Indi
    del Linien
    del Ergebnis

    gc.collect()
#    if i == 3:
#        file5.flush()
#        file5.close()
#        hh


#--HDF5-Text zu Tabellenbeschreibung--#
text = "Datum: "+str(time.localtime()[0:3])+", Tabelle_A: "+Raster+", Minuten: "+str(Max_Kosten)

Ergebnis_T.attrs.create("Parameter",str(text))


file5.flush()
file5.close()

#--Fertig--#
Sekunden = int(time.clock() - start_time)

print "--Scriptdurchlauf erfolgreich nach",Sekunden,"Sekunden!--"
