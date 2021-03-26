import arcpy,os,sys;
from decimal import Decimal;

import util;
import obj_AllHazardsWasteLogisticsTool;

###############################################################################
import importlib
importlib.reload(util);
importlib.reload(obj_AllHazardsWasteLogisticsTool);

def execute(self, parameters, messages):
   
   #########################################################################
   # Step 10
   # Abend if edits are pending
   #########################################################################
   if util.sniff_editing_state():
      raise arcpy.ExecuteError("Error.  Pending edits must be saved or cleared before proceeding.");
      
   #########################################################################
   # Step 20 
   # Read the parameters
   #########################################################################
   scenarioid   = util.clean_id(parameters[2].valueAsText);
   waste_type   = parameters[3].valueAsText;
   waste_medium = parameters[4].valueAsText;
   waste_unit   = parameters[5].valueAsText;
   waste_amount = parameters[6].value;
   
   #########################################################################
   # Step 30 
   # Initialize the haz toc object
   #########################################################################
   haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
   
   #########################################################################
   # Step 40 
   # Check if the Incident Area has content
   #########################################################################
   if haz.incident_area.recordCount() == 0:
      raise arcpy.ExecuteError("Error.  Incident Area Feature Class is empty.");
      
   #########################################################################
   # Step 50 
   # Load the incidents as requested
   #########################################################################
   incident_temp = arcpy.CreateScratchName(
       "Incident_Centroid"
      ,""
      ,"FeatureClass"
      ,arcpy.env.scratchGDB
   );
   
   util.polygons_to_points(
       in_features       = haz.incident_area.dataSource
      ,out_feature_class = incident_temp
   );
   
   str_fm = "Name Name #;"              \
          + "CurbApproach # 0;"         \
          + "Attr_Minutes # 0;"         \
          + "Attr_TravelTime # 0;"      \
          + "Attr_Miles # 0;"           \
          + "Attr_Kilometers # 0;"      \
          + "Attr_TimeAt1KPH # 0;"      \
          + "Attr_WalkTime # 0;"        \
          + "Attr_TruckMinutes # 0;"    \
          + "Attr_TruckTravelTime # 0;" \
          + "Cutoff_Minutes # #;"       \
          + "Cutoff_TravelTime # #;"    \
          + "Cutoff_Miles # #;"         \
          + "Cutoff_Kilometers # #;"    \
          + "Cutoff_TimeAt1KPH # #;"    \
          + "Cutoff_WalkTime # #;"      \
          + "Cutoff_TruckMinutes # #;"  \
          + "Cutoff_TruckTravelTime # #";               
   
   arcpy.na.AddLocations(
       in_network_analysis_layer      = haz.network.lyr()
      ,sub_layer                      = haz.network.incidents.name
      ,in_table                       = incident_temp
      ,field_mappings                 = str_fm
      ,search_tolerance               = None
      ,sort_field                     = None
      ,search_criteria                = None
      ,match_type                     = None
      ,append                         = False
      ,snap_to_position_along_network = None
      ,snap_offset                    = None
      ,exclude_restricted_elements    = None
      ,search_query                   = None
   );
   
   arcpy.AddMessage("Network Incidents Layer loaded.");
      
   #########################################################################
   # Step 60 
   # Persist the waste amounts
   #########################################################################
   haz.scenario.upsertScenarioID(
       scenarioid   = scenarioid
      ,waste_type   = waste_type
      ,waste_medium = waste_medium
      ,waste_amount = waste_amount
      ,waste_unit   = waste_unit
   );
   haz.system_cache.set_current_scenarioid(scenarioid);
  
   del haz;
   
   return;
      