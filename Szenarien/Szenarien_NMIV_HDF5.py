# -*- coding: cp1252 -*-
#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:        HDF-Vergleich
# Purpose:     Script zum Vergleich unterschiedlicher Szenarien
#
# Author:      mape
#
# Created:     13/10/2016
# Copyright:   (c) mape 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import h5py
import numpy as np

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','Szenarien','Szenarien_NMIV_HDF5.txt')
f = path.read_text()
f = f.split('\n')

#--Input--#
Datenbank = "V:"+f[0]
##Datenbank = "V:"+f[1]
Group = "E_Varianten"
##Group = "LDN"
##Var = ["K_Elmshorn_Hamburg"]
##Var = ["E_Ostkreis_Nullfall","E_Ostkreis_V1"]
##Var = ["K_Elmshorn_Hamburg",\
##"K_Ahrensburg_Sued",\
##"K_Winsen",\
##"Stade_Harburg",\
##"K_Finkenwerder",\
##"Norderstedt_Bad_Bramstedt",\
##"Uetersen_Tornesch",\
##"Stockelsdorf_Sankt_Hubertus",\
##"Israeldorf_Bunte_Kuh",\
##"Stockelsdorf_Schlutup",\
##"Bad_Schwartau_Sankt_Hubertus",\
##"Wedel_Variante",\
##"K_Bergedorf_Geesthacht",\
##"Neumuenster_Bad_Bramstedt",\
##"K_Ost_Reinbek",\
##"Wismar_Schwerin",\
##"Wismar_Grevesmuehlen",\
##"K_Hafen",\
##"K_Schenefeld",\
##"K_Wedel",\
##"K_Norderstedt",\
##"Lueneburg_Winsen",\
##"Amelinghausen_Bleckede",\
##"K_Buchholz_Tostedt",\
##"K_Buxtehude",\
##"K_Harburg_Elbbruecken",\
##"Hanstedt_Bispingen",\
##"K_Quickborn",\
##"K_Ahrensburg_Nord",\
##"K_Ost_Glinde",\
##"K_Ost_Barsbuettel",\
##"Bad_Oldesloe_Ahrensburg",\
##"K_Ost"]

Var = ["K_Ost_Reinbek",\
"K_Ost_Glinde",\
"K_Ost_Barsbuettel"]



ID = "ID"
##ID = "Start_ID"

###########################################################################
#--Verbindung zur HDF-5 Datenbank--#
###########################################################################
#--Datenzugriff--#
file5 = h5py.File(Datenbank,'r+') ##HDF5-File
group5 = file5[Group]

for i in Var:
    print i
    Nullfall = "Nullfall_"+str(i)
    Szenario = "Variante_"+str(i)
##    Nullfall = Var[0]
##    Szenario = Var[1]
    Tabelle_E = "Vergleich_"+str(i)
##    Tabelle_E = "E_Ostkreis_Vergleich"
    Ergebnis_array = []

    dset_N = group5[Nullfall]
    dset_V = group5[Szenario]

    #--erzeuge Liste mit zu berechnenden Indikatoren--"
    Spaltennamen = list(dset_N.dtype.names)
    Spaltennamen.remove(ID) ##Wird nicht benötigt


    ###########################################################################
    #--Beginne die Berechnung--#
    ###########################################################################
    Raster = np.concatenate((dset_N[ID],dset_V[ID])) ##erstmal alle verbinden. Fall Werte in N oder V einzigartig sind.
    Raster = np.unique(Raster) ##Es wird für jeden einzigartigen Wert die Berechnung durchgeführt
    for Zelle in Raster:
        N = dset_N[dset_N[ID]==Zelle]
        V = dset_V[dset_V[ID]==Zelle]
        Zeile = []
        Zeile.append(Zelle)
        for Indikator in Spaltennamen:
            if len(N) == 0: ##Falls es im Nufall noch keine Anbindung gab
                Zeile.append(1234) #absolut
                Zeile.append(1234) #relativ
                continue
            if len(V) == 0: ##Falls es in der Variante keine Anbindung mehr gibt
                Zeile.append(-1234)
                Zeile.append(-1234)
                continue
            Zeile.append((V[Indikator]-N[Indikator])[0]) #absolut
            try: ##Falls ein Indikator-Wert = 0, dann Division durch 0 nicht möglichi.
                if V[Indikator][0] < N[Indikator][0]: ##Um prozentuale Abnahme zu berechnen
                    Zeile.append(-1*(1-float(V[Indikator][0])/N[Indikator][0])) #relativ
                else:
                    Zeile.append(float(V[Indikator][0])/N[Indikator][0]) #relativ
            except:
                Zeile.append(float(0))

        Ergebnis_array.append(tuple(Zeile))


    ###########################################################################
    #--Erstelle Ergebnis-Tabelle--#
    ###########################################################################
    Spalten = [(ID,'int32')]
    for Name in Spaltennamen:
        Spalten.append((Name+"abs",'<f8'))
        Spalten.append((Name+"rel",'<f8'))

    Spalten = np.dtype(Spalten) ##Wandle Spalten-Tuple in dtype um


    data = np.array(Ergebnis_array,Spalten)
    if Tabelle_E in group5.keys():
        del group5[Tabelle_E] ##Ergebnisliste wird gelöscht falls schon vorhanden
    group5.create_dataset(Tabelle_E, data=data, dtype=Spalten, maxshape = (None,))
    Ergebnis_T = group5[Tabelle_E]
    file5.flush()

###########
#--Ende--#
###########
file5.flush()
file5.close()
hh