#-------------------------------------------------------------------------------
# Name:        Skript, um aus Struktur-Gruppen einzelne Files zu machen.
# Purpose:
#
# Author:      mape
#
# Created:     19/05/2016
# Copyright:   (c) mape 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
import h5py
import numpy

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Aufbereitung_MRH','Reservate.txt')
f = path.read_text()
f = f.split('\n')

#--Input--#
Datenbank = "C:"+f[0]
Group ="Ergebnisse"
TabelleHDF5 = "E_Biosphere"
Pfad_GIS = "C:"+f[1]
GIS_Layer = "C:"+f[2]


Gruppen = \
[[[1],"Kloster_Rehna"],\
[[2],"Bahnhof_Burgsee"],\
[[3],"GRENZHUS_Schlagsdorf"],\
[[4],"Schloss_Wedendorf"],\
[[5],"Apmanns_Design"],\
[[6],"Schmiede_Radsack"],\
[[7],"Fliesenmuseum_Boizenburg"],\
[[8],"Amt_Biosphaerenreservat"],\
[[9],"Festung_Doemitz"],\
[[10],"Doemitzer_Hafen"],\
[[11],"Infozentrum_Bioshaerenreservat"],\
[[12],"Schloss_Dreiluetzow"],\
[[13],"Metallgestaltung"],\
[[14],"Biber_Tours"],\
[[15],"Reederei_Andreas_Heckert"],\
[[16],"Schwerin_Schloss_Ludwigslust"],\
[[17],"Alexander_von_Stenglin"],\
[[18],"Landgestuet_Redefin"],\
[[19],"Schwechower_Obstbrennerei"],\
[[20],"Toepferhof_Hohenwoos"],\
[[21],"VIELANKER_Brauhaus"],\
[[22],"alpincenter"],\
[[23],"Mehl_Welten_Museum"],\
[[24],"PAHLHUUS"],\
[[25],"Archaeologisches_Zentrum_Hitzacker"],\
[[26],"Wendland_Therme"],\
[[27],"Amtsturm_Museum"],\
[[28],"Wanderparkplatz_Darchau"],\
[[29],"Grenzlandmuseum"],\
[[30],"Rundlingsmuseum"],\
[[31],"Nemitzer_Heide"],\
[[32],"Findlingspark_Clenze"],\
[[33],"Gutshof_Gross_Zecher"],\
[[34],"Kulturzentrum_Priesterkate"]]




###########################################################################
#--Verbindung zur HDF-5 Datenbank--#
###########################################################################
#--Datenzugriff--#
file5 = h5py.File(Datenbank,'r+') ##HDF5-File
group5 = file5[Group]

###########################################################################
#--Berechnung--#
###########################################################################
dset = group5[TabelleHDF5]
for i in Gruppen:
    print(i)
    dset_gruppe = dset[numpy.in1d(dset["Start_ID"],i[0][0])]
    a = numpy.array(dset_gruppe)
    if len(a) == 0:continue
#    arcpy.da.NumPyArrayToTable(a,Pfad_GIS+"/"+i[1]+"_Tab")
#    GIS_Ergebnisse = "C:"+f[1]+"\\"+i[1]
#    
#    try: arcpy.CopyFeatures_management(GIS_Layer,GIS_Ergebnisse)
#    except:
#        arcpy.Delete_management(GIS_Ergebnisse)
#        arcpy.CopyFeatures_management(GIS_Layer,GIS_Ergebnisse)
#        
#    arcpy.JoinField_management(GIS_Ergebnisse,"ID",Pfad_GIS+"/"+i[1]+"_Tab","Ziel_ID",["Reisezeit","UH"])
#    arcpy.Delete_management(Pfad_GIS+"/"+i[1]+"_Tab")
#    with arcpy.da.UpdateCursor(GIS_Ergebnisse, "UH") as cursor:
#        for row in cursor:
#            if row[0] is None: cursor.deleteRow()
#    with arcpy.da.UpdateCursor(GIS_Ergebnisse, "UH") as cursor:
#        for row in cursor:
#            if row[0] == 111:
#                row[0]=0
#            cursor.updateRow(row)
#
#    arcpy.CheckOutExtension("Spatial")
#    arcpy.NaturalNeighbor_3d(GIS_Ergebnisse,"Reisezeit","C:"+f[1]+"\\"+i[1]+"_iso",200)
#    arcpy.NaturalNeighbor_3d(GIS_Ergebnisse,"UH","C:"+f[1]+"\\"+i[1]+"_uh",200)
#    arcpy.CheckInExtension("Spatial")
#    
    ##MXD Reisezeit##
    mxd = arcpy.mapping.MapDocument(r"V:"+f[3])
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    addLayer = arcpy.mapping.Layer("C:"+f[1]+"\\"+i[1]+"_iso")
    arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
    layer = arcpy.mapping.ListLayers(mxd, "*", df)
    layer[1].definitionQuery = "ID = "+str(i[0][0])
    layer[1].name = i[1].replace("_"," ")
    df.extent = layer[7].getExtent()
    arcpy.ApplySymbologyFromLayer_management(layer[7],layer[5])
    arcpy.mapping.ExportToPDF(mxd, r"C:"+f[1]+"\\"+i[1]+"_iso.pdf")
    arcpy.mapping.RemoveLayer(df, layer[7])
#    arcpy.Delete_management("C:"+f[1]+"\\"+i[1]+"_iso")
    
    del mxd
    
    ##MXD Umstiege##
    mxd = arcpy.mapping.MapDocument(r"V:"+f[4])
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    addLayer = arcpy.mapping.Layer("C:"+f[1]+"\\"+i[1]+"_uh")
    arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
    layer = arcpy.mapping.ListLayers(mxd, "*", df)
    layer[1].definitionQuery = "ID = "+str(i[0][0])
    layer[1].name = i[1].replace("_"," ")
    df.extent = layer[7].getExtent()
    arcpy.ApplySymbologyFromLayer_management(layer[7],layer[5])
    arcpy.mapping.ExportToPDF(mxd, r"C:"+f[1]+"\\"+i[1]+"_uh.pdf")
    arcpy.mapping.RemoveLayer(df, layer[7])
#    arcpy.Delete_management("C:"+f[1]+"\\"+i[1]+"_uh")
    
    del mxd
    
file5.flush()
file5.close()