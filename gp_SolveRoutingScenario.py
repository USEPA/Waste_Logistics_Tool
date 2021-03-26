import arcpy,os,sys;
import json;

import util;
import obj_AllHazardsWasteLogisticsTool;
import obj_NetworkAnalysisDataset;

###############################################################################
import importlib
importlib.reload(util);
importlib.reload(obj_AllHazardsWasteLogisticsTool);
importlib.reload(obj_NetworkAnalysisDataset);

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
   scenarioid               = util.clean_id(parameters[2].valueAsText);
   numberoffacilitiestofind = parameters[3].value;
   old_scenarioid           = parameters[4].valueAsText;
   unit_system              = parameters[5].valueAsText;

   #########################################################################
   # Step 30
   # Initialize the haz toc object
   #########################################################################
   haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

   #########################################################################
   # Step 40
   # Update the properties of the analysis as requested
   #########################################################################
   lyrx_target = haz.network.createLayerFile();

   with open(lyrx_target,"r") as jsonFile_target:
      data_target = json.load(jsonFile_target);

   for item in data_target["layerDefinitions"]:
      if item["name"] == "Network":
         item["solver"]["defaultTargetFacilityCount"] = numberoffacilitiestofind;

   with open(lyrx_target,"w") as jsonFile:
      json.dump(data_target,jsonFile);

   haz.network = obj_NetworkAnalysisDataset.NetworkAnalysisDataset(layerfile=lyrx_target);
   arcpy.AddMessage("Network analysis parameters adjusted.");

   #########################################################################
   # Step 50
   # Solve the network analysis
   #########################################################################
   arcpy.na.Solve(
       in_network_analysis_layer = haz.network.lyr()
      ,ignore_invalids           = "HALT"
      ,terminate_on_solve_error  = "TERMINATE"
      ,simplification_tolerance  = None
   );
   arcpy.AddMessage("Network routing scenario solve complete.");

   #########################################################################
   # Step 60
   # Check for results
   #########################################################################
   record_count = haz.network.routes.recordCount();

   if record_count == 0:
      arcpy.AddMessage("Warning, no results returned from network solve.");

   arcpy.AddMessage("Route Count = " + str(record_count) + ".");

   #########################################################################
   # Step 70
   # Persist the system objects
   #########################################################################
   haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
   haz.system_cache.writeSystemCache('current_scenarioid',scenarioid);

   if scenarioid != old_scenarioid:

      haz.scenario.duplicateScenarioID(
          sourceid = old_scenarioid
         ,targetid = scenarioid
      );

   #########################################################################
   # Step 80
   # Update the routes tables with attribute from facilities table
   #########################################################################
   curDict = {};

   cursor_in = arcpy.da.SearchCursor(
       in_table     = haz.network.facilities.dataSource
      ,field_names  = (
          'objectid'
         ,'facility_identifier'
         ,'facility_name'
         ,'facility_address'
         ,'facility_city'
         ,'facility_state'
         ,'facility_zip'
         ,'facility_telephone'
         ,'facility_waste_mgt'
         ,'facility_capacity_trucks_perday'
         ,'facility_qty_accepted_volume_solid'
         ,'facility_qty_accepted_volume_solid_unit'
         ,'facility_qty_accepted_volume_liquid'
         ,'facility_qty_accepted_volume_liquid_unit'
       )
   );

   for row in cursor_in:
      curDict[row[0]] = row[1:14];

   del cursor_in;

   cursor_out = arcpy.da.UpdateCursor(
       in_table     = haz.network.routes.dataSource
      ,field_names  = (
          'facilityid'
         ,'facility_identifier'
         ,'facility_name'
         ,'facility_address'
         ,'facility_city'
         ,'facility_state'
         ,'facility_zip'
         ,'facility_telephone'
         ,'facility_waste_mgt'
         ,'facility_capacity_trucks_perday'
         ,'facility_qty_accepted_volume_solid'
         ,'facility_qty_accepted_volume_solid_unit'
         ,'facility_qty_accepted_volume_liquid'
         ,'facility_qty_accepted_volume_liquid_unit'
      )
   );

   for row in cursor_out:
      if row[0] in curDict:
         row[1]  = curDict[row[0]][0];
         row[2]  = curDict[row[0]][1];
         row[3]  = curDict[row[0]][2];
         row[4]  = curDict[row[0]][3];
         row[5]  = curDict[row[0]][4];
         row[6]  = curDict[row[0]][5];
         row[7]  = curDict[row[0]][6];
         row[8]  = curDict[row[0]][7];
         row[9]  = curDict[row[0]][8];
         row[10] = curDict[row[0]][9];
         row[11] = curDict[row[0]][10];
         row[12] = curDict[row[0]][11];
         row[13] = curDict[row[0]][12];

         cursor_out.updateRow(row);

   del cursor_out;

   arcpy.AddMessage("Routes attributes loaded.");

   #########################################################################
   # Step 90
   #
   #########################################################################
   del jsonFile_target;
   del jsonFile;
   del haz;

   return;
