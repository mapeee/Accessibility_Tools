# -*- coding: cp1252 -*-
#!/usr/bin/python
#
#Marcus September 2017
#für Python 2.7.5
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      mape
#
# Created:     13/09/2017
# Copyright:   (c) mape 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#---Vorbereitung---#
import arcpy

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Aufbereitung_MRH','Edit_results_LGV.txt')
f = path.read_text()
f = f.split('\n')

GDB = ["Bildung","Einzelhandel","Gesundheit","Raumplanung","Soziales","Verkehrsinfrastruktur"]

for work in GDB:
    arcpy.env.workspace = "C:"+f[0]+work+".gdb"
    fc = arcpy.ListFeatureClasses()
    if work != "Gesundheit": continue

    for i in fc:
        if "E_Krankenhaus_500" not in i: continue
        print(i)
        
    
        try: arcpy.AlterField_management(i,"EW","Einwohner")
        except: pass
        if "Abfahrten" in i:
            arcpy.AlterField_management(i,"Abfahrten_Dienstags","abf_di")
            arcpy.AlterField_management(i,"Abfahrten_Sonntags","abf_so")
            continue
       
        if "100" in i: raum = "100"
        elif "500" in i: raum = "500"
        else: raum = ""
        if "Foerder" in i: k = "fs"
        if "Grundsch" in i: k = "gs"
        if "Hochschu" in i: k = "hs"
        if "Oberstu" in i: k = "os"
        if "WeiterF" in i: k = "ws"
        if "Supermarkt" in i: k = "spm"
        if "Apothe" in i: k = "apo"
        if "Hausarz" in i: k = "ha"
        if "Augenar" in i: k = "aa"
        if "Internist" in i: k = "int"
        if "Kinderar" in i: k = "ka"
        if "Orthopa" in i: k = "op"
        if "Krankenha" in i: k = "kh"
        if "OZ" in i: k = "oz"
        if "MZ" in i: k = "mz"
        if "Kita" in i: k = "kita"
        if "_Bahnhof" in i: k = "bf"
        if "Fernbahn" in i: k = "fb"
        if "Airport" in i: k = "flghf"
        if "HBF" in i: k = "hbf"
        
        arcpy.AlterField_management(i,"Minuten_OEV","minoev_"+k+raum)
        arcpy.AlterField_management(i,"Minuten_Rad","minrad_"+k+raum)
        arcpy.AlterField_management(i,"Minuten_Fuss","minfuss_"+k+raum)
        arcpy.AlterField_management(i,"Minuten_Pkw","minpkw_"+k+raum)
        

        
        if "Potenzial" in i:continue
        arcpy.Delete_management("Shape")
        arcpy.MakeFeatureLayer_management (i, "Shape")
        try: arcpy.DeleteField_management(i,["MRH","EW_Zensus","EW_dezi","Start_ID","StartHst","ZielHst","ID_OEV","ID_Pkw","ID_NMIV"])
        except:pass
            
        try:
            arcpy.SelectLayerByAttribute_management("Shape", "NEW_SELECTION", ' "Minuten_OEV" > "Minuten_Fuss" and "Minuten_Fuss"<=20')
            arcpy.CalculateField_management("Shape","Minuten_OEV","Minuten_Fuss","PYTHON_9.3")
            arcpy.CalculateField_management("Shape","Umstiege","111","PYTHON_9.3")
            arcpy.CalculateField_management("Shape","Verbindungen","111","PYTHON_9.3")
        except: pass
    
        try:
            arcpy.SelectLayerByAttribute_management("Shape", "NEW_SELECTION",  "Name_OEV = '999'")
            arcpy.CalculateField_management("Shape","Name_OEV","'kein Ziel erreicht'","PYTHON_9.3")
            arcpy.SelectLayerByAttribute_management("Shape", "NEW_SELECTION",  "Name_NMIV = '999'")
            arcpy.CalculateField_management("Shape","Name_NMIV","'kein Ziel erreicht'","PYTHON_9.3")
            arcpy.SelectLayerByAttribute_management("Shape", "NEW_SELECTION",  "Name_Pkw = '999'")
            arcpy.CalculateField_management("Shape","Name_Pkw","'kein Ziel erreicht'","PYTHON_9.3")
        except: pass



print "fertig"