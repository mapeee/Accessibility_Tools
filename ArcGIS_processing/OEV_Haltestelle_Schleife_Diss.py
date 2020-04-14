# -*- coding: cp1252 -*-
#!/usr/bin/python
#Skript, mit dem Potenziale von bestimmten Einrichtungen aus berechnet werden.
#Marcus September 2015
#für Python 2.7.5


#---Vorbereitung---#
import time
import h5py
import numpy as np
import pandas
start_time = time.clock() ##Ziel: am Ende die Berechnungsdauer ausgeben

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','ArcGIS_processing','IV_Schleife.txt')
f = path.read_text()
f = f.split('\n')

print "--Dieses Skript ermoeglicht die Potenzialberechnung von ausgewaehlten Standorten.--"
print "--Beginne mit der Berechnung!--"


##Single?
s = False


#--Eingabe-Parameter--#
Modus = "OEV;Anbindung_aggregiert;keine_IsoChronen"
Datenbank = "C:"+f[0]+"MRH_OEV_2019.h5"
Datenbank_erg = "C:"+f[0]+"Diss_2019.h5"
#Tabelle_A = "A_Raster_100"
Knoten_A = "Ziel_Knoten"
#Tabelle_S = "A_Potenzial_500"
Knoten_S = "Ziel_Knoten"
#IsoChronen_Name = "MRH_0608"
Group = "Anbindungen"
ID_A = "Start_ID"
ID_S = "Start_ID"
#Tabelle_E = "E_Potenziale_OEV_100"
k_A = "tFuss"
k_S = "tFuss"

Zeitschranke = "120;20;20;0"
Zeitbezug = "Matrize_Abfahrt"
#Filter_S = False
Group_Iso = "Isochronen"
Filter_Gruppe = False
Group_Erg = "Anbindung_OEV"




#######################
#--Raumbezugssysteme--#
#######################
Bezuege = [["A_Raster_5_ungew","ID_5000","_5km_ungew"],\
           ["A_Raster_5","ID_5000","_5km"],\
           ["A_Raster_1_ungew","ID_1000","_1km_ungew"],\
           ["A_Raster_1","ID_1000","_1km"],\
           ["A_Gemeinden_ungew","ID_Gemeinde","_Gem_ungew"],\
           ["A_Gemeinden","ID_Gemeinde","_Gem"],\
           ["A_StatGeb_ungew","ID_StatGeb","_Stat_ungew"],\
           ["A_StatGeb","ID_StatGeb","_Stat"],\
           ["A_Raster_500_ungew","ID_500","_500_ungew"],\
           ["A_Raster_500","ID_500","_500"],\
           ["A_Raster_100_EW","ID","_100"]]


################################################
#--Gelegenheiten--#
################################################

l = [["A_Apotheken",False,"E_Apotheken","MRH_0912"],\
["A_Schulen","Grundsch","E_Grundschulen","MRH_0608"],\
["A_Schulen","WeiterF","E_WeiterFSchule","MRH_0608"],\
["A_Schulen","Oberstufe","E_Oberstufe","MRH_0608"],\
["A_Schulen","Foerder","E_Foerderschule","MRH_0608"],\
["A_Uni","UNI","E_Hochschule","MRH_0912"],\
["A_Krankenhaus",False,"E_Krankenhaus","MRH_0912"],\
["A_Aerzte","Hausarzt","E_Hausarzt","MRH_0912"],\
["A_Aerzte","Internist","E_Internist","MRH_0912"],\
["A_Aerzte","Kinderarzt","E_Kinderarzt","MRH_0912"],\
["A_Aerzte","Augenarzt","E_Augenarzt","MRH_0912"],\
["A_Aerzte","Orthopaede","E_Orthopaede","MRH_0912"],\
["A_Supermarkt",False,"E_Supermarkt","MRH_0912"],\
["A_Zentren","OZ","E_OZ","MRH_0912"],\
["A_Zentren","MZ","E_MZ","MRH_0912"],\
["A_Infrastrukturen","AIRPORT","E_Flughafen","MRH_0608"],\
["A_Infrastrukturen","HBF","E_HBF","MRH_0608"],\
["A_Bahnhof",False,"E_Bahnhof","MRH_0608"],\
["A_Bahnhof","Fernbahn","E_Fernbahnhof","MRH_0608"],\
["A_Kita",False,"E_Kita","MRH_0608"]]

#--Generierung weiterer Parameter--#
Modus = Modus.split(";")
Zeitschranke = Zeitschranke.split(";")

#--Überführung Länge in Zeit--#
Schranke_A = Zeitschranke[1]
Schranke_S = Zeitschranke[2]


###########################################################################
#--Funktionen--#
###########################################################################
def Iso_Auswahl (dset_A,Knoten__A,dset_S,Knoten__S,Bezug_1,Bezug_2,Iso_I,Kosten_maximal,Modus_):

    #1. Auswahl jener HstBer die überhaupt in den Rasterzellen und Zielen vertreten sind
    Raster_HstBer = np.unique(dset_A[Knoten__A]) ##Array mit allen HstBer an den Rasterzelle
    Ziele_HstBer = np.unique(dset_S[Knoten__S]) ##Erzeuge Liste mit eindueitgen HstBereichen der Strukturen

    if True in map(lambda element_: 'Anbindung' in element_, Modus_):
        header = 20
    else:
        header = 10000
    schleifenstart = 0
    schleifenziel = 1000000 ##eine Million
    schleifenumfang = 1000000 ##eine Million
    schleifen = (len(Iso_I)/schleifenziel)+1 ##Da abgerundet wird und dann oft schleifen = 0

    #2. IsoChronen werden aufgrund der Größe in Schichten bzw. Schleifen zerlegt
    for k in range(schleifen):
        iso_schleife = Iso_I[schleifenstart:schleifenziel]
        iso_schleife = iso_schleife[np.in1d(iso_schleife[Bezug_1].ravel(), Ziele_HstBer)] ##Wähle nur die IsoChronen, wo auch die ZielHstBer enthalten sind.
        iso_schleife = iso_schleife[np.in1d(iso_schleife[Bezug_2].ravel(), Raster_HstBer)] ##Wähle nur die IsoChronen, wo auch die RastHstBer enthalten sind.
        iso_schleife = np.array(iso_schleife)
        iso_schleife = pandas.DataFrame(iso_schleife)
        iso_schleife = iso_schleife[iso_schleife["Kosten"]<=int(Kosten_maximal)] ##Wähle nur die Verbindungen von den Raster-HstBer, die innerhalb der Zeitschranke liegen.
        iso_schleife = iso_schleife.sort_values([Bezug2,"Kosten"]) ##Erst sortieren
        iso_schleife = iso_schleife.groupby(Bezug2).head(header).reset_index(drop=True) ##Dann jeweils die ersten zwanzig auswählen

        if k==0: Iso_f = iso_schleife
        else: Iso_f = pandas.concat([Iso_f,iso_schleife])

        schleifenstart+=schleifenumfang
        schleifenziel+=schleifenumfang

    return Iso_f ##Pandas Dataframe


###########################################################################
#--Vorbereitung Anbindungsberechnung--#
###########################################################################
if True in map(lambda element: 'Anbindung' in element, Modus):
    Modus.append("Anbindung")
    Berechnung = ("StartHst","Ziel_ID", "ZielHst", "Reisezeit", "UH", "Anbindungszeit", "Abgangszeit","BH")



###########################################################################
#--Verbindung zur HDF-5 Datenbank--#
###########################################################################
#--Datenzugriff--#
file5 = h5py.File(Datenbank,'r+') ##HDF5-File
file5_erg = h5py.File(Datenbank_erg,'r+') ##HDF5-File
group5 = file5_erg[Group]
group5_Iso = file5[Group_Iso]
group5_Ergebnisse = file5_erg[Group_Erg]


for Bezug in Bezuege:
    for Einrichtung in l:
        
        ##--Parameter--##
        Tabelle_A = Bezug[0]      
        Tabelle_S = Einrichtung[0]
        if s == True:
            Tabelle_A = Bezug[0]+"_1"   
            Tabelle_S = Einrichtung[0]+"_1"
        
        IsoChronen_Name = Einrichtung[3]     
        Tabelle_E = Einrichtung[2]+"_OEV"+Bezug[2]    
        if s == True: Tabelle_E = Tabelle_E+"_1"
        Filter_S = Einrichtung[1]
                
        print "--beginne mit: "+Bezug[0]+" und "+Einrichtung[2]+"--"
        text = "Datum: "+str(time.localtime()[0:3])+", Modus: " +str(Modus)+"; Zeitbezug: "+ Zeitbezug+"; Zeitschranken: "+str(Zeitschranke)+", IsoName: "+IsoChronen_Name+", Tabelle_A: "+Tabelle_A+", Tabelle_S: "+Tabelle_S ##Für das Ergebnis-Attribut
        

        #--Zugriff auf HstBer der Einrichtungen--#
        dsetA = group5[Tabelle_A]
        dsetA = dsetA[dsetA[k_A]<int(Schranke_A)]
        
        #--Zugriff auf HstBer der Strukturen--#
        dsetS = group5[Tabelle_S]
        dsetS = dsetS[dsetS[k_S]<int(Schranke_S)]
        if Filter_S:dsetS = dsetS[dsetS[Filter_S]>0] ##Wähle nur die Anbindungen, an denen auch wirklich die gewünschten Strukturen sind.


        ###########################################################################
        #--HDF5 --> Erstelle Ergebnistabelle--#
        ###########################################################################
        #--HDF5-->Spalten für Ergebnistabelle--#
        Ergebnis_array = []
        Spalten = [('Start_ID', '<f8')]
        """
        1. Für jede Berechnungsart soll eine Spalte angelegt werden.
        2. Bei der Berechnung von gewichteten Potenzialen soll außerdem der Gewichtungsfaktor angehängt werden.
        """
        for i in Berechnung: Spalten.append((i.encode('ascii'),'int32'))
        
        #--Erhebnistabelle erstellen--#
        Spalten = np.dtype(Spalten) ##Wandle Spalten-Tuple in dtype um
        data = np.array(Ergebnis_array,Spalten)
        if Tabelle_E in group5_Ergebnisse.keys():
            del group5_Ergebnisse[Tabelle_E] ##Ergebnisliste wird gelöscht falls schon vorhanden
        group5_Ergebnisse.create_dataset(Tabelle_E, data=data, dtype=Spalten, maxshape = (None,))
        Ergebnis_T = group5_Ergebnisse[Tabelle_E]
        file5.flush()


        ###########################################################################
        #--Berechnung der Indikatoren (Vorbereitung)--#
        ###########################################################################
        dataS = pandas.DataFrame(dsetS)
        IsoChronen = group5_Iso[IsoChronen_Name]
        text = text.split(IsoChronen_Name)
        text = text[0]+IsoChronen_Name+" ("+IsoChronen.attrs.values()[0]+")"+text[1]

        ###########################################################################
        #--Berechnung der Anbindungen--#
        ###########################################################################
#        print "--Beginne mit der Indikatorberechnung--"



        if Filter_Gruppe:
            Gruppen = np.unique(dsetS[Filter_Gruppe]) ##Liste aller Gruppen-Codes
        else:
            Gruppen = [1] ##Um ohne Filter dennoch ein iterierbares Objekt zu erhalten
    
        dataA = pandas.DataFrame(dsetA)
    
        if Zeitbezug == "Ankunft" or Zeitbezug == "Matrize_Abfahrt": ##Wenn der Zeitbezug Ankunft ist, dann sind die Strukturen/Ziele auch die ZielHstber. Bei Abfahrt, sind es die StartHstBereiche.
            Bezug1 = "ZielHstBer"
            Bezug2 = "StartHstBer"
        else:
            Bezug1 = "StartHstBer"
            Bezug2 = "ZielHstBer"
    
        for i, m in enumerate(Gruppen):
    
            if Filter_Gruppe:
                dataG = dataS[dataS[Filter_Gruppe]==m] ##wähle nur die Strukturen aus, die in der entsprechenden Gruppe sind
                Gruppen_Auswahl = dsetS[dsetS[Filter_Gruppe]==m]
                Iso_p = Iso_Auswahl(dsetA,Knoten_A,Gruppen_Auswahl,Knoten_S,Bezug1,Bezug2,IsoChronen,Zeitschranke[0],Modus)
                print "--Beginne mit der Berechnung aggregierter Anbindungen fuer Gruppe "+str(m)+" mit "+str(len(np.unique(dataG[ID_S])))+" Strukturgroessen--"
                IsoS = pandas.merge(dataG,Iso_p,left_on=Knoten_S,right_on=Bezug1)
    
            else:
                dataG = dataS ##wähle nur die Strukturen aus, die in der entsprechenden Gruppe sind
                Iso_p = Iso_Auswahl(dsetA,Knoten_A,dsetS,Knoten_S,Bezug1,Bezug2,IsoChronen,Zeitschranke[0],Modus)
                print "--Beginne mit der Berechnung aggregierter Anbindungen fuer "+str(len(np.unique(dsetS[ID_S])))+" Strukturgroessen--"
                IsoS = pandas.merge(dataG,Iso_p,left_on=Knoten_S,right_on=Bezug1)
    
    
            IsoS["Kosten"] = IsoS[k_S]+IsoS["Kosten"]
            gb = IsoS.groupby(Bezug2) ##Group über HstBer
            IsoS = IsoS.iloc[gb["Kosten"].idxmin()] ##Index der Minimalen Kostenwerte; Dann slicing über diese IDs
    
            IsoA = pandas.merge(dataA,IsoS,left_on=Knoten_A,right_on=Bezug2)    
            IsoA["Kosten"] = IsoA[k_A+"_x"]+IsoA["Kosten"]
            gb = IsoA.groupby(ID_A+"_x")["Kosten"].idxmin()
            IsoA = IsoA.iloc[gb]
    
    
            #--Befülle HDF5-Ergebnistabelle--#
            """
            Wenn der Zeitbezug Abfahrt (nicht Ankunft) ist, dann bezieht sich dies auf die Abfahrt an der Struktur. Entsprechend sind die Rasterzellen dann die Zielpunkte.
            Entsprechend müssen hier die Spalten jeweils vertauscht werden.
            """
            if Zeitbezug == "Ankunft" or "Matrize_Abfahrt":
                Ergebnis = IsoA[["Start_ID_x","StartHstBer","Start_ID_y", "ZielHstBer", "Kosten", "UH", k_A+"_x", k_S+"_y","BH"]]
            else:
                Ergebnis = IsoA[["Start_ID_y","ZielHstBer","Start_ID_x", "StartHstBer", "Kosten", "UH", k_A+"_x", k_S+"_y","BH"]]
            Ergebnis.loc[Ergebnis["ZielHstBer"]==Ergebnis["StartHstBer"],"UH"] = 111 ##Wenn StarHstBer = ZielHstBer bedeutet das einen Direktweg, damit UH = 111
            Ergebnis.loc[Ergebnis["ZielHstBer"]==Ergebnis["StartHstBer"],"BH"] = 111 ##Wenn StarHstBer = ZielHstBer bedeutet das einen Direktweg, damit BH = 111
            Ergebnis = np.array(Ergebnis)
            Ergebnis = list(map(tuple, Ergebnis))
            size = len(Ergebnis_T)
            sizer = size+len(Ergebnis)
            Ergebnis_T.resize((sizer,))
            Ergebnis_T[size:sizer] = Ergebnis
    
    
            #--HDF5-Text zu Tabellenbeschreibung--#
            Ergebnis_T.attrs.create("Parameter",str(text))
            file5_erg.flush()
            


#--Fertig--#
Sekunden = int(time.clock() - start_time)
file5_erg.flush()
file5_erg.close()

print "--Scriptdurchlauf erfolgreich nach",Sekunden,"Sekunden!--"