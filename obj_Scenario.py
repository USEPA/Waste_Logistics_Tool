import arcpy,os

import util;
import obj_Layer;

###############################################################################
import importlib
importlib.reload(util);
importlib.reload(obj_Layer);

###############################################################################
class Scenario:

   scenario_layer             = None;
   scenarioid                 = None;
   waste_type                 = None;
   waste_medium               = None;
   waste_amount               = None;
   waste_unit                 = None;
   route_count_requested      = None;
   route_count_returned       = None;
   map_image                  = None;
   conditionid                = None;
   factorid                   = None;

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
   );

   #...........................................................................
   def __init__(self
      ,scenario_layer = None
      ,scenario_id    = None
   ):

      if scenario_layer is not None:
         self.scenario_layer = scenario_layer;

      else:
         aprx = arcpy.mp.ArcGISProject("CURRENT");
         map  = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];

         for lyr in map.listLayers():

            if lyr.supports("name") and lyr.name == "Scenario":
               self.scenario_layer = obj_Layer.Layer(lyr);

         if self.scenario_layer is None:
            raise arcpy.ExecuteError("Error. Scenario layer not found.");

      if scenario_id is not None:
         self.loadScenarioID(scenario_id);

   #...........................................................................
   def fetchScenarioIDs(self):

      rows = arcpy.da.SearchCursor(
          in_table     = self.scenario_layer.dataSource
         ,field_names  = (
             'scenarioid'
          )
         ,where_clause = None
      );

      output = [];

      for row in rows:
         output.append(row[0]);

      del rows;

      return output;

   #...........................................................................
   def loadScenarioID(self,scenarioid):

      rows = arcpy.da.SearchCursor(
          in_table     = self.scenario_layer.dataSource
         ,field_names  = self.fields
         ,where_clause = "scenarioid = " + util.sql_quote(scenarioid)
      );

      for row in rows:
         self.scenarioid               = row[0];
         self.waste_type               = row[1];
         self.waste_medium             = row[2];
         self.waste_amount             = row[3];
         self.waste_unit               = row[4];
         self.numberoffacilitiestofind = row[5];
         self.route_count_requested    = row[6];
         self.route_count_returned     = row[7];
         self.map_image                = row[8];
         self.conditionid              = row[9];
         self.factorid                 = row[10];

      del rows;

   #...........................................................................
   def upsertScenarioID(self
      ,scenarioid
      ,waste_type               = None
      ,waste_medium             = None
      ,waste_amount             = None
      ,waste_unit               = None
      ,numberoffacilitiestofind = None
      ,route_count_requested    = None
      ,route_count_returned     = None
      ,map_image                = None
      ,conditionid              = None
      ,factorid                 = None
   ):

      existing_ids = self.fetchScenarioIDs();

      if scenarioid in existing_ids:

         with arcpy.da.UpdateCursor(
             in_table     = self.scenario_layer.dataSource
            ,field_names  = self.fields
            ,where_clause = "scenarioid = " + util.sql_quote(scenarioid)
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

               cursor.updateRow(
                  row
               );

      else:

         cursor = arcpy.da.InsertCursor(
             in_table    = self.scenario_layer.dataSource
            ,field_names = self.fields
         );
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
            )
         );

      del cursor;
      
   #...........................................................................
   def duplicateScenarioID(self
      ,sourceid
      ,targetid
   ):
   
      rows = arcpy.da.SearchCursor(
          in_table     = self.scenario_layer.dataSource
         ,field_names  = self.fields
         ,where_clause = "scenarioid = " + util.sql_quote(sourceid)
      );

      for row in rows:
         scenarioid               = row[0];
         waste_type               = row[1];
         waste_medium             = row[2];
         waste_amount             = row[3];
         waste_unit               = row[4];
         numberoffacilitiestofind = row[5];
         route_count_requested    = row[6];
         route_count_returned     = row[7];
         map_image                = row[8];
         conditionid              = row[9];
         factorid                 = row[10];
         
      del rows;

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
         )
      );
   
      del cursor;
      