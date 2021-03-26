import arcpy,os

###############################################################################
class CPLMUnitRates:

   factorid         = None;
   vehicle          = None;
   cplmdist_lower   = None;
   cplmdist_upper   = None;
   cplmunit         = None;
   wastetype        = None;
   wastemedium      = None;
   cplunit_rate     = None;
   unit             = None;

   fields = (
       'factorid'
      ,'vehicle'
      ,'cplmdist_lower'
      ,'cplmdist_upper'
      ,'cplmunit'
      ,'wastetype'
      ,'wastemedium'
      ,'cplunit_rate'
      ,'unit'
   );

   #...........................................................................
   def __init__(self
      ,factorid
      ,vehicle
      ,cplmdist_lower
      ,cplmdist_upper
      ,cplmunit
      ,wastetype
      ,wastemedium
      ,cplunit_rate
      ,unit
   ):

      self.factorid         = factorid;
      self.vehicle          = vehicle;
      self.cplmdist_lower   = cplmdist_lower;
      self.cplmdist_upper   = cplmdist_upper;
      self.cplmunit         = cplmunit;
      self.wastetype        = wastetype;
      self.wastemedium      = wastemedium;
      self.cplunit_rate     = cplunit_rate;
      self.unit             = unit;
