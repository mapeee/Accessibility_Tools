# -*- coding: cp1252 -*-
#!/usr/bin/python
#Skript, mit dem der Datenaustausch mit HDF5-Datenbanken gelingt.
#Marcus September 2015
#für Python 2.7.5
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      mape
#
# Created:     15/06/2017
# Copyright:   (c) mape 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#---Vorbereitung---#
import arcpy
import h5py
import pandas
import gc
import numpy as np

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Aufbereitung_MRH','HDF5_to_Shape.txt')
f = path.read_text()
f = f.split('\n')

#--HDF5--#
HDF5_OEV = "C:"+f[0]+"MRH_OEV_2019.h5"
HDF5_IV = "C:"+f[0]+"MRH_IV_2019.h5"
file5_OEV = h5py.File(HDF5_OEV,'r+') ##HDF5-File
file5_IV = h5py.File(HDF5_IV,'r+') ##HDF5-File
group5_OEV = file5_OEV["Ergebnisse"]
group5_IV = file5_IV["Ergebnisse"]

for Raster_500 in [1,0]:
    ################################################
    #--Inhalte--#
    ################################################
    if Raster_500 == 1:
        GIS_Layer = "C:"+f[1]+"Raster/MRH_LGV_500"
        """schleife Anfang"""
        l = [["E_Bahnhof_500","C:"+f[1]+"Punkte_Verkehr/MRH_Bahnhalte_2017","E_Bahnhof_NMIV_500","E_Bahnhof_MIV_500"],\
        ["E_Fernbahn_500","C:"+f[1]+"Punkte_Verkehr/MRH_Bahnhalte_2017","E_Fernbahnhof_NMIV_500","E_Fernbahnhof_MIV_500"],\
        ["E_Grundschulen_500","C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","E_Grundschulen_NMIV_500","E_Grundschulen_MIV_500"],\
        ["E_WeiterF_500","C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","E_WeiterFSchule_NMIV_500","E_WeiterFSchule_MIV_500"],\
        ["E_Oberstufe_500","C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","E_Oberstufe_NMIV_500","E_Oberstufe_MIV_500"],\
        ["E_Foerder_500","C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","E_Foerderschule_NMIV_500","E_Foerderschule_MIV_500"],\
        ["E_Hochschule_500","C:"+f[1]+"Punkte_Admin/MRH_Hochschulen_2017","E_Hochschule_NMIV_500","E_Hochschule_MIV_500"],\
        ["E_Krankenhaus_500","C:"+f[1]+"Punkte_Admin/MRH_Krankenhaus_2019","E_Krankenhaus_NMIV_500","E_Krankenhaus_MIV_500"],\
        ["E_Apotheken_500","C:"+f[1]+"Punkte_Admin/MRH_Apotheken_2019","E_Apotheken_NMIV_500","E_Apotheken_MIV_500"],\
        ["E_Hausarzt_500","C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","E_Hausarzt_NMIV_500","E_Hausarzt_MIV_500"],\
        ["E_Internist_500","C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","E_Internist_NMIV_500","E_Internist_MIV_500"],\
        ["E_Kinderarzt_500","C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","E_Kinderarzt_NMIV_500","E_Kinderarzt_MIV_500"],\
        ["E_Augenarzt_500","C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","E_Augenarzt_NMIV_500","E_Augenarzt_MIV_500"],\
        ["E_Orthopaede_500","C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","E_Orthopaede_NMIV_500","E_Orthopaede_MIV_500"],\
        ["E_Kita_500","C:"+f[1]+"Punkte_Admin/MRH_Kita_2019","E_Kita_NMIV_500","E_Kita_MIV_500"],\
        ["E_Airport_500","C:"+f[1]+"Punkte_Verkehr/MRH_Infrastrukturen","E_Flughafen_NMIV_500","E_Flughafen_MIV_500"],\
        ["E_HBF_500","C:"+f[1]+"Punkte_Verkehr/MRH_Infrastrukturen","E_HBF_NMIV_500","E_HBF_MIV_500"],\
        ["E_Supermarkt_500","C:"+f[1]+"Punkte_Admin/MRH_Supermarkt_2019","E_Supermarkt_NMIV_500","E_Supermarkt_MIV_500"],\
        ["E_OZ_500","C:"+f[1]+"Punkte_Admin/MRH_Zentrale_Orte_2016","E_OZ_NMIV_500","E_OZ_MIV_500"],\
        ["E_MZ_500","C:"+f[1]+"Punkte_Admin/MRH_Zentrale_Orte_2016","E_MZ_NMIV_500","E_MZ_MIV_500"]]
        """schleife Ende"""
        
    else:
        GIS_Layer = "C:"+f[1]+"Raster/MRH_LGV_100"
        """schleife Anfang"""
        l = [["E_Bahnhof","C:"+f[1]+"Punkte_Verkehr/MRH_Bahnhalte_2017","E_Bahnhof_NMIV","E_Bahnhof_MIV"],
        ["E_Fernbahn","C:"+f[1]+"Punkte_Verkehr/MRH_Bahnhalte_2017","E_Fernbahnhof_NMIV","E_Fernbahnhof_MIV"],
        ["E_Grundschulen","C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","E_Grundschulen_NMIV","E_Grundschulen_MIV"],
        ["E_WeiterF","C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","E_WeiterFSchule_NMIV","E_WeiterFSchule_MIV"],
        ["E_Oberstufe","C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","E_Oberstufe_NMIV","E_Oberstufe_MIV"],
        ["E_Foerder","C:"+f[1]+"Punkte_Admin/MRH_Schulen_2019","E_Foerderschule_NMIV","E_Foerderschule_MIV"],
        ["E_Hochschule","C:"+f[1]+"Punkte_Admin/MRH_Hochschulen_2017","E_Hochschule_NMIV","E_Hochschule_MIV"],
        ["E_Krankenhaus","C:"+f[1]+"Punkte_Admin/MRH_Krankenhaus_2019","E_Krankenhaus_NMIV","E_Krankenhaus_MIV"],
        ["E_Apotheken","C:"+f[1]+"Punkte_Admin/MRH_Apotheken_2019","E_Apotheken_NMIV","E_Apotheken_MIV"],
        ["E_Hausarzt","C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","E_Hausarzt_NMIV","E_Hausarzt_MIV"],
        ["E_Internist","C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","E_Internist_NMIV","E_Internist_MIV"],
        ["E_Kinderarzt","C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","E_Kinderarzt_NMIV","E_Kinderarzt_MIV"],
        ["E_Augenarzt","C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","E_Augenarzt_NMIV","E_Augenarzt_MIV"],
        ["E_Orthopaede","C:"+f[1]+"Punkte_Admin/MRH_Aerzte_2019","E_Orthopaede_NMIV","E_Orthopaede_MIV"],
        ["E_Kita","C:"+f[1]+"Punkte_Admin/MRH_Kita_2019","E_Kita_NMIV","E_Kita_MIV"],
        ["E_Airport","C:"+f[1]+"Punkte_Verkehr/MRH_Infrastrukturen","E_Flughafen_NMIV","E_Flughafen_MIV"],
        ["E_HBF","C:"+f[1]+"Punkte_Verkehr/MRH_Infrastrukturen","E_HBF_NMIV","E_HBF_MIV"],
        ["E_Supermarkt","C:"+f[1]+"Punkte_Admin/MRH_Supermarkt_2019","E_Supermarkt_NMIV","E_Supermarkt_MIV"],
        ["E_OZ","C:"+f[1]+"Punkte_Admin/MRH_Zentrale_Orte_2016","E_OZ_NMIV","E_OZ_MIV"],
        ["E_MZ","C:"+f[1]+"Punkte_Admin/MRH_Zentrale_Orte_2016","E_MZ_NMIV","E_MZ_MIV"]]
        """schleife Ende"""

    ################################################
    #--Testschleife--#
    ################################################
    for i in l:
        group5_OEV[i[0]]
        group5_IV[i[2]]
        group5_IV[i[3]]
        arcpy.MakeFeatureLayer_management(i[1], "Shape")
        arcpy.Delete_management("Shape")
        arcpy.da.FeatureClassToNumPyArray(i[1],["ID","Name"])
        print "--Test erfolgreich, alle Tabellen und Datensätze vorhanden--"


    ################################################
    #--Berechnung--#
    ################################################
    for i in l:
        
        if "E_Hochschule" not in i[0]:continue
        
        if Raster_500 == 1: GIS_Ergebnisse = "C:"+f[2]+i[0]
        else: GIS_Ergebnisse = "C:"+f[2]+i[0]+"_100"
        HDF5_Tabelle = i[0]
        Layer_Name = i[1]
        HDF5_Tabelle_NMIV = i[2]
        HDF5_Tabelle_MIV = i[3]
        Spalte_Name = "Name"

        print "--Beginne mit: "+HDF5_Tabelle+"--"

        #--Copy Feature--#
        print "--Kopiere GIS-Layer--"
        try: arcpy.CopyFeatures_management(GIS_Layer,GIS_Ergebnisse)
        except:
            arcpy.Delete_management(GIS_Ergebnisse)
            arcpy.CopyFeatures_management(GIS_Layer,GIS_Ergebnisse)

        #--Zugriff auf HDF5-Tabellen--#
        dset_OEV = pandas.DataFrame(np.array(group5_OEV[HDF5_Tabelle]))
        dset_NMIV = pandas.DataFrame(np.array(group5_IV[HDF5_Tabelle_NMIV]))
        dset_MIV = pandas.DataFrame(np.array(group5_IV[HDF5_Tabelle_MIV]))

        #--Zugriff auf Strukturdaten--#
        dset_Struktur = pandas.DataFrame(arcpy.da.FeatureClassToNumPyArray(Layer_Name,["ID","Name"]))
        dset_NMIV.dtypes
        #--Bearbeiten OEV-Tabelle und MIV-Tabelle--#
        dset_OEV[["Start_ID"]] = dset_OEV[["Start_ID"]].astype(int) ##Sonst klappt der Merge nicht

        #--Merge--#
        dset = pandas.merge(dset_OEV,dset_NMIV,how="outer",on="Start_ID")
        dset = pandas.merge(dset,dset_MIV,how="outer",on="Start_ID")

        #--Merge Namen Zieleinrichtungen--#
        dset = pandas.merge(dset,dset_Struktur,left_on="Ziel_ID_x",right_on="ID",how="left") ##OEV
        dset = pandas.merge(dset,dset_Struktur,left_on="Ziel_ID_y",right_on="ID",how="left")##NMIV
        dset = pandas.merge(dset,dset_Struktur,left_on="Ziel_ID",right_on="ID",how="left")##MIV
        del dset["ID_x"]
        del dset["ID_y"]
        del dset["ID"]

        #--Felder umbenennen--#
        dset = dset.rename(columns = {'Reisezeit':'Minuten_OEV','tFuss':'Minuten_Fuss','tRad':'Minuten_Rad','tAkt':'Minuten_Pkw'})
        dset = dset.rename(columns = {'Ziel_ID_x':'ID_OEV','Ziel_ID_y':'ID_NMIV','Ziel_ID':'ID_Pkw'})
        dset = dset.rename(columns = {'Meter_x':'Meter_NMIV','Meter_y':'Meter_Pkw'})
        dset = dset.rename(columns = {'UH':'Umstiege','BH':'Verbindungen'})
        dset = dset.rename(columns = {'Name_x':'Name_OEV','Name_y':'Name_NMIV','Name':'Name_Pkw'})

        #--Null-Values und Feldtyp
        dset.fillna(999, inplace=True)
        for n in dset.dtypes.index.tolist():
            try:dset[[n]] = dset[[n]].astype(int)
            except:pass

        #--Pandas in GIS--#
        x = np.array(dset.values)
        names = ", ".join(dset.dtypes.index.tolist())
        dtypes = 'int32, int32, int32, int32, int32, int32, int32, int32, int32, int32, int32, int32, int32, int32, int32, int32, <U80, <U80, <U80'
        x = np.core.records.fromarrays(x.transpose(), names=names, formats = dtypes)
    ##    x = np.array(x)
        try: arcpy.da.NumPyArrayToTable(x,"C:"+f[1]+""+HDF5_Tabelle)
        except:
            arcpy.Delete_management("C:"+f[1]+""+HDF5_Tabelle)
            arcpy.da.NumPyArrayToTable(x,"C:"+f[1]+""+HDF5_Tabelle)

        #--JOIN--#
        print "--Joine die Felder an den GIS-Layer--"
        if Raster_500 == 1: injoinField = "ID_500"
        else:injoinField = "ID"
        joinTable = "C:"+f[1]+""+HDF5_Tabelle
        outjoinField = "Start_ID"
        fieldList = dset.dtypes.index.tolist()

        arcpy.JoinField_management (GIS_Ergebnisse, injoinField, joinTable, outjoinField, fieldList)

        arcpy.Delete_management("C:"+f[1]+""+HDF5_Tabelle)

        Shape = GIS_Ergebnisse
        print Shape
        gc.collect()

        #--alle--#
        update = arcpy.da.UpdateCursor(Shape,["Start_ID","Minuten_Pkw","Meter_Pkw","Name_Pkw","ID_Pkw","Minuten_OEV","Name_OEV","ID_OEV",\
        "Minuten_Rad","Meter_NMIV","Name_NMIV","ID_NMIV","ZielHst","StartHst","Anbindungszeit","Abgangszeit","Umstiege","Verbindungen","Minuten_Fuss"],"Minuten_Pkw is null")
        for m in update:
            m[0] = 999
            m[1] = 999
            m[3] = "nicht erreicht"
            m[4] = 999
            m[5] = 999
            m[6] = "nicht erreicht"
            m[7] = 999
            m[8] = 999
            m[9] = 999
            m[10] = "nicht erreicht"
            m[11] = 999
            m[12] = 999
            m[13] = 999
            m[14] = 999
            m[15] = 999
            m[16] = 999
            m[17] = 999
            m[18] = 999
            update.updateRow(m)

print "--FERTIG--"
file5_OEV.close()
file5_IV.close()