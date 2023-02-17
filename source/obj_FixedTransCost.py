import arcpy,os

###############################################################################
class FixedTransCost:

   fields = (
       'factorid'
      ,'mode'
      ,'fixedcost_type'
      ,'wastetype'
      ,'wastemedium'
      ,'fixedcost_value'
      ,'fixedcost_valueunit'
   );

   #...........................................................................
   def __init__(self
      ,factorid
      ,mode
      ,fixedcost_type
      ,wastetype
      ,wastemedium
      ,fixedcost_value
      ,fixedcost_valueunit
   ):
      #////////////////////////////////////////////////////////////////////////
      self.factorid             = None;
      self.mode                 = None;
      self.fixedcost_type       = None;
      self.wastetype            = None;
      self.wastemedium          = None;
      self.fixedcost_value      = None;
      self.fixedcost_valueunit  = None;
      #////////////////////////////////////////////////////////////////////////

      self.factorid             = factorid;
      self.mode                 = mode;
      self.fixedcost_type       = fixedcost_type;
      self.wastetype            = wastetype;
      self.wastemedium          = wastemedium;
      self.fixedcost_value      = fixedcost_value;
      self.fixedcost_valueunit  = fixedcost_valueunit;
