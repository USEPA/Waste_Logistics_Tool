import arcpy,os

###############################################################################
class Modes:

   fields = (
       'factorid'
      ,'mode'
      ,'name'
      ,'description'
   );

   #...........................................................................
   def __init__(self
      ,factorid
      ,mode
      ,name
      ,description
   ):
      #////////////////////////////////////////////////////////////////////////
      self.factorid         = None;
      self.mode             = None;
      self.name             = None;
      self.description      = None;
      #////////////////////////////////////////////////////////////////////////

      self.factorid         = factorid;
      self.mode             = mode
      self.name             = name;
      self.description      = description;
