import arcpy,os

import obj_Layer;

###############################################################################
import importlib
importlib.reload(obj_Layer);

###############################################################################
class NetworkAnalysisDataset:

   aprx             = None;
   map              = None;
   network          = None;
   facilities       = None;
   incidents        = None;
   routes           = None;
   point_barriers   = None;
   line_barriers    = None;
   polygon_barriers = None;

   #...........................................................................
   def __init__(self,layerfile=None):

      self.aprx = arcpy.mp.ArcGISProject("CURRENT");
      self.map  = self.aprx.listMaps("AllHazardsWasteLogisticsMap")[0];

      if self.map is None:
         raise arcpy.ExecuteError("Error.  Project map not found.");

      if layerfile is not None:
         netfile = arcpy.mp.LayerFile(layerfile);

         self.load_layers(netfile.listLayers('*'));

      else:
         self.load_layers(self.map.listLayers('*'));

   #...........................................................................
   def createLayerFile(self):

      file_target = arcpy.CreateScratchName(
          "Network.lyrx"
         ,""
         ,"Folder"
         ,arcpy.env.scratchFolder
      );

      arcpy.SaveToLayerFile_management(
          in_layer  = self.network.lyr()
         ,out_layer = file_target
      );

      return file_target;

   #...........................................................................
   def lyr(self):

      return self.network.lyr();

   #...........................................................................
   def load_layers(self,ary_layers):

      for lyr in ary_layers:

         if lyr.supports("name") and  \
         ( "AllHazardsWasteLogisticsTool" + '/' + lyr.name == "AllHazardsWasteLogisticsTool" + '/' + "Network" \
           or lyr.longName == "Network" ):

            if lyr.isNetworkAnalystLayer:
               self.network = obj_Layer.Layer(lyr);

      if self.network is not None:

         network_sublayers = arcpy.na.GetNAClassNames(
            self.network.lyr()
         );

         for lyr in ary_layers:

            if lyr.supports("name") and lyr.name == network_sublayers["Incidents"]:
               self.incidents = obj_Layer.Layer(lyr);

            if lyr.supports("name") and lyr.name == network_sublayers["Facilities"]:
               self.facilities = obj_Layer.Layer(lyr);

            if lyr.supports("name") and lyr.name == network_sublayers["CFRoutes"]:
               self.routes = obj_Layer.Layer(lyr);

            if lyr.supports("name") and lyr.name == network_sublayers["Barriers"]:
               self.point_barriers = obj_Layer.Layer(lyr);

            if lyr.supports("name") and lyr.name == network_sublayers["PolylineBarriers"]:
               self.line_barriers = obj_Layer.Layer(lyr);

            if lyr.supports("name") and lyr.name == network_sublayers["PolygonBarriers"]:
               self.polygon_barriers = obj_Layer.Layer(lyr);
            