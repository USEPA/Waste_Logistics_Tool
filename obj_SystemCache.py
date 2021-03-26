import arcpy,os

import obj_Layer;

###############################################################################
import importlib
importlib.reload(obj_Layer);

###############################################################################
class SystemCache:

   system_cache_layer                      = None;
   
   current_unit_system                     = None;
   current_scenarioid                      = None;
   current_conditionid                     = None;
   current_factorid                        = None;
   network_dataset                         = None;
   network_distance_fieldname              = None;
   network_distance_unit                   = None;
   network_time_fieldname                  = None;
   network_time_unit                       = None;

   fields = (
       'current_unit_system'
      ,'current_scenarioid'
      ,'current_conditionid'
      ,'current_factorid'
      ,'network_dataset'
      ,'network_distance_fieldname'
      ,'network_distance_unit'
      ,'network_time_fieldname'
      ,'network_time_unit'
   );

   #...........................................................................
   def __init__(self
      ,system_cache_layer=None
   ):
      if system_cache_layer is not None:
         self.system_cache_layer = system_cache_layer;

      else:
         aprx = arcpy.mp.ArcGISProject("CURRENT");
         map  = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];

         for lyr in map.listLayers():

            if lyr.supports("name") and lyr.name == "SystemCache":
               self.system_cache_layer = obj_Layer.Layer(lyr);

         if self.system_cache_layer is None:
            raise arcpy.ExecuteError("Error. SystemCache layer not found.");

      self.loadSystemCache();

   #...........................................................................
   def loadSystemCache(self):

      rows = arcpy.da.SearchCursor(
          in_table     = self.system_cache_layer.dataSource
         ,field_names  = self.fields
         ,where_clause = None
      );

      for row in rows:
         self.current_unit_system                     = row[0];
         self.current_scenarioid                      = row[1];
         self.current_conditionid                     = row[2];
         self.current_factorid                        = row[3];
         self.network_dataset                         = row[4];
         self.network_distance_fieldname              = row[5];
         self.network_distance_unit                   = row[6];
         self.network_time_fieldname                  = row[7];
         self.network_time_unit                       = row[8];         

      del rows;

   #...........................................................................
   def writeSystemCache(self,key,value):

      with arcpy.da.UpdateCursor(
          in_table     = self.system_cache_layer.dataSource
         ,field_names  = key
         ,where_clause = None
      ) as cursor:

         for row in cursor:
            row[0] = value;

            cursor.updateRow(
               row
            );

      del cursor;
      
   #...........................................................................
   def set_current_scenarioid(self,value):
   
      self.current_scenarioid = value;
      self.writeSystemCache('current_scenarioid',value);

   #...........................................................................
   def set_current_conditionid(self,value):
   
      self.current_conditionid = value;
      self.writeSystemCache('current_conditionid',value);

   #...........................................................................
   def set_current_factorid(self,value):
   
      self.current_factorid = value;
      self.writeSystemCache('current_factorid',value);

