# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 11:47:46 2019

@author: mape
"""

import arcpy
import h5py
import pandas
import numpy as np

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','ArcGIS_processing','IV_Schleife.txt')
f = path.read_text()
f = f.split('\n')

#--Datenzugriff--#
Datenbank = "C:"+f[0]+"Diss_2019.h5"
file5 = h5py.File(Datenbank,'r+') ##HDF5-File
group5 = file5["Luftlinie_NMIV"]


#######################
#--Raumbezugssysteme--#
#######################
Bezuege = [["C:"+f[1]+"Raster\MRH_5km","ID_5000","_5km_ungew"],\
           ["C:"+f[1]+"Raster\MRH_5km_gew","ID_5000","_5km"],\
           ["C:"+f[1]+"Raster\MRH_1km","ID_1000","_1km_ungew"],\
           ["C:"+f[1]+"Raster\MRH_1km_gew","ID_1000","_1km"],\
           ["C:"+f[1]+"Raster\MRH_Gemeinden","ID_Gemeinde","_Gem_ungew"],\
           ["C:"+f[1]+"Raster\MRH_Gemeinden_gew","ID_Gemeinde","_Gem"],\
           ["C:"+f[1]+"Raster\HH_StatGeb","ID_StatGeb","_Stat_ungew"],\
           ["C:"+f[1]+"Raster\HH_StatGeb_gew","ID_StatGeb","_Stat"],\
           ["C:"+f[1]+"Raster\MRH_500","ID_500","_500_ungew"],\
           ["C:"+f[1]+"Raster\MRH_500_gew","ID_500","_500"],\
           ["C:"+f[1]+"Raster\MRH_100_EW","ID","_100"]]

################################################
#--Schleife--#
################################################

Ziele = [["C:/Geodaten/Material.gdb/Punkte_Verkehr/MRH_PR_2017",False,"E_PuR"],\
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
#for i in Ziele:
#    arcpy.MakeFeatureLayer_management(i[0], "Shape")
#    arcpy.Delete_management("Shape")

print "--Test erfolgreich, alle Tabellen und Datensätze vorhanden--"

################################################
#--Berechnung--#
################################################
for Bezug in Bezuege:
    if Bezug[2] != "_100":continue
    for Gelegenheiten in Ziele:
        Tabelle_E = Gelegenheiten[2]+"_NMIV"+Bezug[2]        
        print Tabelle_E
        
        Ziel = Gelegenheiten[0]
        Raster = Bezug[0]
        
        ##--calculation of connections--##
        Lines = arcpy.PointDistance_analysis(Raster, Ziel, "C:"+f[0]+"Default.gdb/test", 11830)            
        Lines_tab = arcpy.da.FeatureClassToNumPyArray(Lines,["OBJECTID","INPUT_FID","NEAR_FID","DISTANCE"])
        Lines_tab = pandas.DataFrame(Lines_tab)
        try: arcpy.Delete_management("C:"+f[0]+"Default.gdb\\test")
        except: pass        
 
#        field_ziel = [f.name for f in arcpy.ListFields(Ziel)]   

        Ziel_tab = pandas.DataFrame(arcpy.da.FeatureClassToNumPyArray(Ziel,["OBJECTID","ID"]))
        Raster_tab = pandas.DataFrame(arcpy.da.FeatureClassToNumPyArray(Raster,["OBJECTID",Bezug[1]]))

        ##--joins--##
        Relation = pandas.merge(Lines_tab,Ziel_tab,left_on="NEAR_FID",right_on="OBJECTID")
        Relation = pandas.merge(Relation,Raster_tab,left_on="INPUT_FID",right_on="OBJECTID")       
        Relation = Relation.drop(['OBJECTID_y', 'INPUT_FID','NEAR_FID','OBJECTID_y','OBJECTID','OBJECTID_x'],axis=1)
        Relation = Relation.rename(columns={"ID": "Ziel_ID", Bezug[1]: "Start_ID", "DISTANCE": "Meter"})
        if Bezug[2] == "_100": Relation = Relation.rename(columns={"ID_x": "Ziel_ID", "ID_y": "Start_ID"})
        Relation["Meter"]  = Relation["Meter"]*1.2 ##muessen wieder umgerechnet werden.
        Relation["tFuss"]  = Relation["Meter"]/66.6666 ##4.0 km/h
        Relation["tRad"]  = Relation["Meter"]/216.6666 ##14.2 km/h
        Relation = Relation.sort_values(['tFuss'],ascending=True).groupby('Start_ID').head(1)
        Relation = Relation.sort_values(['Start_ID'],ascending=True)
        Relation = Relation[['Start_ID', 'Ziel_ID', 'tRad','Meter','tFuss']]
        
        ##--to table--##
        x = np.array(np.rec.fromrecords(Relation.values))
        names = Relation.dtypes.index.tolist()
        x.dtype.names = tuple(names)
        
        Spalten = [('Start_ID', 'int32'),('Ziel_ID', 'int32'),('tRad', 'f8'),('Meter', 'f8'),('tFuss', 'f8')]        
        Spalten = np.dtype(Spalten) ##Wandle Spalten-Tuple in dtype um
        data = np.array(x,Spalten)
        
        
        if Tabelle_E in group5.keys():
            del group5[Tabelle_E] ##Ergebnisliste wird gelöscht falls schon vorhanden
        group5.create_dataset(Tabelle_E, data=data, dtype=Spalten)
        file5.flush()


file5.close()