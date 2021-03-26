import arcpy,os

###############################################################################
class LaborCosts:

   factorid         = None;
   laborcategory    = None;
   laborcost        = None;
   unit             = None;

   fields = (
       'factorid'
      ,'laborcategory'
      ,'laborcost'
      ,'unit'
   );

   #...........................................................................
   def __init__(self
      ,factorid
      ,laborcategory
      ,laborcost
      ,unit
   ):

      self.factorid         = factorid;
      self.laborcategory    = laborcategory;
      self.laborcost        = laborcost;
      self.unit             = unit;
