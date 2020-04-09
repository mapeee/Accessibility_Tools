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
import gc
import h5py

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Large_areas','OEV.txt')
f = path.read_text()
f = f.split('\n')

start_time = time.clock()
print "start script seconds: "+str(int(time.clock() - start_time))
arcpy.env.overwriteOutput = True ##delete all layers

#--Geodaten--#
Raster_o = "C:"+f[0]

#--HDF5--#
HDF = "C:"+f[4]
group5_I = "Isochronen"
group5_A = "Anbindungen"
Text = "Analyse, 23.07.19_06 Dienstag bis 08, 2h Nachlauf, Zeitschranke 2h, ohne Fernverkehr, Quantil 20%"
I_Name = "Nds_0608"

file5 = h5py.File(HDF,'r+') ##HDF5-File
group5_I = file5[group5_I] ##Gruppe Isochronen
group5_A = file5[group5_A] ##Gruppe Anbindungen
dset_I = pandas.DataFrame(group5_I[I_Name][:])
dset_anb = pandas.DataFrame(group5_A["A_raster100_quellraster"][:])
dset_abg = pandas.DataFrame(group5_A["A_Zielraster100"][:])

##preparing egress table--#
dset_abg = dset_abg.drop('Bahn', axis=1)
dset_abg.columns = ['Ziel_ID','Ziel_Knoten_abg','dist_nmiv_abg','t_rad_abg', 't_fuss_abg']


#--csv-files--#
csv_line = 'C:'+f[1]
csv_error = 'V:'+f[2]
f = open(csv_error, "w") ##clear the error csv
f.truncate()
f.close()

#--Parameter--#
Kosten = "dist_nmiv"
Max_time = [30,90]
loop = 500

###--pgadmin database--###
#--connection to database--#
#to prevent adding _x and _y after merging
pgadmin = psycopg2.connect(f[3])
pgcur = pgadmin.cursor()

#--Create table--#
pgcur.execute('DROP TABLE IF EXISTS tmp_errbk."nds_oev_0608"')
pgcur.execute('CREATE TABLE tmp_errbk."nds_oev" (von integer, nach integer,reisezeit smallint, fahrtzeit smallint, e_zeit smallint, fuss_von smallint, fuss_nach smallint, meter_von integer, meter_nach integer, uh smallint, bh smallint, starthst integer, zielhst integer,bezug smallint)')
pgadmin.commit()



###-------------------------###
###---PT querry 100-meter---###
###-------------------------###
print "start PT calculation-routing seconds: "+str(int(time.clock() - start_time))
arr_start = arcpy.da.FeatureClassToNumPyArray(Raster_o, ('Name'))

length = len(arr_start)
print "Zeilen: "+str(length)
loops = (length/loop)+1
loops = range(loops)
print "Anzahl loops: "+str(len(loops))


for i in loops:
#    if i ==4:hh
    print "start loop "+str(i+1)+" von "+str(len(loops))+" seconds: "+str(int(time.clock() - start_time))

    #--select stops from starting point--#
    start = pandas.DataFrame(arr_start[i*loop:(i+1)*loop])
    start[["Name"]] = start[["Name"]].astype(int) ##Sonst klappt das Mergen später nicht
    df = pandas.merge(start,dset_anb,left_on="Name",right_on="Start_ID")
    df = df.drop(['Name','Bahn'], axis=1) ##delete columns Name and Bahn
    #--merging isochrones to stops--#
    df = pandas.merge(df,dset_I,left_on="Ziel_Knoten",right_on="StartHstBer")
    df = df.drop('Ziel_Knoten', axis=1)
    df['Reisezeit']=df['Fahrtzeit']
    df['Bezug'] = 100
    df.loc[:,"E_Zeit"] = df.loc[:,"t_fuss"]+df.loc[:,"E_Zeit"] ##summing access and traveltime
    df.loc[:,"Reisezeit"] = df.loc[:,"t_fuss"]+df.loc[:,"Reisezeit"] ##summing access and traveltime
    df = df[df["Reisezeit"]<=Max_time[0]]
    df = df.reset_index(drop=True)
    gb = df.groupby(["Start_ID","ZielHstBer"]) ##group for start IDs and stops near destinations
    df = df.iloc[gb["Reisezeit"].idxmin()] ##group by for minimal traveltime
    df = df.reset_index(drop=True)
    #-- mergin egress to table--#
    df = pandas.merge(df,dset_abg,left_on="ZielHstBer",right_on="Ziel_Knoten_abg")
    df.loc[:,"E_Zeit"] = df.loc[:,"E_Zeit"]+df.loc[:,"t_fuss_abg"] ##summing egress and traveltime
    df.loc[:,"Reisezeit"] = df.loc[:,"Reisezeit"]+df.loc[:,"t_fuss_abg"] ##summing egress and traveltime
    df = df[df["Reisezeit"]<=Max_time[0]]
    df = df.drop(['t_rad','t_rad_abg','Ziel_Knoten_abg'], axis=1) ##delete columns Name and Bahn
    df = df.reset_index(drop=False)
    gb = df.groupby(["Start_ID","Ziel_ID"]) ##group for start IDs and dest IDs
    df = df.iloc[gb["Reisezeit"].idxmin()] ##group by for minimal traveltime
    df = df.reset_index(drop=True)

    ###--Data preparation--###
    df = df.drop("index",axis=1)
    df = df[['Start_ID', 'Ziel_ID','Reisezeit', 'Fahrtzeit', 'E_Zeit', 't_fuss','t_fuss_abg','dist_nmiv','dist_nmiv_abg','UH','BH','StartHstBer','ZielHstBer','Bezug']] ##changing order of columns
    df = df[df['StartHstBer']!=df['ZielHstBer']]
    df[['dist_nmiv']] = df[['dist_nmiv']].round(0).astype(int)
    df[['dist_nmiv_abg']] = df[['dist_nmiv_abg']].round(0).astype(int)
    df[['t_fuss']] = df[['t_fuss']].round(0).astype(int)
    df[['t_fuss_abg']] = df[['t_fuss_abg']].round(0).astype(int)
    df[['Fahrtzeit']] = df[['Fahrtzeit']].round(0).astype(int)
    df[['E_Zeit']] = df[['E_Zeit']].round(0).astype(int)
    df[['Reisezeit']] = df[['Reisezeit']].round(0).astype(int)
    df.to_csv("C:"+f[1], header=False, index=False)
    ###--saving into database--###
    #--open and write data--#
    f = open(csv_line, 'r')
    pgcur.copy_from(f, 'tmp_errbk."nds_oev"', sep=',')
    pgadmin.commit()
    #--memory management--#
    del df,gb,f
    gc.collect()

###-------------------------###
###---PT querry 500-meter---###
###-------------------------###
dset_abg = pandas.DataFrame(group5_A["A_Zielraster500"][:])
dset_abg = dset_abg.drop('Bahn', axis=1)
dset_abg.columns = ['Ziel_ID','Ziel_Knoten_abg','dist_nmiv_abg','t_rad_abg', 't_fuss_abg']


print "start PT calculation-routing (500 meter) seconds: "+str(int(time.clock() - start_time))
arr_start = arcpy.da.FeatureClassToNumPyArray(Raster_o, ('Name'))

length = len(arr_start)
loops = (length/loop)+1
loops = range(loops)


for i in loops:
    print "start loop (500) "+str(i+1)+" von "+str(len(loops))+" seconds: "+str(int(time.clock() - start_time))

    #--select stops from starting point--#
    start = pandas.DataFrame(arr_start[i*loop:(i+1)*loop])
    start[["Name"]] = start[["Name"]].astype(int) ##Sonst klappt das Mergen später nicht
    df = pandas.merge(start,dset_anb,left_on="Name",right_on="Start_ID")
    df = df.drop(['Name','Bahn'], axis=1) ##delete columns Name and Bahn

    #--merging isochrones to stops--#
    df = pandas.merge(df,dset_I,left_on="Ziel_Knoten",right_on="StartHstBer")
    df = df.drop('Ziel_Knoten', axis=1)
    df['Reisezeit']=df['Fahrtzeit']
    df['Bezug'] = 500
    df.loc[:,"E_Zeit"] = df.loc[:,"t_fuss"]+df.loc[:,"E_Zeit"] ##summing access and traveltime
    df.loc[:,"Reisezeit"] = df.loc[:,"t_fuss"]+df.loc[:,"Reisezeit"] ##summing access and traveltime
    df = df[df["Reisezeit"]<=Max_time[1]]
    df = df.reset_index(drop=True)
    gb = df.groupby(["Start_ID","ZielHstBer"]) ##group for start IDs and stops near destinations
    df = df.iloc[gb["Reisezeit"].idxmin()] ##group by for minimal traveltime
    df = df.reset_index(drop=True)

    #-- mergin egress to table--#
    df = pandas.merge(df,dset_abg,left_on="ZielHstBer",right_on="Ziel_Knoten_abg")
    df.loc[:,"E_Zeit"] = df.loc[:,"E_Zeit"]+df.loc[:,"t_fuss_abg"] ##summing egress and traveltime
    df.loc[:,"Reisezeit"] = df.loc[:,"Reisezeit"]+df.loc[:,"t_fuss_abg"] ##summing egress and traveltime
    df = df[df["Reisezeit"]<=Max_time[1]]
    df = df.drop(['t_rad','t_rad_abg','Ziel_Knoten_abg'], axis=1) ##delete columns Name and Bahn
    df = df.reset_index(drop=False)
    gb = df.groupby(["Start_ID","Ziel_ID"]) ##group for start IDs and dest IDs
    df = df.iloc[gb["Reisezeit"].idxmin()] ##group by for minimal traveltime
    df = df.reset_index(drop=True)
    df = df[df["Reisezeit"]>=Max_time[0]-4]

    ###--Data preparation--###
    df = df.drop("index",axis=1)
    df = df[['Start_ID', 'Ziel_ID','Reisezeit', 'Fahrtzeit', 'E_Zeit', 't_fuss','t_fuss_abg','dist_nmiv','dist_nmiv_abg','UH','BH','StartHstBer','ZielHstBer','Bezug']] ##changing order of columns
    df = df[df['StartHstBer']!=df['ZielHstBer']]
    df[['dist_nmiv']] = df[['dist_nmiv']].round(0).astype(int)
    df[['dist_nmiv_abg']] = df[['dist_nmiv_abg']].round(0).astype(int)
    df[['t_fuss']] = df[['t_fuss']].round(0).astype(int)
    df[['t_fuss_abg']] = df[['t_fuss_abg']].round(0).astype(int)
    df[['Fahrtzeit']] = df[['Fahrtzeit']].round(0).astype(int)
    df[['E_Zeit']] = df[['E_Zeit']].round(0).astype(int)
    df[['Reisezeit']] = df[['Reisezeit']].round(0).astype(int)
    df.to_csv("C:"+f[1], header=False, index=False)

    ###--saving into database--###
    #--open and write data--#
    f = open(csv_line, 'r')
    pgcur.copy_from(f, 'tmp_errbk."nds_oev"', sep=',')
    pgadmin.commit()
    #--memory management--#
    del df,gb,f
    gc.collect()


#--create index--#
pgcur.execute('CREATE INDEX ON tmp_errbk."nds_oev" (von)')
pgadmin.commit()
pgcur.close()  ##pgadmin
pgadmin.close() ##pgadmin


###--end--###
pgcur.close()  ##pgadmin
pgadmin.close() ##pgadmin
print "END seconds: "+str(int(time.clock() - start_time))