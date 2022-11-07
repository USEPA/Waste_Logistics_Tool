import arcpy,os

###############################################################################
class Transporters:

   fields = (
       'transporterattrid'
      ,'mode'
      ,'wastetype'
      ,'wastemedium'
      ,'containercapacity'
      ,'containercapacityunit'
      ,'containercountpertransporter'
      ,'transportersavailable'
      ,'transportersprocessedperday'
   );

   #...........................................................................
   def __init__(self
      ,transporterattrid
      ,mode
      ,wastetype
      ,wastemedium
      ,containercapacity
      ,containercapacityunit
      ,containercountpertransporter
      ,transportersavailable
      ,transportersprocessedperday
   ):
      #////////////////////////////////////////////////////////////////////////
      self.transporterattrid            = None;
      self.mode                         = None;
      self.wastetype                    = None;
      self.wastemedium                  = None;
      self.containercapacity            = None;
      self.containercapacityunit        = None;
      self.containercountpertransporter = None;
      self.transportersavailable        = None;
      self.transportersprocessedperday  = None;
      
      #////////////////////////////////////////////////////////////////////////

      self.transporterattrid            = transporterattrid;
      self.mode                         = mode;
      self.wastetype                    = wastetype;
      self.wastemedium                  = wastemedium;
      self.containercapacity            = containercapacity;
      self.containercapacityunit        = containercapacityunit;
      self.containercountpertransporter = containercountpertransporter;
      self.transportersavailable        = transportersavailable;
      self.transportersprocessedperday  = transportersprocessedperday;
      
