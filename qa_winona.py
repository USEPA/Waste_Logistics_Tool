import arcpy,os;

wgs = arcpy.SpatialReference(4326);
wbm = arcpy.SpatialReference(3857);

aprx = arcpy.mp.ArcGISProject("CURRENT");
map = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];
for lyr in map.listLayers():
   if lyr.supports("name") and lyr.name == "SupportArea":
      sup = lyr;
   if lyr.supports("name") and lyr.name == "IncidentArea":
      inc = lyr;
   if lyr.supports("name") and lyr.name == "Line Barriers":
      lbr = lyr;

arcpy.TruncateTable_management(sup.dataSource);
coordinates = [
    (-87.8966599, 37.2321335)
   ,(-87.7444257, 30.1627998)
   ,(-76.8186663, 30.3818999)
   ,(-75.1950254, 37.6751982)
]
with arcpy.da.InsertCursor(sup.dataSource,['SHAPE@']) as cur:
   cur.insertRow([coordinates])
sup.visible = False;
sup.visible = True;

arcpy.TruncateTable_management(inc.dataSource);
coordinates = [
    (-79.6160145, 34.2141739)
   ,(-79.6077882, 34.2033394)
   ,(-79.5910310, 34.2051033)
   ,(-79.5962105, 34.2149298)
];
with arcpy.da.InsertCursor(inc.dataSource,['SHAPE@']) as cur:
   cur.insertRow([coordinates]);
inc.visible = False;
inc.visible = True;

arcpy.TruncateTable_management(lbr.dataSource);
geo = arcpy.Polyline(arcpy.Array([
    arcpy.Point(-79.5168422, 34.0879472)
   ,arcpy.Point(-79.5963438, 34.1604600)
   ,arcpy.Point(-79.7758175, 34.1797600)
]),wgs).projectAs(wbm);
with arcpy.da.InsertCursor(lbr.dataSource,['SHAPE@']) as cur:
   cur.insertRow((geo,));
lbr.visible = False;
lbr.visible = True;

