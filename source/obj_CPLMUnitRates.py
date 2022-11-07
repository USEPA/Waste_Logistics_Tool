import arcpy,os

###############################################################################
class CPLMUnitRates:

   fields = (
       'factorid'
      ,'mode'
      ,'cplmdist_lower'
      ,'cplmdist_upper'
      ,'cplmunit'
      ,'wastetype'
      ,'wastemedium'
      ,'cplunit_rate'
      ,'cplunit_rateunit'
   );

   #...........................................................................
   def __init__(self
      ,factorid
      ,mode
      ,cplmdist_lower
      ,cplmdist_upper
      ,cplmunit
      ,wastetype
      ,wastemedium
      ,cplunit_rate
      ,cplunit_rateunit
   ):
      #////////////////////////////////////////////////////////////////////////
      self.factorid         = None;
      self.mode             = None;
      self.cplmdist_lower   = None;
      self.cplmdist_upper   = None;
      self.cplmunit         = None;
      self.wastetype        = None;
      self.wastemedium      = None;
      self.cplunit_rate     = None;
      self.cplunit_rateunit = None;
      #////////////////////////////////////////////////////////////////////////

      self.factorid         = factorid;
      self.mode             = mode;
      self.cplmdist_lower   = cplmdist_lower;
      self.cplmdist_upper   = cplmdist_upper;
      self.cplmunit         = cplmunit;
      self.wastetype        = wastetype;
      self.wastemedium      = wastemedium;
      self.cplunit_rate     = cplunit_rate;
      self.cplunit_rateunit = cplunit_rateunit;
