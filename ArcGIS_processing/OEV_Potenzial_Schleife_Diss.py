# -*- coding: cp1252 -*-
#!/usr/bin/python
#Skript, mit dem Potenziale von bestimmten Einrichtungen aus berechnet werden.
#Marcus September 2015
#für Python 2.7.5

"""
Die Idee ist die Folgende:
pass
"""

#---Vorbereitung---#
import time
import h5py
import numpy as np
import pandas
import gc
start_time = time.clock() ##Ziel: am Ende die Berechnungsdauer ausgeben

from pathlib import Path
path = Path.home() / 'python32' / 'python_dir.txt'
f = open(path, mode='r')
for i in f: path = i
path = Path.joinpath(Path(r'C:'+path),'Accessibility_Tools','ArcGIS_processing','IV_Schleife.txt')
f = path.read_text()
f = f.split('\n')

print "--Dieses Skript ermöglicht die Potenzialberechnung von ausgewählten Standorten.--"
print "--Beginne mit der Berechnung!--"


Bezuege = [["A_Raster_5_ungew","ID_5000","_5km_ungew"],\
           ["A_Raster_5","ID_5000","_5km"],\
           ["A_Raster_1_ungew","ID_1000","_1km_ungew"],\
           ["A_Raster_1","ID_1000","_1km"],\
           ["A_Gemeinden_ungew","ID_Gemeinde","_Gem_ungew"],\
           ["A_Gemeinden","ID_Gemeinde","_Gem"],\
           ["A_StatGeb_ungew","ID_StatGeb","_Stat_ungew"],\
           ["A_StatGeb","ID_StatGeb","_Stat"],\
           ["A_Raster_500_ungew","ID_500","_500_ungew"]]


#--Eingabe-Parameter--#
Modus = "OEV;Erreichbarkeiten;keine_IsoChronen"
Datenbank = "C:"+f[0]+"MRH_OEV_2019.h5"
Datenbank_erg = "C:"+f[0]+"Diss_2019.h5"
Tabelle_A = "A_Raster_100"
Knoten_A = "Ziel_Knoten"
Tabelle_S = "A_Potenzial_500"
Knoten_S = "Ziel_Knoten"
Strukturgr = "AP;Freizeit;EW_Zensus;Versorgung"
Netz = ""
IsoChronen_Name = "MRH_0608"
Berechnung = "AP__Sum;AP__Expo;AP__UH0;Freizeit__Sum;Freizeit__Expo;Freizeit__UH0;EW_Zensus__Sum;EW_Zensus__Expo;EW_Zensus__UH0;Versorgung__Sum;Versorgung__Expo;Versorgung__UH0"
Group = "Anbindungen"
ID_A = "Start_ID"
ID_S = "Start_ID"
#Tabelle_E = "E_Potenziale_OEV_100"
k_A = "tFuss"
k_S = "tFuss"
kmh_A = int(0)
kmh_S = int(0)
Nachlauf = int(2)##für VISUM-Isochronen
Stunden = ""
sumfak = "15;30;60"
potfak = "-0.05;-0.02"
##22 bis 29 NMIV
##22 bis 29 NMIV
Zeitschranke = "120;20;20;0"
Zeitbezug = "Matrize_Abfahrt"
Filter_S = False
Group_Iso = "Isochronen"
Filter_Gruppe = False
Group_Erg = "Potenzial_OEV"



#--Generierung weiterer Parameter--#
Modus = Modus.split(";")
Berechnung = Berechnung.split(";")
Strukturgr = Strukturgr.split(";")
potfak = potfak.replace(",",";") ##Damit das auch für "," funktioniert.
potfak = potfak.split(";")
sumfak = sumfak.replace(",",";") ##Damit das auch für "," funktioniert.
sumfak = sumfak.split(";")
Stunden = Stunden.replace(",",";")
Stunden = Stunden.split(";")
Zeitschranke = Zeitschranke.split(";")


#--Überführung Länge in Zeit--#
if kmh_A > 0: ##für die Auswahl der HstBer über Schranke
    Schranke_A = (kmh_A/3.6*60)*int(Zeitschranke[1]) ##Schranke_A = Ernfernung (in Metern) bei x kmh und y Zeitschranke
else:
    Schranke_A = Zeitschranke[1]
if kmh_S > 0: ##für die Auswahl der HstBer über Schranke
    Schranke_S = (kmh_S/3.6*60)*int(Zeitschranke[2])
else:
    Schranke_S = Zeitschranke[2]

#--Anzahl der Einzelindikatoren--#
Indikatoren = len(Berechnung)+((len(potfak)-1)*len(Strukturgr))+((len(sumfak)-1)*len(Strukturgr)) ##-1, da einmal schon in Berechnung drinnen ist


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
#--Verbindung zur HDF-5 Datenbank--#
###########################################################################
#--Datenzugriff--#
file5 = h5py.File(Datenbank,'r+') ##HDF5-File
file5_erg = h5py.File(Datenbank_erg,'r+') ##HDF5-File
group5 = file5[Group]
group5_Iso = file5[Group_Iso]
group5_Ergebnisse = file5_erg[Group_Erg]


for Bezug in Bezuege:
    print "--beginne mit: "+Bezug[0]+"--"
    text = "Datum: "+str(time.localtime()[0:3])+", Modus: " +str(Modus)+"; Zeitschranken: "+str(Zeitschranke)+", IsoName: "+IsoChronen_Name+", Tabelle_A: "+Bezug[0]+", Tabelle_S: "+Tabelle_S+ ", Berechnungen: "+str(Berechnung) ##Für das Ergebnis-Attribut
    Tabelle_E = "E_Potenzial_OEV" + Bezug[2]

    #--Zugriff auf HstBer der Einrichtungen--#
    dsetA = group5[Bezug[0]]
    dsetA = dsetA[dsetA[k_A]<int(Schranke_A)]
    if kmh_A >0:
        dsetA[k_A] = dsetA[k_A]/(kmh_A/3.6*60) ##Um aus den Metern eine Zeit in Minuten zu machen
    
    #--Zugriff auf HstBer der Strukturen--#
    dsetS = group5[Tabelle_S]
    dsetS = dsetS[dsetS[k_S]<int(Schranke_S)]
    if Filter_S:
        dsetS = dsetS[dsetS[Filter_S]>0] ##Wähle nur die Anbindungen, an denen auch wirklich die gewünschten Strukturen sind.
    if kmh_S >0:
        dsetS[k_S] = dsetS[k_S]/(kmh_S/3.6*60) ##Um aus den Metern eine Zeit in Minuten zu machen
    
    
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
    for i in Berechnung:
        if i[-4:] == "Expo": ##wenn Expo in den letzten vier Stellen, dann zusätzlich auch Potenzial-Faktor.
            for e in potfak:
                e = str(e.split(".")[1])
                if len(e)==2:
                    e+="0"
                Spalten.append(((i+e).encode('ascii'),'int32'))
    
        elif i[-3:] == "Sum": ##wenn Sum in den letzten drei Stellen, dann zusätzlich auch Maximalzeit anhängen.
            for e in sumfak:
                Spalten.append(((i+e).encode('ascii'),'int32'))
    
        else:
            Spalten.append((i.encode('ascii'),'int32'))
    
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
    
    if "keine_IsoChronen" in Modus:
        text = text.split(IsoChronen_Name)
        text = text[0]+IsoChronen_Name+" ("+IsoChronen.attrs.values()[0]+")"+text[1]
    
    
    ###########################################################################
    #--Erreichbarkeiten--#
    ###########################################################################
    """
    2. Auswahl der zu betrachtenden Isochronen über die Funktion
    3. Merge der Startpunkte an diese Isochronen. Anschl. Addition von Kosten (Reisezeit) und Anbindungszeit
    4. Anschließend wird für jede Start_ID die minimale Reisezeit zu jeder Zielhaltestelle ermittelt.
    5. Merge der Zielpunkte an diese Isochronen. Anschl. Addition von Kosten (Reisezeit) und Abgangszeit
    6. Anschließend wird für jede Start_ID die minimale Reisezeit zu jeder Ziel_ID ermittelt.
    """
    
    
    if "Erreichbarkeiten" in Modus:
        if Zeitbezug == "Ankunft" or Zeitbezug == "Matrize_Abfahrt": ##Wenn der Zeitbezug Ankunft ist, dann sind die Strukturen/Ziele auch die ZielHstber. Bei Abfahrt, sind es die StartHstBereiche.
            Bezug1 = "ZielHstBer"
            Bezug2 = "StartHstBer"
        else:
            Bezug1 = "StartHstBer"
            Bezug2 = "ZielHstBer"
    
        #0.
        a = np.unique(dsetA["Start_ID"])
        schleifenstart = 0
        schleifenziel = 100 ##eine Million
        schleifenumfang = 100 ##eine Million
        schleifen = (len(a)/schleifenziel)+1 ##Da abgerundet wird und dann oft schleifen = 0
        #1.
        Iso = Iso_Auswahl(dsetA,Knoten_A,dsetS,Knoten_S,Bezug1,Bezug2,IsoChronen,Zeitschranke[0],Modus)
        gc.collect()
        #2.
        for schleife in range(schleifen):
            print "--Beginne mit Schleife "+str(schleife+1)+" von "+str(schleifen)+"--"
            dsetA_s = a[schleifenstart:schleifenziel]
            dsetA_s = dsetA[np.in1d(dsetA["Start_ID"],dsetA_s)]
            schleifenstart+=schleifenumfang
            schleifenziel+=schleifenumfang
    
            #3.
            dataA = pandas.DataFrame(dsetA_s)
            dataiso = pandas.merge(dataA,Iso,left_on=Knoten_A,right_on="StartHstBer")
            dataiso.loc[:,"Kosten"] = dataiso.loc[:,k_A]+dataiso.loc[:,"Kosten"] ##mit .loc, da von pandas so vorgegeben
            dataiso = dataiso[dataiso["Kosten"]<=(int(Zeitschranke[0]))-4] ##-4 um den array hier schonmal klein zu halten. Später kommt ja noch die Abgangszeit dazu.
            dataiso = dataiso.reset_index(drop=True)
            #4.
            try:
                gb = dataiso.groupby([ID_A,"ZielHstBer"]) ##Group über ZielHstBer
                dataiso = dataiso.iloc[gb["Kosten"].idxmin()] ##Index der Minimalen Kostenwerte; Dann slicing über diese IDs
                dataiso = dataiso.reset_index(drop=True)
                #5.
                dataS_in = dataS.loc[dataS["Ziel_Knoten"].isin(dataiso["ZielHstBer"])] ##Erstmal nur die Anbindungen auswählen, die anschließend überhaupt gemerged werden.
                dataiso = pandas.merge(dataiso,dataS_in,left_on="ZielHstBer",right_on="Ziel_Knoten")
                gc.collect()
                dataiso.loc[:,"Kosten"] = dataiso.loc[:,k_S+"_y"]+dataiso.loc[:,"Kosten"]
                #6.
                gb = dataiso.groupby([ID_A+"_x",ID_S+"_y"])
                dataiso = dataiso.iloc[gb["Kosten"].idxmin()] ##Index der Minimalen Kostenwerte; Dann slicing über diese IDs
                Einrichtungen = np.unique(dsetA_s[ID_A])
                print "--Insgesamt werden Indikatoren  für: "+str(len(Einrichtungen))+" Punkte berechnet--"
            except:
                try:
                    dataiso = dataiso[::2] ##wähle nur die gerade Indexe aus
                    dataiso = dataiso.reset_index(drop=True)
                    gb = dataiso.groupby([ID_A,"ZielHstBer"]) ##Group über ZielHstBer
                    dataiso = dataiso.iloc[gb["Kosten"].idxmin()] ##Index der Minimalen Kostenwerte; Dann slicing über diese IDs
                    dataiso = dataiso.reset_index(drop=True)
                    #5.
                    dataS_in = dataS.loc[dataS["Ziel_Knoten"].isin(dataiso["ZielHstBer"])] ##Erstmal nur die Anbindungen auswählen, die anschließend überhaupt gemerged werden.
                    dataiso = pandas.merge(dataiso,dataS_in,left_on="ZielHstBer",right_on="Ziel_Knoten")
                    gc.collect()
                    dataiso.loc[:,"Kosten"] = dataiso.loc[:,k_S+"_y"]+dataiso.loc[:,"Kosten"]
                    #6.
                    gb = dataiso.groupby([ID_A+"_x",ID_S+"_y"])
                    dataiso = dataiso.iloc[gb["Kosten"].idxmin()] ##Index der Minimalen Kostenwerte; Dann slicing über diese IDs
                    Einrichtungen = np.unique(dsetA_s[ID_A])
                    print "--Insgesamt werden Indikatoren  für: "+str(len(Einrichtungen))+" (gerade)Punkte berechnet--"
                except:
                    print "--Fehler in Schleife "+str(schleife+1)+"--"
                    continue
            for i in Einrichtungen:
                t1 = time.clock()
                ##arcpy.AddMessage("--Berechne Indikatoren für ID "+str(i)+"--") ##+1, da sonst Beginn bei 0
                Ergebnis = []
                Ergebnis.append(i)
                IsoS = dataiso[dataiso[ID_A+"_x"]==i]
                IsoS = IsoS.reset_index(drop=False)
                try: IsoS = IsoS.rename(columns = {"EW_Zensus_y":"EW_Zensus"})
                except: pass
    
                #--Berechne die Indikatorwerte--#
                for e in Berechnung:
                    Column = e.split("__")[0] ##Um wieder den eigentlichen Namen der Strukturspalte zu erhalten!!
    
                    if e[-3:] == "Sum":
                        for n in sumfak:
                            Indi = IsoS[IsoS["Kosten"]<=int(n)]
                            Wert = Indi[Column].sum()
                            Ergebnis.append(Wert)
    
                    elif e[-4:] == "Expo":
                        for n in potfak:
                            n = float(n)
                            Wert = round(sum(np.exp(IsoS["Kosten"]*n) * IsoS[Column]))
                            Ergebnis.append(Wert)
    
                    elif e[-3:] == "UH0":
                        Indi = IsoS[IsoS["UH"]==0]
                        Wert = Indi[Column].sum()
                        Ergebnis.append(Wert)
    
                    elif e[-3:] == "UH1":
                        Indi = IsoS[IsoS["UH"]<2]
                        Wert = Indi[Column].sum()
                        Ergebnis.append(Wert)
    
                    elif e[-6:] == "direkt":
                        Indi = IsoS[IsoS["UH"]==111]
                        Wert = Indi[Column].sum()
                        Ergebnis.append(Wert)
    
                    elif e[-3:] == "BH3":
                        Indi = IsoS[IsoS["BH"]>=3]
                        Wert = Indi[Column].sum()
                        Ergebnis.append(Wert)
    
                    elif e[-4:] == "BH10":
                        Indi = IsoS[IsoS["BH"]>=10]
                        Wert = Indi[Column].sum()
                        Ergebnis.append(Wert)
    
                    elif e[-4:] == "BH20":
                        Indi = IsoS[IsoS["BH"]>=20]
                        Wert = Indi[Column].sum()
                        Ergebnis.append(Wert)
    
                    elif e[-4:] == "P310":
                        Indi = IsoS[IsoS["Preis"] <=3]
                        Indi = Indi[Indi["Preis"] >0] ##Falls es Null-Preise gibt. Null = Kein Preissystem hinterlegt
                        Wert = Indi[Column].sum()
                        Ergebnis.append(Wert)
    
                    elif e[-4:] == "P500":
                        Indi = IsoS[IsoS["Preis"]<=5]
                        Indi = Indi[Indi["Preis"] >0] ##Falls es Null-Preise gibt. Null = Kein Preissystem hinterlegt
                        Wert = Indi[Column].sum()
                        Ergebnis.append(Wert)
    
                    elif e[-4:] == "P690":
                        Indi = IsoS[IsoS["Preis"]<=7]
                        Indi = Indi[Indi["Preis"] >0] ##Falls es Null-Preise gibt. Null = Kein Preissystem hinterlegt
                        Wert = Indi[Column].sum()
                        Ergebnis.append(Wert)
    
                    else:
                        pass
    
    
                #--Fülle Daten in HDF5-Tabelle--#
                Ergebnis =[tuple(Ergebnis)]
                size = len(Ergebnis_T)
                Ergebnis_T.resize((size+1,))
                Ergebnis_T[size:(size+1)] = Ergebnis
                file5.flush()
#                print "--Berechnung für ID "+str(i)+" erfolgreich nach "+str(int(time.clock())-int(t1))+" Sekunden--"
            del dataiso
            gc.collect()
    
    
    #--HDF5-Text zu Tabellenbeschreibung--#
    Ergebnis_T.attrs.create("Parameter",str(text))
    file5.flush()


###########
#--Ende--#
###########
file5.flush()
file5.close()

#--Fertig--#
Sekunden = int(time.clock() - start_time)

print "--Scriptdurchlauf erfolgreich nach",Sekunden,"Sekunden!--"