import arcpy,os,sys,zipfile;
from importlib.util import spec_from_loader, module_from_spec;
from importlib.machinery import SourceFileLoader;

File_Network_Dataset = r"C:\Users\PDziemiela\Documents\ArcGIS\Projects\frarail\truckrail.gdb\allhaz_fra_here2019\allhaz_fra_here2019";

###############################################################################
# Step 10
# Add project path to python path and import util forcing project to aprx file
###############################################################################
project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)));
print("Step 10: Importing utilities from project at " + project_root + os.sep + "source" + os.sep + "util.py");
sys.path.append(project_root);
import source.util;
source.util.g_prj = source.util.g_pn + os.sep + "AllHazardsWasteLogisticsTool.aprx";

###############################################################################
# Step 20
# Short circuit the toolbox and load the tool class directly in order to 
# access the parameters.  ArcPy remains a buggy mess and these contortions are
# the only way I can test the tools without just recreating steps from scratch
###############################################################################
toolbx = os.path.join(source.util.g_pn,"AllHazardsWasteLogisticsTool.pyt");
print("Step 20: Sideloading project toolbox from " + toolbx);
spec = spec_from_loader(
    'ahsideloaded'
   ,SourceFileLoader(
       'ahsideloaded'
      ,toolbx
   )
);
module = module_from_spec(spec);
spec.loader.exec_module(module);
sys.modules['ahsideloaded'] = module;
import ahsideloaded;
source.util.g_prj = source.util.g_pn + os.sep + "AllHazardsWasteLogisticsTool.aprx";

###############################################################################
# Step 30
# Set project common variables
###############################################################################
print("Step 30: Loading workspace, project and map.")
wrksp = os.path.join(source.util.g_pn,"AllHazardsWasteLogisticsTool.gdb");
arcpy.env.workspace = wrksp;
print("  workspace: " + str(wrksp));
arcpy.env.scratchWorkspace = os.path.join(source.util.g_pn,"scratch.gdb");
arcpy.env.overwriteOutput = True;
if source.util.g_aprx is None:
   source.util.g_aprx = arcpy.mp.ArcGISProject(source.util.g_prj);
print("  project: " + str(source.util.g_aprx.filePath));
map  = source.util.g_aprx.listMaps("AllHazardsWasteLogisticsMap")[0];
print("  map: AllHazardsWasteLogisticsMap");
wgs  = arcpy.SpatialReference(4326);
wbm  = arcpy.SpatialReference(3857);

###############################################################################
# Step 40
# Pull default parameters for CreateWorkEnvironment
###############################################################################
print("Step 40: Setting CreateWorkEnvironment parameters."); 
ah = ahsideloaded.CreateWorkEnvironment();
parameters = ah.getParameterInfo();
parameters[1].value  = 'US Customary';
parameters[2].value  = 'File Network Dataset';
parameters[3].value  = File_Network_Dataset;
parameters[8].value  = 'TruckRail_DistanceKm';
parameters[9].value  = 'Impedance_DistanceKm';
parameters[10].value = 'Overall_DistanceKm';
parameters[11].value = 'km';
parameters[12].value = 'Overall_TimeOfTravelMin';
parameters[13].value = 'min';
parameters[14].value = 'Truck_DistanceKm';
parameters[15].value = 'km';
parameters[16].value = 'Truck_TimeOfTravelMin';
parameters[17].value = 'min';
parameters[18].value = 'Rail_DistanceKm';
parameters[19].value = 'km';
parameters[20].value = 'Rail_TimeOfTravelMin';
parameters[21].value = 'min';
parameters[22].value = 'Station_Count';
parameters[23].value = 'False';
print("  ProjectUnitSystem: "            + str(parameters[1].valueAsText));
print("  NetworkDatasetType: "           + str(parameters[2].valueAsText));
print("  FileNetworkDataset: "           + str(parameters[3].valueAsText));
print("  RemoteNetworkDataset: "         + str(parameters[4].valueAsText));
print("  CurrentPortal: "                + str(parameters[5].valueAsText));
print("  PortalUsername: "               + str(parameters[6].valueAsText));
print("  ArcGISOnlineAvailableCredits: " + str(parameters[7].valueAsText));
print("  NetworkDatasetTravelMode: "     + str(parameters[8].valueAsText));
print("  NetworkImpedanceField: "        + str(parameters[9].valueAsText));
print("  OverallDistanceField: "         + str(parameters[10].valueAsText));
print("  OverallDistanceFieldUnit: "     + str(parameters[11].valueAsText));
print("  OverallTimeField: "             + str(parameters[12].valueAsText));
print("  OverallTimeFieldUnit: "         + str(parameters[13].valueAsText));
print("  RoadDistanceField: "            + str(parameters[14].valueAsText));
print("  RoadDistanceFieldUnit: "        + str(parameters[15].valueAsText));
print("  RoadTimeField: "                + str(parameters[16].valueAsText));
print("  RoadTimeFieldUnit: "            + str(parameters[17].valueAsText));
print("  RailDistanceField: "            + str(parameters[18].valueAsText));
print("  RailDistanceFieldUnit: "        + str(parameters[19].valueAsText));
print("  RailTimeField: "                + str(parameters[20].valueAsText));
print("  RailTimeFieldUnit: "            + str(parameters[21].valueAsText));
print("  StationCountField: "            + str(parameters[22].valueAsText));
print("  isAGO: "                        + str(parameters[23].valueAsText));

###############################################################################
# Step 50
# Run CreateWorkEnvironment
###############################################################################
print("Step 50: Executing gp_createWorkEnvironment...");
messages = None;
rez = ah.execute(parameters,messages);

###############################################################################
# Step 280
# Reload the settings file for kicks
###############################################################################
#print("Step 280: Reload the settings file for kicks."); 
#ah = ahsideloaded.ReloadProjectSettings();
#parameters = ah.getParameterInfo();
#print("  ProjectSettingsLastUpdatedDate: " + str(parameters[1].valueAsText));
#print("  ProjectSettingsLastUpdatedBy: "   + str(parameters[2].valueAsText));
#print("  FileSettingsLastUpdatedDate: "    + str(parameters[3].valueAsText));
#print("  FileSettingsLastUpdatedBy: "      + str(parameters[4].valueAsText));

###############################################################################
# Step 290
# Run ReloadProjectSettings
###############################################################################
#print("Step 290: Executing gp_ReloadProjectSettings.");
#messages = None;
#rez = ah.execute(parameters,messages);

###############################################################################
# Step 60
# Get references to the editable layers
###############################################################################
print("Step 60: Get references to the editable layers.");
for lyr in map.listLayers():
   print(lyr.name)
   if lyr.supports("name") and lyr.name == "SupportArea":
      sup = lyr;
      print("  Found SupportArea")
   if lyr.supports("name") and lyr.name == "IncidentArea":
      inc = lyr;
      print("  Found Incident")
   if lyr.supports("name") and lyr.name == "Line Barriers":
      lbr = lyr;
      print("  Found Line Barrier")

###############################################################################
# Step 70
# Draw support area
###############################################################################
print("Step 70: Draw the support area.");
arcpy.TruncateTable_management(sup.dataSource);
coordinates = [
    (-94.951416629999983, 39.918790872000045)
   ,(-96.671484689999943, 43.880140937000078)
   ,(-91.913849629999959, 46.003928857000062)
   ,(-87.174513166999986, 44.366152376000059)
   ,(-87.156214570999964, 41.362749042000075)
   ,(-90.340170341999965, 40.324572096000054)
]
with arcpy.da.InsertCursor(sup.dataSource,['SHAPE@']) as cur:
   cur.insertRow([coordinates])
sup.visible = False;
sup.visible = True;

###############################################################################
# Step 80
# Draw incident area
###############################################################################
print("Step 80: Draw the incident area.");
arcpy.TruncateTable_management(inc.dataSource);
coordinates = [
    (-90.136083025999937, 43.099873853000076)
   ,(-90.134423901999980, 43.099025845000028)
   ,(-90.136193633999937, 43.097975913000028)
   ,(-90.137631540999962, 43.099025845000028)
];
with arcpy.da.InsertCursor(inc.dataSource,['SHAPE@']) as cur:
   cur.insertRow([coordinates]);
inc.visible = False;
inc.visible = True;

###############################################################################
# Step 90
# Pull default parameters for DefineScenario
###############################################################################
print("Step 90: Setting DefineScenario parameters."); 
ah = ahsideloaded.DefineScenario();
parameters = ah.getParameterInfo();
parameters[3].value = 'Construction and Demolition';
parameters[4].value = 'Volume Solid';
parameters[5].value = 'm3';
parameters[6].value = 2000000;
print("  scenarioid: " + source.util.clean_id(parameters[2].valueAsText));
print("  waste_type: " + str(parameters[3].valueAsText));
print("  waste_medium: " + str(parameters[4].valueAsText));
print("  waste_unit: " + str(parameters[5].valueAsText));
print("  waste_amount: " + str(parameters[6].value));

###############################################################################
# Step 100
# Run DefineScenario
###############################################################################
print("Step 100: Executing gp_DefineScenario.");
messages = None;
rez = ah.execute(parameters,messages);

###############################################################################
# Step 110
# Pull default parameters for SetScenarioConditions
###############################################################################
print("Step 110: Setting SetScenarioConditions parameters."); 
ah = ahsideloaded.SetScenarioConditions();
parameters = ah.getParameterInfo();
parameters[2].value = 'High';
print("  ConditionID: "              + str(parameters[2].valueAsText));
print("  NewConditionSetID: "        + str(source.util.clean_id(parameters[3].valueAsText)));
print("  RoadTollsPerRoadShipment: " + str(parameters[4].value));
print("  MiscCostPerRoadShipment: "  + str(parameters[5].value));
print("  MiscCostPerRailShipment: "  + str(parameters[6].value));
print("  RoadTransporterDeconCost: " + str(parameters[7].value));
print("  RailTransporterDeconCost: " + str(parameters[8].value));
print("  StagingSiteCost: "          + str(parameters[9].value));
print("  RoadDrivingHoursPerDay: "   + str(parameters[10].value));
print("  RailDrivingHoursPerDay: "   + str(parameters[11].value));
print("  TotalCostMultiplier: "      + str(parameters[12].value));
print("  FactorSetID: "              + str(parameters[13].value));
print("  Facility Attributes ID: "   + str(parameters[14].value));
print("  accepting all defaults.");

###############################################################################
# Step 120
# Run SetScenarioConditions
###############################################################################
print("Step 120: Executing gp_setScenarioConditions.");
messages = None;
rez = ah.execute(parameters,messages);

###############################################################################
# Step 130
# Pull default parameters for SetTransporterAttributes
###############################################################################
print("Step 110: Setting SetTransporterAttributes parameters."); 
ah = ahsideloaded.SetTransporterAttributes();
parameters = ah.getParameterInfo();
print("  Waste Type: "                           + str(parameters[2].valueAsText));
print("  Waste Medium: "                         + str(parameters[3].valueAsText));
print("  RoadTransporterAttributesName: "        + str(parameters[4].value));
print("  NewRoadTransporterAttributesName: "     + str(parameters[5].value));
print("  RoadTransporterContainerCapacity: "     + str(parameters[6].value));
print("  RoadTransporterContainerCapacityUnit: " + str(parameters[7].value));
print("  RoadTransporterContainerCountPerTransporter: " + str(parameters[8].value));
print("  RoadTransportersAvailable: "            + str(parameters[9].value));
print("  RoadTransportersProcessedPerDay: "      + str(parameters[10].value));
print("  RailTransporterAttributesName: "        + str(parameters[11].value));
print("  NewRailTransporterAttributesName: "     + str(parameters[12].value));
print("  RailTransporterContainerCapacity: "     + str(parameters[13].value));
print("  RailTransporterContainerCapacityUnit: " + str(parameters[14].value));
print("  RailTransporterContainerCountPerTransporter: " + str(parameters[15].value));
print("  RailTransportersAvailable: "            + str(parameters[16].value));
print("  RailTransportersProcessedPerDay: "      + str(parameters[17].value));
print("  accepting all defaults.");

###############################################################################
# Step 140
# Run SetScenarioConditions
###############################################################################
print("Step 140: Executing gp_SetTransporterAttributes.");
messages = None;
rez = ah.execute(parameters,messages);

###############################################################################
# Step 150
# Unpack if needed the userdefined examples
###############################################################################
print("Step 150: Validate the userdefined examples.");
example_gdb = project_root + os.sep + 'data' + os.sep + 'ExampleUserData.gdb';
example_zip = project_root + os.sep + 'data' + os.sep + 'ExampleUserData.gdb.zip';
if not arcpy.Exists(example_gdb):
   with zipfile.ZipFile(example_zip) as zf:
      zf.extractall(project_root + os.sep + 'data');

###############################################################################
# Step 160
# Pull default parameters for LoadFacilitiesToNetwork
###############################################################################
print("Step 160: Setting LoadFacilitiesToNetwork parameters."); 
ah = ahsideloaded.LoadFacilitiesToNetwork();
parameters = ah.getParameterInfo();
parameters[4].value = example_gdb + os.sep + 'UserDefinedFacilities2;';
print("  IWasteDisposalFacilitySubTypes: " + str(parameters[2].valueAsText));
print("  loadDefaultFacilities: "          + str(parameters[3].valueAsText));
print("  ary_user_defined: "               + str(parameters[4].valueAsText));
print("  limitBySupport: "                 + str(parameters[5].valueAsText));
print("  truncateFacilities: "             + str(parameters[6].value));

###############################################################################
# Step 170
# Run LoadFacilitiesToNetwork
###############################################################################
print("Step 170: Executing gp_LoadFacilitiesToNetwork.");
messages = None;
rez = ah.execute(parameters,messages);

###############################################################################
# Step 180
# Export all facilities to user defined dataset
###############################################################################
print("Step 180: Export all facilities to user defined dataset."); 
target = wrksp + os.sep + 'houseonrock_userdefined';
if arcpy.Exists(target):
   arcpy.Delete_management(target);
   
ah = ahsideloaded.ExportFacilitiesToUserDataset();
parameters = ah.getParameterInfo();
parameters[1].value = target;
print("  ExportFacilityDataset: " + str(parameters[1].valueAsText));
print("  OptionalQueryClause: "   + str(parameters[2].valueAsText));

###############################################################################
# Step 190
# Run ExportFacilitiesToUserDataset
###############################################################################
print("Step 190: Executing gp_ExportFacilitiesToUserDataset.");
messages = None;
rez = ah.execute(parameters,messages);

###############################################################################
# Step 200
# Reload the results back in as user defined facilities
###############################################################################
print("Step 200: Setting LoadFacilitiesToNetwork parameters."); 
ah = ahsideloaded.LoadFacilitiesToNetwork();
parameters = ah.getParameterInfo();
parameters[3].value = 'False';
parameters[4].value = target + ';';
parameters[5].value = 'True';
parameters[6].value = 'True';
print("  IWasteDisposalFacilitySubTypes: " + str(parameters[2].valueAsText));
print("  loadDefaultFacilities: "          + str(parameters[3].valueAsText));
print("  ary_user_defined: "               + str(parameters[4].valueAsText));
print("  limitBySupport: "                 + str(parameters[5].valueAsText));
print("  truncateFacilities: "             + str(parameters[6].value));

###############################################################################
# Step 210
# Run LoadFacilitiesToNetwork
###############################################################################
print("Step 210: Executing gp_LoadFacilitiesToNetwork.");
messages = None;
rez = ah.execute(parameters,messages);

###############################################################################
# Step 220
# Pull default parameters for SolveRoutingScenario
###############################################################################
print("Step 220: Setting SolveRoutingScenario parameters."); 
ah = ahsideloaded.SolveRoutingScenario();
parameters = ah.getParameterInfo();
parameters[3].value = 10;
print("  scenarioid: "               + source.util.clean_id(parameters[2].valueAsText));
print("  numberoffacilitiestofind: " + str(parameters[3].value));
print("  old_scenarioid: "           + str(parameters[4].valueAsText));
print("  unit_system: "              + str(parameters[5].value));

###############################################################################
# Step 230
# Run SolveRoutingScenario
###############################################################################
print("Step 230: Executing gp_SolveRoutingScenario.");
messages = None;
rez = ah.execute(parameters,messages);

###############################################################################
# Step 240
# Pull default parameters for CalculateLogisticsPlanningEstimates
###############################################################################
print("Step 240: Setting CalculateLogisticsPlanningEstimates parameters."); 
ah = ahsideloaded.CalculateLogisticsPlanningEstimates();
parameters = ah.getParameterInfo();
parameters[6].value = 'Zoom to Support Area';
print("  Scenario ID: "          + source.util.clean_id(parameters[2].valueAsText));
print("  Condition ID: "         + str(parameters[3].valueAsText));
print("  Factor ID: "            + str(parameters[4].valueAsText));
print("  Facility Attributes ID" + str(parameters[5].valueAsText));
print("  Map Settings: "         + str(parameters[6].value));
print("  Stashed Scenario ID: "  + str(parameters[7].valueAsText));
print("  Stashed Condition ID: " + str(parameters[8].valueAsText));
print("  Stashed Facility Attributes ID: " + str(parameters[9].valueAsText));
print("  Stashed Road Transporter: "       + str(parameters[10].valueAsText));
print("  Stashed Rail Transporter: "       + str(parameters[11].valueAsText));

###############################################################################
# Step 250
# Run CalculateLogisticsPlanningEstimates
###############################################################################
print("Step 250: Executing gp_CalculateLogisticsPlanningEstimates.");
messages = None;
rez = ah.execute(parameters,messages);

###############################################################################
# Step 260
# Pull default parameters for ExportLogisticsPlanningResults
###############################################################################
print("Step 260: Setting ExportLogisticsPlanningResults parameters."); 
ah = ahsideloaded.ExportLogisticsPlanningResults();
parameters = ah.getParameterInfo();
print("  dest_filename: " + str(parameters[2].valueAsText));
print("  scenarioid: " + str(parameters[3].valueAsText));
xls_fn = arcpy.CreateScratchName(
    "Output"
   ,".xlsx"
   ,"Dataset"
   ,arcpy.env.scratchFolder
);
print("  force filename to " + str(xls_fn));
parameters[2].value = xls_fn;

###############################################################################
# Step 270
# Run ExportLogisticsPlanningResults
###############################################################################
print("Step 270: Executing gp_ExportLogisticsPlanningResults.");
messages = None;
rez = ah.execute(parameters,messages);

###############################################################################
# Step 300
# Save the aprx
###############################################################################
print("Step 300: Saving aprx.");
source.util.g_aprx.saveACopy(source.util.g_prj);
print("Script complete.");

