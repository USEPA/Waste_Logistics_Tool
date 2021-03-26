import arcpy,os

###############################################################################
class FixedTransCost:

   factorid         = None;
   vehicle          = None;
   fixedcost_type   = None;
   wastetype        = None;
   wastemedium      = None;
   fixedcost_value  = None;
   unit             = None;

   fields = (
       'factorid'
      ,'vehicle'
      ,'fixedcost_type'
      ,'wastetype'
      ,'wastemedium'
      ,'fixedcost_value'
      ,'unit'
   );

   #...........................................................................
   def __init__(self
      ,factorid
      ,vehicle
      ,fixedcost_type
      ,wastetype
      ,wastemedium
      ,fixedcost_value
      ,unit
   ):

      self.factorid         = factorid;
      self.vehicle          = vehicle;
      self.fixedcost_type   = fixedcost_type;
      self.wastetype        = wastetype;
      self.wastemedium      = wastemedium;
      self.fixedcost_value  = fixedcost_value;
      self.unit             = unit;
