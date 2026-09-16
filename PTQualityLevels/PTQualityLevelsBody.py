# -*- coding: utf-8 -*-
import numpy as np
import os
from osgeo import ogr, osr
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
from pathlib import Path
import tempfile
import sys
import wx
from VisumPy.helpers import SetMulti
from VisumPy.AddIn import AddIn, AddInState, AddInParameter
_ = AddIn.gettext



def Run(param):
    '''
    1. Erstelle POI-Kategorie falls noch nicht vorhanden (return Nummer dieser Kat.).
    2. Erstelle fehlende BDA
    3. Erzeuge HstKat auf Ebene der Haltestellen, schreibe diese an Haltestellen und liefere DataFrame mit diesen
    4. Erzeuge temporäre GeoJSON mit allen notwendigen Attributen
    5. Erstelle Polygone
    5.1 Schneide diese Polygone aus, falls gewünscht (clip)
    6. Importiere Polygone nach Visum
    
    Parameters
    ----------
    param : Dictionary
        Übergabe von Parametern aus dem Dialog

    Returns
    -------
    bool
        False falls Fehler.
    '''
    Visum.Log(20480, _("Calculate stop categories for %s stops") %(str(Visum.Net.Stops.CountActive)))
    
    # Parameter
    poiNAME = param["poi"]
    poiClip = param["clip"]
    
    poiNO = createPOICat(poiNAME)
    createUDA(poiNAME, poiNO)
    Stops = StopCategories()
    GeoJSONPath, GeoJSONDef, DataSource = CreateGeoJSON()
    CreatePolygons(GeoJSONDef, Stops, DataSource)
    if poiClip:
        GeoJSONPath = ClipGeoJSON(GeoJSONPath)
    ImportPOI2Visum(GeoJSONPath, poiClip, poiNO)
    Visum.Graphic.Redraw()
    
def ClipGeoJSON(_GeoJSONPath):
    '''
    Schneide bestehende GeoJSON-Datei auf Basis gelieferter Geometrien aus.
    Speicher die ausgeschnittenen Polygone unter neuem Pfad und liefere diesen zurück.

    Parameters
    ----------
    geoj_GeoJSONPathson_path : String / Path
        path of temporary GeoJSON File

    Returns
    -------
    cliped_GeoJSON_path : String / Path
        path of clipped temporary GeoJSON File
    '''
    clipGeoJSON = param["clipfiles"]
    Visum.Log(20480, _("Start clipping polygons"))
    import geopandas as gpd # not at beginning, because often not installed
    _GeoJSONGpd = gpd.read_file(_GeoJSONPath)
    for i in clipGeoJSON:
        _clipGeoJSONGpd = gpd.read_file(i)
        _clipGeoJSONGpd = _clipGeoJSONGpd[['geometry']]
        _clipGeoJSONGpd = _clipGeoJSONGpd.to_crs(_GeoJSONGpd.crs)
        _GeoJSONGpd = gpd.clip(_GeoJSONGpd, _clipGeoJSONGpd)
    
    _GeoJSON_path = Path(_GeoJSONPath)
    cliped_GeoJSON_path = _GeoJSON_path.with_name("polygons_clip.geojson")
    _GeoJSONGpd.to_file(cliped_GeoJSON_path, driver="GeoJSON")
    Visum.Log(20480, _("Polygons cut out"))
    return cliped_GeoJSON_path

def CreateGeoJSON():  
    '''
    1. getting temporäres Speicherverzeichnis
    2. Erzeuge dort eine (temporäre) GeoJSON
    3. Füge notwendige Felder / Attribute zur GeoJSON hinzu

    Returns
    -------
    geojson_path : String / Path
        path of temporary GeoJSON File
    _GeoJSON : GeoJSON
        GeoJSON File
    _DataSource : data driver
        DESCRIPTION.
    '''
    
    # Getting temp path
    temp_dir = tempfile.mkdtemp()
    geojson_path  = os.path.join(temp_dir, "buffered_polygons.geojson")
    Visum.Log(20480, _("Temporary GeoJSON path: %s") %(geojson_path))
    # Create GeoJSON
    driver = ogr.GetDriverByName("GeoJSON")
    if os.path.exists(geojson_path):
        driver.DeleteDataSource(geojson_path)
    _DataSource = driver.CreateDataSource(geojson_path)
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(25832) # EPSG:25832 (ETRS89 / UTM zone 32N)
    _GeoJSON = _DataSource.CreateLayer("buffered_polygons", srs=spatial_ref, geom_type=ogr.wkbPolygon, options=["RFC7946=YES"])
    
    # Add attribute fields
    _GeoJSON.CreateField(ogr.FieldDefn("StopNo", ogr.OFTInteger))
    _GeoJSON.CreateField(ogr.FieldDefn("StopName", ogr.OFTString))
    _GeoJSON.CreateField(ogr.FieldDefn("Comment", ogr.OFTString))
    _GeoJSON.CreateField(ogr.FieldDefn("Scenario", ogr.OFTString))
    _GeoJSON.CreateField(ogr.FieldDefn("Distance", ogr.OFTInteger))
    _GeoJSON.CreateField(ogr.FieldDefn("StopType", ogr.OFTInteger))
    _GeoJSON.CreateField(ogr.FieldDefn("StopCat", ogr.OFTString))
    _GeoJSON.CreateField(ogr.FieldDefn("PTQL", ogr.OFTString))
    
    _GeoJSON.SyncToDisk()
    _DataSource.FlushCache()
    return geojson_path, _GeoJSON, _DataSource

def CreatePolygons(_GeoJSON, _Stops, _DataSource):
    '''
    1. Ermittle Parameter, die nur hier benötigt werden.
    2. Erstelle Dict mit Zuordnung der ÖVGK zu den HstKat in Abhängigkeit von Einzugsbereichen (sa)
    3. Loop über alle HstKategorien
    3.1 Erhalte alle Stops dieser HstKat
    3.2 Loop über die Stops je HstKat
    3.3 Erstelle Geometrie für jeden Einzugsbereich je Stop je HstKat
    3.4 Befülle diese Geometrien mit Attributen

    Parameters
    ----------
    _GeoJSON : GeoJSON
        GeoJSON File
    _Stops : pandas DataFrame
        Beinhaltet römische HKat je Stop (über alle, 1-3 und nach 'hvv Regel')
    _DataSource : data driver
        DESCRIPTION.

    Raises
    ------
    ValueError
        Fehler, falls keine Polygone erzeugt wurden.
    '''
    # Parameter
    ct = param["ct"]
    list_sa = param["sa"]
    scenario = param["scen"]

    HKAT = ["HKAT", "HKAT_HVV"][ct]
    sa1 = list_sa[0]
    sa2 = list_sa[1]
    sa3 = list_sa[2]
    sa4 = list_sa[3]
    sa5 = list_sa[4]
    # Zuordung HstKategorie zur Entfernungsklasse (Luflinie)
    categories = {
        "I": [[sa1, "A"], [sa2, "A"], [sa3, "B"], [sa4, "C"], [sa5, "D"]],
        "II": [[sa1, "A"], [sa2, "B"], [sa3, "C"], [sa4, "D"], [sa5, "E"]],
        "III": [[sa1, "B"], [sa2, "C"], [sa3, "D"], [sa4, "E"], [sa5, "F"]],
        "IV": [[sa1, "C"], [sa2, "D"], [sa3, "E"], [sa4, "F"], [sa5, "G"]],
        "V": [[sa1, "D"], [sa2, "E"], [sa3, "F"], [sa4, "G"], [sa5, "H"]],
        "VI": [[sa1, "E"], [sa2, "F"], [sa3, "G"], [sa4, "H"], [sa5, "I"]],
        "VII": [[sa1, "F"], [sa2, "G"], [sa3, "H"], [sa4, "I"], [sa5, "I"]],
        "VIII": [[sa1, "Z1"], [sa2, "Z2"], [sa3, "Z3"], [sa4, "Z4"], [sa5, "Z5"]],
    }
    
    polygon_count = 0
    for StopCat, distancesPTQL in categories.items():
        stops_cat = _Stops[_Stops[HKAT] == StopCat]
        stops_cat = list(zip(stops_cat["STOPNO"].astype(int), stops_cat["STOPNAME"],stops_cat["StopType_all"], stops_cat["X"], stops_cat["Y"], stops_cat["DepHour"].astype(int)))
        for StopNo, StopName, StopType, x, y, Dep in stops_cat:
            point = ogr.Geometry(ogr.wkbPoint)
            if "GCS_WGS_1984" in Visum.Net.AttValue("PROJECTIONDEFINITION"):
                point.AddPoint(y, x)
                src_srs = osr.SpatialReference()
                src_srs.ImportFromEPSG(4326) # EPSG:4325 (GCS_WGS_1984)
                dst_srs = osr.SpatialReference()
                dst_srs.ImportFromEPSG(25832) # EPSG:25832 (ETRS89 / UTM zone 32N)
                transform = osr.CoordinateTransformation(src_srs, dst_srs)
                point.Transform(transform)
            else:
                point.AddPoint(x, y)
        
            for distance, PTQL in distancesPTQL:
                # buffer
                feature_def = _GeoJSON.GetLayerDefn()
                feature = ogr.Feature(feature_def)
                buffered_polygon = point.Buffer(distance)
                feature.SetGeometry(buffered_polygon)
                feature.SetField("Comment", f"StopNo: {StopNo} - AbStunde: {Dep}")
                feature.SetField("Scenario", scenario)
                feature.SetField("StopType", StopType)
                feature.SetField("StopCat", StopCat)
                feature.SetField("PTQL", PTQL)
                feature.SetField("Distance", distance)
                feature.SetField("StopNo", StopNo)
                feature.SetField("StopName", f"{StopName} - {distance}m")
                # Add to file
                _GeoJSON.CreateFeature(feature)
                feature = None  # Free memory
                polygon_count+=1
    
    _DataSource.FlushCache()
    if not polygon_count:
        raise ValueError(_("No active VehicleJourneys at active Stops in Timeintervals or at valid day"))
    Visum.Log(20480, _("%s Polygons created") %(str(polygon_count)))
    
def ImportPOI2Visum(_GeoImport, _clip, poiNO):
    '''
    SUMMARY.

    Parameters
    ----------
    _GeoImport : GeoJSON / Shape File
        Import-File mit Geometrien
    _clip : Bool
        True, falls Clip-Polygone verwendet werden sollen.
    poiNO : Integer
        Neue POI-Kategorie

    Returns
    -------
    None
    '''
    deloldPOI = param["poidel"]
    
    if deloldPOI:
        Visum.Net.POICategories.ItemByKey(poiNO).POIs.RemoveAll()
    
    if _clip:
        # import als Shape, da clip geojson nicht in spezifikation RFC7946 gespeichert werden kann und dann fehlerhaft importiert wird.
        import geopandas as gpd
        _Shape = _GeoImport.with_suffix(".shp")
        _GeoJSON_data = gpd.read_file(_GeoImport)
        _GeoJSON_data.to_file(_Shape, driver='ESRI Shapefile')
        
        ShapeImport = Visum.IO.CreateImportShapeFilePara()
        ShapeImport.AddAttributeAllocation("StopName", "Name")
        ShapeImport.AddAttributeAllocation("PTQL", "Code")
        ShapeImport.AddAttributeAllocation("Comment", "Comment")
        ShapeImport.AddAttributeAllocation("StopType", "HTYP")
        ShapeImport.AddAttributeAllocation("StopCat", "HKAT")
        ShapeImport.AddAttributeAllocation("Distance", "Distanz")
        ShapeImport.AddAttributeAllocation("Scenario", "Szenario")
        ShapeImport.ObjectType = 9 # import as POI
        ShapeImport.SetAttValue("POIKEY", poiNO)
        Visum.IO.ImportShapefile(_Shape, ShapeImport)
    
    else:
        GeoJSONImport = Visum.IO.CreateImportGeoJSONPara()
        GeoJSONImport.AddAttributeAllocation("StopName", "Name")
        GeoJSONImport.AddAttributeAllocation("PTQL", "Code")
        GeoJSONImport.AddAttributeAllocation("Comment", "Comment")
        GeoJSONImport.AddAttributeAllocation("StopType", "HTYP")
        GeoJSONImport.AddAttributeAllocation("StopCat", "HKAT")
        GeoJSONImport.AddAttributeAllocation("Distance", "Distanz")
        GeoJSONImport.AddAttributeAllocation("Scenario", "Szenario")
        GeoJSONImport.ObjectType = 9 # import as POI
        GeoJSONImport.SetAttValue("POIKEY", poiNO)
        Visum.IO.ImportGeoJSON(_GeoImport, GeoJSONImport)

def StopCategories():
    '''
    1. Lese Parameter, die nur hier verwendet werden.
    2.1 Wähle nur FahrplanFahrten an vorgegebenen Tagen
    2.2 Wähle nur FahrplanFahrten in vorgegebenen Zeitfenstern
    3. Ergänze HstTyp an FahrplanFahrten über MODE (VSys oder Oberlinie)
    4. Erzeuge Zähler (nDEP) an FahrplanFahrtElementen
    5. Erstelle DataFrame mit aktiven Stops
    6. Verschneide Stops mit FahrplanFahrtElementen
    7. Erstelle HstKategorie in Abhängigkeit von mittleren Abfahrten je Stunde
    8. Erstelle HstKategorie nach 'hvv Regel'

    Returns
    -------
    _Stops : pandas DataFrame
        Beinhaltet römische HKat je Stop (über alle, 1-3 und nach 'hvv Regel')
    '''
    
    # Parameter
    intervals = param["ti"]
    lineend = param["le"]
    day = param["day"]
    list_sc = param["sc"]
    dict_scml = param["scml"]
    adddep = param["adddep"] # add additional journey count on stop-level from Stop-Attribute
    mode = ["TSYSCODE", "MAINLINENAME"][param["mode"]]

    # chose only VJ on valid days (valid day or daily (all))
    if Visum.Net.CalendarPeriod.AttValue("TYPE") == "CALENDARPERIODWEEK":
        validday = ["ISVALID(MO)", "ISVALID(TU)", "ISVALID(WE)", "ISVALID(TH)", "ISVALID(FR)", "ISVALID(SA)", "ISVALID(SU)"][day]
    elif Visum.Net.CalendarPeriod.AttValue("TYPE") == "CALENDARPERIODYEAR":
        validday = f"ISVALID({day})"
    else:
        validday = "ISVALID(1)"
    
    # Read VJI
    VJI = pd.DataFrame(Visum.Net.VehicleJourneyItems.GetMultipleAttributes(
        ["VEHJOURNEYNO", "INDEX", "Dep",r"TIMEPROFILEITEM\LINEROUTEITEM\STOPPOINT\STOPAREA\STOPNO",
         rf"VEHJOURNEY\LINEROUTE\LINE\{mode}", r"COUNT:COUPLEDVEHJOURNEYITEMS", validday], True))
    VJI.columns = ["VJNO", "INDEX", "DEP", "STOPNO", "MODE", "CHAINED", "DAY"]
    VJI = VJI[VJI["DEP"].notna()]
    VJI = VJI[VJI["DAY"] == 1] # only valid days
    
    # Filter out rows where STOPNO is equal to the previous row's STOPNO (two Departures at same Stop)
    VJI = VJI[~(
    (VJI['STOPNO'] == VJI['STOPNO'].shift(1)) & 
    (VJI['VJNO'] == VJI['VJNO'].shift(1)))]
    
    # Selecting VehJourneys by time intervals; double the intervals for the next morning (also for weekcalendar due to trips after 24:00)
    scaled_intervals = [[start, end] for start, end in intervals] + [[start + 86400, end + 86400] for start, end in intervals] # 86400 seconds a day
    VJI = VJI[VJI["DEP"].apply(lambda x: any(start <= x <= end for start, end in scaled_intervals))]
    VJI = VJI.reset_index(drop=True)
    
    # Adding StopTypes to VJI
    VJI = VJI.merge(dict_scml[["MODE", "STOPTYPE"]], on="MODE", how="left")
    
    # Create nDep, coupled sections and line ends
    VJI["nDEP"] = 1 / VJI["CHAINED"] # Coupled sections reducing the weight of departures
    if lineend: VJI.loc[VJI["INDEX"] == 1, "nDEP"] *= 2 # Count first index *2 for missing arrivals (not = 2 for chained VJ)
    
    # get Stops
    StopsDF = pd.DataFrame(Visum.Net.Stops.GetMultipleAttributes(
        ["NO", "NAME", rf"DISTINCT:STOPAREAS\DISTINCT:STOPPOINTS\DISTINCTACTIVE:SERVINGVEHJOURNEYS\LINEROUTE\LINE\{mode}",
         "XCOORD", "YCOORD"], True))
    StopsDF.columns = ["STOPNO", "STOPNAME", "MODES", "X", "Y"]
    if adddep: # add additional journey count on stop-level  from Stop-Attribute
        AdddepDF = pd.DataFrame(Visum.Net.Stops.GetMultipleAttributes([adddep], True))
        StopsDF["ADDDEP"] = AdddepDF.iloc[:, 0].values
    else:
        StopsDF["ADDDEP"] = 0
    
    # StopType_all for later difference between HKAT in different stoptype-level
    for i in [["StopType1", 1, "HKAT1"], ["StopType2", 2, "HKAT2"], ["StopType3", 3, "HKAT3"], ["StopType_all", None, "HKAT"]]:
        _Stops = StopsDF.copy()
        # Get StopType (all or of specific type)
        if i[0] == "StopType_all":
            df_mode = dict_scml
        else:
            df_mode = dict_scml[dict_scml["STOPTYPE"] == i[1]]
        df_mode = df_mode.set_index("MODE")["STOPTYPE"].to_dict()
        # get minimum StopType for each MODE at Stop (calculate PT Quality Level for each StopType and for all)
        _Stops[i[0]] = _Stops['MODES'].apply(lambda x: min(df_mode.get(e, 3) for e in x.split(',')))

        # count StopDepartures in VHI for each stop and each StopType
        if i[0] == "StopType_all": StopCounts = VJI.groupby("STOPNO", as_index = False)["nDEP"].sum()
        else: StopCounts = VJI[VJI["STOPTYPE"] == i[1]].groupby("STOPNO", as_index = False)["nDEP"].sum()
        StopCounts.columns = ["STOPNO", "nDEP"]
        _Stops = _Stops.merge(StopCounts, on="STOPNO", how="left")
        _Stops["nDEP"] = _Stops["nDEP"].fillna(0).astype(int)
        if i[0] in ["StopType3", "StopType_all"]: # add additional journey count only for all and/or stops of type 3
            _Stops["nDEP"] = _Stops["nDEP"] + _Stops["ADDDEP"]
        _Stops["DepHour"] = _Stops["nDEP"] / sum(end/60/60 - start/60/60 for start, end in intervals) # only use single interval and not scaled ones (each time interval twice)
        _Stops["DepHour"] = (_Stops["DepHour"] + 0.1).floordiv(1).astype(int) # round departures (+0.15 means e.g. int(0.86 + 0.15) = int(1.01) = 1 but not 0)
        
        # Stop categories from StopType and departures in PTV Visum
        conditions = [
            (_Stops["DepHour"] >= list_sc[0]) & (_Stops[i[0]] == 1),
            (_Stops["DepHour"] >= list_sc[0]) & (_Stops[i[0]] == 2),
            (_Stops["DepHour"] >= list_sc[0]) & (_Stops[i[0]] == 3),
            (_Stops["DepHour"] >= list_sc[1]) & (_Stops[i[0]] == 1),
            (_Stops["DepHour"] >= list_sc[1]) & (_Stops[i[0]] == 2),
            (_Stops["DepHour"] >= list_sc[1]) & (_Stops[i[0]] == 3),
            (_Stops["DepHour"] >= list_sc[2]) & (_Stops[i[0]] == 1),
            (_Stops["DepHour"] >= list_sc[2]) & (_Stops[i[0]] == 2),
            (_Stops["DepHour"] >= list_sc[2]) & (_Stops[i[0]] == 3),
            (_Stops["DepHour"] >= list_sc[3]) & (_Stops[i[0]] == 1),
            (_Stops["DepHour"] >= list_sc[3]) & (_Stops[i[0]] == 2),
            (_Stops["DepHour"] >= list_sc[3]) & (_Stops[i[0]] == 3),
            (_Stops["DepHour"] >= list_sc[4]) & (_Stops[i[0]] == 1),
            (_Stops["DepHour"] >= list_sc[4]) & (_Stops[i[0]] == 2),
            (_Stops["DepHour"] >= list_sc[4]) & (_Stops[i[0]] == 3),
            (_Stops["DepHour"] >= list_sc[5]) & (_Stops[i[0]] == 1),
            (_Stops["DepHour"] >= list_sc[5]) & (_Stops[i[0]] == 2),
            (_Stops["DepHour"] >= list_sc[5]) & (_Stops[i[0]] == 3),
            (_Stops["nDEP"] > 0) & (_Stops[i[0]] == 1),
            (_Stops["nDEP"] > 0) & (_Stops[i[0]] == 2),
            (_Stops["nDEP"] > 0) & (_Stops[i[0]] == 3)
            ]
    
        choices = [
            "I", "I", "II", 
            "I", "II", "III",
            "II", "III", "IV",
            "III", "IV", "V",
            "IV", "V", "VI",
            "V", "VI", "VII",
            "VI", "VII", "VIII",
            ]
        
        _Stops[i[2]] = np.select(conditions, choices, default = "X")
        
        # to Visum UDA 'HKAT'
        PTClass = _Stops[i[2]].tolist()
        SetMulti(Visum.Net.Stops, i[2], PTClass, True)
    
    # create StopCat on 'hvv Rule' and write to Visum
    _Stops_HVV = _stopcat_hvv()
    SetMulti(Visum.Net.Stops, 'HKAT_HVV', _Stops_HVV['HKAT_HVV'].tolist(), True)
    _Stops = _Stops.merge(_Stops_HVV[['STOPNO', 'HKAT_HVV']], on='STOPNO', how='left')

    return _Stops

def createPOICat(poiNAME):
    '''
    Erstelle POI-Kategorie falls noch nicht vorhanden.

    Parameters
    ----------
    poiNAME : String
        Name der POI-Kategorie, in die die ÖVGK-Polygone gespeichert werden sollen

    Returns
    -------
    int
        Nummer der zugehörigen POI-Kategorie
    '''
    poiNO = next((i.AttValue("NO") for i in Visum.Net.POICategories.GetAll if i.AttValue("NAME") == poiNAME), None)
    if not poiNO:
        poi = Visum.Net.AddPOICategory()
        poi.SetAttValue("NAME", poiNAME)
        poiNO = poi.AttValue("NO")
        Visum.Log(20480,_("POI-Category '%s' added") %(poiNAME))
    return int(poiNO)

def createUDA(poiNAME, poiNO):
    '''
    1. Fehlende BDA der Haltestellen
    2. Fehöender BDA der POI-Kategorie

    Parameters
    ----------
    poiNAME : String
        Name der POI-Kategorie
    poiNO : Integer
        Nummer der POI-Kategorie

    Returns
    -------
    None
    '''
    
    n = 0
    # Stops
    for name in ["HKAT", "HKAT_HVV", "HKAT1", "HKAT2", "HKAT3"]:
        if Visum.Net.Stops.AttrExists(name):
            continue
        if name == "HKAT":
            label = "Haltestellenkategorie"
            comment = _("Stop category (PT quality levels)")
        elif name == "HKAT_HVV":
            label = "Haltestellenkategorie im hvv"
            comment = _("Stop category 'hvv rule' (PT quality levels)")
        else:
            label = f"Haltestellenkategorie HstTyp {name[-1]}"
            comment = _("Stop category for Stop type %s (PT quality levels)") % name[-1]
        Visum.Net.Stops.AddUserDefinedAttribute(name, label, label, 5)
        uda = Visum.Net.Stops.Attributes.ItemByKey(name)
        uda.Comment = comment
        uda.MaxStringLen = 4
        uda.StringValueDefault = "X"
        n += 1
    # POI-Cat
    POIs = Visum.Net.POICategories.ItemByKey(poiNO).POIs
    for name in ["Szenario", "HKAT"]:
        if POIs.AttrExists(name):
            continue
        POIs.AddUserDefinedAttribute(name, name, name, 5)
        uda = POIs.Attributes.ItemByKey(name)
        uda.Comment = _("PT Qualities: %s") % name
        uda.MaxStringLen = 30
        uda.StringValueDefault = "X"
        n += 1
    for name in ["Distanz", "HTYP"]:
        if POIs.AttrExists(name):
            continue
        POIs.AddUserDefinedAttribute(name, name, name, 1)
        uda = POIs.Attributes.ItemByKey(name)
        uda.Comment = _("PT Qualities: %s") % name
        uda.ValueMax = 1500
        uda.ValueDefault = -1
        n += 1
    if n > 0:
        Visum.Log(20480, _("%s UDA added (to POI-Category: %s)") %(n, poiNAME))


def _stopcat_hvv():
    '''
    1. Lese HKAT und HKAT1 bis HKAT3 auf Stop-Ebene
    2. Erstelle Dict mit römischen und lateinischen Zahlen
    3. Wende hvv Regel an
    4. Übertrage 

    Returns
    -------
    _StopsDF : pandas DataFrame
        Beinhaltet römische HKat je Stop nach 'hvv Regel'
    '''
    StopAttr = ["HKAT", "HKAT1", "HKAT2", "HKAT3"]
    StopCatRoman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
    _StopsDF = pd.DataFrame(Visum.Net.Stops.GetMultipleAttributes(["NO"] + StopAttr, True),columns=["STOPNO"] + StopAttr)
    
    x = _StopsDF[StopAttr].replace({r: i for i, r in enumerate(StopCatRoman, 1)})
    _StopsDF["HKAT_HVV"] = pd.concat([x["HKAT"],
        (x[["HKAT1", "HKAT2", "HKAT3"]].min(axis=1) - 1).clip(lower=1)
    ], axis=1).max(axis=1).map(dict(enumerate(StopCatRoman, 1)))
    
    return _StopsDF


if len(sys.argv) > 1:
    addIn = AddIn()
else:
    addIn = AddIn(Visum)

if addIn.IsInDebugMode:
    app = wx.PySimpleApp(0)
    Visum = addIn.VISUM
    addInParam = AddInParameter(addIn, None)
else:
    addInParam = AddInParameter(addIn, Parameter)

if addIn.State != AddInState.OK:
    addIn.ReportMessage(addIn.ErrorObjects[0].ErrorMessage)
else:
    try:
        defaultParam = {"" : False}
        param = addInParam.Check(True, defaultParam)
        Run(param)
        addIn.ReportMessage(_("PT Quality levels: created!"), 2)
    except ValueError as e:
        addIn.ReportMessage(str(e))
    except Exception:
        addIn.HandleException(addIn.TemplateText.MainApplicationError)
