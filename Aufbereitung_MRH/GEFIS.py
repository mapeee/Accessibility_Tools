# -*- coding: utf-8 -*-
"""
Created on Thu May 09 16:25:32 2019

@author: mape
"""
import arcpy
import pandas
import time
start_time = time.clock() ##Ziel: am Ende die Berechnungsdauer ausgeben
from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Aufbereitung_MRH','Gefis.txt')
f = path.read_text()
f = f.split('\n')


print("--Beginne mit der Berechnung!--")

#--Input-Parameter--#
A_Shape = "C:"+f[0]
E_Shape = "C:"+f[1]
A_Shape_ID = "ID_500"
E_Shape_ID = "ID_500"
Kosten ="Meter"
Network = "C:"+f[2]


Gruppen = [["C:"+f[4],"BundesS","fclass",0,20000,50],\
           ["C:"+f[5],"BAB","BAB",0,100000,50],\
           ["C:"+f[6],"Bahnhof","Name",0,50000,5],\
           ["C:"+f[7],"Haltestelle","NAME",0,1000,5],\
           ["C:"+f[8],"Int_Flug","name",1,150000,10],\
           ["C:"+f[8],"Reg_Flug","name",2,150000,5],\
           ["C:"+f[8],"Hafen","name",3,150000,5],\
           ["C:"+f[8],"KV_Terminal","name",4,100000,3],\
           ["C:"+f[8],"Gueter_Bhf","name",5,100000,3],\
           ["C:"+f[8],"Landepl","name",7,150000,5]]


################################################
#--Berechnung--#
################################################
arcpy.Delete_management("ODMATRIX")
arcpy.Delete_management("A_Shape")
arcpy.Delete_management("E_Shape")
ODLayer = arcpy.MakeODCostMatrixLayer_na(Network,"ODMATRIX",Kosten,10,10,[Kosten],"","","","","NO_LINES")
arcpy.MakeFeatureLayer_management(A_Shape, "A_Shape")
arcpy.MakeFeatureLayer_management(E_Shape, "E_Shape")
field_mappings = "Name "+A_Shape_ID+" 0; SourceID SourceID_MIV 0;SourceOID SourceOID_MIV 0;PosAlong PosAlong_MIV 0;SideOfEdge SideOfEdge_MIV 0"
arcpy.AddLocations_na(ODLayer,"Origins","A_Shape",field_mappings,"","","","","","","","EXCLUDE")


for typ in Gruppen:
    print(typ[1])
#    if "Lande" not in typ[1]: continue
    
    #--create new field--#    
    try: arcpy.AddField_management("E_Shape", typ[1], "TEXT", field_length=400)
    except: 
        arcpy.DeleteField_management("E_Shape", typ[1])
        arcpy.AddField_management("E_Shape", typ[1], "TEXT", field_length=400)
                   
    #--Add-locations--#
    arcpy.Delete_management("S_Shape")    
    if typ[3]!= 0 : arcpy.MakeFeatureLayer_management(typ[0], "S_Shape","Gruppe = "+str(typ[3]))
    else: arcpy.MakeFeatureLayer_management(typ[0], "S_Shape")      
    S_Shape_ID = typ[2]    
    field_mappings = "Name "+S_Shape_ID+" 0; SourceID SourceID_MIV 0;SourceOID SourceOID_MIV 0;PosAlong PosAlong_MIV 0;SideOfEdge SideOfEdge_MIV 0"
    arcpy.AddLocations_na(ODLayer,"Destinations","S_Shape",field_mappings,"","","","","CLEAR","","","EXCLUDE")
    
    #--restrictions--#
    r = []
    desc = arcpy.Describe(Network)
    attributes = desc.attributes
    for i in attributes:
        if i.usageType =='Restriction':
            r.append(i.name)
    o = arcpy.mapping.Layer("ODMATRIX")
    p = arcpy.na.GetSolverProperties(o)
    p.restrictions = r
     
    #--solver properties--#
    arcpy.CheckOutExtension("Network")
    analysis_layer = ODLayer.getOutput(0)
    solverProps = arcpy.na.GetSolverProperties(analysis_layer)
    solverProps.defaultCutoff = typ[4]
    solverProps.defaultTargetDestinationCount = typ[5]    
    arcpy.na.Solve(ODLayer)
 
    #--lines--#
    Lines = arcpy.da.FeatureClassToNumPyArray("ODMATRIX\Lines",["Name", "Total_"+Kosten],skip_nulls=True)
    df = pandas.DataFrame(Lines)
    try:a = pandas.DataFrame(df.Name.str.split(' - ').tolist(), columns = "Start Ziel".split())
    except:
        a = pandas.DataFrame(df.Name.str.split(' - ').tolist(), columns = "Start Ziel Rest".split()) ##if ' - ' in names
        del a["Rest"]
    df = pandas.DataFrame.reset_index(df) ##wichtig!!!!!
    df["Start"] = a["Start"] ##Hänge Spalte mit den Struktur-IDs an. Name wie später bei Indikatoren
    df["Ziel"] = a["Ziel"] ##Hänge Spalte mit den Struktur-IDs an. Name wie später bei Indikatoren
    df[["Start"]] = df[["Start"]].astype(int) ##Sonst klappt das Mergen später nicht
    
    #--calculating values--#
    with arcpy.da.UpdateCursor("E_Shape", [E_Shape_ID,typ[1]]) as cursor:
        for row in cursor:
            Ziele = []
            zeile = row[0]
            werte = df[df.Start == zeile]
            werte = werte[["Ziel","Total_"+Kosten]]
            if len(werte) == 0:
                row[1] = "kein Ziel erreicht"
            
            else:
                werte.drop_duplicates(subset = "Ziel",keep = 'first',inplace = True)
                for w in werte.iterrows():
                    j = w[1]["Ziel"]
                    m = w[1]["Total_Meter"]/1000
                    m = str(round(m,1))
                    j = j+" ("+m+" km)"
                    Ziele.append(j)
                Ziele = ";".join(Ziele)
                row[1] = Ziele
            cursor.updateRow(row)