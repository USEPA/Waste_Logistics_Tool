import arcpy,os

###############################################################################
class ShipmentLoading:

   factorid         = None;
   vehicle          = None;
   wastetype        = None;
   wastemedium      = None;
   loadingrate      = None;
   unitpershipment  = None;

   fields = (
       'factorid'
      ,'vehicle'
      ,'wastetype'
      ,'wastemedium'
      ,'loadingrate'
      ,'unitpershipment'
   );

   #...........................................................................
   def __init__(self
      ,factorid
      ,vehicle
      ,wastetype
      ,wastemedium
      ,loadingrate
      ,unitpershipment
   ):

      self.factorid         = factorid;
      self.vehicle          = vehicle;
      self.wastetype        = wastetype;
      self.wastemedium      = wastemedium;
      self.loadingrate      = loadingrate;
      self.unitpershipment  = unitpershipment;
