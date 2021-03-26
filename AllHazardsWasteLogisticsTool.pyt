import arcpy
import sys,os,json,copy;

###############################################################################
import gp_CreateWorkEnvironment;
import gp_SetScenarioConditions;
import gp_DefineScenario;
import gp_LoadFacilitiesToNetwork;
import gp_SolveRoutingScenario;
import gp_CalculateLogisticsPlanningEstimates;
import gp_ExportLogisticsPlanningResults;
import gp_RemoveWorkEnvironment;
import util;
import obj_NetworkDataset;
import obj_AllHazardsWasteLogisticsTool;
import obj_Waste;
import obj_Condition;

###############################################################################
import importlib
try:
   importlib.reload(gp_CreateWorkEnvironment);
   importlib.reload(gp_SetScenarioConditions);
   importlib.reload(gp_DefineScenario);
   importlib.reload(gp_LoadFacilitiesToNetwork);
   importlib.reload(gp_SolveRoutingScenario);
   importlib.reload(gp_CalculateLogisticsPlanningEstimates);
   importlib.reload(gp_ExportLogisticsPlanningResults);
   importlib.reload(gp_RemoveWorkEnvironment);
   importlib.reload(util);
   importlib.reload(obj_NetworkDataset);
   importlib.reload(obj_AllHazardsWasteLogisticsTool);
   importlib.reload(obj_Waste);
   importlib.reload(obj_Condition);

except:
   pass;

###############################################################################
class Toolbox(object):

   def __init__(self):

      self.label = "Toolbox";
      self.alias = "AllHazardsWasteLogisticsTool";

      self.tools = [];
      self.tools.append(CreateWorkEnvironment);
      self.tools.append(SetScenarioConditions);
      self.tools.append(RemoveWorkEnvironment);
      self.tools.append(DefineScenario);
      self.tools.append(LoadFacilitiesToNetwork);
      self.tools.append(SolveRoutingScenario);
      self.tools.append(CalculateLogisticsPlanningEstimates);
      self.tools.append(ExportLogisticsPlanningResults);
      self.tools.append(ClearScenarios);

###############################################################################
class CreateWorkEnvironment(object):

   #...........................................................................
   def __init__(self):

      self.label = "Create Work Environment"
      self.name  = "CreateWorkEnvironment"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

      (username,portal_url) = util.portal_info();
      
      #########################################################################
      if util.sniff_editing_state():
         err_val = "Please save or delete all pending edits before proceeding.";
         err_enb = True;
      else:
         err_val = None;
         err_enb = False;

      param0 = arcpy.Parameter(
          displayName   = ""
         ,name          = "ErrorCondition"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = err_enb
      );
      param0.value = err_val;
      
      #########################################################################
      param1 = arcpy.Parameter(
          displayName   = ''
         ,name          = "ScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Scenario Characteristics"
      );
      (param1.columns,param1.value) = haz.get_scenario_characteristics();

      param2 = arcpy.Parameter(
          displayName   = "Project Unit System"
         ,name          = "UnitSystem"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );

      jd = util.load_settings();
      if jd is None:
         param2.value = "Metric";
      else:
         param2.value = jd["SystemCache"]["Default_Unit_System"];

      param2.filter.type = "ValueList";
      param2.filter.list = ["Metric","US Customary"];

      param3 = arcpy.Parameter(
          displayName   = "Network Source"
         ,name          = "NetworkSource"
         ,datatype      = ["GPNetworkDatasetLayer","GPString"]
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param3.value = portal_url;

      param4 = arcpy.Parameter(
          displayName   = "ArcGIS Online Account"
         ,name          = "ArcGISOnlineAccount"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );
      param4.value = username;

      nd = obj_NetworkDataset.NetworkDataset(
         dataset = param3.value
      );

      param5 = arcpy.Parameter(
          displayName   = "Network Dataset Travel Mode"
         ,name          = "NetworkDatasetTravelMode"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Network Dataset Characteristics"
      );
      param5.value       = nd.current_travel_mode;
      param5.filter.type = "ValueList";
      param5.filter.list = nd.travel_modes_keys;

      param6 = arcpy.Parameter(
          displayName   = "Network Distance Field"
         ,name          = "NetworkDistanceField"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Network Dataset Characteristics"
      );
      param6.value = nd.current_distance_fieldname;

      param7 = arcpy.Parameter(
          displayName   = "Network Distance Field Unit"
         ,name          = "NetworkDistanceFieldUnit"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Network Dataset Characteristics"
      );
      param7.value = nd.current_distance_unit;

      param8 = arcpy.Parameter(
          displayName   = "Network Time Field"
         ,name          = "NetworkTimeField"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Network Dataset Characteristics"
      );
      param8.value  = nd.current_time_fieldname;

      param9 = arcpy.Parameter(
          displayName   = "Network Time Field Unit"
         ,name          = "NetworkTimeFieldUnit"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Network Dataset Characteristics"
      );
      param9.value  = nd.current_time_unit;

      ## Stashes
      param10 = arcpy.Parameter(
          displayName   = "Stash Username"
         ,name          = "StashUsername"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param10.value = username;

      param11 = arcpy.Parameter(
          displayName   = "Stash Network"
         ,name          = "StashNetwork"
         ,datatype      = ["GPNetworkDatasetLayer","GPString"]
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param11.value = param3.value;

      param12 = arcpy.Parameter(
          displayName   = "Stash TravelMode"
         ,name          = "StashTravelMode"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param12.value = param5.value;

      param13 = arcpy.Parameter(
          displayName   = "Stash NetworkDistanceField"
         ,name          = "StashNetworkDistanceField"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param13.value = param6.value;

      param14 = arcpy.Parameter(
          displayName   = "Stash NetworkTimeField"
         ,name          = "StashNetworkTimeField"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param14.value = param8.value;

      param15 = arcpy.Parameter(
          displayName   = "Stashed Scenario Characteristics"
         ,name          = "StashedScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param15.columns = copy.deepcopy(param1.columns);
      param15.value   = copy.deepcopy(param1.value);

      params = [
          param0
         ,param1
         ,param2
         ,param3
         ,param4
         ,param5
         ,param6
         ,param7
         ,param8
         ,param9
         ,param10
         ,param11
         ,param12
         ,param13
         ,param14
         ,param15
      ];

      del haz;
      return params;

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      if  parameters[1].valueAsText != parameters[15].valueAsText             \
      and parameters[1].valueAsText is not None                               \
      and parameters[15].valueAsText is not None:
         if parameters[1].value[0][0] == 'Information is read-only':
            parameters[1].value = copy.deepcopy(parameters[15].value);
         else:
            parameters[1].value = [['Information is read-only','']] + copy.deepcopy(parameters[15].value);

      network_source = parameters[3].valueAsText;

      if network_source is not None:
         network_source = network_source.rstrip('/');

      old_network_source = parameters[11].valueAsText;

      if old_network_source is not None:
         old_network_source = old_network_source.rstrip('/');

      travel_mode     = parameters[5].valueAsText;
      old_travel_mode = parameters[12].valueAsText;

      if parameters[3].altered                                                \
      and network_source != old_network_source                                \
      and network_source is not None:
      
         parameters[0].enabled = False;
         parameters[0].value   = None;
         parameters[0].clearMessage();
         
         if network_source.lower()[0:4] == 'http':
            (username,portal_url) = util.portal_info();
            
         if network_source.lower()[0:4] == 'http'                             \
         and username is None:
            parameters[3].value = None;
            parameters[0].enabled = True;
            parameters[0].value = "** User is not logged into Portal **";
            parameters[0].setErrorMessage("** User is not logged into Portal **");
            
         else:
            nd = obj_NetworkDataset.NetworkDataset(
                dataset = network_source
               ,current = travel_mode
            );

            parameters[5].value = nd.current_travel_mode;
            parameters[5].filter.type = "ValueList";
            parameters[5].filter.list = nd.travel_modes_keys;

            if network_source is not None and network_source[0:4] == "http":
               parameters[4].value = util.portal_name();

            else:
               parameters[4].value = None;

               if network_source is not None and arcpy.CheckExtension("Network") != "Available":
                  parameters[3].value = None;
                  parameters[0].enabled = True;
                  parameters[0].value = "** Network Analyst not licensed **";
                  parameters[0].setErrorMessage("** Network Analyst not licensed **");

            parameters[6].value = nd.current_distance_fieldname;
            parameters[7].value = nd.current_distance_unit;
            parameters[8].value = nd.current_time_fieldname;
            parameters[9].value = nd.current_time_unit;

      elif travel_mode != old_travel_mode                                     \
      and travel_mode is not None                                             \
      and old_travel_mode is not None:

         nd = obj_NetworkDataset.NetworkDataset(
             dataset = network_source
            ,current = travel_mode
         );

         parameters[6].value = nd.current_distance_fieldname;
         parameters[7].value = nd.current_distance_unit;
         parameters[8].value = nd.current_time_fieldname;
         parameters[9].value = nd.current_time_unit;

      parameters[10].value = parameters[4].value;
      parameters[11].value = network_source;
      parameters[12].value = travel_mode;
      parameters[13].value = parameters[6].value;
      parameters[14].value = parameters[8].value;

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return gp_CreateWorkEnvironment.execute(self,parameters,messages);

###############################################################################
class SetScenarioConditions(object):

   #...........................................................................
   def __init__(self):

      self.label = "Set Scenario Conditions"
      self.name  = "SetScenarioConditions"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

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

      if haz.system_cache.current_factorid is None:
         factorlist = haz.factors.fetchFactorIDs();
         haz.system_cache.set_current_factorid(factorlist[0]);

      factorid = haz.system_cache.current_factorid;
      
      #########################################################################
      if util.sniff_editing_state():
         err_val = "Please save or delete all pending edits before proceeding.";
         err_enb = True;
      else:
         err_val = None;
         err_enb = False;

      param0 = arcpy.Parameter(
          displayName   = ""
         ,name          = "ErrorCondition"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = err_enb
      );
      param0.value = err_val;
      
      #########################################################################
      param1 = arcpy.Parameter(
          displayName   = ''
         ,name          = "ScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Scenario Characteristics"
      );
      (param1.columns,param1.value) = haz.get_scenario_characteristics();

      param2 = arcpy.Parameter(
          displayName   = "Condition ID"
         ,name          = "ConditionID"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );
      param2.value       = conditionid;
      param2.filter.type = "ValueList";
      param2.filter.list = conditionlist;

      param3 = arcpy.Parameter(
          displayName   = "New Condition Set ID"
         ,name          = "NewConditionSetID"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );

      conditions = haz.conditions;
      conditions.loadConditionID(haz.system_cache.current_conditionid);

      param4 = arcpy.Parameter(
          displayName   = "Road Tolls ($/shipment)"
         ,name          = "RoadTolls"
         ,datatype      = "GPDouble"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param4.value = conditions.roadtolls;

      param5 = arcpy.Parameter(
          displayName   = "Misc Cost ($/shipment)"
         ,name          = "MiscCost"
         ,datatype      = "GPDouble"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param5.value = conditions.misccost;

      param6 = arcpy.Parameter(
          displayName   = "Total Cost Multiplier (add % of total cost)"
         ,name          = "TotalCostMultiplier"
         ,datatype      = "GPDouble"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param6.value = conditions.totalcostmultiplier;

      param7 = arcpy.Parameter(
          displayName   = "Vehicle Decon Cost ($/shipment)"
         ,name          = "VehicleDeconCost"
         ,datatype      = "GPDouble"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param7.value = conditions.vehicledeconcost;

      param8 = arcpy.Parameter(
          displayName   = "Staging Site Cost ($/day)"
         ,name          = "StagingSiteCost"
         ,datatype      = "GPDouble"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param8.value = conditions.stagingsitecost;

      param9 = arcpy.Parameter(
          displayName   = "Number of Trucks Available"
         ,name          = "NumberofTrucksAvailable"
         ,datatype      = "GPLong"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param9.value = conditions.numberoftrucksavailable;

      param10 = arcpy.Parameter(
          displayName   = "Driving Hours (hrs/day)"
         ,name          = "DrivingHours"
         ,datatype      = "GPDouble"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param10.value = conditions.drivinghours;

      param11 = arcpy.Parameter(
          displayName   = "Stashed Condition ID"
         ,name          = "StashedConditionID"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param11.value = param2.value;

      param12 = arcpy.Parameter(
          displayName   = "Stashed Scenario Characteristics"
         ,name          = "StashedScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param12.columns = copy.deepcopy(param1.columns);
      param12.value   = copy.deepcopy(param1.value);

      params = [
          param0
         ,param1
         ,param2
         ,param3
         ,param4
         ,param5
         ,param6
         ,param7
         ,param8
         ,param9
         ,param10
         ,param11
         ,param12
      ];

      del haz;
      return params;

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      if not parameters[9].hasBeenValidated and parameters[9].value <= 0:
         parameters[9].value = 1;
         
      if not parameters[10].hasBeenValidated and parameters[10].value <= 0:
         parameters[10].value = 1;
      
      if parameters[1].valueAsText != parameters[12].valueAsText              \
      and parameters[1].valueAsText is not None                               \
      and parameters[12].valueAsText is not None:
         if parameters[1].value[0][0] == 'Information is read-only':
            parameters[1].value = copy.deepcopy(parameters[12].value);
         else:
            parameters[1].value = [['Information is read-only','']] + copy.deepcopy(parameters[12].value);

      if not parameters[3].hasBeenValidated:

         if parameters[3].value is not None and parameters[3].valueAsText != "":
            parameters[2].value = None;
            parameters[2].filter.list = [' '];

         elif parameters[3].value is None or parameters[3].valueAsText == "":
            haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

            conditionlist = haz.conditions.fetchConditionIDs();

            if haz.system_cache.current_conditionid is None:
               haz.system_cache.current_conditionid = conditionlist[0];

            parameters[2].value = haz.system_cache.current_conditionid;
            parameters[2].filter.list = conditionlist;

      if not parameters[2].hasBeenValidated and parameters[2].value != parameters[11].value  \
      and parameters[11].value is not None                                                   \
      and parameters[3].valueAsText is None:

         conditions = obj_Condition.Condition();
         conditions.loadConditionID(parameters[2].valueAsText);

         parameters[4].value  = conditions.roadtolls;
         parameters[5].value  = conditions.misccost;
         parameters[6].value  = conditions.totalcostmultiplier;
         parameters[7].value  = conditions.vehicledeconcost;
         parameters[8].value  = conditions.stagingsitecost;
         parameters[9].value  = conditions.numberoftrucksavailable;
         parameters[10].value = conditions.drivinghours;

         parameters[11].value = parameters[1].valueAsText;

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return gp_SetScenarioConditions.execute(self,parameters,messages);

###############################################################################
class DefineScenario(object):

   #...........................................................................
   def __init__(self):

      self.label = "Define Scenario"
      self.name  = "DefineScenario"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      ws  = obj_Waste.Waste();

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
      if util.sniff_editing_state():
         err_val = "Please save or delete all pending edits before proceeding.";
         err_enb = True;
      else:
         err_val = None;
         err_enb = False;

      param0 = arcpy.Parameter(
          displayName   = ""
         ,name          = "ErrorCondition"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = err_enb
      );
      param0.value = err_val;
      
      #########################################################################
      param1 = arcpy.Parameter(
          displayName   = ''
         ,name          = "ScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Scenario Characteristics"
      );
      (param1.columns,param1.value) = haz.get_scenario_characteristics();

      param2 = arcpy.Parameter(
          displayName   = "Scenario ID"
         ,name          = "ScenarioID"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
      );
      param2.value = scenarioid;

      param3 = arcpy.Parameter(
          displayName   = "Waste Type"
         ,name          = "WasteType"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = True
      );
      param3.value       = waste_type;
      param3.filter.type = "ValueList";
      param3.filter.list = ws.waste_types();

      param4 = arcpy.Parameter(
          displayName   = "Waste Medium"
         ,name          = "WasteMedium"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = True
      );
      param4.value       = waste_medium;
      param4.filter.type = "ValueList";
      param4.filter.list = ws.waste_mediums();

      param5 = arcpy.Parameter(
          displayName   = "Waste Unit"
         ,name          = "WasteUnit"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = True
      );
      param5.value       = waste_unit;
      param5.filter.type = "ValueList";
      param5.filter.list = ws.waste_units(unit_system = unit_system);

      param6 = arcpy.Parameter(
          displayName   = "Waste Amount"
         ,name          = "WasteAmount"
         ,datatype      = "GPDouble"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param6.value = waste_amount;

      param7 = arcpy.Parameter(
          displayName   = "Stashed Unit System"
         ,name          = "StashedUnitSystem"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param7.value = unit_system;

      param8 = arcpy.Parameter(
          displayName   = "Stashed Waste Type"
         ,name          = "StashedWasteType"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param8.value = param3.value;

      param9 = arcpy.Parameter(
          displayName   = "Stashed Waste Medium"
         ,name          = "StashedWasteMedium"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param9.value = param4.value;

      param10 = arcpy.Parameter(
          displayName   = "Stashed Waste Unit"
         ,name          = "StashedWasteUnit"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param10.value = param5.value;

      param11 = arcpy.Parameter(
          displayName   = "Stashed Scenario Characteristics"
         ,name          = "StashedScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param11.columns = copy.deepcopy(param1.columns);
      param11.value   = copy.deepcopy(param1.value);

      params = [
          param0
         ,param1
         ,param2
         ,param3
         ,param4
         ,param5
         ,param6
         ,param7
         ,param8
         ,param9
         ,param10
         ,param11
      ];

      del haz;
      del ws;
      return params;

   #...........................................................................
   def isLicensed(self):

      return True;

   #...........................................................................
   def updateParameters(self, parameters):

      ws = obj_Waste.Waste();

      if parameters[1].valueAsText != parameters[11].valueAsText              \
      and parameters[1].valueAsText is not None                               \
      and parameters[11].valueAsText is not None:
         if parameters[1].value[0][0] == 'Information is read-only':
            parameters[1].value = copy.deepcopy(parameters[11].value);
         else:
            parameters[1].value = [['Information is read-only','']] + copy.deepcopy(parameters[11].value);

      if parameters[3].value and not parameters[3].hasBeenValidated:

         if parameters[3].value != parameters[8].value:

            medium = ws.filter_medium(
                waste_type   = parameters[3].valueAsText
               ,waste_medium = None
            );

            if len(medium) > 1:
               parameters[4].value = None;
               parameters[4].filter.list = medium + [' '];
               parameters[5].value = None;
               parameters[5].filter.list = [' '];

            elif len(medium) == 1:
               parameters[4].value = medium[0];
               parameters[4].filter.list = medium;

               units = ws.filter_unit(
                   waste_type   = parameters[3].valueAsText
                  ,waste_medium = medium[0]
                  ,unit_system  = parameters[7].valueAsText
               );

               parameters[5].value = units[0];
               parameters[5].filter.list = units;

      elif parameters[4].value and not parameters[4].hasBeenValidated:

         if parameters[4].valueAsText == " ":
            parameters[4].value = parameters[4].filter.list[0];

            units = ws.filter_unit(
                waste_type   = parameters[3].valueAsText
               ,waste_medium = parameters[4].valueAsText
               ,unit_system  = parameters[7].valueAsText
            );

            parameters[5].value = units[0];
            parameters[5].filter.list = units;

         elif parameters[4].value != parameters[9].value:

            units = ws.filter_unit(
                waste_type   = parameters[3].valueAsText
               ,waste_medium = parameters[4].valueAsText
               ,unit_system  = parameters[7].valueAsText
            );

            if len(units) > 1:
               parameters[5].value = None;
               parameters[5].filter.list = units + [' '];

            elif len(units) == 1:
               parameters[5].value = units[0];
               parameters[5].filter.list = units;

      elif parameters[5].valueAsText == " ":

         if parameters[4].valueAsText == " " or parameters[4].value is None:
            parameters[4].value = parameters[4].filter.list[0];

         units = ws.filter_unit(
             waste_type   = parameters[3].valueAsText
            ,waste_medium = parameters[4].valueAsText
            ,unit_system  = parameters[7].valueAsText
         );

         parameters[5].value = units[0];
         parameters[5].filter.list = units;

      parameters[8].value  = parameters[3].value;
      parameters[9].value  = parameters[4].value;
      parameters[10].value = parameters[5].value;

      del ws;
      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return gp_DefineScenario.execute(self,parameters,messages);

###############################################################################
class LoadFacilitiesToNetwork(object):

   #...........................................................................
   def __init__(self):
      self.label = "Load Facilities To Network"
      self.name  = "LoadFacilitiesToNetwork"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

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
      if util.sniff_editing_state():
         err_val = "Please save or delete all pending edits before proceeding.";
         err_enb = True;
      else:
         err_val = None;
         err_enb = False;

      param0 = arcpy.Parameter(
          displayName   = ""
         ,name          = "ErrorCondition"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = err_enb
      );
      param0.value = err_val;
      
      #########################################################################
      param1 = arcpy.Parameter(
          displayName   = ''
         ,name          = "ScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Scenario Characteristics"
      );
      (param1.columns,param1.value) = haz.get_scenario_characteristics();

      if waste_medium == 'Volume Liquid':
         facility_subtypes = [
             'RCRA Hazardous Waste Landfill'
            ,'RCRA Hazardous Waste Landfill with LARW'
            ,'Radioactive Waste Facility'
         ];
      
      else:      
         facility_subtypes = [
             'RCRA Hazardous Waste Landfill'
            ,'RCRA Hazardous Waste Landfill with LARW'
            ,'Radioactive Waste Facility'
            ,'Municipal Solid Waste (MSW) Landfill'
            ,'Construction and Demolition (C&D) Landfill'
         ];

      if waste_type == 'Radioactive: Contact-Handled' \
      or waste_type == 'Radioactive: Remote-Handled':
         facility_defaults = '"' + facility_subtypes[2] + '"';

      elif waste_type == 'Hazardous':
         facility_defaults = '"' + facility_subtypes[0] + '"';

      elif waste_type == 'Municipal Solid Waste (MSW)':
         facility_defaults = '"' + facility_subtypes[3] + '"';

      elif waste_type == 'Construction and Demolition':
         facility_defaults = '"' + facility_subtypes[4] + '"';

      param2 = arcpy.Parameter(
          displayName   = "Select Disposal Facility Types"
         ,name          = "SelectDispFacTypes"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = True
         ,enabled       = True
      );
      param2.value       = facility_defaults;
      param2.filter.type = "ValueList";
      param2.filter.list = facility_subtypes;

      param3 = arcpy.Parameter(
          displayName   = "Load Default Facilities"
         ,name          = "LoadDefaultFacilities"
         ,datatype      = "GPBoolean"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param3.value = True;

      param4 = arcpy.Parameter(
          displayName   = "Add User-Defined Facilities"
         ,name          = "AddUserDefinedFacilities"
         ,datatype      = "DEFeatureClass"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = True
         ,enabled       = True
      );

      param5 = arcpy.Parameter(
          displayName   = "Limit By Support Area"
         ,name          = "LimitBySupportArea"
         ,datatype      = "GPBoolean"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param5.value = True;

      param6 = arcpy.Parameter(
          displayName   = "Truncate Existing Facilities"
         ,name          = "TruncateFacilities"
         ,datatype      = "GPBoolean"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param6.value = False;

      param7 = arcpy.Parameter(
          displayName   = "Stashed Scenario Characteristics"
         ,name          = "StashedScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param7.columns = copy.deepcopy(param1.columns);
      param7.value   = copy.deepcopy(param1.value);

      params = [
          param0
         ,param1
         ,param2
         ,param3
         ,param4
         ,param5
         ,param6
         ,param7
      ];

      del haz;
      return params;

   #...........................................................................
   def isLicensed(self):

      return True

   #...........................................................................
   def updateParameters(self,parameters):

      if parameters[1].valueAsText != parameters[7].valueAsText               \
      and parameters[1].valueAsText is not None                               \
      and parameters[7].valueAsText is not None:
         if parameters[1].value[0][0] == 'Information is read-only':
            parameters[1].value = copy.deepcopy(parameters[7].value);
         else:
            parameters[1].value = [['Information is read-only','']] + copy.deepcopy(parameters[7].value);

      return;

   #...........................................................................
   def updateMessages(self,parameters):

      return;

   #...........................................................................
   def execute(self,parameters,messages):

      return gp_LoadFacilitiesToNetwork.execute(self,parameters,messages);

###############################################################################
class SolveRoutingScenario(object):

   #...........................................................................
   def __init__(self):
      self.label = "Solve Routing Scenario"
      self.name  = "SolveRoutingScenario"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
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
      if util.sniff_editing_state():
         err_val = "Please save or delete all pending edits before proceeding.";
         err_enb = True;
      else:
         err_val = None;
         err_enb = False;

      param0 = arcpy.Parameter(
          displayName   = ""
         ,name          = "ErrorCondition"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = err_enb
      );
      param0.value = err_val;
      
      #########################################################################
      param1 = arcpy.Parameter(
          displayName   = ''
         ,name          = "ScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Scenario Characteristics"
      );
      (param1.columns,param1.value) = haz.get_scenario_characteristics();

      param2 = arcpy.Parameter(
          displayName   = "Change Scenario ID"
         ,name          = "ChangeScenarioID"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param2.value = scenarioid;

      param3 = arcpy.Parameter(
          displayName   = "Suggested # Of Facilities To Find"
         ,name          = "SuggestedNumbOfFacilitiesToFind"
         ,datatype      = "GPLong"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      
      wstat = haz.facility_amt_accepted_stats();

      if wstat is None                                                        \
      or wstat.average_fac_amt_accepted is None                               \
      or waste_amount is None                                                 \
      or wstat.average_fac_amt_accepted <= 0:
         param3.value =  None;
      
      else:
         suggested_count = waste_amount / wstat.average_fac_amt_accepted;

         if suggested_count < 1:
            param3.value = 1;
            
         elif suggested_count > 1 and suggested_count < 5:
            param3.value = suggested_count + 1;
            
         else:
            param3.value = int(suggested_count * 1.25);

      param4 = arcpy.Parameter(
          displayName   = "Stashed Scenario ID"
         ,name          = "StashedScenarioID"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
      );
      param4.value = scenarioid;

      param5 = arcpy.Parameter(
          displayName   = "Stashed Unit System"
         ,name          = "StashedUnitSystem"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
      );
      param5.value = unit_system;

      param6 = arcpy.Parameter(
          displayName   = "Stashed Scenario Characteristics"
         ,name          = "StashedScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param6.columns = copy.deepcopy(param1.columns);
      param6.value   = copy.deepcopy(param1.value);

      params = [
          param0
         ,param1
         ,param2
         ,param3
         ,param4
         ,param5
         ,param6
      ];

      del haz;
      return params;

   #...........................................................................
   def isLicensed(self):

      return True

   #...........................................................................
   def updateParameters(self, parameters):

      if parameters[1].valueAsText != parameters[6].valueAsText               \
      and parameters[1].valueAsText is not None                               \
      and parameters[6].valueAsText is not None:
         if parameters[1].value[0][0] == 'Information is read-only':
            parameters[1].value = copy.deepcopy(parameters[6].value);
         else:
            parameters[1].value = [['Information is read-only','']] + copy.deepcopy(parameters[6].value);

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return gp_SolveRoutingScenario.execute(self,parameters,messages);

###############################################################################
class CalculateLogisticsPlanningEstimates(object):

   #...........................................................................
   def __init__(self):
      self.label = "Calculate Logistics Planning Estimates"
      self.name  = "CalculateLogisticsPlanningEstimates"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
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

      #########################################################################
      if util.sniff_editing_state():
         err_val = "Please save or delete all pending edits before proceeding.";
         err_enb = True;
      else:
         err_val = None;
         err_enb = False;

      param0 = arcpy.Parameter(
          displayName   = ""
         ,name          = "ErrorCondition"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = err_enb
      );
      param0.value = err_val;
      
      #########################################################################
      param1 = arcpy.Parameter(
          displayName   = ''
         ,name          = "ScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Scenario Characteristics"
      );
      (param1.columns,param1.value) = haz.get_scenario_characteristics();

      param2 = arcpy.Parameter(
          displayName   = "Scenario ID"
         ,name          = "ScenarioID"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param2.value       = scenarioid;
      param2.filter.type = "ValueList";
      param2.filter.list = haz.scenario.fetchScenarioIDs();

      param3 = arcpy.Parameter(
          displayName   = "Condition ID"
         ,name          = "ConditionID"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param3.value       = conditionid;
      param3.filter.type = "ValueList";
      param3.filter.list = conditionlist;

      param4 = arcpy.Parameter(
          displayName   = "Factor Set ID"
         ,name          = "FactorSetID"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param4.value       = factorid;
      param4.filter.type = "ValueList";
      param4.filter.list = factorlist;

      param5 = arcpy.Parameter(
          displayName   = "Map Settings"
         ,name          = "MapSettings"
         ,datatype      = "GPString"
         ,parameterType = "Required"
         ,direction     = "Input"
         ,enabled       = True
      );
      param5.value       = 'Disable Map';
      param5.filter.type = "ValueList";
      param5.filter.list = [
          'Zoom to Routes'
         ,'Zoom to Support Area'
         ,'User Zoom'
         ,'Disable Map'
      ];

      param6 = arcpy.Parameter(
          displayName   = "Stashed Scenario ID"
         ,name          = "StashedScenarioID"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = False
      );
      param6.value = param2.value;
      
      param7 = arcpy.Parameter(
          displayName   = "Stashed Condition ID"
         ,name          = "StashedConditionID"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = False
      );
      param7.value = param3.value;
      
      param8 = arcpy.Parameter(
          displayName   = "Stashed Factor ID"
         ,name          = "StashedFactorID"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = False
      );
      param8.value = param4.value;

      param9 = arcpy.Parameter(
          displayName   = "Stashed Scenario Characteristics"
         ,name          = "StashedScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param9.columns = copy.deepcopy(param1.columns);
      param9.value   = copy.deepcopy(param1.value);

      params = [
          param0
         ,param1
         ,param2
         ,param3
         ,param4
         ,param5
         ,param6
         ,param7
         ,param8
         ,param9
      ];

      del haz;
      return params;

   #...........................................................................
   def isLicensed(self):

      return True

   #...........................................................................
   def updateParameters(self, parameters):

      if parameters[1].valueAsText != parameters[9].valueAsText               \
      and parameters[1].valueAsText is not None                               \
      and parameters[9].valueAsText is not None:
         if parameters[1].value[0][0] == 'Information is read-only':
            parameters[1].value = copy.deepcopy(parameters[9].value);
         else:
            parameters[1].value = [['Information is read-only','']] + copy.deepcopy(parameters[9].value);

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return gp_CalculateLogisticsPlanningEstimates.execute(self,parameters,messages);

###############################################################################
class ExportLogisticsPlanningResults(object):

   #...........................................................................
   def __init__(self):
      self.label = "Export Logistics Planning Results"
      self.name  = "ExportLogisticsPlanningResults"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
      (
          scenarioid
         ,unit_system
         ,waste_type
         ,waste_medium
         ,waste_amount
         ,waste_unit
      ) = haz.current_scenario();

      #########################################################################
      if util.sniff_editing_state():
         err_val = "Please save or delete all pending edits before proceeding.";
         err_enb = True;
      else:
         err_val = None;
         err_enb = False;

      param0 = arcpy.Parameter(
          displayName   = ""
         ,name          = "ErrorCondition"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = err_enb
      );
      param0.value = err_val;
      
      #########################################################################
      param1 = arcpy.Parameter(
          displayName   = ''
         ,name          = "ScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = True
         ,category      = "Scenario Characteristics"
      );
      (param1.columns,param1.value) = haz.get_scenario_characteristics();
      
      #########################################################################
      param2 = arcpy.Parameter(
          displayName   = "Export File"
         ,name          = "ExportFile"
         ,datatype      = "DEFile"
         ,parameterType = "Required"
         ,direction     = "Output"
         ,enabled       = True
      );
      param2.filter.list = ['xlsx'];

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

      # This parameter should be a multiValue but bugs
      param3 = arcpy.Parameter(
          displayName   = "Scenario IDs"
         ,name          = "ScenarioIDs"
         ,datatype      = "String"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = True
      );
      param3.value = deflt;
      param3.filter.type = "ValueList";
      param3.filter.list = ary;
      
      param4 = arcpy.Parameter(
          displayName   = "Stashed Scenario Characteristics"
         ,name          = "StashedScenarioCharacteristics"
         ,datatype      = "GPValueTable"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,multiValue    = False
         ,enabled       = False
         ,category      = "Scenario Characteristics"
      );
      param4.columns = copy.deepcopy(param1.columns);
      param4.value   = copy.deepcopy(param1.value);

      params = [
          param0
         ,param1
         ,param2
         ,param3
         ,param4
      ];

      del haz;
      return params;

   #...........................................................................
   def isLicensed(self):

      return True

   #...........................................................................
   def updateParameters(self, parameters):

      if parameters[1].valueAsText != parameters[4].valueAsText               \
      and parameters[1].valueAsText is not None                               \
      and parameters[4].valueAsText is not None:
         if parameters[1].value[0][0] == 'Information is read-only':
            parameters[1].value = copy.deepcopy(parameters[4].value);
         else:
            parameters[1].value = [['Information is read-only','']] + copy.deepcopy(parameters[4].value);

      return;

   #...........................................................................
   def updateMessages(self, parameters):

      return;

   #...........................................................................
   def execute(self, parameters, messages):

      return gp_ExportLogisticsPlanningResults.execute(self,parameters,messages);

###############################################################################
class RemoveWorkEnvironment(object):

   #...........................................................................
   def __init__(self):

      self.label = "Remove Work Environment"
      self.name  = "RemoveWorkEnvironment"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):
      
      #########################################################################
      if util.sniff_editing_state():
         err_val = "Please save or delete all pending edits before proceeding.";
         err_enb = True;
      else:
         err_val = None;
         err_enb = False;

      param0 = arcpy.Parameter(
          displayName   = ""
         ,name          = "ErrorCondition"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = err_enb
      );
      param0.value = err_val;
      
      #########################################################################
      
      params = [
         param0
      ];

      return params;

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

      return gp_RemoveWorkEnvironment.execute(self,parameters,messages);

###############################################################################
class ClearScenarios(object):

   #...........................................................................
   def __init__(self):

      self.label = "Clear Scenarios"
      self.name  = "ClearScenarios"
      self.description = "Documentation.";
      self.canRunInBackground = False;

   #...........................................................................
   def getParameterInfo(self):

      #########################################################################
      if util.sniff_editing_state():
         err_val = "Please save or delete all pending edits before proceeding.";
         err_enb = True;
      else:
         err_val = None;
         err_enb = False;

      param0 = arcpy.Parameter(
          displayName   = ""
         ,name          = "ErrorCondition"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = err_enb
      );
      param0.value = err_val;
      
      #########################################################################
      
      params = [
         param0
      ];

      return params;

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

      haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

      arcpy.TruncateTable_management(haz.scenario_results.dataSource);
      arcpy.TruncateTable_management(haz.network.routes.dataSource);
      haz.network.routes.visible = True;

      del haz;
      return None;

###############################################################################

