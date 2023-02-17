import arcpy,os

###############################################################################
class Layer:

   #...........................................................................
   def __init__(self
      ,layer = None
   ):
      #////////////////////////////////////////////////////////////////////////
      self.layer          = None;
      self.dataSource     = None;
      self.datasetName    = None;
      self.name           = None;   
      #////////////////////////////////////////////////////////////////////////
      
      if layer is not None:

         self.layer          = layer;
         self.dataSource     = layer.dataSource;
         self.datasetName    = os.path.basename(layer.dataSource);
         self.name           = layer.name;

   #...........................................................................
   def recordCount(self
      ,fieldname = None
      ,value     = None
      ,fieldtype = "String"
   ):
      if fieldname is None:
         return int(
            arcpy.GetCount_management(
               self.dataSource
            ).getOutput(0)
         );

      else:

         if fieldtype == "String":
            delim = "'";
         else:
            delim = "";

         rows = arcpy.da.SearchCursor(
             in_table     = self.dataSource
            ,field_names  = (
               fieldname
             )
            ,where_clause = fieldname + " = " + delim + value + delim
         );

         output = 0;

         for row in rows:
            output =+ 1;

         return output;

   #...........................................................................
   def lyr(self):

      return self.layer;