import arcpy,os

import source.obj_Layer;
import source.util;

###############################################################################
import importlib
importlib.reload(source.obj_Layer);
importlib.reload(source.util);

###############################################################################
class SystemCache:

   fields = (
       'current_unit_system'
      ,'current_scenarioid'
      ,'current_conditionid'
      ,'current_factorid'
      ,'current_facilityattributesid'
      ,'current_road_transporter'
      ,'current_rail_transporter'
      ,'network_dataset'
      ,'nd_travel_mode'
      ,'nd_impedance_field'
      ,'nd_overall_distance_field'
      ,'nd_overall_distance_unt'
      ,'nd_overall_time_field'
      ,'nd_overall_time_unt'
      ,'nd_road_distance_field'
      ,'nd_road_distance_unt'
      ,'nd_road_time_field'
      ,'nd_road_time_unt'
      ,'nd_rail_distance_field'
      ,'nd_rail_distance_unt'
      ,'nd_rail_time_field'
      ,'nd_rail_time_unt'
      ,'nd_station_count_field'
      ,'isAGO'
      ,'maximum_facilities_to_find'
      ,'settings_last_updated_date'
      ,'settings_last_updated_by'
   );

   #...........................................................................
   def __init__(self
      ,system_cache_layer=None
   ):
      #////////////////////////////////////////////////////////////////////////
      self.system_cache_layer                      = None;
      self.current_unit_system                     = None;
      self.current_scenarioid                      = None;
      self.current_conditionid                     = None;
      self.current_factorid                        = None;
      self.current_facilityattributesid            = None;
      self.current_road_transporter                = None;
      self.current_rail_transporter                = None;
      self.network_dataset                         = None;
      self.nd_travel_mode                          = None;
      self.nd_impedance_field                      = None;
      self.nd_overall_distance_field               = None;
      self.nd_overall_distance_unt                 = None;
      self.nd_overall_time_field                   = None;
      self.nd_overall_time_unt                     = None;
      self.nd_road_distance_field                  = None;
      self.nd_road_distance_unt                    = None;
      self.nd_road_time_field                      = None;
      self.nd_road_time_unt                        = None;
      self.nd_rail_distance_field                  = None;
      self.nd_rail_distance_unt                    = None;
      self.nd_rail_time_field                      = None;
      self.nd_rail_time_unt                        = None;
      self.nd_station_count_field                  = None;
      self.isAGO                                   = None;
      self.maximum_facilities_to_find              = None;
      self.settings_last_updated_date              = None;
      self.settings_last_updated_by                = None;
      #////////////////////////////////////////////////////////////////////////
      
      if system_cache_layer is not None:
         self.system_cache_layer = system_cache_layer;

      else:
         aprx = arcpy.mp.ArcGISProject(source.util.g_prj);
         map  = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];

         for lyr in map.listLayers():

            if lyr.supports("name") and lyr.name == "SystemCache":
               self.system_cache_layer = source.obj_Layer.Layer(lyr);

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
         self.current_facilityattributesid            = row[4];
         self.current_road_transporter                = row[5];
         self.current_rail_transporter                = row[6];
         self.network_dataset                         = row[7];
         self.nd_travel_mode                          = row[8];
         self.nd_impedance_field                      = row[9];
         self.nd_overall_distance_field               = row[10];
         self.nd_overall_distance_unt                 = row[11];
         self.nd_overall_time_field                   = row[12];
         self.nd_overall_time_unt                     = row[13];
         self.nd_road_distance_field                  = row[14];
         self.nd_road_distance_unt                    = row[15];
         self.nd_road_time_field                      = row[16];
         self.nd_road_time_unt                        = row[17];
         self.nd_rail_distance_field                  = row[18];
         self.nd_rail_distance_unt                    = row[19];
         self.nd_rail_time_field                      = row[20];
         self.nd_rail_time_unt                        = row[21];
         self.nd_station_count_field                  = row[22];
         self.isAGO                                   = row[23];
         self.maximum_facilities_to_find              = row[24];
         self.settings_last_updated_date              = row[25];
         self.settings_last_updated_by                = row[26];

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
      
   #...........................................................................
   def set_current_facilityattributesid(self,value):
   
      self.current_facilityattributesid = value;
      self.writeSystemCache('current_facilityattributesid',value);
      
   #...........................................................................
   def set_current_road_transporter(self,value):
   
      self.current_road_transporter = value;
      self.writeSystemCache('current_road_transporter',value);
      
   #...........................................................................
   def set_current_rail_transporter(self,value):
   
      self.current_rail_transporter = value;
      self.writeSystemCache('current_rail_transporter',value);
      
   #...........................................................................
   def total_nd_impedance_field(self):
   
      if self.nd_impedance_field is None:
         return None;
         
      else:
         return 'Total_' + self.nd_impedance_field;
      
   #...........................................................................
   def total_nd_overall_distance_field(self):
   
      if self.nd_overall_distance_field is None:
         return None;
         
      else:
         return 'Total_' + self.nd_overall_distance_field;
      
   #...........................................................................
   def total_nd_overall_time_field(self):
   
      if self.nd_overall_time_field is None:
         return None;
         
      else:
         return 'Total_' + self.nd_overall_time_field;
      
   #...........................................................................
   def total_nd_road_distance_field(self):
   
      if self.nd_road_distance_field is None:
         return None;
         
      else:
         return 'Total_' + self.nd_road_distance_field;
      
   #...........................................................................
   def total_nd_road_time_field(self):
   
      if self.nd_road_time_field is None:
         return None;
         
      else:
         return 'Total_' + self.nd_road_time_field;
      
   #...........................................................................
   def total_nd_rail_distance_field(self):
   
      if self.nd_rail_distance_field is None:
         return None;
         
      else:
         return 'Total_' + self.nd_rail_distance_field;
      
   #...........................................................................
   def total_nd_rail_time_field(self):
   
      if self.nd_rail_time_field is None:
         return None;
         
      else:
         return 'Total_' + self.nd_rail_time_field;
         
   #...........................................................................
   def total_nd_station_count_field(self):
   
      if self.nd_station_count_field is None:
         return None;
         
      else:
         return 'Total_' + self.nd_station_count_field;      
         
