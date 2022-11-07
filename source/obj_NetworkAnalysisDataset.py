import arcpy,os,sys;
import time;
import source.obj_Layer;
import source.util;

###############################################################################
import importlib
importlib.reload(source.obj_Layer);
importlib.reload(source.util);

###############################################################################
class NetworkAnalysisDataset:

   #...........................................................................
   def __init__(self
      ,layerfile = None
   ):
      #////////////////////////////////////////////////////////////////////////
      self.aprx               = None;
      self.map                = None;
      self.network            = None;
      self.facilities         = None;
      self.incidents          = None;
      self.routes             = None;
      self.point_barriers     = None;
      self.line_barriers      = None;
      self.polygon_barriers   = None;
      #////////////////////////////////////////////////////////////////////////

      if source.util.g_aprx is not None:
         self.aprx = source.util.g_aprx;
      else:
         try:
            source.util.g_aprx = arcpy.mp.ArcGISProject(source.util.g_prj);
            self.aprx = source.util.g_aprx;
         except Exception as e:
            source.util.dzlog_e(sys.exc_info(),'ERROR');
            raise;

      try:
         self.map  = self.aprx.listMaps("AllHazardsWasteLogisticsMap")[0];
      except Exception as e:
         source.util.dzlog_e(sys.exc_info(),'ERROR');
         raise;

      if self.map is None:
         msg = "Error.  Project map not found.";
         source.util.dzlog(msg,'ERROR');
         raise arcpy.ExecuteError(msg);

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
               self.network = source.obj_Layer.Layer(lyr);

      if self.network is not None:

         try:
            network_sublayers = arcpy.na.GetNAClassNames(
               network_analyst_layer = self.network.lyr()
            );
         except Exception as e:
            source.util.dzlog('network dataset: ' + str(self.network.lyr()) + ' unable to access.');
            source.util.dzlog_e(sys.exc_info(),'ERROR');
            raise;

         for lyr in ary_layers:

            if lyr.supports("name") and lyr.name == network_sublayers["Incidents"]:
               self.incidents = source.obj_Layer.Layer(lyr);

            if lyr.supports("name") and lyr.name == network_sublayers["Facilities"]:
               self.facilities = source.obj_Layer.Layer(lyr);

            if lyr.supports("name") and lyr.name == network_sublayers["CFRoutes"]:
               self.routes = source.obj_Layer.Layer(lyr);

            if lyr.supports("name") and lyr.name == network_sublayers["Barriers"]:
               self.point_barriers = source.obj_Layer.Layer(lyr);

            if lyr.supports("name") and lyr.name == network_sublayers["PolylineBarriers"]:
               self.line_barriers = source.obj_Layer.Layer(lyr);

            if lyr.supports("name") and lyr.name == network_sublayers["PolygonBarriers"]:
               self.polygon_barriers = source.obj_Layer.Layer(lyr);
