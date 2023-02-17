import arcpy,psutil;
import sys,os,json;

###############################################################################
import source.gp_CreateWorkEnvironment;
import source.gp_SetScenarioConditions;
import source.gp_DefineScenario;
import source.gp_SetTransporterAttributes;
import source.gp_LoadFacilitiesToNetwork;
import source.gp_SolveRoutingScenario;
import source.gp_CalculateLogisticsPlanningEstimates;
import source.gp_ExportLogisticsPlanningResults;
import source.gp_RemoveWorkEnvironment;
import source.gp_QueryIWasteFacilities;
import source.gp_UpdateIWasteFacilities;
import source.gp_ReloadProjectSettings;
import source.gp_ExportFacilitiesToUserDataset;
import source.util;
import source.obj_NetworkDataset;
import source.obj_AllHazardsWasteLogisticsTool;
import source.obj_Waste;
import source.obj_Condition;
import source.obj_ParmFramework;

###############################################################################
import importlib
try:
   importlib.reload(source.gp_CreateWorkEnvironment);
   importlib.reload(source.gp_SetScenarioConditions);
   importlib.reload(source.gp_DefineScenario);
   importlib.reload(source.gp_SetTransporterAttributes);
   importlib.reload(source.gp_LoadFacilitiesToNetwork);
   importlib.reload(source.gp_SolveRoutingScenario);
   importlib.reload(source.gp_CalculateLogisticsPlanningEstimates);
   importlib.reload(source.gp_ExportLogisticsPlanningResults);
   importlib.reload(source.gp_RemoveWorkEnvironment);
   importlib.reload(source.gp_QueryIWasteFacilities);
   importlib.reload(source.gp_UpdateIWasteFacilities);
   importlib.reload(source.gp_ReloadProjectSettings);
   importlib.reload(source.gp_ExportFacilitiesToUserDataset);
   importlib.reload(source.util);
   importlib.reload(source.obj_NetworkDataset);
   importlib.reload(source.obj_AllHazardsWasteLogisticsTool);
   importlib.reload(source.obj_Waste);
   importlib.reload(source.obj_Condition);
   importlib.reload(source.obj_ParmFramework);

except:
   pass;
   
nd = None;

###############################################################################
class Toolbox(object):

   def __init__(self):

      self.label = "AllHazardsWasteLogisticsTool";
      self.alias = "ahtoolbox";

      self.tools = [
          CreateWorkEnvironment
         ,DefineScenario
         ,SetScenarioConditions
         ,SetTransporterAttributes
         ,LoadFacilitiesToNetwork
         ,SolveRoutingScenario
         ,CalculateLogisticsPlanningEstimates
         ,ExportLogisticsPlanningResults
         ,RemoveWorkEnvironment
         ,ClearScenarios
         ,ClearFacilities
         ,QueryIWasteFacilities
         ,UpdateIWasteFacilities
         ,ReloadProjectSettings
         ,ExportFacilitiesToUserDataset
      ];
      
###############################################################################
def flushmem(noflush):
   
   if noflush != 1:
      global g_frmwrk1;
      g_frmwrk1 = None;
      del g_frmwrk1;
      
   if noflush != 2:
      global g_frmwrk2;
      g_frmwrk2 = None;
      del g_frmwrk2;
      
   if noflush != 3:
      global g_frmwrk3;
      g_frmwrk3 = None;
      del g_frmwrk3;
      
   if noflush != 4:
      global g_frmwrk4;
      g_frmwrk4 = None;
      del g_frmwrk4;
      
   if noflush != 5:
      global g_frmwrk5;
      g_frmwrk5 = None;
      del g_frmwrk5;
      
   if noflush != 6:
      global g_frmwrk6;
      g_frmwrk6 = None;
      del g_frmwrk6;
      
   if noflush != 7:
      global g_frmwrk7;
      g_frmwrk7 = None;
      del g_frmwrk7;
      
   if noflush != 8:
      global g_frmwrk8;
      g_frmwrk8 = None;
      del g_frmwrk8;
      
   if noflush != 9:
      global g_frmwrk9;
      g_frmwrk9 = None;
      del g_frmwrk9;
      
   if noflush != 10:
      global g_frmwrk10;
      g_frmwrk10 = None;
      del g_frmwrk10;
      
   if noflush != 11:
      global g_frmwrk11;
      g_frmwrk11 = None;
      del g_frmwrk11;
         
   if noflush != 12:
      global g_frmwrk12;
      g_frmwrk12 = None;
      del g_frmwrk12;
         
   if noflush != 13:
      global g_frmwrk13;
      g_frmwrk13 = None;
      del g_frmwrk13;
      
   if noflush != 14:
      global g_frmwrk14;
      g_frmwrk14 = None;
      del g_frmwrk14;
      
   if noflush != 15:
      global g_frmwrk15;
      g_frmwrk15 = None;
      del g_frmwrk15;
               
###############################################################################
class CreateWorkEnvironment(object):

   #...........................................................................
   def __init__(self):

      self.label              = "T1 Create Work Environment"
      self.name               = "CreateWorkEnvironment"
      self.description        = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      mem = psutil.Process().memory_info().rss / 1024 ** 2;
      source.util.dzlog('Entering CreateWorkEnvironment Form: ' + str(mem) + ' MB','DEBUG');
      flushmem(noflush=1);
      global g_frmwrk1;

      # Commented out
      # ,"filter.list"  : ["Portal Helper","Remote Network Dataset","File Network Dataset"]
      g_frmwrk1 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : "Project Unit System"
               ,"name"         : "ProjectUnitSystem"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : ["Metric","US Customary"]
             }
            ,{
                "displayName"  : "Network Dataset Type"
               ,"name"         : "NetworkDatasetType"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : ["Portal Helper","File Network Dataset"]
             }
            ,{
                "displayName"  : "File Network Dataset"
               ,"name"         : "FileNetworkDataset"
               ,"datatype"     : "GPNetworkDatasetLayer"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Remote Network Dataset"
               ,"name"         : "RemoteNetworkDataset"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Current Portal"
               ,"name"         : "CurrentPortal"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Portal Username"
               ,"name"         : "PortalUsername"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "ArcGIS Online Available Credits"
               ,"name"         : "ArcGISOnlineAvailableCredits"
               ,"datatype"     : "GPLong"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Network Dataset Travel Mode"
               ,"name"         : "NetworkDatasetTravelMode"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Network Impedance Field"
               ,"name"         : "NetworkImpedanceField"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Overall Distance Field"
               ,"name"         : "OverallDistanceField"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Overall Distance Field Unit"
               ,"name"         : "OverallDistanceFieldUnit"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Overall Time Field"
               ,"name"         : "OverallTimeField"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Overall Time Field Unit"
               ,"name"         : "OverallTimeFieldUnit"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Road Distance Field"
               ,"name"         : "RoadDistanceField"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Road Distance Field Unit"
               ,"name"         : "RoadDistanceFieldUnit"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Road Time Field"
               ,"name"         : "RoadTimeField"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Road Time Field Unit"
               ,"name"         : "RoadTimeFieldUnit"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Rail Distance Field"
               ,"name"         : "RailDistanceField"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Rail Distance Field Unit"
               ,"name"         : "RailDistanceFieldUnit"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Rail Time Field"
               ,"name"         : "RailTimeField"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Rail Time Field Unit"
               ,"name"         : "RailTimeFieldUnit"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "Station Count Field"
               ,"name"         : "StationCountField"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
            ,{
                "displayName"  : "ArcGIS Online Routing for Credits"
               ,"name"         : "isAGO"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"category"     : "Network Dataset Characteristics"
             }
          ]
      });
      
      #########################################################################
      try:
         jd = source.util.load_settings();
      except:
         g_frmwrk1.setErrorCode(99,"settings.json configuration file is invalid.");
         return g_frmwrk1.getParms();
         
      if jd is None:
         project_unit_system_value = "Metric";
      else:
         project_unit_system_value = jd["SystemCache"]["Default_Unit_System"];

      g_frmwrk1.setParmValueByName(
          name    = "ProjectUnitSystem"
         ,value   = project_unit_system_value
      );
      
      #########################################################################
      starting_nd_type     = " "; 
      starting_nd_file     = None;
      starting_nd_file_e   = False;
      starting_nd_remote   = None;
      starting_nd_remote_e = False;
      portal_info  = source.util.portal_info();
      
      if 'portal_url' in portal_info:
         nd = source.obj_NetworkDataset.NetworkDataset(
             network_dataset      = portal_info['portal_url']
            ,network_dataset_type = 'PortalHelper'
         );
         
         isAGO                = portal_info['isAGO']
         starting_nd_type     = 'Portal Helper';
         starting_nd_file     = None;
         starting_nd_file_e   = False;
         starting_nd_remote   = None;
         starting_nd_remote_e = False;
         
         if 'error' in nd.describe:
            msg = 'Portal Error: ' + str(nd.describe['error']['message'].replace("'",""));
            g_frmwrk1.setErrorCode(1,msg);
            isAGO                = False;
            starting_nd_file     = None;
            starting_nd_file_e   = False;
            starting_nd_remote   = None;
            starting_nd_remote_e = False;

      else:
         isAGO                = False;
         starting_nd_type     = 'Remote Network Dataset';
         starting_nd_file     = None;
         starting_nd_file_e   = False;
         starting_nd_remote   = None;
         starting_nd_remote_e = True;
         
         nd = source.obj_NetworkDataset.NetworkDataset();
      
      g_frmwrk1.setParmValueByName(
          name    = "NetworkDatasetType"
         ,value   = starting_nd_type
      );
      
      g_frmwrk1.setParmValueByName(
          name    = "FileNetworkDataset"
         ,value   = starting_nd_file
      );
      
      g_frmwrk1.setParmEnabledByName(
          name    = "FileNetworkDataset"
         ,value   = starting_nd_file_e
      );
      
      g_frmwrk1.setParmValueByName(
          name    = "RemoteNetworkDataset"
         ,value   = starting_nd_remote
      );
      
      g_frmwrk1.setParmEnabledByName(
          name    = "RemoteNetworkDataset"
         ,value   = starting_nd_remote_e
      );
      
      g_frmwrk1.setParmValueByName(
          name    = "CurrentPortal"
         ,value   = portal_info['portal_url']
      );

      g_frmwrk1.setParmValueByName(
          name    = "PortalUsername"
         ,value   = portal_info['username']
      );
      
      g_frmwrk1.setParmValueByName(
          name    = "ArcGISOnlineAvailableCredits"
         ,value   = portal_info['availableCredits']
      );

      g_frmwrk1.setParmValueByName(
          name    = "NetworkDatasetTravelMode"
         ,value   = nd.current_travel_mode
         ,filter_list = nd.getTravelModeNames()
      );
      
      g_frmwrk1.setParmValueByName(
          name    = "NetworkImpedanceField"
         ,value   = nd.getCurrentTravelModeImpedanceAttributeName()
      );
      
      bocd = nd.bestOverallCost('distance');
      g_frmwrk1.setParmValueByName(
          name    = "OverallDistanceField"
         ,value   = bocd
         ,filter_list = nd.getDistanceCostNames(add_empty=False)
      );

      g_frmwrk1.setParmValueByName(
          name    = "OverallDistanceFieldUnit"
         ,value   = nd.costUnit(bocd)
      );

      boct = nd.bestOverallCost('time');
      g_frmwrk1.setParmValueByName(
          name    = "OverallTimeField"
         ,value   = boct
         ,filter_list = nd.getTimeCostNames(add_empty=False)
      );

      g_frmwrk1.setParmValueByName(
          name    = "OverallTimeFieldUnit"
         ,value   = nd.costUnit(boct)
      );
      
      btcd = nd.bestRoadCost('distance');
      g_frmwrk1.setParmValueByName(
          name    = "RoadDistanceField"
         ,value   = btcd
         ,filter_list = nd.getDistanceCostNames(add_empty=True)
      );

      g_frmwrk1.setParmValueByName(
          name    = "RoadDistanceFieldUnit"
         ,value   = nd.costUnit(btcd)
      );

      btct = nd.bestRoadCost('time');
      g_frmwrk1.setParmValueByName(
          name    = "RoadTimeField"
         ,value   = btct
         ,filter_list = nd.getTimeCostNames(add_empty=True)
      );

      g_frmwrk1.setParmValueByName(
          name    = "RoadTimeFieldUnit"
         ,value   = nd.costUnit(btct)
      );
      
      brcd = nd.bestRailCost('distance');
      g_frmwrk1.setParmValueByName(
          name    = "RailDistanceField"
         ,value   = brcd
         ,filter_list = nd.getDistanceCostNames(add_empty=True)
      );

      g_frmwrk1.setParmValueByName(
          name    = "RailDistanceFieldUnit"
         ,value   = nd.costUnit(brcd)
      );

      brct = nd.bestRailCost('time');
      g_frmwrk1.setParmValueByName(
          name    = "RailTimeField"
         ,value   = brct
         ,filter_list = nd.getTimeCostNames(add_empty=True)
      );

      g_frmwrk1.setParmValueByName(
          name    = "RailTimeFieldUnit"
         ,value   = nd.costUnit(brct)
      );
      
      g_frmwrk1.setParmValueByName(
          name    = "StationCountField"
         ,value   = nd.bestStationCost()
         ,filter_list = nd.getIntegerCostNames(add_empty=True)
      );
      
      g_frmwrk1.setParmValueByName(
          name    = "isAGO"
         ,value   = str(isAGO)
      );
      
      g_frmwrk1.setStash("PortalInfo",portal_info);
      ndt = g_frmwrk1.getParmValueByName("NetworkDatasetType");
      g_frmwrk1.setStash(ndt + "NetworkDataset",nd);
      
      source.util.dzlog('Exiting CreateWorkEnvironment Form','DEBUG');
      return g_frmwrk1.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self,parameters):
      
      global g_frmwrk1;
      global nd;
      
      travel_mode = parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].valueAsText;
      
      nd_type = parameters[g_frmwrk1.getIndexByName("NetworkDatasetType")];
      nd_type_v = g_frmwrk1.getParmValueByName("NetworkDatasetType");
      
      if  nd_type.altered and not nd_type.hasBeenValidated and nd_type.valueAsText is not None \
      and nd_type.valueAsText != nd_type_v:
      
         parameters[0].enabled = False;
         parameters[0].value   = None;
         parameters[0].clearMessage();
         
         if nd_type.valueAsText == "Remote Network Dataset":
         
            parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled           = False;
            parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].value             = None;
            parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled         = True;
            
            parameters[g_frmwrk1.getIndexByName("CurrentPortal")].enabled                = False;
            parameters[g_frmwrk1.getIndexByName("CurrentPortal")].value                  = None;
            parameters[g_frmwrk1.getIndexByName("PortalUsername")].enabled               = False;
            parameters[g_frmwrk1.getIndexByName("PortalUsername")].value                 = None;
            parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = False;
            parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].value   = None;
            
            parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].value       = None;
            parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].filter.list = [];
            
            parameters[g_frmwrk1.getIndexByName("NetworkImpedanceField")].value          = None;
            
            parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].value           = None;
            parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].filter.list     = [];
            parameters[g_frmwrk1.getIndexByName("OverallDistanceFieldUnit")].value       = None;
            
            parameters[g_frmwrk1.getIndexByName("OverallTimeField")].value               = None;
            parameters[g_frmwrk1.getIndexByName("OverallTimeField")].filter.list         = [];
            parameters[g_frmwrk1.getIndexByName("OverallTimeFieldUnit")].value           = None;
            
            parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].value              = None;
            parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].filter.list        = [];
            parameters[g_frmwrk1.getIndexByName("RoadDistanceFieldUnit")].value          = None;

            parameters[g_frmwrk1.getIndexByName("RoadTimeField")].value                  = None;
            parameters[g_frmwrk1.getIndexByName("RoadTimeField")].filter.list            = [];
            parameters[g_frmwrk1.getIndexByName("RoadTimeFieldUnit")].value              = None;

            parameters[g_frmwrk1.getIndexByName("RailDistanceField")].value              = None;
            parameters[g_frmwrk1.getIndexByName("RailDistanceField")].filter.list        = [];
            parameters[g_frmwrk1.getIndexByName("RailDistanceFieldUnit")].value          = None;

            parameters[g_frmwrk1.getIndexByName("RailTimeField")].value                  = None;
            parameters[g_frmwrk1.getIndexByName("RailTimeField")].filter.list            = [];
            parameters[g_frmwrk1.getIndexByName("RailTimeFieldUnit")].value              = None;
            
            parameters[g_frmwrk1.getIndexByName("StationCountField")].value              = None;
            
            parameters[g_frmwrk1.getIndexByName("isAGO")].value                          = None;
            
            g_frmwrk1.refreshFromParameters(parameters);
            
         elif nd_type.valueAsText == "File Network Dataset":
         
            parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled           = True;
            parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].value           = None;
            parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled         = False;
            
            parameters[g_frmwrk1.getIndexByName("CurrentPortal")].enabled                = False;
            parameters[g_frmwrk1.getIndexByName("CurrentPortal")].value                  = None;
            parameters[g_frmwrk1.getIndexByName("PortalUsername")].enabled               = False;
            parameters[g_frmwrk1.getIndexByName("PortalUsername")].value                 = None;
            parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = False;
            parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].value   = None;
            
            parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].value       = None;
            parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].filter.list = [];
            
            parameters[g_frmwrk1.getIndexByName("NetworkImpedanceField")].value          = None;
            
            parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].value           = None;
            parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].filter.list     = [];
            parameters[g_frmwrk1.getIndexByName("OverallDistanceFieldUnit")].value       = None;
            
            parameters[g_frmwrk1.getIndexByName("OverallTimeField")].value               = None;
            parameters[g_frmwrk1.getIndexByName("OverallTimeField")].filter.list         = [];
            parameters[g_frmwrk1.getIndexByName("OverallTimeFieldUnit")].value           = None;
            
            parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].value              = None;
            parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].filter.list        = [];
            parameters[g_frmwrk1.getIndexByName("RoadDistanceFieldUnit")].value          = None;

            parameters[g_frmwrk1.getIndexByName("RoadTimeField")].value                  = None;
            parameters[g_frmwrk1.getIndexByName("RoadTimeField")].filter.list            = [];
            parameters[g_frmwrk1.getIndexByName("RoadTimeFieldUnit")].value              = None;

            parameters[g_frmwrk1.getIndexByName("RailDistanceField")].value              = None;
            parameters[g_frmwrk1.getIndexByName("RailDistanceField")].filter.list        = [];
            parameters[g_frmwrk1.getIndexByName("RailDistanceFieldUnit")].value          = None;

            parameters[g_frmwrk1.getIndexByName("RailTimeField")].value                  = None;
            parameters[g_frmwrk1.getIndexByName("RailTimeField")].filter.list            = [];
            parameters[g_frmwrk1.getIndexByName("RailTimeFieldUnit")].value              = None;
            
            parameters[g_frmwrk1.getIndexByName("StationCountField")].value              = None;
            
            parameters[g_frmwrk1.getIndexByName("isAGO")].value                          = None;
            
            g_frmwrk1.refreshFromParameters(parameters);
         
         elif nd_type.value == "Portal Helper":
            
            portal_info = g_frmwrk1.getStash("PortalInfo");

            nd = source.obj_NetworkDataset.NetworkDataset(
                network_dataset      = portal_info['portal_url']
               ,network_dataset_type = 'PortalHelper'
               ,current              = None
            );
            g_frmwrk1.setStash("Portal HelperNetworkDataset",nd);
            
            if 'error' in nd.describe:
               parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled            = False;
               parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].value              = None;
               parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled          = False;
               parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].value            = None;
               
               parameters[g_frmwrk1.getIndexByName("CurrentPortal")].value                   = portal_info['portal_url'];
               parameters[g_frmwrk1.getIndexByName("CurrentPortal")].enabled                 = True;
               parameters[g_frmwrk1.getIndexByName("PortalUsername")].value                  = portal_info['username'];
               parameters[g_frmwrk1.getIndexByName("PortalUsername")].enabled                = True;
               
               if portal_info['isAGO']:
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].value   = portal_info['availableCredits'];
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = True;
               else:
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].value   = None;
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = False;
                  
               msg = 'Portal Error: ' + str(nd.describe['error']['message'].replace("'",""));
               parameters[0].enabled = True;
               parameters[0].value = msg;
               parameters[0].setErrorMessage(msg);
               
            elif portal_info['username'] is None:
               parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled            = False;
               parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].value              = None;
               parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled          = False;
               parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].value            = None;
               
               parameters[g_frmwrk1.getIndexByName("CurrentPortal")].value                   = portal_info['portal_url'];
               parameters[g_frmwrk1.getIndexByName("PortalUsername")].value                  = portal_info['username'];
               
               if portal_info['isAGO']:
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].value   = portal_info['availableCredits'];
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = True;
               else:
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].value   = None;
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = False;
                  
               parameters[0].enabled = True;
               parameters[0].value = "** User is not logged into a Portal **";
               parameters[0].setErrorMessage("** User is not logged into Portal **");
               
            else:
               parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled            = False;
               parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].value              = None;
               parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled          = False;
               parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].value            = None;
               
               parameters[g_frmwrk1.getIndexByName("CurrentPortal")].value                   = portal_info['portal_url'];
               parameters[g_frmwrk1.getIndexByName("CurrentPortal")].enabled                 = True;
               parameters[g_frmwrk1.getIndexByName("PortalUsername")].value                  = portal_info['username'];
               parameters[g_frmwrk1.getIndexByName("PortalUsername")].enabled                = True;
               
               if portal_info['isAGO']:
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].value   = portal_info['availableCredits'];
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = True;
               else:
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].value   = None;
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = False;
               
            parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].value       = nd.current_travel_mode;
            parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].filter.list = nd.getTravelModeNames();
            
            parameters[g_frmwrk1.getIndexByName("NetworkImpedanceField")].value          = nd.getCurrentTravelModeImpedanceAttributeName();
            
            bocd = nd.bestOverallCost('distance');
            parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].value       = bocd;
            parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].filter.list = nd.getDistanceCostNames(add_empty=False);
            parameters[g_frmwrk1.getIndexByName("OverallDistanceFieldUnit")].value   = nd.costUnit(bocd);
            
            boct = nd.bestOverallCost('time');
            parameters[g_frmwrk1.getIndexByName("OverallTimeField")].value           = boct;
            parameters[g_frmwrk1.getIndexByName("OverallTimeField")].filter.list     = nd.getTimeCostNames(add_empty=False);
            parameters[g_frmwrk1.getIndexByName("OverallTimeFieldUnit")].value       = nd.costUnit(boct);
            
            btcd = nd.bestRoadCost('distance');
            parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].value          = btcd;
            parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].filter.list    = nd.getDistanceCostNames(add_empty=True);
            parameters[g_frmwrk1.getIndexByName("RoadDistanceFieldUnit")].value      = nd.costUnit(btcd);
            btct = nd.bestRoadCost('time');
            parameters[g_frmwrk1.getIndexByName("RoadTimeField")].value              = btct;
            parameters[g_frmwrk1.getIndexByName("RoadTimeField")].filter.list        = nd.getTimeCostNames(add_empty=True);
            parameters[g_frmwrk1.getIndexByName("RoadTimeFieldUnit")].value          = nd.costUnit(btct);
            
            brcd = nd.bestRailCost('distance');
            parameters[g_frmwrk1.getIndexByName("RailDistanceField")].value          = brcd;
            parameters[g_frmwrk1.getIndexByName("RailDistanceField")].filter.list    = nd.getDistanceCostNames(add_empty=True);
            parameters[g_frmwrk1.getIndexByName("RailDistanceFieldUnit")].value      = nd.costUnit(brcd);
            brct = nd.bestRailCost('time');
            parameters[g_frmwrk1.getIndexByName("RailTimeField")].value              = brct;
            parameters[g_frmwrk1.getIndexByName("RailTimeField")].filter.list        = nd.getTimeCostNames(add_empty=True);
            parameters[g_frmwrk1.getIndexByName("RailTimeFieldUnit")].value          = nd.costUnit(brct);
            
            parameters[g_frmwrk1.getIndexByName("StationCountField")].value          = nd.bestStationCost();
            parameters[g_frmwrk1.getIndexByName("StationCountField")].filter.list    = nd.getIntegerCostNames(add_empty=True);
            
            parameters[g_frmwrk1.getIndexByName("isAGO")].value                      = str(portal_info['isAGO']);
               
            g_frmwrk1.refreshFromParameters(parameters);
      
      else:
         
         nd_prm = parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")];
         nd_prm_v = g_frmwrk1.getParmValueByName("FileNetworkDataset");
         
         if  nd_prm.altered and not nd_prm.hasBeenValidated and nd_prm.valueAsText is not None \
         and nd_prm.valueAsText != nd_prm_v:
         
            if nd_type.valueAsText == 'Portal Helper':
               parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled           = False;
               parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled         = False;
               
               parameters[g_frmwrk1.getIndexByName("CurrentPortal")].enabled                = True;
               parameters[g_frmwrk1.getIndexByName("PortalUsername")].enabled               = True;
               parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = True;
               
               g_frmwrk1.refreshFromParameters(parameters);
               
            elif nd_type.valueAsText == 'Remote Network Dataset':
               parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled           = False;
               parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled         = True;
               
               parameters[g_frmwrk1.getIndexByName("CurrentPortal")].enabled                = False;
               parameters[g_frmwrk1.getIndexByName("PortalUsername")].enabled               = False;
               parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = False;
               
               g_frmwrk1.refreshFromParameters(parameters);
            
            elif nd_type.valueAsText == 'File Network Dataset':
               parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled           = True;
               parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled         = False;
               
               parameters[g_frmwrk1.getIndexByName("CurrentPortal")].enabled                = False;
               parameters[g_frmwrk1.getIndexByName("PortalUsername")].enabled               = False;
               parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = False;
               
               nd = source.obj_NetworkDataset.NetworkDataset(
                   network_dataset      = nd_prm.valueAsText
                  ,network_dataset_type = 'FileNetworkDataset'
                  ,current              = travel_mode
               );
               g_frmwrk1.setStash("File Network DatasetNetworkDataset",nd);
               
               parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].value       = nd.current_travel_mode;
               parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].filter.list = nd.getTravelModeNames();
               
               parameters[g_frmwrk1.getIndexByName("NetworkImpedanceField")].value          = nd.getCurrentTravelModeImpedanceAttributeName();
               
               bocd = nd.bestOverallCost('distance');
               parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].value       = bocd;
               parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].filter.list = nd.getDistanceCostNames(add_empty=False);
               parameters[g_frmwrk1.getIndexByName("OverallDistanceFieldUnit")].value   = nd.costUnit(bocd);
               
               boct = nd.bestOverallCost('time');
               parameters[g_frmwrk1.getIndexByName("OverallTimeField")].value           = boct;
               parameters[g_frmwrk1.getIndexByName("OverallTimeField")].filter.list     = nd.getTimeCostNames(add_empty=False);
               parameters[g_frmwrk1.getIndexByName("OverallTimeFieldUnit")].value       = nd.costUnit(boct);
               
               btcd = nd.bestRoadCost('distance');
               parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].value         = btcd;
               parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].filter.list   = nd.getDistanceCostNames(add_empty=True);
               parameters[g_frmwrk1.getIndexByName("RoadDistanceFieldUnit")].value     = nd.costUnit(btcd);
               btct = nd.bestRoadCost('time');
               parameters[g_frmwrk1.getIndexByName("RoadTimeField")].value             = btct;
               parameters[g_frmwrk1.getIndexByName("RoadTimeField")].filter.list       = nd.getTimeCostNames(add_empty=True);
               parameters[g_frmwrk1.getIndexByName("RoadTimeFieldUnit")].value         = nd.costUnit(btct);
               
               brcd = nd.bestRailCost('distance');
               parameters[g_frmwrk1.getIndexByName("RailDistanceField")].value          = brcd;
               parameters[g_frmwrk1.getIndexByName("RailDistanceField")].filter.list    = nd.getDistanceCostNames(add_empty=True);
               parameters[g_frmwrk1.getIndexByName("RailDistanceFieldUnit")].value      = nd.costUnit(brcd);
               brct = nd.bestRailCost('time');
               parameters[g_frmwrk1.getIndexByName("RailTimeField")].value              = brct;
               parameters[g_frmwrk1.getIndexByName("RailTimeField")].filter.list        = nd.getTimeCostNames(add_empty=True);
               parameters[g_frmwrk1.getIndexByName("RailTimeFieldUnit")].value          = nd.costUnit(brct);
               
               parameters[g_frmwrk1.getIndexByName("StationCountField")].value          = nd.bestStationCost();
               parameters[g_frmwrk1.getIndexByName("StationCountField")].filter.list    = nd.getIntegerCostNames(add_empty=True);
               
               parameters[g_frmwrk1.getIndexByName("isAGO")].value                      = 'False';
               
               g_frmwrk1.refreshFromParameters(parameters);
            
         else:
            
            nd_prm = parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")];
            nd_prm_v = g_frmwrk1.getParmValueByName("RemoteNetworkDataset");
         
            if nd_prm.altered and not nd_prm.hasBeenValidated and nd_prm.valueAsText is not None \
            and nd_prm.valueAsText != nd_prm_v:
               
               if nd_type.valueAsText == 'Portal Helper':
                  parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled           = False;
                  parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled         = False;
                  
                  g_frmwrk1.refreshFromParameters(parameters);
                  
               elif nd_type.valueAsText == 'File Network Dataset':
                  parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled           = True;
                  parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled         = False;
                  
                  g_frmwrk1.refreshFromParameters(parameters);
               
               elif nd_type.valueAsText == 'Remote Network Dataset':
                  parameters[g_frmwrk1.getIndexByName("FileNetworkDataset")].enabled           = False;
                  parameters[g_frmwrk1.getIndexByName("RemoteNetworkDataset")].enabled         = True;
                  
                  parameters[g_frmwrk1.getIndexByName("CurrentPortal")].enabled                = False;
                  parameters[g_frmwrk1.getIndexByName("PortalUsername")].enabled               = False;
                  parameters[g_frmwrk1.getIndexByName("ArcGISOnlineAvailableCredits")].enabled = False;
                  
                  nd = source.obj_NetworkDataset.NetworkDataset(
                      network_dataset      = nd_prm.valueAsText
                     ,network_dataset_type = 'RemoteNetworkDataset'
                     ,current              = travel_mode
                  );
                  g_frmwrk1.setStash("Remote Network DatasetNetworkDataset",nd);
                  
                  parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].value       = nd.current_travel_mode;
                  parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")].filter.list = nd.getTravelModeNames();
                  
                  parameters[g_frmwrk1.getIndexByName("NetworkImpedanceField")].value          = nd.getCurrentTravelModeImpedanceAttributeName();
                  
                  bocd = nd.bestOverallCost('distance');
                  parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].value       = bocd;
                  parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].filter.list = nd.getDistanceCostNames(add_empty=False);
                  parameters[g_frmwrk1.getIndexByName("OverallDistanceFieldUnit")].value   = nd.costUnit(bocd);
                  
                  boct = nd.bestOverallCost('time');
                  parameters[g_frmwrk1.getIndexByName("OverallTimeField")].value           = boct;
                  parameters[g_frmwrk1.getIndexByName("OverallTimeField")].filter.list     = nd.getTimeCostNames(add_empty=False);
                  parameters[g_frmwrk1.getIndexByName("OverallTimeFieldUnit")].value       = nd.costUnit(boct);
                  
                  btcd = nd.bestRoadCost('distance');
                  parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].value          = btcd;
                  parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].filter.list    = nd.getDistanceCostNames(add_empty=True);
                  parameters[g_frmwrk1.getIndexByName("RoadDistanceFieldUnit")].value      = nd.costUnit(btcd);
                  btct = nd.bestRoadCost('time');
                  parameters[g_frmwrk1.getIndexByName("RoadTimeField")].value              = btct;
                  parameters[g_frmwrk1.getIndexByName("RoadTimeField")].filter.list        = nd.getTimeCostNames(add_empty=True);
                  parameters[g_frmwrk1.getIndexByName("RoadTimeFieldUnit")].value          = nd.costUnit(btct);
                  
                  brcd = nd.bestRailCost('distance');
                  parameters[g_frmwrk1.getIndexByName("RailDistanceField")].value          = brcd;
                  parameters[g_frmwrk1.getIndexByName("RailDistanceField")].filter.list    = nd.getDistanceCostNames(add_empty=True);
                  parameters[g_frmwrk1.getIndexByName("RailDistanceFieldUnit")].value      = nd.costUnit(brcd);
                  brct = nd.bestRailCost('time');
                  parameters[g_frmwrk1.getIndexByName("RailTimeField")].value              = brct;
                  parameters[g_frmwrk1.getIndexByName("RailTimeField")].filter.list        = nd.getTimeCostNames(add_empty=True);
                  parameters[g_frmwrk1.getIndexByName("RailTimeFieldUnit")].value          = nd.costUnit(brct);
                  
                  parameters[g_frmwrk1.getIndexByName("StationCountField")].value          = nd.bestStationCost();
                  parameters[g_frmwrk1.getIndexByName("StationCountField")].filter.list    = nd.getIntegerCostNames(add_empty=True);
                  
                  parameters[g_frmwrk1.getIndexByName("isAGO")].value                      = 'False';
                  
                  g_frmwrk1.refreshFromParameters(parameters);

            else:
            
               trv_mode = parameters[g_frmwrk1.getIndexByName("NetworkDatasetTravelMode")];
               trv_mode_v = g_frmwrk1.getParmValueByName("NetworkDatasetTravelMode");
               
               if  trv_mode.altered and not trv_mode.hasBeenValidated and trv_mode.valueAsText is not None \
               and trv_mode.valueAsText != trv_mode_v:

                  ndt = parameters[g_frmwrk1.getIndexByName("NetworkDatasetType")].value;
                  nd = g_frmwrk1.getStash(ndt + "NetworkDataset");
                  nd.setCurrentTravelMode(trv_mode.valueAsText);

                  parameters[g_frmwrk1.getIndexByName("NetworkImpedanceField")].value      = nd.getCurrentTravelModeImpedanceAttributeName();
                  
                  bocd = nd.bestOverallCost('distance');
                  
                  parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].filter.list = nd.getDistanceCostNames(add_empty=False);
                  parameters[g_frmwrk1.getIndexByName("OverallDistanceField")].value       = bocd;
                  parameters[g_frmwrk1.getIndexByName("OverallDistanceFieldUnit")].value   = nd.costUnit(bocd);
                  boct = nd.bestOverallCost('time');
                  parameters[g_frmwrk1.getIndexByName("OverallTimeField")].filter.list     = nd.getTimeCostNames(add_empty=False);
                  parameters[g_frmwrk1.getIndexByName("OverallTimeField")].value           = boct;
                  parameters[g_frmwrk1.getIndexByName("OverallTimeFieldUnit")].value       = nd.costUnit(boct);
                  
                  btcd = nd.bestRoadCost('distance');
                  parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].filter.list    = nd.getDistanceCostNames(add_empty=True);
                  parameters[g_frmwrk1.getIndexByName("RoadDistanceField")].value          = btcd;
                  parameters[g_frmwrk1.getIndexByName("RoadDistanceFieldUnit")].value      = nd.costUnit(btcd);
                  btct = nd.bestRoadCost('time');
                  parameters[g_frmwrk1.getIndexByName("RoadTimeField")].filter.list        = nd.getTimeCostNames(add_empty=True);
                  parameters[g_frmwrk1.getIndexByName("RoadTimeField")].value              = btct;
                  parameters[g_frmwrk1.getIndexByName("RoadTimeFieldUnit")].value          = nd.costUnit(btct);
                  
                  brcd = nd.bestRailCost('distance');
                  parameters[g_frmwrk1.getIndexByName("RailDistanceField")].filter.list    = nd.getDistanceCostNames(add_empty=True);
                  parameters[g_frmwrk1.getIndexByName("RailDistanceField")].value          = brcd;
                  parameters[g_frmwrk1.getIndexByName("RailDistanceFieldUnit")].value      = nd.costUnit(brcd);
                  brct = nd.bestRailCost('time');
                  parameters[g_frmwrk1.getIndexByName("RailTimeField")].filter.list        = nd.getTimeCostNames(add_empty=True);
                  parameters[g_frmwrk1.getIndexByName("RailTimeField")].value              = brct;
                  parameters[g_frmwrk1.getIndexByName("RailTimeFieldUnit")].value          = nd.costUnit(brct);
                  
                  parameters[g_frmwrk1.getIndexByName("StationCountField")].filter.list    = nd.getIntegerCostNames(add_empty=True);
                  parameters[g_frmwrk1.getIndexByName("StationCountField")].value          = nd.bestStationCost();
                  
                  g_frmwrk1.refreshFromParameters(parameters);
                  
               else:
                  ndt = parameters[g_frmwrk1.getIndexByName("NetworkDatasetType")].value;
                  
                  nd = g_frmwrk1.getStash(ndt + "NetworkDataset");
                  ovr_dist = parameters[g_frmwrk1.getIndexByName("OverallDistanceField")];
                  ovr_dist_v = g_frmwrk1.getParmValueByName("OverallDistanceField");
                  
                  if  ovr_dist.altered and not ovr_dist.hasBeenValidated and ovr_dist.valueAsText is not None \
                  and ovr_dist.valueAsText != ovr_dist_v:
                     parameters[g_frmwrk1.getIndexByName("OverallDistanceFieldUnit")].value = nd.costUnit(ovr_dist.value);
                     g_frmwrk1.refreshFromParameters(parameters);
                     
                  else:
                  
                     ovr_time = parameters[g_frmwrk1.getIndexByName("OverallTimeField")];
                     ovr_time_v = g_frmwrk1.getParmValueByName("OverallTimeField");
                     
                     if  ovr_time.altered and not ovr_time.hasBeenValidated and ovr_time.valueAsText is not None \
                     and ovr_time.valueAsText != ovr_time_v:
                        parameters[g_frmwrk1.getIndexByName("OverallTimeFieldUnit")].value = nd.costUnit(ovr_time.value);
                        g_frmwrk1.refreshFromParameters(parameters);
                        
                     else:
                     
                        road_dist = parameters[g_frmwrk1.getIndexByName("RoadDistanceField")];
                        road_dist_v = g_frmwrk1.getParmValueByName("RoadDistanceField");
                        
                        if  road_dist.altered and not road_dist.hasBeenValidated and road_dist.valueAsText is not None \
                        and road_dist.valueAsText != road_dist_v:
                           parameters[g_frmwrk1.getIndexByName("RoadDistanceFieldUnit")].value = nd.costUnit(road_dist.value);
                           g_frmwrk1.refreshFromParameters(parameters);
                           
                        else:
                        
                           road_time = parameters[g_frmwrk1.getIndexByName("RoadTimeField")];
                           road_time_v = g_frmwrk1.getParmValueByName("RoadTimeField");
                           
                           if road_time.altered and not road_time.hasBeenValidated and road_time.valueAsText is not None \
                           and road_time.valueAsText != road_time_v:
                              parameters[g_frmwrk1.getIndexByName("RoadTimeFieldUnit")].value = nd.costUnit(road_time.value);
                              g_frmwrk1.refreshFromParameters(parameters);
                              
                           else:
                           
                              rail_dist = parameters[g_frmwrk1.getIndexByName("RailDistanceField")];
                              raid_dist_v = g_frmwrk1.getParmValueByName("RailDistanceField");
                              
                              if  rail_dist.altered and not rail_dist.hasBeenValidated and rail_dist.valueAsText is not None \
                              and rail_dist.valueAsText != raid_dist_v:
                                 parameters[g_frmwrk1.getIndexByName("RailDistanceFieldUnit")].value = nd.costUnit(rail_dist.value);
                                 g_frmwrk1.refreshFromParameters(parameters);
                                 
                              else:
                              
                                 rail_time = parameters[g_frmwrk1.getIndexByName("RailTimeField")];
                                 rail_time_v = g_frmwrk1.getParmValueByName("RailTimeField");
                                 
                                 if  rail_time.altered and not rail_time.hasBeenValidated and rail_time.valueAsText is not None \
                                 and rail_time.valueAsText != rail_time_v:
                                    parameters[g_frmwrk1.getIndexByName("RailTimeFieldUnit")].value = nd.costUnit(rail_time.value);
                                    g_frmwrk1.refreshFromParameters(parameters);
            
      return;

   #...........................................................................
   def updateMessages(self,parameters):

      return;

   #...........................................................................
   def execute(self,parameters,messages):

      return source.gp_CreateWorkEnvironment.execute(self,parameters,messages);
      
###############################################################################
class DefineScenario(object):

   #...........................................................................
   def __init__(self):

      self.label = "T2 Define Scenario"
      self.name  = "DefineScenario"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      source.util.dzlog('Entering DefineScenario Form','DEBUG');
      flushmem(noflush=3);
      global g_frmwrk3;
      
      g_frmwrk3 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : ""
               ,"name"         : "ScenarioCharacteristics"
               ,"datatype"     : "GPValueTable"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"category"     : "Scenario Characteristics"
               ,"columns"      : [["String","       Characteristic"],["String","Value"]] 
               ,"value"        : ""
             }
            ,{
                "displayName"  : "Scenario ID"
               ,"name"         : "ScenarioID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Waste Type"
               ,"name"         : "WasteType"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : None
             }
            ,{
                "displayName"  : "Waste Medium"
               ,"name"         : "WasteMedium"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : None
             }
            ,{
                "displayName"  : "Waste Unit"
               ,"name"         : "WasteUnit"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : None
             }
            ,{
                "displayName"  : "Waste Amount"
               ,"name"         : "WasteAmount"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
             }
          ]
      });

      #try:
      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      #except:
      #   g_frmwrk3.setErrorCode(99,"Network dataset and/or NA license appears unavailable.");
      #   return g_frmwrk3.getParms();
         
      if haz.system_cache is None:
         g_frmwrk3.setErrorCode(99,"System has not been initialized.");
         return g_frmwrk3.getParms();

      (
          scenarioid
         ,unit_system
         ,waste_type
         ,waste_medium
         ,waste_amount
         ,waste_unit
      ) = haz.current_scenario();

      if haz.system_cache.current_conditionid is None:
         conditionlist = haz.conditions.fetchConditionIDs();
         haz.system_cache.set_current_conditionid(conditionlist[0]);

      conditionid = haz.system_cache.current_conditionid;
      
      if haz.system_cache.current_factorid is None:
         factorlist = haz.factors.fetchFactorIDs();
         haz.system_cache.set_current_factorid(factorlist[0]);

      factorid = haz.system_cache.current_factorid;
      
      #########################################################################
      if source.util.sniff_editing_state():
         g_frmwrk3.setErrorCode(1,"Please save or delete all pending edits before proceeding.");
      
      #########################################################################
      (scenario_columns,scenario_value) = haz.get_scenario_characteristics();
      g_frmwrk3.setParmValueByName(
          name    = "ScenarioCharacteristics"
         ,value   = scenario_value
         ,columns = scenario_columns
      );
      
      g_frmwrk3.setParmValueByName(
          name    = "ScenarioID"
         ,value   = scenarioid
      );
      
      g_frmwrk3.setParmValueByName(
          name    = "WasteType"
         ,value   = waste_type
         ,filter_list = haz.waste.waste_types()
      );

      g_frmwrk3.setParmValueByName(
          name    = "WasteMedium"
         ,value   = waste_medium
         ,filter_list = haz.waste.waste_mediums()
      );

      g_frmwrk3.setParmValueByName(
          name    = "WasteUnit"
         ,value   = waste_unit
         ,filter_list = haz.waste.waste_units(unit_system = unit_system)
      );

      g_frmwrk3.setParmValueByName(
          name    = "WasteAmount"
         ,value   = waste_amount
      );
      
      g_frmwrk3.setStash(
          stash   = "UnitSystem"
         ,value   = unit_system
      );
      
      g_frmwrk3.setStash(
          stash   = "nd_rail_distance_field"
         ,value   = haz.system_cache.nd_rail_distance_field
      );

      del haz;
      source.util.dzlog('Exiting DefineScenario Form','DEBUG');
      return g_frmwrk3.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      global g_frmwrk3;
      
      ws = source.obj_Waste.Waste();
      unit_system = g_frmwrk3.getStash("UnitSystem");
      
      wt = parameters[g_frmwrk3.getIndexByName("WasteType")];
      wt_v = g_frmwrk3.getParmValueByName("WasteType");
      
      wm = parameters[g_frmwrk3.getIndexByName("WasteMedium")];
      wm_v = g_frmwrk3.getParmValueByName("WasteMedium");
         
      wu = parameters[g_frmwrk3.getIndexByName("WasteUnit")];
      wu_v = g_frmwrk3.getParmValueByName("WasteUnit");
      
      if  wt.altered and not wt.hasBeenValidated and wt.valueAsText is not None \
      and wt.valueAsText != wt_v:

         medium = ws.filter_medium(
             waste_type   = wt.valueAsText
            ,waste_medium = None
         );
         
         if len(medium) > 1:
            wm.value = None;
            wm.filter.list = medium + [' '];
            wu.value = None;
            wu.filter.list = [' '];

         elif len(medium) == 1:
            
            wm.value = medium[0];
            wm.filter.list = medium;

            units = ws.filter_unit(
                waste_type   = wt.valueAsText
               ,waste_medium = medium[0]
               ,unit_system  = unit_system
            );
            
            wu.value = units[0];
            wu.filter.list = units;
            
            g_frmwrk3.setParmValueByName("WasteType"   ,wt.value);
            g_frmwrk3.setParmValueByName("WasteMedium" ,wm.value);
            g_frmwrk3.setParmValueByName("WasteUnit"   ,wu.value);

      else:
      
         if wm.altered and not wm.hasBeenValidated and wm.valueAsText is not None:

            if wm.valueAsText == " ":
               wm.value = wm.filter.list[0];

               units = ws.filter_unit(
                   waste_type   = wt.valueAsText
                  ,waste_medium = wm.valueAsText
                  ,unit_system  = unit_system
               );
               
               wu.value = units[0];
               wu.filter.list = units;

            elif wm.valueAsText != wm_v:

               units = ws.filter_unit(
                   waste_type   = wt.valueAsText
                  ,waste_medium = wm.valueAsText
                  ,unit_system  = unit_system
               );

               if len(units) > 1:
                  wu.value = None;
                  wu.filter.list = units + [' '];

               elif len(units) == 1:
                  wu.value = units[0];
                  wu.filter.list = units;
                  
            g_frmwrk3.setParmValueByName("WasteMedium" ,wm.value);
            g_frmwrk3.setParmValueByName("WasteUnit"   ,wu.value);

         else:
         
            if wu.valueAsText == " " and not wu.hasBeenValidated and wu.valueAsText is not None:

               if wm.valueAsText == " " or wm.value is None:
                  wm.value = wm.filter.list[0];

               units = ws.filter_unit(
                   waste_type   = wt.valueAsText
                  ,waste_medium = wm.valueAsText
                  ,unit_system  = unit_system
               );

               wu.value = units[0];
               wu.filter.list = units;
               
               g_frmwrk3.setParmValueByName("WasteUnit",wu.value);
  
      del ws;  
      return;

   #...........................................................................
   def updateMessages(self, parameters):

      global g_frmwrk3;
      
      nd_rail_distance_field = g_frmwrk3.getStash("nd_rail_distance_field");
      new_wastetype = parameters[g_frmwrk3.getIndexByName("WasteType")].valueAsText;
      
      if new_wastetype == 'Radioactive: Remote-Handled' and nd_rail_distance_field is not None:
         
         parameters[g_frmwrk3.getIndexByName("WasteType")].setErrorMessage(
            "ERROR: Radioactive: Remote-Handled waste is not a valid selection when routing on a network that includes rail. Choose a different waste type or choose a trucking-only routing network."
         );
      
      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return source.gp_DefineScenario.execute(self,parameters,messages);


###############################################################################
class SetScenarioConditions(object):

   #...........................................................................
   def __init__(self):

      self.label = "T3 Set Scenario Conditions"
      self.name  = "SetScenarioConditions"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      source.util.dzlog('Entering SetScenarioConditions Form','DEBUG');
      flushmem(noflush=2);
      global g_frmwrk2;
      
      try:
         haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      except Exception as e:
         source.util.dzlog_e(sys.exc_info(),'ERROR');
         raise;

      (
          scenarioid
         ,unit_system
         ,waste_type
         ,waste_medium
         ,waste_amount
         ,waste_unit
      ) = haz.current_scenario();
          
      g_frmwrk2 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : ""
               ,"name"         : "ScenarioCharacteristics"
               ,"datatype"     : "GPValueTable"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"category"     : "Scenario Characteristics"
               ,"columns"      : [["String","       Characteristic"],["String","Value"]] 
               ,"value"        : ""
             }
            ,{
                "displayName"  : "Condition ID"
               ,"name"         : "ConditionID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : None
             }
            ,{
                "displayName"  : "New Condition Set ID"
               ,"name"         : "NewConditionSetID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Road Tolls ($/shipment)"
               ,"name"         : "RoadTollsPerRoadShipment"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Misc Road Cost ($/shipment)"
               ,"name"         : "MiscCostPerRoadShipment"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Misc Rail Cost ($/shipment)"
               ,"name"         : "MiscCostPerRailShipment"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Road Transporter Decon Cost ($/shipment)"
               ,"name"         : "RoadTransporterDeconCost"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Optional"
               ,"direction"    : "Required"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Rail Transporter Decon Cost ($/shipment)"
               ,"name"         : "RailTransporterDeconCost"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Optional"
               ,"direction"    : "Required"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Staging Site Cost ($/day)"
               ,"name"         : "StagingSiteCost"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Road Driving Hours (hrs/day)"
               ,"name"         : "RoadDrivingHoursPerDay"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Rail Driving Hours (hrs/day)"
               ,"name"         : "RailDrivingHoursPerDay"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Total Cost Multiplier (add % of total cost)"
               ,"name"         : "TotalCostMultiplier"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "FactorSet ID"
               ,"name"         : "FactorSetID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
             }
            ,{
                "displayName"  : "Facility Attributes ID"
               ,"name"         : "FacilityAttributesID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
             }
          ]
      }); 
      
      if haz.system_cache is None:
         g_frmwrk2.setErrorCode(99,"System has not been initialized.");
         return g_frmwrk2.getParms();

      #########################################################################
      if source.util.sniff_editing_state():
         g_frmwrk2.setErrorCode(1,"Please save or delete all pending edits before proceeding.");
      
      #########################################################################
      (scenario_columns,scenario_value) = haz.get_scenario_characteristics();
      g_frmwrk2.setParmValueByName(
          name    = "ScenarioCharacteristics"
         ,value   = scenario_value
         ,columns = scenario_columns
      );
      
      conditionid  = haz.system_cache.current_conditionid;
      conditionIDs = haz.conditions.fetchConditionIDs();
      if conditionid is None and len(conditionIDs) > 0:
         conditionid = conditionIDs[0];
         haz.system_cache.set_current_conditionid(conditionIDs[0]);
         
      factorlist = haz.factors.fetchFactorIDs();

      if haz.system_cache.current_factorid is None:
         haz.system_cache.set_current_factorid(factorlist[0]);

      factorid = haz.system_cache.current_factorid;
      
      
      
      g_frmwrk2.setParmValueByName(
          name    = "ConditionID"
         ,value   = conditionid
         ,filter_list = conditionIDs
      );
      g_frmwrk2.setStash("CurrentConditionID",conditionid);
      g_frmwrk2.setStash("ConditionIDList",conditionIDs);
      
      conditions = haz.conditions;
      conditions.loadConditionID(conditionid);
       
      g_frmwrk2.setParmValueByName(
          name    = "RoadTollsPerRoadShipment"
         ,value   = conditions.roadtollsperroadshipment
      );

      g_frmwrk2.setParmValueByName(
          name    = "MiscCostPerRoadShipment"
         ,value   = conditions.misccostperroadshipment
      );
      
      g_frmwrk2.setParmValueByName(
          name    = "MiscCostPerRailShipment"
         ,value   = conditions.misccostperrailshipment
      );

      g_frmwrk2.setParmValueByName(
          name    = "RoadTransporterDeconCost"
         ,value   = conditions.roadtransporterdeconcost
      );
      
      g_frmwrk2.setParmValueByName(
          name    = "RailTransporterDeconCost"
         ,value   = conditions.railtransporterdeconcost
      );

      g_frmwrk2.setParmValueByName(
          name    = "StagingSiteCost"
         ,value   = conditions.stagingsitecost
      );
      
      g_frmwrk2.setParmValueByName(
          name    = "RoadDrivingHoursPerDay"
         ,value   = conditions.roaddrivinghoursperday
      );
      
      g_frmwrk2.setParmValueByName(
          name    = "RailDrivingHoursPerDay"
         ,value   = conditions.raildrivinghoursperday
      );
      
      g_frmwrk2.setParmValueByName(
          name    = "TotalCostMultiplier"
         ,value   = conditions.totalcostmultiplier
      );
      
      g_frmwrk2.setParmValueByName(
          name    = "FactorSetID"
         ,value   = factorid
         ,filter_list = factorlist
      );
      
      facilityattribute_list = haz.get_facilityattributesids();
      facilityattribute_def  = haz.system_cache.current_facilityattributesid;
      if facilityattribute_def is None and len(facilityattribute_list) > 0:
         facilityattribute_def = facilityattribute_list[0];
      g_frmwrk2.setParmValueByName(
          name    = "FacilityAttributesID"
         ,value   = facilityattribute_def
         ,filter_list = facilityattribute_list
      );

      del haz;
      source.util.dzlog('Exiting SetScenarioConditions Form','DEBUG');
      return g_frmwrk2.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      global g_frmwrk2;
      
      parameters = g_frmwrk2.isAtLeast(parameters,"RoadDrivingHoursPerDay",1);
      parameters = g_frmwrk2.isAtLeast(parameters,"RailDrivingHoursPerDay",1);
         
      if not parameters[g_frmwrk2.getIndexByName("NewConditionSetID")].hasBeenValidated:

         if parameters[g_frmwrk2.getIndexByName("NewConditionSetID")].value is not None \
         and parameters[g_frmwrk2.getIndexByName("NewConditionSetID")].valueAsText != "":
            parameters[g_frmwrk2.getIndexByName("ConditionID")].value = None;
            parameters[g_frmwrk2.getIndexByName("ConditionID")].filter.list = [' '];
            g_frmwrk2.setStash("CurrentConditionID",parameters[g_frmwrk2.getIndexByName("NewConditionSetID")].value);

         elif parameters[g_frmwrk2.getIndexByName("NewConditionSetID")].value is None   \
         or parameters[g_frmwrk2.getIndexByName("NewConditionSetID")].valueAsText == "":
            parameters[g_frmwrk2.getIndexByName("ConditionID")].value       = g_frmwrk2.getStash("CurrentConditionID");
            parameters[g_frmwrk2.getIndexByName("ConditionID")].filter.list = g_frmwrk2.getStash("ConditionIDList");

      if not parameters[g_frmwrk2.getIndexByName("ConditionID")].hasBeenValidated \
      and parameters[g_frmwrk2.getIndexByName("ConditionID")].value != g_frmwrk2.getParmValueByName("ConditionID")  \
      and g_frmwrk2.getParmValueByName("ConditionID") is not None                 \
      and parameters[g_frmwrk2.getIndexByName("NewConditionSetID")].valueAsText is None:

         conditions = source.obj_Condition.Condition();
         conditions.loadConditionID(parameters[g_frmwrk2.getIndexByName("ConditionID")].valueAsText);

         parameters[g_frmwrk2.getIndexByName("RoadTollsPerRoadShipment")].value          = conditions.roadtollsperroadshipment;
         parameters[g_frmwrk2.getIndexByName("MiscCostPerRoadShipment")].value           = conditions.misccostperroadshipment;
         parameters[g_frmwrk2.getIndexByName("MiscCostPerRailShipment")].value           = conditions.misccostperrailshipment;
         parameters[g_frmwrk2.getIndexByName("RoadTransporterDeconCost")].value          = conditions.roadtransporterdeconcost;
         parameters[g_frmwrk2.getIndexByName("RailTransporterDeconCost")].value          = conditions.railtransporterdeconcost;
         parameters[g_frmwrk2.getIndexByName("StagingSiteCost")].value                   = conditions.stagingsitecost;
         parameters[g_frmwrk2.getIndexByName("RoadDrivingHoursPerDay")].value            = conditions.roaddrivinghoursperday;
         parameters[g_frmwrk2.getIndexByName("RailDrivingHoursPerDay")].value            = conditions.raildrivinghoursperday;
         parameters[g_frmwrk2.getIndexByName("TotalCostMultiplier")].value               = conditions.totalcostmultiplier;
         
         g_frmwrk2.setParmValueByName("ConditionID",parameters[1].value);

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return source.gp_SetScenarioConditions.execute(self,parameters,messages);

###############################################################################
class LoadFacilitiesToNetwork(object):

   #...........................................................................
   def __init__(self):
      self.label = "T5 Load Facilities To Network"
      self.name  = "LoadFacilitiesToNetwork"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):
   
      source.util.dzlog('Entering LoadFaciltiiesToNetwork Form','DEBUG');
      flushmem(noflush=4);
      global g_frmwrk4;
      
      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      
      g_frmwrk4 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : ""
               ,"name"         : "ScenarioCharacteristics"
               ,"datatype"     : "GPValueTable"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"category"     : "Scenario Characteristics"
               ,"columns"      : [["String","       Characteristic"],["String","Value"]] 
               ,"value"        : ""
             }
            ,{
                "displayName"  : "I-WASTE Disposal Facility Types"
               ,"name"         : "IWasteDisposalFacilitySubTypes"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"multiValue"   : True
               ,"filter.type"  : "ValueList"
             }
            ,{
                "displayName"  : "Load Eligible I-Waste Facilities"
               ,"name"         : "LoadIWasteFacilities"
               ,"datatype"     : "GPBoolean"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : True
             }
            ,{
                "displayName"  : "Add User-Defined Facilities"
               ,"name"         : "AddUserDefinedFacilities"
               ,"datatype"     : "DEFeatureClass"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"multiValue"   : True
             }
            ,{
                "displayName"  : "Limit By Support Area"
               ,"name"         : "LimitBySupportArea"
               ,"datatype"     : "GPBoolean"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : True
             }
            ,{
                "displayName"  : "Truncate Existing Facilities"
               ,"name"         : "TruncateExistingFacilities"
               ,"datatype"     : "GPBoolean"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : False
             }
             ,{
                "displayName"  : "Override Incident Search Tol (m)"
               ,"name"         : "OverrideIncidentSearchTolerance"
               ,"datatype"     : "GPLong"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
             ,{
                "displayName"  : "Override Facility Search Tol (m)"
               ,"name"         : "OverrideFacilitySearchTolerance"
               ,"datatype"     : "GPLong"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
          ]
      });
      
      #########################################################################
      if haz.system_cache is None:
         g_frmwrk4.setErrorCode(99,"System has not been initialized.");
         return g_frmwrk4.getParms();

      (
          scenarioid
         ,unit_system
         ,waste_type
         ,waste_medium
         ,waste_amount
         ,waste_unit
      ) = haz.current_scenario();

      if haz.system_cache.current_conditionid is None:
         conditionlist = haz.conditions.fetchConditionIDs();
         haz.system_cache.set_current_conditionid(conditionlist[0]);

      conditionid = haz.system_cache.current_conditionid;

      if haz.system_cache.current_factorid is None:
         factorlist = haz.factors.fetchFactorIDs();
         haz.system_cache.set_current_factorid(factorlist[0]);

      factorid = haz.system_cache.current_factorid;
      
      #########################################################################
      try:
         jd = source.util.load_settings();
      except:
         g_frmwrk1.setErrorCode(99,"settings.json configuration file is invalid.");
         return g_frmwrk1.getParms();
                
      subtypes = [];
      subtypnm = [];
      amaps = jd["IWasteImport"]["acceptedMaps"];
      for item in amaps:
         if item['WasteType'] == waste_type:
            for item2 in item['facilitySubtypeIDs']:
               subtypes.append(item2);
               subtypnm.append(haz.waste.subtypeids2txt(str(item2)));
                  
      #########################################################################
      if source.util.sniff_editing_state():
         g_frmwrk4.setErrorCode(1,"Please save or delete all pending edits before proceeding.");
         
      #########################################################################
      (scenario_columns,scenario_value) = haz.get_scenario_characteristics();
      g_frmwrk4.setParmValueByName(
          name        = "ScenarioCharacteristics"
         ,value       = scenario_value
         ,columns     = scenario_columns
      );
      
      subt_enabled = True;
      if len(subtypnm) == 0:
         subt_enabled = False;
      
      g_frmwrk4.setParmValueByName(
          name        = "IWasteDisposalFacilitySubTypes"
         ,value       = subtypnm
         ,filter_list = subtypnm
      );
      
      g_frmwrk4.setParmEnabledByName(
          name        = "IWasteDisposalFacilitySubTypes"
         ,value       = subt_enabled
      );

      del haz;
      source.util.dzlog('Exiting LoadFaciltiiesToNetwork Form','DEBUG');
      return g_frmwrk4.getParms();

   #...........................................................................
   def isLicensed(self):

      return True

   #...........................................................................
   def updateParameters(self,parameters):

      global g_frmwrk4;
      
      siw = parameters[g_frmwrk4.getIndexByName("IWasteDisposalFacilitySubTypes")];
      liw = parameters[g_frmwrk4.getIndexByName("LoadIWasteFacilities")];
      if liw.altered and not liw.hasBeenValidated:

         if liw.value:
            siw.enabled = True;
         else:
            siw.enabled = False;
      
         g_frmwrk4.setParmValueByName("LoadIWasteFacilities",liw.value);
         
      return;

   #...........................................................................
   def updateMessages(self,parameters):

      return;

   #...........................................................................
   def execute(self,parameters,messages):

      return source.gp_LoadFacilitiesToNetwork.execute(self,parameters,messages);

###############################################################################
class SolveRoutingScenario(object):

   #...........................................................................
   def __init__(self):
      self.label = "T6 Solve Routing Scenario"
      self.name  = "SolveRoutingScenario"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      source.util.dzlog('Entering SolveRoutingScenario Form','DEBUG');
      flushmem(noflush=7);
      global g_frmwrk7;
      
      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      (
          scenarioid
         ,unit_system
         ,waste_type
         ,waste_medium
         ,waste_amount
         ,waste_unit
      ) = haz.current_scenario();
      
      g_frmwrk7 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : ""
               ,"name"         : "ScenarioCharacteristics"
               ,"datatype"     : "GPValueTable"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"category"     : "Scenario Characteristics"
               ,"columns"      : [["String","       Characteristic"],["String","Value"]] 
               ,"value"        : ""
             }
            ,{
                "displayName"  : "Change Scenario ID"
               ,"name"         : "ChangeScenarioID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Suggested # Of Facilities To Find"
               ,"name"         : "SuggestedNumbOfFacilitiesToFind"
               ,"datatype"     : "GPLong"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Stashed Scenario ID"
               ,"name"         : "StashedScenarioID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"enabled"      : False
               ,"value"        : None
             }
            ,{
                "displayName"  : "Stashed Unit System"
               ,"name"         : "StashedUnitSystem"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"enabled"      : False
               ,"value"        : None
             }
          ]
      }); 
      
      if haz.system_cache is None:
         g_frmwrk7.setErrorCode(99,"System has not been initialized.");
         return g_frmwrk7.getParms();

      if haz.system_cache.current_conditionid is None:
         conditionlist = haz.conditions.fetchConditionIDs();
         haz.system_cache.set_current_conditionid(conditionlist[0]);

      conditionid = haz.system_cache.current_conditionid;

      if haz.system_cache.current_factorid is None:
         factorlist = haz.factors.fetchFactorIDs();
         haz.system_cache.set_current_factorid(factorlist[0]);

      factorid = haz.system_cache.current_factorid;

      #########################################################################
      if source.util.sniff_editing_state():
         g_frmwrk7.setErrorCode(1,"Please save or delete all pending edits before proceeding.");
      
      #########################################################################
      (scenario_columns,scenario_value) = haz.get_scenario_characteristics();
      g_frmwrk7.setParmValueByName(
          name    = "ScenarioCharacteristics"
         ,value   = scenario_value
         ,columns = scenario_columns
      );
      
      g_frmwrk7.setParmValueByName(
          name    = "ChangeScenarioID"
         ,value   = scenarioid
      );

      wstat = haz.facility_amt_accepted_stats(
         unit_system = haz.system_cache.current_unit_system
      );

      if wstat is None                                                        \
      or wstat.average_fac_amt_accepted is None                               \
      or waste_amount is None                                                 \
      or wstat.average_fac_amt_accepted <= 0:
         param3_value =  None;
      
      else:
         suggested_count = waste_amount / wstat.average_fac_amt_accepted;

         if suggested_count < 1:
            param3_value = 1;
            
         elif suggested_count > 1 and suggested_count < 5:
            param3_value = suggested_count + 1;
            
         else:
            param3_value = int(suggested_count * 1.25);
            
         if  wstat.maximum_facilities_to_find is not None \
         and wstat.maximum_facilities_to_find < param3_value:
            param3_value = wstat.maximum_facilities_to_find;
            
      g_frmwrk7.setParmValueByName(
          name    = "SuggestedNumbOfFacilitiesToFind"
         ,value   = param3_value
      );
      
      g_frmwrk7.setParmValueByName(
          name    = "StashedScenarioID"
         ,value   = scenarioid
      );
      
      g_frmwrk7.setParmValueByName(
          name    = "StashedUnitSystem"
         ,value   = unit_system
      );

      del haz;
      source.util.dzlog('Exiting SolveRoutingScenario Form','DEBUG');
      return g_frmwrk7.getParms();

   #...........................................................................
   def isLicensed(self):

      return True

   #...........................................................................
   def updateParameters(self, parameters):

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return source.gp_SolveRoutingScenario.execute(self,parameters,messages);

###############################################################################
class CalculateLogisticsPlanningEstimates(object):

   #...........................................................................
   def __init__(self):
      self.label = "T7 Calculate Logistics Planning Estimates"
      self.name  = "CalculateLogisticsPlanningEstimates"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):
   
      source.util.dzlog('Entering CalculateLogisticsPlanningEstimates Form','DEBUG');
      flushmem(noflush=8);  
      global g_frmwrk8;
         
      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      
      g_frmwrk8 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : ""
               ,"name"         : "ScenarioCharacteristics"
               ,"datatype"     : "GPValueTable"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"category"     : "Scenario Characteristics"
               ,"columns"      : [["String","       Characteristic"],["String","Value"]] 
               ,"value"        : ""
             }
            ,{
                "displayName"  : "Scenario ID"
               ,"name"         : "ScenarioID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
             }
            ,{
                "displayName"  : "Condition ID"
               ,"name"         : "ConditionID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
             }
            ,{
                "displayName"  : "FactorSet ID"
               ,"name"         : "FactorSetID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
             }             
            ,{
                "displayName"  : "Facility Attributes ID"
               ,"name"         : "FacilityAttributesID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
             }
            ,{
                "displayName"  : "Map Settings"
               ,"name"         : "MapSettings"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : "Disable Map"
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : [
                   'Zoom to Routes'
                  ,'Zoom to Support Area'
                  ,'User Zoom'
                  ,'Disable Map'
               ]
             }
            ,{
                "displayName"  : "Stashed Scenario ID"
               ,"name"         : "StashedScenarioID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"enabled"      : False
               ,"value"        : None
             }
            ,{
                "displayName"  : "Stashed Condition ID"
               ,"name"         : "StashedConditionID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"enabled"      : False
               ,"value"        : None
             }
            ,{
                "displayName"  : "Stashed Factor ID"
               ,"name"         : "StashedFactorID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"enabled"      : False
               ,"value"        : None
             }
            ,{
                "displayName"  : "Stashed Facility Attributes ID"
               ,"name"         : "StashedFacilityAttributesID"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"enabled"      : False
               ,"value"        : None
             }
            ,{
                "displayName"  : "Stashed Road Transporter"
               ,"name"         : "StashedRoadTransporter"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"enabled"      : False
               ,"value"        : None
             }
            ,{
                "displayName"  : "Stashed Rail Transporter"
               ,"name"         : "StashedRailTransporter"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"enabled"      : False
               ,"value"        : None
             }
          ]
      }); 
      
      if haz.system_cache is None:
         g_frmwrk8.setErrorCode(99,"System has not been initialized.");
         return g_frmwrk8.getParms();

      (
          scenarioid
         ,unit_system
         ,waste_type
         ,waste_medium
         ,waste_amount
         ,waste_unit
      ) = haz.current_scenario();

      conditionlist = haz.conditions.fetchConditionIDs();

      if haz.system_cache.current_conditionid is None:
         haz.system_cache.set_current_conditionid(conditionlist[0]);

      conditionid = haz.system_cache.current_conditionid;

      factorlist = haz.factors.fetchFactorIDs();

      if haz.system_cache.current_factorid is None:
         haz.system_cache.set_current_factorid(factorlist[0]);

      factorid = haz.system_cache.current_factorid;
      
      scenarioids = haz.scenario.fetchScenarioIDs();

      #########################################################################
      if source.util.sniff_editing_state():
         g_frmwrk8.setErrorCode(1,"Please save or delete all pending edits before proceeding.");
      
      #########################################################################
      (scenario_columns,scenario_value) = haz.get_scenario_characteristics();
      g_frmwrk8.setParmValueByName(
          name    = "ScenarioCharacteristics"
         ,value   = scenario_value
         ,columns = scenario_columns
      );
      
      g_frmwrk8.setParmValueByName(
          name    = "ScenarioID"
         ,value   = scenarioid
         ,filter_list = scenarioids
      );

      g_frmwrk8.setParmValueByName(
          name    = "ConditionID"
         ,value   = conditionid
         ,filter_list = conditionlist
      );

      g_frmwrk8.setParmValueByName(
          name    = "FactorSetID"
         ,value   = factorid
         ,filter_list = factorlist
      );
      
      facilityattribute_list = haz.get_facilityattributesids();
      facilityattribute_def  = haz.system_cache.current_facilityattributesid;
      if facilityattribute_def is None and len(facilityattribute_list) > 0:
         facilityattribute_def = facilityattribute_list[0];
      g_frmwrk8.setParmValueByName(
          name    = "FacilityAttributesID"
         ,value   = facilityattribute_def
         ,filter_list = facilityattribute_list
      );

      g_frmwrk8.setParmValueByName(
          name    = "StashedScenarioID"
         ,value   = scenarioid
      );

      g_frmwrk8.setParmValueByName(
          name    = "StashedConditionID"
         ,value   = conditionid
      );
      
      g_frmwrk8.setParmValueByName(
          name    = "StashedFactorID"
         ,value   = factorid
      );
      
      g_frmwrk8.setParmValueByName(
          name    = "StashedFacilityAttributesID"
         ,value   = haz.system_cache.current_facilityattributesid
      );
      
      g_frmwrk8.setParmValueByName(
          name    = "StashedRoadTransporter"
         ,value   = haz.system_cache.current_road_transporter
      );
      
      g_frmwrk8.setParmValueByName(
          name    = "StashedRailTransporter"
         ,value   = haz.system_cache.current_rail_transporter
      );

      del haz;
      source.util.dzlog('Exiting CalculateLogisticsPlanningEstimates Form','DEBUG');
      return g_frmwrk8.getParms();

   #...........................................................................
   def isLicensed(self):

      return True

   #...........................................................................
   def updateParameters(self, parameters):

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return source.gp_CalculateLogisticsPlanningEstimates.execute(self,parameters,messages);

###############################################################################
class ExportLogisticsPlanningResults(object):

   #...........................................................................
   def __init__(self):
      self.label = "T8 Export Logistics Planning Results"
      self.name  = "ExportLogisticsPlanningResults"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):
   
      global g_frmwrk9;
      flushmem(noflush=9); 
      source.util.dzlog('Entering ExportLogisticsPlanningResults Form','DEBUG');
      
      g_frmwrk9 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : ""
               ,"name"         : "ScenarioCharacteristics"
               ,"datatype"     : "GPValueTable"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"category"     : "Scenario Characteristics"
               ,"columns"      : [["String","       Characteristic"],["String","Value"]] 
               ,"value"        : ""
             }
            ,{
                "displayName"  : "Export File"
               ,"name"         : "ExportFile"
               ,"datatype"     : "DEFile"
               ,"parameterType": "Required"
               ,"direction"    : "Output"
               ,"value"        : None
               ,"filter.list"  : ['xlsx']
             }
            ,{
                "displayName"  : "Scenario IDs"
               ,"name"         : "ScenarioIDs"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
             }
          ]
      });
      
      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      
      if haz.system_cache is None:
         g_frmwrk9.setErrorCode(99,"System has not been initialized.");
         return g_frmwrk9.getParms();

      (
          scenarioid
         ,unit_system
         ,waste_type
         ,waste_medium
         ,waste_amount
         ,waste_unit
      ) = haz.current_scenario();
      
      #########################################################################
      if source.util.sniff_editing_state():
         g_frmwrk9.setErrorCode(1,"Please save or delete all pending edits before proceeding.");
      
      #########################################################################
      (scenario_columns,scenario_value) = haz.get_scenario_characteristics();
      g_frmwrk9.setParmValueByName(
          name    = "ScenarioCharacteristics"
         ,value   = scenario_value
         ,columns = scenario_columns
      );
      
      rows = arcpy.da.SearchCursor(
          in_table     = haz.scenario_results.dataSource
         ,field_names  = (
             'OBJECTID'
            ,'scenarioid'
          )
      );

      ary = [];
      deflt = None;
      
      for row in rows:
         val = row[1];

         if val not in ary:
            ary.append(val);
            
      del rows;
      
      if len(ary) == 0:
         deflt = None;
         
      elif len(ary) == 1:
         deflt = ary[0];
            
      elif len(ary) > 1:
         for item in ary:
            if item == scenarioid:
               deflt = item;
                  
         if deflt is None:
            deflt = ary[0];

      g_frmwrk9.setParmValueByName(
          name    = "ScenarioIDs"
         ,value   = deflt
         ,filter_list = ary
      );            

      del haz; 
      source.util.dzlog('Exiting ExportLogisticsPlanningResults Form','DEBUG');
      return g_frmwrk9.getParms();

   #...........................................................................
   def isLicensed(self):

      return True

   #...........................................................................
   def updateParameters(self, parameters):

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return source.gp_ExportLogisticsPlanningResults.execute(self,parameters,messages);

###############################################################################
class RemoveWorkEnvironment(object):

   #...........................................................................
   def __init__(self):

      self.label = "U1 Remove Work Environment"
      self.name  = "RemoveWorkEnvironment"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):
      
      flushmem(noflush=10); 
      global g_frmwrk10;
      
      g_frmwrk10 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
      });

      return g_frmwrk10.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return source.gp_RemoveWorkEnvironment.execute(self,parameters,messages);

###############################################################################
class ClearScenarios(object):

   #...........................................................................
   def __init__(self):

      self.label = "U2 Clear Scenarios"
      self.name  = "ClearScenarios"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      flushmem(noflush=11); 
      global g_frmwrk11;
      
      g_frmwrk11 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
      });
      
      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      
      if haz.system_cache is None:
         g_frmwrk11.setErrorCode(99,"System has not been initialized.");
         return g_frmwrk11.getParms();
         
      del haz;
      return g_frmwrk11.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

      arcpy.TruncateTable_management(haz.scenario_results.dataSource);
      arcpy.TruncateTable_management(haz.network.routes.dataSource);
      arcpy.TruncateTable_management(haz.network.facilities.dataSource);
      arcpy.TruncateTable_management(haz.network.incidents.dataSource);
      arcpy.TruncateTable_management(haz.network.point_barriers.dataSource);
      arcpy.TruncateTable_management(haz.network.line_barriers.dataSource);
      arcpy.TruncateTable_management(haz.network.polygon_barriers.dataSource);
      arcpy.TruncateTable_management(haz.support_area.dataSource);
      arcpy.TruncateTable_management(haz.incident_area.dataSource);
      haz.network.routes.visible = True;

      del haz;
      return None;
      
###############################################################################
class ClearFacilities(object):

   #...........................................................................
   def __init__(self):

      self.label = "U3 Clear Facilities"
      self.name  = "ClearFacilities"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):
   
      flushmem(noflush=14); 
      global g_frmwrk14;
      
      g_frmwrk14 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
      });

      return g_frmwrk14.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):
   
      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

      arcpy.TruncateTable_management(haz.scenario_results.dataSource);
      arcpy.TruncateTable_management(haz.network.routes.dataSource);
      arcpy.TruncateTable_management(haz.network.facilities.dataSource);
      haz.network.routes.visible = True;

      del haz;
      return None;
      
###############################################################################
class QueryIWasteFacilities(object):

   #...........................................................................
   def __init__(self):

      self.label = "U4 Query I-Waste Facilities"
      self.name  = "QueryIWasteFacilities"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):
   
      flushmem(noflush=5); 
      global g_frmwrk5;
      
      g_frmwrk5 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : "Local Audit File Timestamp"
               ,"name"         : "LocalFileTimestamp"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Remote Audit File Timestamp"
               ,"name"         : "RemoteFileTimestamp"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "I-Waste Vintage Report"
               ,"name"         : "IWasteVintageReport"
               ,"datatype"     : "GPValueTable"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"multiValue"   : False
               ,"value"        : ""
               ,"columns"      : [['String','Dataset'],['String','Local'],['String','Remote']]
             }
          ]
      }); 
      
      #########################################################################
      local_iwaste  = {};
      remote_iwaste = {};
      tbl_types     = [];
      tbl_value     = "";
      local_ts      = None;
      remote_ts     = None;
      
      fc = os.path.join(source.util.g_pn,"data","IWasteVintage_Local.json");
      if not os.path.exists(fc):
         err_val = "IWasteVintage_Local.json vintage file is missing.";
         err_enb = True;
         prm_enb = False;
         
      else:
         with open(fc,"r") as json_f:
            json_d = json.load(json_f);
         
         local_ts = json_d["timestamp"];
         for row in json_d["wasteGroupings"]:
            local_iwaste[row["wasteType"]] = row;
            tbl_types.append(row["wasteType"]);
         
         fc = os.path.join(source.util.g_pn,"data","IWasteVintage_Remote.json");
         if os.path.exists(fc):
         
            with open(fc,"r") as json_f:
               json_d = json.load(json_f);
               
            if json_d is not None:            
               remote_ts = json_d["timestamp"];
               for row in json_d["wasteGroupings"]:
                  remote_iwaste[row["wasteType"]] = row;
                  tbl_types.append(row["wasteType"]);
         
         tbl_types = sorted(set(tbl_types));

         for item in tbl_types:
            val_local  = "";
            val_remote = "";
            
            if item in local_iwaste:
               val_local = ','.join(list(sorted(set(local_iwaste[item]["dateLastUpdate"]))));
               
            if item in remote_iwaste:
               val_remote = ','.join(list(sorted(set(remote_iwaste[item]["dateLastUpdate"]))));
               
            tbl_value += "\"" + item + "\" \"" + val_local + "\" \"" + val_remote + "\";";
      
      #########################################################################
      g_frmwrk5.setParmValueByName(
          name    = "LocalFileTimestamp"
         ,value   = local_ts
      );
      
      g_frmwrk5.setParmValueByName(
          name    = "RemoteFileTimestamp"
         ,value   = remote_ts
      );
      
      g_frmwrk5.setParmValueByName(
          name    = "IWasteVintageReport"
         ,value   = tbl_value
      );
      
      return g_frmwrk5.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return source.gp_QueryIWasteFacilities.execute(self,parameters,messages);
     
###############################################################################
class UpdateIWasteFacilities(object):

   #...........................................................................
   def __init__(self):

      self.label = "U5 Update I-Waste Facilities"
      self.name  = "LoadIWasteFacilities"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):
   
      flushmem(noflush=6); 
      global g_frmwrk6;
      
      g_frmwrk6 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
      });

      return g_frmwrk6.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):
   
      return source.gp_UpdateIWasteFacilities.execute(self,parameters,messages);

###############################################################################
class ReloadProjectSettings(object):

   #...........................................................................
   def __init__(self):

      self.label = "U6 Reload Project Settings"
      self.name  = "ReloadProjectSettings"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):
   
      flushmem(noflush=12); 
      global g_frmwrk12;
      
      g_frmwrk12 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : "Project Settings Last Updated Date"
               ,"name"         : "ProjectSettingsLastUpdatedDate"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Project Settings Last Updated By"
               ,"name"         : "ProjectSettingsLastUpdatedBy"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "File Settings Last Updated Date"
               ,"name"         : "FileSettingsLastUpdatedDate"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "File Settings Last Updated By"
               ,"name"         : "FileSettingsLastUpdatedBy"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
          ]
      });
      
      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      
      if haz.system_cache is None:
         g_frmwrk12.setErrorCode(99,"System has not been initialized.");
         return g_frmwrk12.getParms();
         
      details = haz.get_settings_vintage();
      
      g_frmwrk12.setParmValueByName(
          name    = "ProjectSettingsLastUpdatedDate"
         ,value   = details["ProjectSettingsLastUpdatedDate"]
      );
      
      g_frmwrk12.setParmValueByName(
          name    = "ProjectSettingsLastUpdatedBy"
         ,value   = details["ProjectSettingsLastUpdatedBy"]
      );
      
      g_frmwrk12.setParmValueByName(
          name    = "FileSettingsLastUpdatedDate"
         ,value   = details["FileSettingsLastUpdatedDate"]
      );
      
      g_frmwrk12.setParmValueByName(
          name    = "FileSettingsLastUpdatedBy"
         ,value   = details["FileSettingsLastUpdatedBy"]
      );

      return g_frmwrk12.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):
   
      return source.gp_ReloadProjectSettings.execute(self,parameters,messages);

###############################################################################
class ExportFacilitiesToUserDataset(object):

   #...........................................................................
   def __init__(self):

      self.label = "U7 Export Facilities To User Dataset"
      self.name  = "ExportFacilitiesToUserDataset"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):
   
      flushmem(noflush=13); 
      global g_frmwrk13;
      
      g_frmwrk13 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : "Export Facility Dataset"
               ,"name"         : "ExportFacilityDataset"
               ,"datatype"     : "DEFeatureClass"
               ,"parameterType": "Required"
               ,"direction"    : "Output"
               ,"value"        : "UserFacilityDataset"
             }
            ,{
                "displayName"  : "Optional Query Clause"
               ,"name"         : "OptionalQueryClause"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
          ]
      });
      
      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      
      if haz.system_cache is None:
         g_frmwrk13.setErrorCode(99,"System has not been initialized.");
         return g_frmwrk13.getParms();
 
      #########################################################################
      if source.util.sniff_editing_state():
         g_frmwrk13.setErrorCode(1,"Please save or delete all pending edits before proceeding.");
      
      return g_frmwrk13.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):
   
      return source.gp_ExportFacilitiesToUserDataset.execute(self,parameters,messages);
      
###############################################################################
class SetTransporterAttributes(object):

   #...........................................................................
   def __init__(self):

      self.label = "T4 Set Transporter Attributes"
      self.name  = "SetTransporterAttributes"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      source.util.dzlog('Entering SetTransporterAttributes Form','DEBUG');
      flushmem(noflush=15);
      global g_frmwrk15;
      
      #try:
      haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      #except Exception as e:
      #   source.util.dzlog_e(sys.exc_info(),'ERROR');
      #   raise;

      (
          scenarioid
         ,unit_system
         ,waste_type
         ,waste_medium
         ,waste_amount
         ,waste_unit
      ) = haz.current_scenario();
          
      g_frmwrk15 = source.obj_ParmFramework.ParmFramework(framework = {
          "status_code": 0
         ,"error_message": None
         ,"framework": [
             {
                "displayName"  : ""
               ,"name"         : "ScenarioCharacteristics"
               ,"datatype"     : "GPValueTable"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"category"     : "Scenario Characteristics"
               ,"columns"      : [["String","       Characteristic"],["String","Value"]] 
               ,"value"        : ""
             }
            ,{
                "displayName"  : "Waste Type"
               ,"name"         : "WasteType"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : waste_type
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : None
             }
            ,{
                "displayName"  : "Waste Medium"
               ,"name"         : "WasteMedium"
               ,"datatype"     : "GPString"
               ,"parameterType": "Required"
               ,"direction"    : "Input"
               ,"value"        : waste_medium
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : None
             }
            ,{
                "displayName"  : "Road Transporter Attributes Name"
               ,"name"         : "RoadTransporterAttributesName"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "New Road Transporter Attributes Name"
               ,"name"         : "NewRoadTransporterAttributesName"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Road Transporter Container Capacity"
               ,"name"         : "RoadTransporterContainerCapacity"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Road Transporter Container Capacity Unit"
               ,"name"         : "RoadTransporterContainerCapacityUnit"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : None
             }
            ,{
                "displayName"  : "Road Transporter Container Count Per Transporter"
               ,"name"         : "RoadTransporterContainerCountPerTransporter"
               ,"datatype"     : "GPLong"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Road Transporters Available"
               ,"name"         : "RoadTransportersAvailable"
               ,"datatype"     : "GPLong"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Road Transporters Processed Per Day"
               ,"name"         : "RoadTransportersProcessedPerDay"
               ,"datatype"     : "GPLong"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Rail Transporter Attributes Name"
               ,"name"         : "RailTransporterAttributesName"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "New Rail Transporter Attributes Name"
               ,"name"         : "NewRailTransporterAttributesName"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Rail Transporter Container Capacity"
               ,"name"         : "RailTransporterContainerCapacity"
               ,"datatype"     : "GPDouble"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Rail Transporter Container Capacity Unit"
               ,"name"         : "RailTransporterContainerCapacityUnit"
               ,"datatype"     : "GPString"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
               ,"filter.type"  : "ValueList"
               ,"filter.list"  : None
             }
            ,{
                "displayName"  : "Rail Transporter Container Count Per Transporter"
               ,"name"         : "RailTransporterContainerCountPerTransporter"
               ,"datatype"     : "GPLong"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Rail Transporters Available"
               ,"name"         : "RailTransportersAvailable"
               ,"datatype"     : "GPLong"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
            ,{
                "displayName"  : "Rail Transporters Processed Per Day"
               ,"name"         : "RailTransportersProcessedPerDay"
               ,"datatype"     : "GPLong"
               ,"parameterType": "Optional"
               ,"direction"    : "Input"
               ,"value"        : None
             }
          ]
      }); 
      
      if haz.system_cache is None:
         g_frmwrk15.setErrorCode(99,"System has not been initialized.");
         return g_frmwrk15.getParms();

      #########################################################################
      if source.util.sniff_editing_state():
         g_frmwrk15.setErrorCode(1,"Please save or delete all pending edits before proceeding.");
         
      #########################################################################
      (scenario_columns,scenario_value) = haz.get_scenario_characteristics();
      g_frmwrk15.setParmValueByName(
          name    = "ScenarioCharacteristics"
         ,value   = scenario_value
         ,columns = scenario_columns
      );

      road_transporter_attr_choice = None;
      road_transporter_attr_list   = [];
      if waste_type is not None:
         road_transporter_attr_list = haz.road_transporter_list;
         road_transporter_attr_choice = haz.system_cache.current_road_transporter;
         if road_transporter_attr_choice is None and len(haz.road_transporter_list) > 0:
            road_transporter_attr_choice = haz.road_transporter_list[0];
            
         road_transporter = haz.transporterCapacity(
             mode = 'Road'
            ,transporterattrid = road_transporter_attr_choice
         );
         
         g_frmwrk15.setParmValueByName(
             name        = "RoadTransporterContainerCapacity"
            ,value       = road_transporter['containercapacity']
         );
         
         g_frmwrk15.setParmValueByName(
             name        = "RoadTransporterContainerCapacityUnit"
            ,value       = road_transporter['containercapacityunit']
            ,filter_list = haz.waste.units(medium = waste_medium)
         );
         
         g_frmwrk15.setParmValueByName(
             name        = "RoadTransporterContainerCountPerTransporter"
            ,value       = road_transporter['containercountpertransporter']
         );
         
         g_frmwrk15.setParmValueByName(
             name        = "RoadTransportersAvailable"
            ,value       = road_transporter['transportersavailable']
         );
         
         g_frmwrk15.setParmValueByName(
             name        = "RoadTransportersProcessedPerDay"
            ,value       = road_transporter['transportersprocessedperday']
         );
      
      g_frmwrk15.setParmValueByName(
          name        = "RoadTransporterAttributesName"
         ,value       = road_transporter_attr_choice
         ,filter_list = road_transporter_attr_list
      );

      rail_transporter_attr_choice = None;
      rail_transporter_attr_list   = [];
      if waste_type is not None:
         rail_transporter_attr_list = haz.rail_transporter_list;
         rail_transporter_attr_choice = haz.system_cache.current_rail_transporter;
         if rail_transporter_attr_choice is None and len(haz.rail_transporter_list) > 0:
            rail_transporter_attr_choice = haz.rail_transporter_list[0];
            
         rail_transporter = haz.transporterCapacity(
             mode = 'Rail'
            ,transporterattrid = rail_transporter_attr_choice
         );
         
         g_frmwrk15.setParmValueByName(
             name        = "RailTransporterContainerCapacity"
            ,value       = rail_transporter['containercapacity']
         );
         
         g_frmwrk15.setParmValueByName(
             name        = "RailTransporterContainerCapacityUnit"
            ,value       = rail_transporter['containercapacityunit']
            ,filter_list = haz.waste.units(medium = waste_medium)
         );
         
         g_frmwrk15.setParmValueByName(
             name        = "RailTransporterContainerCountPerTransporter"
            ,value       = rail_transporter['containercountpertransporter']
         );
         
         g_frmwrk15.setParmValueByName(
             name        = "RailTransportersAvailable"
            ,value       = rail_transporter['transportersavailable']
         );
         
         g_frmwrk15.setParmValueByName(
             name        = "RailTransportersProcessedPerDay"
            ,value       = rail_transporter['transportersprocessedperday']
         );
      
      g_frmwrk15.setParmValueByName(
          name        = "RailTransporterAttributesName"
         ,value       = rail_transporter_attr_choice
         ,filter_list = rail_transporter_attr_list
      );
      
      g_frmwrk15.setStash(
          stash       = "haz"
         ,value       = haz
      );

      source.util.dzlog('Exiting SetTransporterAttributes Form','DEBUG');
      return g_frmwrk15.getParms();

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      global g_frmwrk15;
      
      road_attr   = parameters[g_frmwrk15.getIndexByName("RoadTransporterAttributesName")];
      road_attr_v = g_frmwrk15.getParmValueByName("RoadTransporterAttributesName");
      
      if  road_attr.altered and not road_attr.hasBeenValidated and road_attr.valueAsText is not None \
      and road_attr.valueAsText != road_attr_v:
      
         haz = g_frmwrk15.getStash(stash = "haz");
         road_transporter = haz.transporterCapacity(
             mode = 'Road'
            ,transporterattrid = road_attr.valueAsText
         );
      
         parameters[g_frmwrk15.getIndexByName("RoadTransporterContainerCapacity")].value            = road_transporter['containercapacity'];
         parameters[g_frmwrk15.getIndexByName("RoadTransporterContainerCapacityUnit")].value        = road_transporter['containercapacityunit'];
         parameters[g_frmwrk15.getIndexByName("RoadTransporterContainerCountPerTransporter")].value = road_transporter['containercountpertransporter'];
         parameters[g_frmwrk15.getIndexByName("RoadTransportersAvailable")].value                   = road_transporter['transportersavailable'];
         parameters[g_frmwrk15.getIndexByName("RoadTransportersProcessedPerDay")].value             = road_transporter['transportersprocessedperday'];
         
         g_frmwrk15.refreshFromParameters(parameters);
      
      else:
      
         rail_attr   = parameters[g_frmwrk15.getIndexByName("RailTransporterAttributesName")];
         rail_attr_v = g_frmwrk15.getParmValueByName("RailTransporterAttributesName");
         
         if  rail_attr.altered and not rail_attr.hasBeenValidated and rail_attr.valueAsText is not None \
         and rail_attr.valueAsText != rail_attr_v:
         
            haz = g_frmwrk15.getStash(stash = "haz");
            rail_transporter = haz.transporterCapacity(
                mode = 'Rail'
               ,transporterattrid = rail_attr.valueAsText
            );
         
            parameters[g_frmwrk15.getIndexByName("RailTransporterContainerCapacity")].value            = rail_transporter['containercapacity'];
            parameters[g_frmwrk15.getIndexByName("RailTransporterContainerCapacityUnit")].value        = rail_transporter['containercapacityunit'];
            parameters[g_frmwrk15.getIndexByName("RailTransporterContainerCountPerTransporter")].value = rail_transporter['containercountpertransporter'];
            parameters[g_frmwrk15.getIndexByName("RailTransportersAvailable")].value                   = rail_transporter['transportersavailable'];
            parameters[g_frmwrk15.getIndexByName("RailTransportersProcessedPerDay")].value             = rail_transporter['transportersprocessedperday'];
         
            g_frmwrk15.refreshFromParameters(parameters);

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return source.gp_SetTransporterAttributes.execute(self,parameters,messages);

###############################################################################
 