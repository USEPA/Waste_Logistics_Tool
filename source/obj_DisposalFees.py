import arcpy,os

###############################################################################
class DisposalFees:

   fields = (
       'facilityattributesid'
      ,'facility_subtypeid'
      ,'wastetype'
      ,'wastemedium'
      ,'costperone'
      ,'costperoneunit'
   );

   #...........................................................................
   def __init__(self
      ,facilityattributesid
      ,facility_subtypeid
      ,wastetype
      ,wastemedium
      ,costperone
      ,costperoneunit
   ):
      #////////////////////////////////////////////////////////////////////////
      self.facilityattributesid = None;
      self.facility_subtypeid   = None;
      self.wastetype            = None;
      self.wastemedium          = None;
      self.costperone           = None;
      self.costperoneunit       = None;
      #////////////////////////////////////////////////////////////////////////

      self.facilityattributesid = facilityattributesid;
      self.facility_subtypeid   = facility_subtypeid;
      self.wastetype            = wastetype;
      self.wastemedium          = wastemedium;
      self.costperone           = costperone;
      self.costperoneunit       = costperoneunit;
      