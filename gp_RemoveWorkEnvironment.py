import arcpy,os;

import util;

###############################################################################
import importlib
importlib.reload(util);

def execute(self, parameters, messages):
   
   #########################################################################
   # Step 10 
   # Abend if edits are pending
   #########################################################################
   if util.sniff_editing_state():
      raise arcpy.ExecuteError("Error.  Pending edits must be saved or cleared before proceeding.");

   #########################################################################
   # Step 20 
   # Verify the map
   #########################################################################
   aprx = arcpy.mp.ArcGISProject("CURRENT");
   map = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];
   
   if map is None:
      raise arcpy.ExecuteError("Error.  Project map not found.");
   
   #########################################################################
   # Step 40 
   # Remove the AllHazardsWaste folder and all contents
   #########################################################################
   for lyr in map.listLayers():
   
      if lyr is not None and lyr.supports("name") and  \
      ( lyr.name == "AllHazardsWasteLogisticsTool"  or lyr.longName == "AllHazardsWasteLogisticsTool" ):
         map.removeLayer(lyr);

   arcpy.AddMessage("Map Cleanup Complete.");
   
   #########################################################################
   # Step 50 
   # Cleanup preexisting workspace resources in database
   #########################################################################
   for rez in [
       "ScenarioResults"
      ,"IncidentArea"
      ,"SupportArea"
      ,"UserProvidedFacilities"
      ,"Conditions"
      ,"Scenario"
      ,"ShipmentLoading"
      ,"CPLMUnitRates"
      ,"FixedTransCost"
      ,"LaborCosts"
      ,"DisposalFees"
      ,"SystemCache"
      ,"ClosestFacility"
   ]:
   
      for suf in ["","1","2","3","4","5","6","7","8","9"]:
      
         if arcpy.Exists(os.path.join(arcpy.env.workspace,rez + suf)):

            arcpy.Delete_management(os.path.join(arcpy.env.workspace,rez + suf));
        
   arcpy.AddMessage("Database Cleanup Complete.");
   
   return;
   
   