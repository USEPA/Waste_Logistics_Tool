import arcpy,os

###############################################################################
class LaborCosts:

   fields = (
       'factorid'
      ,'mode'
      ,'laborcategory'
      ,'laborcost'
      ,'laborcostunit'
   );

   #...........................................................................
   def __init__(self
      ,factorid
      ,mode
      ,laborcategory
      ,laborcost
      ,laborcostunit
   ):
      #////////////////////////////////////////////////////////////////////////
      self.factorid         = None;
      self.mode             = None;
      self.laborcategory    = None;
      self.laborcost        = None;
      self.laborcostunit    = None;
      #////////////////////////////////////////////////////////////////////////

      self.factorid         = factorid;
      self.mode             = mode;
      self.laborcategory    = laborcategory;
      self.laborcost        = laborcost;
      self.laborcostunit    = laborcostunit;
