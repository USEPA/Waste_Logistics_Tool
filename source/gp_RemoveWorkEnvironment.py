import arcpy,os,sys;

import source.util;

###############################################################################
import importlib
importlib.reload(source.util);

def execute(self,parameters,messages):
   
   #########################################################################
   # Step 10 
   # Abend if edits are pending
   #########################################################################
   if source.util.sniff_editing_state():
      raise arcpy.ExecuteError("Error.  Pending edits must be saved or cleared before proceeding.");

   #########################################################################
   # Step 20 
   # Verify the map
   #########################################################################
   if source.util.g_aprx is None:
      aprx = arcpy.mp.ArcGISProject(source.util.g_prj);
   else:
      aprx = source.util.g_aprx;
   
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

   arcpy.AddMessage("  Map Cleanup Complete.");
   
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
      ,"Modes"
      ,"Transporters"
      ,"CPLMUnitRates"
      ,"FixedTransCost"
      ,"LaborCosts"
      ,"DisposalFees"
      ,"FacilityCapacities"
      ,"SystemCache"
      ,"ClosestFacility"
   ]:
   
      for suf in ["","1","2","3","4","5","6","7","8","9"]:
      
         if arcpy.Exists(os.path.join(arcpy.env.workspace,rez + suf)):

            arcpy.Delete_management(os.path.join(arcpy.env.workspace,rez + suf));
        
   #########################################################################
   # Step 60 
   # Cleanup preexisting network dataset components
   #########################################################################
   datasets = arcpy.ListDatasets("ClosestFacilitySolver*");
   for item in datasets:
      arcpy.Delete_management(aprx.defaultGeodatabase + os.sep + item);
   
   arcpy.AddMessage("  Database Cleanup Complete.");
   
   return;
   
   