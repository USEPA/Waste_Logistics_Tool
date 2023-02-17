import arcpy,os

import source.util;
import source.obj_Layer;

###############################################################################
import importlib
importlib.reload(source.util);
importlib.reload(source.obj_Layer);

###############################################################################
class Scenario:

   fields = (
       'scenarioid'
      ,'waste_type'
      ,'waste_medium'
      ,'waste_amount'
      ,'waste_unit'
      ,'numberoffacilitiestofind'
      ,'route_count_requested'
      ,'route_count_returned'
      ,'map_image'
      ,'conditionid'
      ,'factorid'
      ,'facilityattributesid'
      ,'road_transporter_attributes'
      ,'rail_transporter_attributes'
   );

   #...........................................................................
   def __init__(self
      ,scenario_layer = None
      ,scenario_id    = None
   ):
      #////////////////////////////////////////////////////////////////////////
      self.scenario_layer              = None;
      self.scenarioid                  = None;
      self.waste_type                  = None;
      self.waste_medium                = None;
      self.waste_amount                = None;
      self.waste_unit                  = None;
      self.numberoffacilitiestofind    = None;
      self.route_count_requested       = None;
      self.route_count_returned        = None;
      self.map_image                   = None;
      self.conditionid                 = None;
      self.factorid                    = None;
      self.facilityattributesid        = None;
      self.road_transporter_attributes = None;
      self.rail_transporter_attributes = None;
      #////////////////////////////////////////////////////////////////////////
      
      if scenario_layer is not None:
         self.scenario_layer = scenario_layer;

      else:
         if source.util.g_aprx is not None:
            aprx = source.util.g_aprx;
         else:
            try:
               source.util.g_aprx = arcpy.mp.ArcGISProject(source.util.g_prj);
               aprx = source.util.g_aprx;
            except Exception as e:
               source.util.dzlog_e(sys.exc_info(),'ERROR');
               raise;
         
         try:
            map = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];
         except Exception as e:
            source.util.dzlog_e(sys.exc_info(),'ERROR');
            raise;
         
         for lyr in map.listLayers():

            if lyr.supports("name") and lyr.name == "Scenario":
               self.scenario_layer = source.obj_Layer.Layer(lyr);

         if self.scenario_layer is None:
            raise arcpy.ExecuteError("Error. Scenario layer not found.");
      
      if scenario_id is not None:
         self.loadScenarioID(scenario_id);
      
   #...........................................................................
   def fetchScenarioIDs(self):

      output = [];
      
      with arcpy.da.SearchCursor(
          in_table     = self.scenario_layer.dataSource
         ,field_names  = (
             'scenarioid'
          )
         ,where_clause = None
      ) as cursor:

         for row in cursor:
            output.append(row[0]);

      return output;

   #...........................................................................
   def loadScenarioID(self,scenarioid):

      with arcpy.da.SearchCursor(
          in_table     = self.scenario_layer.dataSource
         ,field_names  = self.fields
         ,where_clause = "scenarioid = " + source.util.sql_quote(scenarioid)
      ) as cursor:

         for row in cursor:
            self.scenarioid                  = row[0];
            self.waste_type                  = row[1];
            self.waste_medium                = row[2];
            self.waste_amount                = row[3];
            self.waste_unit                  = row[4];
            self.numberoffacilitiestofind    = row[5];
            self.route_count_requested       = row[6];
            self.route_count_returned        = row[7];
            self.map_image                   = row[8];
            self.conditionid                 = row[9];
            self.factorid                    = row[10];
            self.facilityattributesid        = row[11];
            self.road_transporter_attributes = row[12];
            self.rail_transporter_attributes = row[13];

   #...........................................................................
   def upsertScenarioID(self
      ,scenarioid
      ,waste_type                  = None
      ,waste_medium                = None
      ,waste_amount                = None
      ,waste_unit                  = None
      ,numberoffacilitiestofind    = None
      ,route_count_requested       = None
      ,route_count_returned        = None
      ,map_image                   = None
      ,conditionid                 = None
      ,factorid                    = None
      ,facilityattributesid        = None
      ,road_transporter_attributes = None
      ,rail_transporter_attributes = None
   ):

      existing_ids = self.fetchScenarioIDs();

      if scenarioid in existing_ids:

         with arcpy.da.UpdateCursor(
             in_table     = self.scenario_layer.dataSource
            ,field_names  = self.fields
            ,where_clause = "scenarioid = " + source.util.sql_quote(scenarioid)
         ) as cursor:

            for row in cursor:

               if waste_type is not None:
                  row[1] = waste_type;

               if waste_medium is not None:
                  row[2] = waste_medium;

               if waste_amount is not None:
                  row[3] = waste_amount;
                  
               if waste_unit is not None:
                  row[4] = waste_unit;
                  
               if numberoffacilitiestofind is not None:
                  row[5] = numberoffacilitiestofind;
                  
               if route_count_requested is not None:
                  row[6] = route_count_requested;

               if route_count_returned is not None:
                  row[7] = route_count_returned;
                  
               if map_image is not None:
                  row[8] = map_image;
                  
               if conditionid is not None:
                  row[9] = conditionid;
                  
               if factorid is not None:
                  row[10] = factorid;
                  
               if facilityattributesid is not None:
                  row[11] = facilityattributesid;
                  
               if road_transporter_attributes is not None:
                  row[12] = road_transporter_attributes;
                  
               if rail_transporter_attributes is not None:
                  row[13] = rail_transporter_attributes;
                  
               cursor.updateRow(
                  row
               );

      else:

         with arcpy.da.InsertCursor(
             in_table    = self.scenario_layer.dataSource
            ,field_names = self.fields
         ) as cursor:
         
            cursor.insertRow(
               (
                   scenarioid
                  ,waste_type
                  ,waste_medium
                  ,waste_amount
                  ,waste_unit
                  ,numberoffacilitiestofind
                  ,route_count_requested
                  ,route_count_returned
                  ,map_image
                  ,conditionid
                  ,factorid
                  ,facilityattributesid
                  ,road_transporter_attributes
                  ,rail_transporter_attributes
               )
            );
      
   #...........................................................................
   def duplicateScenarioID(self
      ,sourceid
      ,targetid
   ):
   
      with arcpy.da.SearchCursor(
          in_table     = self.scenario_layer.dataSource
         ,field_names  = self.fields
         ,where_clause = "scenarioid = " + source.util.sql_quote(sourceid)
      ) as cursor:

         for row in rows:
            scenarioid                  = row[0];
            waste_type                  = row[1];
            waste_medium                = row[2];
            waste_amount                = row[3];
            waste_unit                  = row[4];
            numberoffacilitiestofind    = row[5];
            route_count_requested       = row[6];
            route_count_returned        = row[7];
            map_image                   = row[8];
            conditionid                 = row[9];
            factorid                    = row[10];
            facilityattributesid        = row[11];
            road_transporter_attributes = row[12];
            rail_transporter_attributes = row[13];

      cursor = arcpy.da.InsertCursor(
          in_table    = self.scenario_layer.dataSource
         ,field_names = self.fields
      );
      
      cursor.insertRow(
         (
             targetid
            ,waste_type
            ,waste_medium
            ,waste_amount
            ,waste_unit
            ,numberoffacilitiestofind
            ,route_count_requested
            ,route_count_returned
            ,map_image
            ,conditionid
            ,factorid
            ,facilityattributesid
            ,road_transporter_attributes
            ,rail_transporter_attributes
         )
      );
   
      del cursor;
      
   #...........................................................................
   def updateLinkageIDs(self,
       scenarioid
      ,conditionid                 = None
      ,factorid                    = None
      ,facilityattributesid        = None
      ,road_transporter_attributes = None
      ,rail_transporter_attributes = None
   ):
      
      with arcpy.da.UpdateCursor(
          in_table     = self.scenario_layer.dataSource
         ,field_names  = [
             'scenarioid'
            ,'conditionid'
            ,'factorid'
            ,'facilityattributesid'
            ,'road_transporter_attributes'
            ,'rail_transporter_attributes'
          ]
         ,where_clause = "scenarioid = " + source.util.sql_quote(scenarioid)
      ) as cursor:
      
         for row in cursor:
            if conditionid is not None:
               row[1] = conditionid;
               
            if factorid is not None:
               row[2] = factorid;

            if facilityattributesid is not None:
               row[3] = facilityattributesid;

            if road_transporter_attributes is not None:
               row[4] = road_transporter_attributes;

            if rail_transporter_attributes is not None:
               row[5] = rail_transporter_attributes;
               
            cursor.updateRow(
               row
            );
         
   
      