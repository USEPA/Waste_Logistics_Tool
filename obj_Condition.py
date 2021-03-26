import arcpy,os

import util;
import obj_Layer;

###############################################################################
import importlib
importlib.reload(util);
importlib.reload(obj_Layer);

###############################################################################
class Condition:

   conditions_layer         = None;
   conditionid              = None;
   roadtolls                = None;
   misccost                 = None;
   totalcostmultiplier      = None;
   vehicledeconcost         = None;
   stagingsitecost          = None;
   numberoftrucksavailable  = None;
   drivinghours             = None;

   fields = (
       'conditionid'
      ,'roadtolls'
      ,'misccost'
      ,'totalcostmultiplier'
      ,'vehicledeconcost'
      ,'stagingsitecost'
      ,'numberoftrucksavailable'
      ,'drivinghours'
   );

   #...........................................................................
   def __init__(self,conditions_layer=None):

      if conditions_layer is not None:
         self.conditions_layer = conditions_layer;

      else:
         aprx = arcpy.mp.ArcGISProject("CURRENT");
         map  = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];

         for lyr in map.listLayers():

            if lyr.supports("name") and lyr.name == "Conditions":
               self.conditions_layer = obj_Layer.Layer(lyr);

         if self.conditions_layer is None:
            raise arcpy.ExecuteError("Error. Conditions layer not found.");

   #...........................................................................
   def totalRecordCount(self):

      return int(
         arcpy.GetCount_management(
            self.conditions_layer.dataSource
         ).getOutput(0)
      );

   #...........................................................................
   def fetchConditionIDs(self):

      rows = arcpy.da.SearchCursor(
          in_table     = self.conditions_layer.dataSource
         ,field_names  = (
             'conditionid'
          )
         ,where_clause = None
      );

      output = [];

      for row in rows:
         output.append(row[0]);

      del rows;

      return output;

   #...........................................................................
   def loadConditionID(self,conditionid):

      rows = arcpy.da.SearchCursor(
          in_table     = self.conditions_layer.dataSource
         ,field_names  = self.fields
         ,where_clause = "conditionid = " + util.sql_quote(conditionid)
      );

      for row in rows:
         self.conditionid              = row[0];
         self.roadtolls                = row[1];
         self.misccost                 = row[2];
         self.totalcostmultiplier      = row[3];
         self.vehicledeconcost         = row[4];
         self.stagingsitecost          = row[5];
         self.numberoftrucksavailable  = row[6];
         self.drivinghours             = row[7];

      del rows;

   #...........................................................................
   def upsertConditionID(self
      ,conditionid
      ,roadtolls
      ,misccost
      ,totalcostmultiplier
      ,vehicledeconcost
      ,stagingsitecost
      ,numberoftrucksavailable
      ,drivinghours
   ):

      existing_ids = self.fetchConditionIDs();

      if conditionid in existing_ids:

         with arcpy.da.UpdateCursor(
             in_table     = self.conditions_layer.dataSource
            ,field_names  = self.fields
            ,where_clause = "conditionid = " + util.sql_quote(conditionid)
         ) as cursor:

            for row in cursor:
               row[1] = roadtolls;
               row[2] = misccost;
               row[3] = totalcostmultiplier;
               row[4] = vehicledeconcost;
               row[5] = stagingsitecost;
               row[6] = numberoftrucksavailable;
               row[7] = drivinghours;

               cursor.updateRow(
                  row
               );

      else:

         cursor = arcpy.da.InsertCursor(
             in_table    = self.conditions_layer.dataSource
            ,field_names = self.fields
         );
         cursor.insertRow(
            (
                conditionid
               ,roadtolls
               ,misccost
               ,totalcostmultiplier
               ,vehicledeconcost
               ,stagingsitecost
               ,numberoftrucksavailable
               ,drivinghours
            )
         );

      del cursor;
