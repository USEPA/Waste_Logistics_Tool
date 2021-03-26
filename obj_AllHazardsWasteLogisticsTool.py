import arcpy,os
from types import SimpleNamespace

import obj_NetworkAnalysisDataset;
import obj_Condition;
import obj_Factors;
import obj_SystemCache;
import obj_Scenario;
import obj_Layer;

###############################################################################
import importlib
importlib.reload(obj_NetworkAnalysisDataset);
importlib.reload(obj_Condition);
importlib.reload(obj_Factors);
importlib.reload(obj_SystemCache);
importlib.reload(obj_Scenario);
importlib.reload(obj_Layer);

###############################################################################
class AllHazardsWasteLogisticsTool:

   aprx             = None;
   map              = None;
   network          = None;
   support_area     = None;
   incident_area    = None;
   scenario_results = None;
   conditions       = None;
   factors          = None;
   scenario         = None;
   system_cache     = None;

   #...........................................................................
   def __init__(self):

      self.network = obj_NetworkAnalysisDataset.NetworkAnalysisDataset();

      self.aprx = self.network.aprx;
      self.map  = self.network.map;

      conditions_table = None;
      scenario_table   = None;
      shipment_loading = None;
      cplm_unit_rates  = None;
      fixed_trans_cost = None;
      labor_costs      = None;
      disposal_fees    = None;
      acceptance_rates = None;
      system_cache     = None;

      for lyr in self.map.listLayers():

         if lyr.supports("name") and lyr.name == "SupportArea":
            self.support_area = obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "IncidentArea":
            self.incident_area = obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "ScenarioResults":
            self.scenario_results = obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "Conditions":
            conditions_table = obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "Scenario":
            scenario_table = obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "ShipmentLoading":
            shipment_loading = obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "CPLMUnitRates":
            cplm_unit_rates = obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "FixedTransCost":
            fixed_trans_cost = obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "LaborCosts":
            labor_costs = obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "DisposalFees":
            disposal_fees = obj_Layer.Layer(lyr);
            
         if lyr.supports("name") and lyr.name == "AcceptanceRates":
            acceptance_rates = obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "SystemCache":
            system_cache = obj_Layer.Layer(lyr);

      if conditions_table is not None:
         self.conditions = obj_Condition.Condition(conditions_table);

      if shipment_loading is not None:
         self.factors = obj_Factors.Factors(
             shipment_loading_layer = shipment_loading
            ,cplm_unit_rates_layer  = cplm_unit_rates
            ,fixed_trans_cost_layer = fixed_trans_cost
            ,labor_costs_layer      = labor_costs
            ,disposal_fees_layer    = disposal_fees
            ,acceptance_rates_layer = acceptance_rates
         );

      if system_cache is not None:
         self.system_cache = obj_SystemCache.SystemCache(system_cache);

      if scenario_table is not None:
         self.scenario = obj_Scenario.Scenario(
             scenario_table
            ,self.system_cache.current_scenarioid
         );

   #...........................................................................
   def current_scenario(self):

      self.system_cache.loadSystemCache();
      unit_system = self.system_cache.current_unit_system;
      
      if self.system_cache.current_scenarioid is None:
         sid = self.new_scenarioid();

         return (
             sid
            ,unit_system
            ,None
            ,None
            ,None
            ,None
         );

      else:
         self.scenario.loadScenarioID(
            self.system_cache.current_scenarioid
         );

         return (
             self.system_cache.current_scenarioid
            ,unit_system
            ,self.scenario.waste_type
            ,self.scenario.waste_medium
            ,self.scenario.waste_amount
            ,self.scenario.waste_unit
         );

   #...........................................................................
   def new_scenarioid(self):

      output = [0];

      fields = [
          'scenarioid'
      ];

      rows = arcpy.da.SearchCursor(
          in_table     = self.scenario_results.dataSource
         ,field_names  = (
             'scenarioid'
          )
         ,where_clause = "scenarioid LIKE 'Scenario%'"
      );

      for row in rows:
         val = row[0].replace('Scenario','');

         if val.isdigit():
            output.append(int(val));

      del rows;

      output = sorted(output,reverse=True);

      return 'Scenario' + str(output[0]);
      
   #...........................................................................
   def facility_amt_accepted_stats(self):
      
      if self.scenario is None:
         return None;
         
      count_facility_qty_accepted = 0;
      total_facility_qty_accepted = 0;
      average_fac_amt_accepted    = None;
      percent_fac_of_waste        = None;

      if self.scenario.waste_medium is not None:
      
         if self.scenario.waste_medium == 'Volume Liquid':
            column_name = "facility_qty_accepted_volume_liquid";
            
         elif self.scenario.waste_medium == 'Volume Solid':
            column_name = "facility_qty_accepted_volume_solid";
         
         else:
            raise arcpy.ExecuteError("Error");
         
         rows = arcpy.da.SearchCursor(
             in_table     = self.network.facilities.dataSource
            ,field_names  = (
                'objectid'
               ,column_name
             )
            ,where_clause = None
         );

         for row in rows:
            count_facility_qty_accepted += 1;
            total_facility_qty_accepted += row[1];
            
         if count_facility_qty_accepted == 0:
            average_fac_amt_accepted = 0;
            percent_fac_of_waste     = 0;
            
         else:
            average_fac_amt_accepted = total_facility_qty_accepted / count_facility_qty_accepted;
            
            if self.scenario is None or self.scenario.waste_amount is None:
               percent_fac_of_waste = None;
               
            else:
               percent_fac_of_waste = self.scenario.waste_amount / total_facility_qty_accepted;
               
               if percent_fac_of_waste > 1:
                  percent_fac_of_waste = 1;
               
         del rows;

      ret = {}
      ret["total_facility_qty_accepted"] = total_facility_qty_accepted;
      ret["average_fac_amt_accepted"]    = average_fac_amt_accepted;
      ret["percent_fac_of_waste"]        = percent_fac_of_waste;
      
      return SimpleNamespace(**ret);

   #...........................................................................
   def get_scenario_characteristics(self):
   
      columns = [
          ['String','       Characteristic']
         ,['String','Value']
      ];
   
      if self.system_cache is None or self.system_cache.current_scenarioid is None:
         scenarioid = '';
      else:
         scenarioid = self.system_cache.current_scenarioid;
         
      if self.scenario is None or self.scenario.waste_type is None:
         waste_type = '';
      else:
         waste_type = self.scenario.waste_type;
         
      if self.scenario is None or self.scenario.waste_medium is None:
         waste_medium = '';
      else:
         waste_medium = self.scenario.waste_medium;      
         
      if self.scenario is None or self.scenario.waste_amount is None:
         waste_amount = '';
      else:
         waste_amount = str(self.scenario.waste_amount);
         
      if self.scenario is None or self.scenario.waste_unit is None:
         waste_unit = '';
      else:
         waste_unit = self.scenario.waste_unit;      
         
      if self.system_cache is None or self.system_cache.current_conditionid is None:
         conditionid = '';
      else:
         conditionid = self.system_cache.current_conditionid;
         
      if self.system_cache is None or self.system_cache.current_factorid is None:
         factorid = '';
      else:
         factorid = self.system_cache.current_factorid;
         
      wstat = self.facility_amt_accepted_stats();
      
      if wstat is None or wstat.average_fac_amt_accepted is None:
         average_fac_amt_accepted = '';
      else:
         average_fac_amt_accepted = str(round(wstat.average_fac_amt_accepted,4));
         
      if wstat is None or wstat.total_facility_qty_accepted is None:
         tfqa = '';
      else:
         tfqa = str(round(wstat.total_facility_qty_accepted,4));
      
      value = "\"Scenario ID\" \""            + scenarioid   + "\";"                    \
            + "\"Waste Type\" \""             + waste_type   + "\";"                    \
            + "\"Waste Medium\" \""           + waste_medium + "\";"                    \
            + "\"Waste Amount\" \""           + waste_amount + " " + waste_unit + "\";" \
            + "\"Total Estimated Facility Capacity\" \"" + tfqa + " " + waste_unit + "\";"       \
            + "\"Condition ID\" \""           + conditionid  + "\";"                    \
            + "\"Factor ID\" \""              + factorid     + "\";";
      
      return (columns,value);

