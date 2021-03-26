import arcpy,os

###############################################################################
class DisposalFees:

   factorid         = None;
   wastetype        = None;
   wastemedium      = None;
   disposalcost     = None;
   unit             = None;

   fields = (
       'factorid'
      ,'wastetype'
      ,'wastemedium'
      ,'disposalcost'
      ,'unit'
   );

   #...........................................................................
   def __init__(self
      ,factorid
      ,wastetype
      ,wastemedium
      ,disposalcost
      ,unit
   ):

      self.factorid         = factorid;
      self.wastetype        = wastetype;
      self.wastemedium      = wastemedium;
      self.disposalcost     = disposalcost;
      self.unit             = unit;
      