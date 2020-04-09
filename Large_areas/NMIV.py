# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 10:42:41 2018
Claculating travel times by bike and foot in Nds

@author: mape
"""

import psycopg2
import arcpy
import time
import pandas
import os
import gc

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Large_areas','NMIV.txt')
f = path.read_text()
f = f.split('\n')

start_time = time.clock() 
print "start script seconds: "+str(int(time.clock() - start_time))
arcpy.env.overwriteOutput = True ##delete all layers

#--Geodaten--#
Raster_o = "C:"+f[0]
Raster_d100 = "C:"+f[1]
Raster_d500 = "C:"+f[2]
Raster_d1 = "C:"+f[3]
Network = "C:"+f[4]



#--csv-files--#
csv_line = 'C:'+f[5]♣
csv_error = 'V:'+f[6]
f = open(csv_error, "w") ##clear the error csv
f.truncate()
f.close()

#--Parameter--#
Kosten = "dist_nmiv"
Max_Kosten = [3200,20500]
loop = [250,50]



###--pgadmin database--###
#--connection to database--#
pgadmin = psycopg2.connect(f[7])
pgcur = pgadmin.cursor()
#--Create table--#
#pgcur.execute('DROP TABLE IF EXISTS tmp_errbk."nds_nmiv"')
#pgcur.execute('CREATE TABLE tmp_errbk."nds_nmiv" (von integer, nach integer, meter integer, minuten_fuss integer, minuten_rad integer, bezug integer)')
#pgadmin.commit()

###--------------------------###
###--ArcGIS routing problem--###
###--------------------------###
#Raster_o = "C:\\Geodaten\\Niedersachsen.gdb\\Raster\\Heidekreis_test"
arcpy.MakeFeatureLayer_management(Raster_o, 'R100_start')
arcpy.MakeFeatureLayer_management(Raster_d100, 'R100_ziel') 
arcpy.MakeFeatureLayer_management(Raster_d500, 'R500_ziel') 
#arcpy.MakeFeatureLayer_management(Raster_d1, 'R1_ziel')  

#############
##100m loop##
#############
print "start ArcGIS OD-routing 100 meter seconds: "+str(int(time.clock() - start_time))

#--loops 100 meter--#
length = int(arcpy.GetCount_management('R100_start')[0])
print "Zeilen: "+str(length)
loops = (length/loop[0])+1
loops = range(loops)
print "Anzahl loops: "+str(len(loops))

##--Counter destinations raster--#
##Only select 100-meter destinations within certain distance to origins
##Do this every 1.000 origins for performance reasons
ni = 0
ni_counter = 1000/loop[0] ##Number of loops per 1000 origins

for i in loops:
    print "start loop "+str(i)+" seconds: "+str(int(time.clock() - start_time))
    arcpy.Delete_management("ODMATRIX")
    ODLayer = arcpy.MakeODCostMatrixLayer_na(Network,"ODMATRIX",Kosten,Max_Kosten[0],"",[Kosten,"t_fuss","t_rad"],"","","","","NO_LINES")
    
    #--add origins centroids--#
    arcpy.Delete_management("origi")
    arcpy.MakeFeatureLayer_management('R100_start', "origi","OBJECTID >"+str(i*loop[0])+" and OBJECTID <="+str((i*loop[0])+loop[0]))
    field_mappings = arcpy.na.NAClassFieldMappings(ODLayer.getOutput(0),"Origins",True,arcpy.ListFields("ODMATRIX\Origins"))   
    arcpy.AddLocations_na(ODLayer,"Origins","origi",field_mappings,"","","","","CLEAR")
    
    #--add destination centroids--#
    arcpy.Delete_management("desti")
    if i == ni:
        print "Select destinations: OBJECTID >"+str(ni*loop[0])+" and OBJECTID <="+str((ni*loop[0])+1000)
        arcpy.MakeFeatureLayer_management('R100_start', "ni_bezug","OBJECTID >"+str(ni*loop[0])+" and OBJECTID <="+str((ni*loop[0])+1000))
        arcpy.SelectLayerByLocation_management('R100_ziel', 'WITHIN_A_DISTANCE', 'ni_bezug',Max_Kosten[0])        
        ni = ni + ni_counter
        print "Next selection loop: "+str(ni)
        arcpy.Delete_management("ni_bezug")
       
    arcpy.MakeFeatureLayer_management('R100_ziel', "desti")
    arcpy.AddLocations_na(ODLayer,"Destinations","desti",field_mappings,"") 
    print "Vorbereitung Ende: "+str(int(time.clock() - start_time))  
      
    #--solving--#
    arcpy.CheckOutExtension("Network")
    try:arcpy.na.Solve(ODLayer)
    except:
        print "solver failed loop :"+str(i)
        f = open(csv_error, 'a')
        f.write("loop :"+str(i)+" 100 \n")
        f.close()
        continue
    print "solving seconds: "+str(int(time.clock() - start_time))

    ###--Data preparation--###
    #--get lines--#
    Lines = arcpy.da.FeatureClassToNumPyArray("ODMATRIX\Lines",["Name","Total_"+Kosten,"Total_t_fuss","Total_t_rad"])
    print "Num lines: "+str(len(Lines))
    Lines = pandas.DataFrame(Lines)
    a = pandas.DataFrame(Lines.Name.str.split(' - ').tolist(), columns = "Start Ziel".split())
    #Lines = pandas.DataFrame.reset_index(Lines)
    Lines["Start"] = a["Start"]
    Lines["Ziel"] = a["Ziel"]
    Lines[["Start","Ziel"]] = Lines[["Start","Ziel"]].astype(int) 
    Lines[["Total_dist_nmiv","Total_t_fuss","Total_t_rad"]] = Lines[["Total_dist_nmiv","Total_t_fuss","Total_t_rad"]].round(0).astype(int) ##rounding of numeric values
    Lines = Lines[["Start","Ziel","Total_dist_nmiv","Total_t_fuss","Total_t_rad"]] ##new ordering as in postgresql table
    Lines['bezug'] = 100 #adding cell size
    try: os.remove("C:"+f[5])
    except: pass
    Lines.to_csv("C:"+f[5], header=False, index=False)
    print "copy seconds: "+str(int(time.clock() - start_time))


    ###--saving into database--###
    #--open and write data--#
    f = open(csv_line, 'r')
    pgcur.copy_from(f, 'tmp_errbk."nds_nmiv"', sep=',')
    print "pgadmin seconds: "+str(int(time.clock() - start_time))
    pgadmin.commit()
    #--memory management--#
    del Lines, a, f
    gc.collect()
 
arcpy.Delete_management("ODMATRIX")
arcpy.Delete_management("desti")
arcpy.Delete_management("origi")

 
#############
##500m loop##
#############
print "start ArcGIS OD-routing 500 meter seconds: "+str(int(time.clock() - start_time))

#--loops 500 meter--#
loops = (length/loop[1])+1
loops = range(loops)
print "Anzahl loops: "+str(len(loops))

for i in loops:
    print "start loop (500) "+str(i)+" seconds: "+str(int(time.clock() - start_time))
    arcpy.Delete_management("ODMATRIX")
    ODLayer = arcpy.MakeODCostMatrixLayer_na(Network,"ODMATRIX",Kosten,Max_Kosten[1],"",[Kosten, "t_fuss","t_rad"],"","","","","NO_LINES")
    
    #--add origins centroids--#
    arcpy.Delete_management("centroide")
    arcpy.Delete_management("origi")
    arcpy.MakeFeatureLayer_management('R100_start', "origi","OBJECTID >"+str(i*loop[1])+" and OBJECTID <="+str((i*loop[1])+loop[1]))
    field_mappings = arcpy.na.NAClassFieldMappings(ODLayer.getOutput(0),"Origins",True,arcpy.ListFields("ODMATRIX\Origins"))
    arcpy.AddLocations_na(ODLayer,"Origins","origi",field_mappings,"","","","","CLEAR")
    
    #--add destination centroids--#
    arcpy.Delete_management("desti")
    arcpy.MakeFeatureLayer_management('R500_ziel', "desti")
    arcpy.AddLocations_na(ODLayer,"Destinations","desti",field_mappings,"")       
    print "Vorbereitung Ende: "+str(int(time.clock() - start_time)) 
          
    #--solving--#
    arcpy.CheckOutExtension("Network")
    try:arcpy.na.Solve(ODLayer)
    except:
        print "solver failed loop :"+str(i)
        f = open(csv_error, 'a')
        f.write("loop :"+str(i)+" 500 \n")
        f.close()
        continue
    print "solving seconds: "+str(int(time.clock() - start_time))

    ###--Data preparation--###
    #--get lines--#
    Lines = arcpy.da.FeatureClassToNumPyArray("ODMATRIX\Lines",["Name","Total_"+Kosten,"Total_t_fuss","Total_t_rad"],"Total_"+Kosten+" >"+str(Max_Kosten[0]-400))
    print "Num lines: "+str(len(Lines))
    Lines = pandas.DataFrame(Lines)
    a = pandas.DataFrame(Lines.Name.str.split(' - ').tolist(), columns = "Start Ziel".split())
    #Lines = pandas.DataFrame.reset_index(Lines)
    Lines["Start"] = a["Start"]
    Lines["Ziel"] = a["Ziel"]
    Lines[["Start","Ziel"]] = Lines[["Start","Ziel"]].astype(int) 
    Lines[["Total_dist_nmiv","Total_t_fuss","Total_t_rad"]] = Lines[["Total_dist_nmiv","Total_t_fuss","Total_t_rad"]].round(0).astype(int) ##rounding of numeric values
    Lines = Lines[["Start","Ziel","Total_dist_nmiv","Total_t_fuss","Total_t_rad"]] ##new ordering as in postgresql table
    Lines['bezug'] = 500 #adding cell size
    try: os.remove("C:"+f[5])
    except: pass
    Lines.to_csv("C:"+f[5], header=False, index=False)
    print "copy seconds: "+str(int(time.clock() - start_time))


    ###--saving into database--###
    #--open and write data--#
    f = open(csv_line, 'r')
    pgcur.copy_from(f, 'tmp_errbk."nds_nmiv"', sep=',')
    print "pgadmin seconds: "+str(int(time.clock() - start_time))
    pgadmin.commit()
    #--memory management--#
    del Lines, a, f
    gc.collect()    


#--create index--#
pgcur.execute('CREATE INDEX ON tmp_errbk."nds_nmiv" (von)')
pgadmin.commit()
pgcur.close()  ##pgadmin
pgadmin.close() ##pgadmin
hh
pgcur.execute('CREATE INDEX ON tmp_errbk."nds_nmiv" (nach)')
pgadmin.commit()
pgcur.execute('CREATE INDEX ON tmp_errbk."nds_nmiv" (meter)')
pgadmin.commit()
pgcur.execute('CREATE INDEX ON tmp_errbk."nds_nmiv" (minuten_fuss)')
pgadmin.commit()
pgcur.execute('CREATE INDEX ON tmp_errbk."nds_nmiv" (minuten_rad)')
pgadmin.commit()


###--end--###
pgcur.close()  ##pgadmin
pgadmin.close() ##pgadmin
print "END seconds: "+str(int(time.clock() - start_time))