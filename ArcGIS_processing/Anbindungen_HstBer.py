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

head = 1
b = True


Datenbank = "C:"+f[0]+"Diss_2019.h5"
#--Datenzugriff--#
file5 = h5py.File(Datenbank,'r+') ##HDF5-File
group5 = file5["Anbindungen"]

HstBer = "C:"+f[1]+"Punkte_Verkehr\\MRH_HstBer_2019"
HstBer_tab = arcpy.da.FeatureClassToNumPyArray(HstBer,["OBJECTID","NO","Bahn"])
HstBer_tab = pandas.DataFrame(HstBer_tab)


Ziele = [["C:"+f[1]+"Punkte_Admin/MRH_Apotheken_2019",False,"A_Apotheken"],\
["C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019",["Grundsch","WeiterF","Oberstufe","Foerder"],"A_Schulen"],\
["C:"+f[1]+"Punkte_Admin/MRH_Hochschulen_2017",["UNI"],"A_Uni"],\
["C:"+f[1]+"Punkte_Admin/MRH_Krankenhaus_2019",False,"A_Krankenhaus"],\
["C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019",["Hausarzt","Internist","Kinderarzt","Augenarzt","Orthopaede"],"A_Aerzte"],\
["C:"+f[1]+"Punkte_Admin/MRH_Supermarkt_2019",False,"A_Supermarkt"],\
["C:"+f[1]+"Punkte_Admin/MRH_Zentrale_Orte_2016",["OZ","MZ"],"A_Zentren"],\
["C:"+f[1]+"Punkte_Verkehr/MRH_Infrastrukturen",["AIRPORT","HBF"],"A_Infrastrukturen"],\
["C:"+f[1]+"Punkte_Verkehr/MRH_Bahnhalte_2017",["Fernbahn"],"A_Bahnhof"],\
["C:"+f[1]+"Punkte_Admin/MRH_Kita_2019",False,"A_Kita"]]


if b == True:
    Ziele = [["C:"+f[1]+"Raster\MRH_5km","ID_5000","A_Raster_5_ungew"],\
               ["C:"+f[1]+"Raster\MRH_5km_gew","ID_5000","A_Raster_5"],\
               ["C:"+f[1]+"Raster\MRH_1km","ID_1000","A_Raster_1_ungew"],\
               ["C:"+f[1]+"Raster\MRH_1km_gew","ID_1000","A_Raster_1"],\
               ["C:"+f[1]+"Raster\MRH_Gemeinden","ID_Gemeinde","A_Gemeinden_ungew"],\
               ["C:"+f[1]+"Raster\MRH_Gemeinden_gew","ID_Gemeinde","A_Gemeinden"],\
               ["C:"+f[1]+"Raster\HH_StatGeb","ID_StatGeb","A_StatGeb_ungew"],\
               ["C:"+f[1]+"Raster\HH_StatGeb_gew","ID_StatGeb","A_StatGeb"],\
               ["C"+f[1]+"Raster\MRH_500","ID_500","A_Raster_500_ungew"],\
               ["C:"+f[1]+"Raster\MRH_500_gew","ID_500","A_Raster_500"],\
               ["C:"+f[1]+"Raster\MRH_100_EW","ID","A_Raster_100_EW"]]

for Gelegenheiten in Ziele:
    z = Gelegenheiten[0]
    
    if b == True:fields = ["OBJECTID",Gelegenheiten[1]]    
    else: 
        fields = ["OBJECTID","ID"]
        f = Gelegenheiten[1]
        
    if f: fields = fields+f    
    Ziel_tab = arcpy.da.FeatureClassToNumPyArray(z,fields)
    Ziel_tab = pandas.DataFrame(Ziel_tab)
    Tabelle_A = Gelegenheiten[2]
    if head == 1: Tabelle_A = Tabelle_A+"_1"
    
    print Tabelle_A
    
    ##--calculation of connections--##
    Lines = arcpy.PointDistance_analysis(z, HstBer, "C:"+f[0]+"Default.gdb/test", 1100)            
    Lines_tab = arcpy.da.FeatureClassToNumPyArray(Lines,["OBJECTID","INPUT_FID","NEAR_FID","DISTANCE"])
    Lines_tab = pandas.DataFrame(Lines_tab)
    try: arcpy.Delete_management("C:"+f[0]+"Default.gdb\\test")
    except: pass
    
    ##--joins--##
    Relation = pandas.merge(Lines_tab,HstBer_tab,left_on="NEAR_FID",right_on="OBJECTID")
    Relation = pandas.merge(Relation,Ziel_tab,left_on="INPUT_FID",right_on="OBJECTID")
    Relation = Relation.drop(['OBJECTID_y', 'INPUT_FID','NEAR_FID','OBJECTID_y','Bahn','OBJECTID','OBJECTID_x'],axis=1)
    if b == True: Relation = Relation.rename(columns={"NO": "Ziel_Knoten", Gelegenheiten[1]: "Start_ID", "DISTANCE": "Meter"})
    else: Relation = Relation.rename(columns={"NO": "Ziel_Knoten", "ID": "Start_ID", "DISTANCE": "Meter"})
    Relation["Meter"]  = Relation["Meter"]*1.2 ##muessen wieder umgerechnet werden.
    Relation["tFuss"]  = Relation["Meter"]/66.6666
    Relation = Relation.sort_values(['tFuss'],ascending=True).groupby('Start_ID').head(head)
    Relation = Relation.sort_values(['Start_ID'],ascending=True)
    
    ##--to table--##
    x = np.array(np.rec.fromrecords(Relation.values))
    names = Relation.dtypes.index.tolist()
    x.dtype.names = tuple(names)
    
    Spalten = [('Start_ID', 'int32'),('Ziel_Knoten', 'int32'),('tFuss', 'f8'),('Meter', 'f8')]
    if f:
        for i in f: Spalten.append((i.encode('ascii'),'int32'))
    
    Spalten = np.dtype(Spalten) ##Wandle Spalten-Tuple in dtype um
    data = np.array(x,Spalten)
    if Tabelle_A in group5.keys():
        del group5[Tabelle_A] ##Ergebnisliste wird gelöscht falls schon vorhanden
    group5.create_dataset(Tabelle_A, data=data, dtype=Spalten)
    file5.flush()



file5.close()