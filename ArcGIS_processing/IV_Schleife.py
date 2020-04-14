# -*- coding: cp1252 -*-
#!/usr/bin/python
#Skript, mit dem Potenziale von bestimmten Einrichtungen aus berechnet werden.
#Marcus September 2019
#für Python 2.7.5

"""
Die Idee ist die Folgende:
pass
"""

#---Vorbereitung---#
import arcpy
arcpy.CheckOutExtension("Network")
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

print("--Dieses Skript ermöglicht die Berechnung von Anbindungen ausgewählter Standorte--")
print("--Beginne mit der Berechnung!--")

##############################
####--Eingabe-Parameter--#####
NMIV = False ##Für NMIV berechnen?
R500 = True ##Für 500er Raster berechnen?
##############################



if NMIV == True: Modus = "NMIV, Anbindung_aggregiert"
else: Modus = "MIV, Anbindung_aggregiert"
Datenbank = "C:"+f[0]+"MRH_IV_2019.h5"
ID_A = "Start_ID"
ID_S = "Start_ID"
Group_Erg = "Ergebnisse"
if NMIV == True: Radius = 15000
else: Radius = 70000
S_Shape_ID = "ID"
if NMIV == True: Kosten = "tRad"
else: Kosten ="tAkt"
if NMIV == True: Max_Kosten = 60
else: Max_Kosten = 60
if R500 == False:
    A_Shape = "C:"+f[1]+"Raster\MRH_100_EW"
    A_Shape_ID = "ID"
else:
    A_Shape = "C:"+f[1]+"Raster\MRH_500_EW_gew"
    A_Shape_ID = "ID_500"
if NMIV == True: Network = "C:"+f[1]+"Wegenetz\Wegenetz"
else: Network = "C:"+f[1]+"MRH_Strassen\MRH_Strassen"
if NMIV == True:
    k_S = "tRad"
    k_A = "tRad"
else:
    k_S = "tAkt"
    k_A = "tAkt"

###########################################################################
#--Verbindung zur HDF-5 Datenbank--#
###########################################################################
#--Datenzugriff--#
file5 = h5py.File(Datenbank,'r+') ##HDF5-File
group5_Ergebnisse = file5[Group_Erg]


################################################
#--Schleife--#
################################################

l = [["C:"+f[1]+"Punkte_Verkehr/MRH_PR_2017",False,"E_PuR"],\
["C:"+f[1]+"Punkte_Admin/MRH_Apotheken_2019",False,"E_Apotheken"],\
["C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","Grundsch","E_Grundschulen"],\
["C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","WeiterF","E_WeiterFSchule"],\
["C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","Oberstufe","E_Oberstufe"],\
["C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","Foerder","E_Foerderschule"],\
["C:"+f[1]+"Punkte_Admin/MRH_Hochschulen_2017","UNI","E_Hochschule"],\
["C:"+f[1]+"Punkte_Admin/MRH_Krankenhaus_2019",False,"E_Krankenhaus"],\
["C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","Hausarzt","E_Hausarzt"],\
["C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","Internist","E_Internist"],\
["C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","Kinderarzt","E_Kinderarzt"],\
["C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","Augenarzt","E_Augenarzt"],\
["C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","Orthopaede","E_Orthopaede"],\
["C:"+f[1]+"Punkte_Admin/MRH_Supermarkt_2019",False,"E_Supermarkt"],\
["C:"+f[1]+"Punkte_Admin/MRH_Zentrale_Orte_2016","OZ","E_OZ"],\
["C:"+f[1]+"Punkte_Admin/MRH_Zentrale_Orte_2016","MZ","E_MZ"],\
["C:"+f[1]+"Punkte_Verkehr/MRH_HstBer_2019",False,"E_Hst"],\
["C:"+f[1]+"Punkte_Verkehr/MRH_Infrastrukturen","AIRPORT","E_Flughafen"],\
["C:"+f[1]+"Punkte_Verkehr/MRH_Infrastrukturen","HBF","E_HBF"],\
["C:"+f[1]+"Punkte_Verkehr/MRH_Bahnhalte_2017",False,"E_Bahnhof"],\
["C:"+f[1]+"Punkte_Verkehr/MRH_Bahnhalte_2017","Fernbahn","E_Fernbahnhof"],\
["C:"+f[1]+"Punkte_Admin/MRH_Kita_2019",False,"E_Kita"]]




################################################
#--Testschleife--#
################################################
for i in l:
    arcpy.MakeFeatureLayer_management(i[0], "Shape")
    arcpy.Delete_management("Shape")

print "--Test erfolgreich, alle Tabellen und Datensätze vorhanden--"


################################################
#--Berechnung--#
################################################
arcpy.Delete_management("ODMATRIX")
arcpy.Delete_management("intersect")
arcpy.Delete_management("A_Shape")
arcpy.Delete_management("S_Shape")
arcpy.MakeFeatureLayer_management(A_Shape, "A_Shape")
if NMIV == True: ODLayer = arcpy.MakeODCostMatrixLayer_na(Network,"ODMATRIX",Kosten,Max_Kosten,1,[Kosten,"tFuss","Meter"],"","","","","NO_LINES")
else: ODLayer = arcpy.MakeClosestFacilityLayer_na(Network,"ODMATRIX",Kosten,"",Max_Kosten,1,[Kosten,"Meter"],"","","","","NO_LINES")

if NMIV == True: field_mappings = "Name "+A_Shape_ID+" 0; SourceID SourceID_NMIV 0;SourceOID SourceOID_NMIV 0;PosAlong PosAlong_NMIV 0;SideOfEdge SideOfEdge_NMIV 0"
else: field_mappings = "Name "+A_Shape_ID+" 0; SourceID SourceID_MIV 0;SourceOID SourceOID_MIV 0;PosAlong PosAlong_MIV 0;SideOfEdge SideOfEdge_MIV 0; Attr_tAkt tAb 1"

if NMIV == True: arcpy.AddLocations_na(ODLayer,"Origins","A_Shape",field_mappings,"","","","","","","","EXCLUDE")
else: arcpy.AddLocations_na(ODLayer,"Incidents","A_Shape",field_mappings,"","","","","","","","EXCLUDE")

r = []
desc = arcpy.Describe(Network)
attributes = desc.attributes
for i in attributes:
    if i.usageType =='Restriction':
        r.append(i.name)
o = arcpy.mapping.Layer("ODMATRIX")
p = arcpy.na.GetSolverProperties(o)
p.restrictions = r


for g in l: 
    if "C:"+f[1]+"Punkte_Admin/MRH_Apotheken_2019" not in g[0]: continue
    

    if "C:"+f[1]+"Punkte_Verkehr/MRH_HstBer_2019" == g[0] and NMIV == False: continue ##Damit fuer MIV nicht zur naechsten Hst gerechnet wird   
    if NMIV == True: Tabelle_E = g[2]+"_NMIV"
    else: Tabelle_E = g[2]+"_MIV"
    if R500 == True: Tabelle_E = Tabelle_E+"_500"
    Filter_S = g[1]
    S_Shape = g[0]

    print g[0]
    #--Generierung weiterer Parameter--#
    text = "Datum: "+str(time.localtime()[0:3])+", Modus: " +Modus+", Tabelle_A: "+A_Shape+", Tabelle_S: "+Tabelle_E+ " NMIV-Radius: "+str(Radius)+" Minuten: "+str(Max_Kosten)

    """
    Das nachstehende Vorgehen lautet wie folgt:
    1. Wird nur durchgeführt, wenn Radius vorgegeben; sont keine Nahraumberücksichtigung.
    2. Um das Start-Shape werden in einem vorgegebenen Radius alle Ziele selectiert.
    3. Diese Ziele werden dem OD-Layer hinzugefügt.
    4. Alle Startpunkte werden dem Layer hinzugefügt.
    5. Die Berechnung wird für alle durchgeführt. Max_Kosten bezeichnet die maximale Wegedauer oder Wegelänge.
    """

    print "--Beginne mit der Nahraumberechnung für: "+Tabelle_E+"--"

    #--Löschen von Bearbeitungs-Layern--#
    arcpy.Delete_management("S_Shape")
    arcpy.Delete_management("Shape")



    #--Layer aus Shape-Files erstellen--#
    if Filter_S: arcpy.MakeFeatureLayer_management(S_Shape, "S_Shape",Filter_S+">0") ##Wenn Filter, dann nur die Strukturen, wo das entsprechende Feld größer 0 ist.
    else: arcpy.MakeFeatureLayer_management(S_Shape, "S_Shape")

    #--Durchführung der OD-Berechnung--#
    ##Bereich = arcpy.SelectLayerByLocation_management("A_Shape","intersect","S_Shape",Radius)
    if NMIV == True: field_mappings = "Name "+S_Shape_ID+" 0; SourceID SourceID_NMIV 0;SourceOID SourceOID_NMIV 0;PosAlong PosAlong_NMIV 0;SideOfEdge SideOfEdge_NMIV 0; Attr_tRad # #"
    else: field_mappings = "Name "+S_Shape_ID+" 0; SourceID SourceID_MIV 0;SourceOID SourceOID_MIV 0;PosAlong PosAlong_MIV 0;SideOfEdge SideOfEdge_MIV 0; Attr_tAkt tZu 1"
    
    if NMIV == True: arcpy.AddLocations_na(ODLayer,"Destinations","S_Shape",field_mappings,"","","","","CLEAR","","","EXCLUDE")
    else: arcpy.AddLocations_na(ODLayer,"Facilities","S_Shape",field_mappings,"","","","","CLEAR","","","EXCLUDE")
    gc.collect()
    
    arcpy.na.Solve(ODLayer)

    #--Abgreifen der Ergebniswerte--#
    schleifen = (int(arcpy.GetCount_management("A_Shape").getOutput(0))/50000)+1
    schleifenstart = 0
    schleifenziel = 50000
    schleifenumfang = 50000

    for h in range(schleifen):
        if NMIV == True: Lines = arcpy.da.FeatureClassToNumPyArray("ODMATRIX\Lines",["Name", "Total_"+Kosten, "Total_Meter", "Total_tFuss"],"OriginID >="+str(schleifenstart)+"and OriginID <"+str(schleifenziel),skip_nulls=True) ##Erstelle Numpy-Array aus Ergebnis-Routen
        else: Lines = arcpy.da.FeatureClassToNumPyArray("ODMATRIX\Routes",["Name", "Total_"+Kosten, "Total_Meter"],"IncidentID >="+str(schleifenstart)+"and IncidentID <"+str(schleifenziel),skip_nulls=True)
        if len(Lines)==0:
            schleifenstart+=schleifenumfang
            schleifenziel+=schleifenumfang
            continue
        if h ==0: df = pandas.DataFrame(Lines)
        else:
            try: df = pandas.concat([df,pandas.DataFrame(Lines)])
            except: df = pandas.DataFrame(Lines)
        schleifenstart+=schleifenumfang
        schleifenziel+=schleifenumfang

    a = pandas.DataFrame(df.Name.str.split(' - ').tolist(), columns = "Start Ziel".split())
    df = pandas.DataFrame.reset_index(df) ##wichtig!!!!!
#    hh

    df[ID_S+"_y"] = a["Ziel"] ##Hänge Spalte mit den Struktur-IDs an. Name wie später bei Indikatoren
    df[ID_A+"_x"] = a["Start"] ##Hänge Spalte mit den Struktur-IDs an. Name wie später bei Indikatoren
    df[[ID_S+"_y",ID_A+"_x"]] = df[[ID_S+"_y",ID_A+"_x"]].astype(int) ##Sonst klappt das Mergen später nicht
    df["UH"] = 111 ##UH = 111 bei Anbindung direkt
    df["BH"] = 11111 ##BH = Bedienhäufigkeit ist unendlich
    df["Preis"] = 0 ##Preis = 111 bei Anbindung direkt. Fuß-/Radweg ist umsonst!
    df["ZielHstBer"] = 0
    df["StartHstBer"] = 0
    df[k_S+"_y"] = 0 ##Damit später keine 'None'-Spalte entsteht (und dann kosten + None =0)
    df[k_A+"_x"] = 0 ##Damit später keine 'None'-Spalte entsteht (und dann kosten + None =0)
    df = df.rename(columns = {'Total_'+Kosten:'Kosten'}) ##Ändere den Spaltennamen, für späteren Merge
    del df["Name"]



    print "--Nahraumberechnung erfolgreich!--"

    if "OEV" not in Modus:
        print "--Erstelle Ergebnis-Tabelle für den NMIV/IV--"
        #--HDF5-->Spalten für Ergebnistabelle--#
        Ergebnis_array = []
        if NMIV == True: Spalten = [('Start_ID', 'int32'),('Ziel_ID', 'int32'),('tRad', 'f8'),('Meter', 'f8'),('tFuss', 'f8')]
        else: Spalten = [('Start_ID', 'int32'),('Ziel_ID', 'int32'),('tAkt', 'f8'),('Meter', 'f8')]
        #--Erhebnistabelle erstellen--#
        Spalten = np.dtype(Spalten) ##Wandle Spalten-Tuple in dtype um
        data = np.array(Ergebnis_array,Spalten)
        if Tabelle_E in group5_Ergebnisse.keys():
            del group5_Ergebnisse[Tabelle_E] ##Ergebnisliste wird gelöscht falls schon vorhanden
        group5_Ergebnisse.create_dataset(Tabelle_E, data=data, dtype=Spalten, maxshape = (None,))
        Ergebnis_T = group5_Ergebnisse[Tabelle_E]
        file5.flush()

        #--Bereite Ergebnis-Tabelle vor--#
        if "Anbindung_aggregiert" in Modus:
            gb = df.groupby(ID_A+"_x")["Kosten"].idxmin()
            df = df.iloc[gb]
        if NMIV == True: df = df[[ID_A+"_x",ID_S+"_y","Kosten","Total_Meter", "Total_tFuss"]]
        else: df = df[[ID_A+"_x",ID_S+"_y","Kosten","Total_Meter"]]
        Ergebnis = np.array(df)
        Ergebnis = list(map(tuple, Ergebnis))
        size = len(Ergebnis_T)
        sizer = size+len(Ergebnis)
        Ergebnis_T.resize((sizer,))
        Ergebnis_T[size:sizer] = Ergebnis
        Ergebnis_T.attrs.create("Parameter",str(text))
        try:
            file5.flush()
        except:
            print "Fehler!!!"
            pass

    del df
    del Ergebnis
    del Ergebnis_T


file5.flush()
file5.close()

#--Fertig--#
Sekunden = int(time.clock() - start_time)

print "--Scriptdurchlauf erfolgreich nach",Sekunden,"Sekunden!--"