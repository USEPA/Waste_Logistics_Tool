import arcpy,os

###############################################################################
class FacilityCapacities:

   fields = (
       'facilityattributesid'
      ,'facility_subtypeid'
      ,'wastetype'
      ,'wastemedium'
      ,'dailyvolumeperday'
      ,'dailyvolumeperdayunit'
      ,'totalaccepted_days'
   );

   #...........................................................................
   def __init__(self
      ,facilityattributesid
      ,facility_subtypeid
      ,wastetype
      ,wastemedium
      ,dailyvolumeperday
      ,dailyvolumeperdayunit
      ,totalaccepted_days
   ):
      #////////////////////////////////////////////////////////////////////////
      self.facilityattributesid  = None;
      self.facility_subtypeid    = None;
      self.wastetype             = None;
      self.wastemedium           = None;
      self.dailyvolumeperday     = None;
      self.dailyvolumeperdayunit = None;
      self.totalaccepted_days    = None;
      #////////////////////////////////////////////////////////////////////////

      self.facilityattributesid  = facilityattributesid;
      self.facility_subtypeid    = facility_subtypeid;
      self.wastetype             = wastetype;
      self.wastemedium           = wastemedium;
      self.dailyvolumeperday     = dailyvolumeperday;
      self.dailyvolumeperdayunit = dailyvolumeperdayunit;
      self.totalaccepted_days    = totalaccepted_days;
      