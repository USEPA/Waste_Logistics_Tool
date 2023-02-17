import arcpy,os,sys;

import source.util;
import source.obj_Layer;

###############################################################################
import importlib
importlib.reload(source.util);
importlib.reload(source.obj_Layer);

###############################################################################
class Condition:

   fields = (
       'conditionid'
       
      ,'roadtollsperroadshipment'
      
      ,'misccostperroadshipment'
      ,'misccostperrailshipment'
      
      ,'roadtransporterdeconcost'
      ,'railtransporterdeconcost'
      
      ,'stagingsitecost'
      
      ,'roaddrivinghoursperday'
      ,'raildrivinghoursperday'
      
      ,'totalcostmultiplier'
   );

   #...........................................................................
   def __init__(self
      ,conditions_layer = None
   ):
      #////////////////////////////////////////////////////////////////////////
      self.conditions_layer             = None;
      self.conditionid                  = None;
      
      self.roadtollsperroadshipment     = None;
      
      self.misccostperroadshipment      = None;
      self.misccostperrailshipment      = None;
      
      self.roadtransporterdeconcost     = None;
      self.railtransporterdeconcost     = None;
      
      self.stagingsitecost              = None;
      
      self.roaddrivinghoursperday       = None;
      self.raildrivinghoursperday       = None;
      
      self.totalcostmultiplier          = None;
      #////////////////////////////////////////////////////////////////////////

      if conditions_layer is not None:
         self.conditions_layer = conditions_layer;

      else:
         self.conditions_layer = source.obj_Layer.Layer(
            source.util.fetch_lyr("Conditions")
         );

   #...........................................................................
   def totalRecordCount(self):

      if self.conditions_layer.dataSource is None:
         return 0;      
      else:
         return int(
            arcpy.GetCount_management(
               self.conditions_layer.dataSource
            ).getOutput(0)
         );

   #...........................................................................
   def fetchConditionIDs(self):

      output = [];
      if self.conditions_layer.dataSource is not None:
         rows = arcpy.da.SearchCursor(
             in_table     = self.conditions_layer.dataSource
            ,field_names  = (
                'conditionid'
             )
            ,where_clause = None
         );

         for row in rows:
            output.append(row[0]);

         del rows;

      return output;

   #...........................................................................
   def loadConditionID(self,conditionid):

      if conditionid is None or self.conditions_layer.dataSource is None:
      
         self.conditionid                 = None;
         
         self.roadtollsperroadshipment    = None;
         
         self.misccostperroadshipment     = None;
         self.misccostperrailshipment     = None;
         
         self.roadtransporterdeconcost    = None;
         self.railtransporterdeconcost    = None;
         
         self.stagingsitecost             = None;
         
         self.roaddrivinghoursperday      = None;
         self.raildrivinghoursperday      = None;
         
         self.totalcostmultiplier         = None;
         
         self.conditions_layer            = source.obj_Layer.Layer();
         self.conditions_layer.dataSource = None;
         
      else:         
      
         with arcpy.da.SearchCursor(
             in_table     = self.conditions_layer.dataSource
            ,field_names  = self.fields
            ,where_clause = "conditionid = " + source.util.sql_quote(conditionid)
         ) as cursor:

            for row in cursor:
               self.conditionid                = row[0];
               
               self.roadtollsperroadshipment   = row[1];
               
               self.misccostperroadshipment    = row[2];
               self.misccostperrailshipment    = row[3];
               
               self.roadtransporterdeconcost   = row[4];
               self.railtransporterdeconcost   = row[5];
               
               self.stagingsitecost            = row[6];
               
               self.roaddrivinghoursperday     = row[7];
               self.raildrivinghoursperday     = row[8];
               
               self.totalcostmultiplier        = row[9];

   #...........................................................................
   def upsertConditionID(self
      ,conditionid
      
      ,roadtollsperroadshipment
      
      ,misccostperroadshipment
      ,misccostperrailshipment
      
      ,roadtransporterdeconcost
      ,railtransporterdeconcost
      
      ,stagingsitecost
      
      ,roaddrivinghoursperday
      ,raildrivinghoursperday
      
      ,totalcostmultiplier
   ):

      existing_ids = self.fetchConditionIDs();

      if conditionid in existing_ids:

         with arcpy.da.UpdateCursor(
             in_table     = self.conditions_layer.dataSource
            ,field_names  = self.fields
            ,where_clause = "conditionid = " + source.util.sql_quote(conditionid)
         ) as cursor:

            for row in cursor:
               row[1] = roadtollsperroadshipment;
               
               row[2] = misccostperroadshipment;
               row[3] = misccostperrailshipment;
               
               row[4] = roadtransporterdeconcost;
               row[5] = railtransporterdeconcost;
               
               row[6] = stagingsitecost;
               
               row[7] = roaddrivinghoursperday;
               row[8] = raildrivinghoursperday;

               row[9] = totalcostmultiplier;
               
               cursor.updateRow(row);

      else:

         with arcpy.da.InsertCursor(
             in_table    = self.conditions_layer.dataSource
            ,field_names = self.fields
         ) as cursor:
            cursor.insertRow(
               (
                   conditionid
                   
                  ,roadtollsperroadshipment
                  
                  ,misccostperroadshipment
                  ,misccostperrailshipment
                  
                  ,roadtransporterdeconcost
                  ,railtransporterdeconcost
                  
                  ,stagingsitecost
                  
                  ,roaddrivinghoursperday
                  ,raildrivinghoursperday
                  
                  ,totalcostmultiplier
               )
            );
