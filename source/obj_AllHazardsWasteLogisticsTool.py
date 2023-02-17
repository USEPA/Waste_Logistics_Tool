import arcpy,os,sys;
from types import SimpleNamespace

import source.obj_NetworkAnalysisDataset;
import source.obj_Condition;
import source.obj_Factors;
import source.obj_SystemCache;
import source.obj_Transporters;
import source.obj_Scenario;
import source.obj_Layer;
import source.obj_Waste;
import source.util;

###############################################################################
import importlib
importlib.reload(source.obj_NetworkAnalysisDataset);
importlib.reload(source.obj_Condition);
importlib.reload(source.obj_Factors);
importlib.reload(source.obj_SystemCache);
importlib.reload(source.obj_Transporters);
importlib.reload(source.obj_Scenario);
importlib.reload(source.obj_Layer);
importlib.reload(source.obj_Waste);
importlib.reload(source.util);

###############################################################################
class AllHazardsWasteLogisticsTool:

   #...........................................................................
   def __init__(self):
      #////////////////////////////////////////////////////////////////////////
      self.aprx                     = None;
      self.map                      = None;
      self.network                  = None;
      self.support_area             = None;
      self.incident_area            = None;
      self.scenario_results         = None;
      self.conditions               = None;
      self.factors                  = None;
      self.scenario                 = None;
      self.system_cache             = None;
      self.waste                    = source.obj_Waste.Waste();      
      #////////////////////////////////////////////////////////////////////////

      try:
         self.network = source.obj_NetworkAnalysisDataset.NetworkAnalysisDataset();
      except Exception as e:
         source.util.dzlog_e(sys.exc_info(),'ERROR');
         raise;

      self.aprx = self.network.aprx;
      self.map  = self.network.map;

      self.conditions_table       = None;
      self.scenario_table         = None;
      
      self.modes                  = [];  
      self.disposal_fees          = [];
      self.facility_capacities    = [];
      self.transporters           = [];
      self.road_transporter_list  = [];
      self.rail_transporter_list  = [];
      
      self.modes_layer            = None;
      self.system_cache_table     = None;
      self.transporters_layer     = None;
      self.labor_costs_layer      = None;
      self.fixed_trans_cost_layer = None;
      self.cplm_unit_rates_layer  = None;
      self.disposal_fees_layer    = None;
      
      for lyr in self.map.listLayers():

         ######################################################################
         if lyr.supports("name") and lyr.name == "SupportArea":
            self.support_area     = source.obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "IncidentArea":
            self.incident_area    = source.obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "ScenarioResults":
            self.scenario_results = source.obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "Conditions":
            self.conditions_table = source.obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "Scenario":
            self.scenario_table   = source.obj_Layer.Layer(lyr);
            
         if lyr.supports("name") and lyr.name == "Transporters":
            self.transporters_layer = source.obj_Layer.Layer(lyr);

         ######################################################################
         if lyr.supports("name") and lyr.name == "Modes":
            self.modes_layer = source.obj_Layer.Layer(lyr);
            
         if lyr.supports("name") and lyr.name == "CPLMUnitRates":
            self.cplm_unit_rates_layer = source.obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "FixedTransCost":
            self.fixed_trans_cost_layer = source.obj_Layer.Layer(lyr);

         if lyr.supports("name") and lyr.name == "LaborCosts":
            self.labor_costs_layer = source.obj_Layer.Layer(lyr);

         ######################################################################
         if lyr.supports("name") and lyr.name == "DisposalFees":
            self.disposal_fees_layer = source.obj_Layer.Layer(lyr); 
         
         if lyr.supports("name") and lyr.name == "FacilityCapacities":
            self.facility_capacities_layer = source.obj_Layer.Layer(lyr);
            
         ######################################################################
         if lyr.supports("name") and lyr.name == "SystemCache":
            self.system_cache_table = source.obj_Layer.Layer(lyr);

      #........................................................................
      if self.conditions_table is not None:
         self.conditions = source.obj_Condition.Condition(self.conditions_table);
      else:
         self.conditions = source.obj_Condition.Condition();
         
      #........................................................................
      unit_system = None;
      if self.system_cache_table is not None:
         self.system_cache = source.obj_SystemCache.SystemCache(self.system_cache_table);
         unit_system       = self.system_cache.current_unit_system;

      #........................................................................
      if self.scenario_table is not None:
         
         self.scenario = source.obj_Scenario.Scenario(
             self.scenario_table
            ,self.system_cache.current_scenarioid
         );
         
      #........................................................................   
      if self.transporters_layer is not None:
      
         self.transporters = [];
         
         with arcpy.da.SearchCursor(
             in_table     = self.transporters_layer.dataSource
            ,field_names  = source.obj_Transporters.Transporters.fields
         ) as cursor:

            for row in cursor:
               transporterattrid = row[0];
               mode              = row[1];
               
               self.transporters.append(
                  source.obj_Transporters.Transporters(
                      transporterattrid            = transporterattrid
                     ,mode                         = mode
                     ,wastetype                    = row[2]
                     ,wastemedium                  = row[3]
                     ,containercapacity            = row[4]
                     ,containercapacityunit        = row[5]
                     ,containercountpertransporter = row[6]
                     ,transportersavailable        = row[7]
                     ,transportersprocessedperday  = row[8]
                  )
               );
               
               if   mode in ['road','Road'] and transporterattrid not in self.road_transporter_list:
                  self.road_transporter_list.append(transporterattrid);
                  
               elif mode in ['rail','Rail'] and transporterattrid not in self.rail_transporter_list:
                  self.rail_transporter_list.append(transporterattrid);
                  
      facilityattributesid = self.system_cache.current_facilityattributesid;
      arcpy.AddMessage(".   Current facility attributes id = " + str(facilityattributesid));
      #........................................................................
      if self.disposal_fees_layer is not None and facilityattributesid is not None:
      
         self.disposal_fees = [];
         
         with arcpy.da.SearchCursor(
             in_table     = self.disposal_fees_layer.dataSource
            ,field_names  = source.obj_DisposalFees.DisposalFees.fields
            ,where_clause = "facilityattributesid = " + source.util.sql_quote(facilityattributesid)
         ) as cursor:

            for row in cursor:
               self.disposal_fees.append(
                  source.obj_DisposalFees.DisposalFees(
                      facilityattributesid  = row[0]
                     ,facility_subtypeid    = row[1]
                     ,wastetype             = row[2]
                     ,wastemedium           = row[3]
                     ,costperone            = row[4]
                     ,costperoneunit        = row[5]
                  )
               );
            
      #........................................................................
      if self.facility_capacities_layer is not None and facilityattributesid is not None:
      
         self.facility_capacities = [];
         
         with arcpy.da.SearchCursor(
             in_table     = self.facility_capacities_layer.dataSource
            ,field_names  = source.obj_FacilityCapacities.FacilityCapacities.fields
            ,where_clause = "facilityattributesid = " + source.util.sql_quote(facilityattributesid)
         ) as cursor:

            for row in cursor:
               self.facility_capacities.append(
                  source.obj_FacilityCapacities.FacilityCapacities(
                      facilityattributesid  = row[0]
                     ,facility_subtypeid    = row[1]
                     ,wastetype             = row[2]
                     ,wastemedium           = row[3]
                     ,dailyvolumeperday     = row[4]
                     ,dailyvolumeperdayunit = row[5]
                     ,totalaccepted_days    = row[6]
                  )
               );

      #........................................................................
      if self.modes_layer is not None:
         
         self.factors = source.obj_Factors.Factors(
             modes_layer               = self.modes_layer
            ,cplm_unit_rates_layer     = self.cplm_unit_rates_layer
            ,fixed_trans_cost_layer    = self.fixed_trans_cost_layer
            ,labor_costs_layer         = self.labor_costs_layer
            ,disposal_fees_layer       = self.disposal_fees_layer
            ,facility_capacities_layer = self.facility_capacities
         );
         
         if self.scenario is not None and self.scenario.factorid is not None:
            self.factors.loadFactorID(factorid = self.scenario.factorid);
         
   #...........................................................................
   def current_scenario(self):

      if self.system_cache is None:
         return (
             None
            ,None
            ,None
            ,None
            ,None
            ,None
         );
      
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

      with arcpy.da.SearchCursor(
          in_table     = self.scenario_results.dataSource
         ,field_names  = (
             'scenarioid'
          )
         ,where_clause = "scenarioid LIKE 'Scenario%'"
      ) as cursor:

         for row in cursor:
            val = row[0].replace('Scenario','');

            if val.isdigit():
               output.append(int(val));

      output = sorted(output,reverse=True);

      return 'Scenario' + str(output[0]);
      
   #...........................................................................
   def transporterCapacity(self
      ,mode
      ,transporterattrid = None
      ,waste_type        = None
      ,waste_medium      = None
      ,unit_system       = None
   ):
      rez = {
          'containercapacity'            : None
         ,'containercapacityunit'        : None
         ,'containercountpertransporter' : None
         ,'transportersavailable'        : None
         ,'transportersprocessedperday'  : None
         ,'transportercapacity'          : None
         ,'transportercapacityunit'      : None
      }
      
      if   mode == 'Road' and transporterattrid is None:
         transporterattrid = self.system_cache.current.current_road_transporter;
      elif mode == 'Rail' and transporterattrid is None:  
         transporterattrid = self.system_cache.current.current_rail_transporter;
      
      if (mode == 'Road' and transporterattrid is not None)\
      or (mode == 'Rail' and transporterattrid is not None):
         if waste_type is None:
            waste_type = self.scenario.waste_type;
            
         if waste_medium is None:
            waste_medium = self.scenario.waste_medium;
            
         if unit_system is None:
            unit_system = self.system_cache.current_unit_system;
         
         containercapacity     = None;
         containercapacityunit = None;
         
         for obj in self.transporters:
            
            if  obj.transporterattrid == transporterattrid \
            and obj.mode              == mode              \
            and obj.wastetype         == waste_type        \
            and obj.wastemedium       == waste_medium:
               
               containercapacity            = obj.containercapacity;
               containercapacityunit        = obj.containercapacityunit;
               containercountpertransporter = obj.containercountpertransporter;
               transportersavailable        = obj.transportersavailable;
               transportersprocessedperday  = obj.transportersprocessedperday;
               break;
         
         if containercapacity is None:
            return rez;
            
         (cc,ccunit) = source.util.converter(
             in_unit     = containercapacityunit
            ,in_value    = containercapacity
            ,unit_system = unit_system
         );
         
         rez = {
             'containercapacity'            : cc
            ,'containercapacityunit'        : ccunit
            ,'containercountpertransporter' : containercountpertransporter
            ,'transportersavailable'        : transportersavailable
            ,'transportersprocessedperday'  : transportersprocessedperday
            ,'transportercapacity'          : cc * containercountpertransporter
            ,'transportercapacityunit'      : ccunit
         }
      
      return rez;
 
   #...........................................................................
   def CPLMUnitRate(self
      ,mode
      ,distance
      ,distance_unit
   ):
   
      return self.factors.CPLMUnitRate(
          mode                = mode
         ,distance            = distance
         ,distance_unit       = distance_unit
         ,waste_type          = self.scenario.waste_type
         ,waste_medium        = self.scenario.waste_medium
         ,unit_system         = self.system_cache.current_unit_system
      );
      
   #...........................................................................
   def fixedTransCost(self
      ,mode
      ,fixedcost_type
   ):
   
      return self.factors.fixedTransCost(
          mode                = mode
         ,fixedcost_type      = fixedcost_type
         ,waste_type          = self.scenario.waste_type
         ,waste_medium        = self.scenario.waste_medium
         ,unit_system         = self.system_cache.current_unit_system
      );
      
   #...........................................................................
   def laborCosts(self
      ,mode
   ):
   
      return self.factors.laborCosts(
          mode                = mode
      );
      
   #...........................................................................
   def get_facilityattributesids(self):
   
      rez = [];
      with arcpy.da.SearchCursor(
          in_table     = self.facility_capacities_layer.dataSource
         ,field_names  = ['facilityattributesid']
         ,where_clause = None
      ) as cursor:
      
         for row in cursor:
            if row[0] not in rez:
               rez.append(row[0]);
               
      return rez;
      
   #...........................................................................
   def disposalFees(self
      ,facility_subtypeids
      ,waste_type          = None
      ,waste_medium        = None
      ,unit_system         = None
   ):
      
      if waste_type is None:
         waste_type   = self.scenario.waste_type;
         
      if waste_medium is None:
         waste_medium = self.scenario.waste_medium;
         
      if unit_system is None:
         unit_system  = self.system_cache.current_unit_system;
      
      costperone     = None;
      costperoneunit = None;
      
      rez = {
          "costperone"      : 0
         ,"costperoneunit"  : 'zeroed'
      }
      
      for id in source.util.str2ary(facility_subtypeids):
         
         for obj in self.disposal_fees:
            wm = source.util.mediumMap(obj.wastemedium);
            
            if  obj.facility_subtypeid  == id          \
            and obj.wastetype           == waste_type  \
            and wm                      == waste_medium:
               costperone     = obj.costperone
               costperoneunit = obj.costperoneunit;
               break;
               break;
            
      if costperone is None and costperoneunit is None:
         return rez;
         
      (cpo,cpounit) = source.util.converter(
          in_unit     = costperoneunit
         ,in_value    = costperone
         ,unit_system = unit_system
      );
         
      rez = {
          "costperone"      : cpo
         ,"costperoneunit"  : cpounit
      }

      return rez;
   
   #...........................................................................
   def facilityCapacity(self
      ,facility_subtypeids
      ,waste_type          = None
      ,waste_medium        = None
      ,unit_system         = None
   ):
      
      if waste_type is None:
         waste_type   = self.scenario.waste_type;
         
      if waste_medium is None:
         waste_medium = self.scenario.waste_medium;
         
      if unit_system is None:
         unit_system  = self.system_cache.current_unit_system;
 
      dailyvolumeperday     = None;
      dailyvolumeperdayunit = None;
      
      rez = {
          "facility_dly_cap"      : None
         ,"facility_dly_cap_unit" : None
         ,"facility_qty_acpt"     : None
         ,"facility_qty_acpt_unit": None
      }
      
      for id in source.util.str2ary(facility_subtypeids):
         
         for obj in self.facility_capacities:
            wm = source.util.mediumMap(obj.wastemedium);
            
            if  obj.facility_subtypeid  == id          \
            and obj.wastetype           == waste_type  \
            and wm                      == waste_medium:
               
               totalaccepted_days    = obj.totalaccepted_days;
               dailyvolumeperday     = obj.dailyvolumeperday;
               dailyvolumeperdayunit = obj.dailyvolumeperdayunit;
               break;
               break;
      
      if dailyvolumeperday is None and dailyvolumeperdayunit is None:
         return rez;
         
      (dvpd,unit) = source.util.converter(
          in_unit     = dailyvolumeperdayunit
         ,in_value    = dailyvolumeperday
         ,unit_system = unit_system
      );
      
      rez = {
          "facility_dly_cap":       dvpd
         ,"facility_dly_cap_unit":  unit
         ,"facility_qty_acpt":      dvpd * totalaccepted_days
         ,"facility_qty_acpt_unit": unit
      }
      
      return rez;
      
   #...........................................................................
   def facility_amt_accepted_stats(self
      ,unit_system
   ):
      
      if self.scenario is None:
         return None;
         
      count_facility_qty_accepted = 0;
      total_facility_qty_accepted = 0;
      average_fac_amt_accepted    = None;
      percent_fac_of_waste        = None;

      if  self.scenario.waste_medium is not None \
      and self.system_cache.current_factorid is not None:
      
         with arcpy.da.SearchCursor(
             in_table     = self.network.facilities.dataSource
            ,field_names  = (
                'facility_subtypeids'
               ,'facility_accepts_no_waste'
               ,'fac_radc_solid_tot_acp'
               ,'fac_radc_solid_tot_acp_unt'
               ,'fac_radc_liquid_tot_acp'
               ,'fac_radc_liquid_tot_acp_unt'
               ,'fac_radr_solid_tot_acp'
               ,'fac_radr_solid_tot_acp_unt'
               ,'fac_radr_liquid_tot_acp'
               ,'fac_radr_liquid_tot_acp_unt'
               ,'fac_larw_solid_tot_acp'
               ,'fac_larw_solid_tot_acp_unt'
               ,'fac_haz_solid_tot_acp'
               ,'fac_haz_solid_tot_acp_unt'
               ,'fac_haz_liquid_tot_acp'
               ,'fac_haz_liquid_tot_acp_unt'
               ,'fac_msw_solid_tot_acp'
               ,'fac_msw_solid_tot_acp_unt'
               ,'fac_cad_solid_tot_acp'
               ,'fac_cad_solid_tot_acp_unt'
               ,'fac_nhaq_liquid_tot_acp'
               ,'fac_nhaq_liquid_tot_acp_unt'
             )
            ,where_clause = None
         ) as cursor:

            for row in cursor:
               facility_subtypeids         = source.util.clean_string(row[0]);
               facility_accepts_no_waste   = source.util.clean_boo(row[1]);
               
               fac_radc_solid_tot_acp      = source.util.clean_double(row[2]);
               fac_radc_solid_tot_acp_unt  = source.util.clean_string(row[3]);
               fac_radc_liquid_tot_acp     = source.util.clean_double(row[4]);
               fac_radc_liquid_tot_acp_unt = source.util.clean_string(row[5]);
               fac_radr_solid_tot_acp      = source.util.clean_double(row[6]);
               fac_radr_solid_tot_acp_unt  = source.util.clean_string(row[7]);
               fac_radr_liquid_tot_acp     = source.util.clean_double(row[8]);
               fac_radr_liquid_tot_acp_unt = source.util.clean_string(row[9]);
               fac_larw_solid_tot_acp      = source.util.clean_double(row[10]);
               fac_larw_solid_tot_acp_unt  = source.util.clean_string(row[11]);
               fac_haz_solid_tot_acp       = source.util.clean_double(row[12]);
               fac_haz_solid_tot_acp_unt   = source.util.clean_string(row[13]);
               fac_haz_liquid_tot_acp      = source.util.clean_double(row[14]);
               fac_haz_liquid_tot_acp_unt  = source.util.clean_string(row[15]);
               fac_msw_solid_tot_acp       = source.util.clean_double(row[16]);
               fac_msw_solid_tot_acp_unt   = source.util.clean_string(row[17]);
               fac_cad_solid_tot_acp       = source.util.clean_double(row[18]);
               fac_cad_solid_tot_acp_unt   = source.util.clean_string(row[19]);
               fac_nhaq_liquid_tot_acp     = source.util.clean_double(row[20]);
               fac_nhaq_liquid_tot_acp_unt = source.util.clean_string(row[21]);
               
               rez_amt = None;
               rez_unt = None;
               
               if facility_accepts_no_waste:
                  rez_amt = 0;
                  rez_unt = 'zeroed';
               
               else:
                  if   self.scenario.waste_type == 'Radioactive: Contact-Handled' and self.scenario.waste_medium == 'Volume Solid' \
                  and fac_radc_solid_tot_acp is not None:
                     rez_amt = fac_radc_solid_tot_acp;
                     rez_unt = fac_radc_solid_tot_acp_unt;
                     
                  elif self.scenario.waste_type == 'Radioactive: Contact-Handled' and self.scenario.waste_medium == 'Volume Liquid' \
                  and fac_radc_liquid_tot_acp is not None:
                     rez_amt = fac_radc_liquid_tot_acp;
                     rez_unt = fac_radc_liquid_tot_acp_unt;   
                     
                  elif   self.scenario.waste_type == 'Radioactive: Remote-Handled' and self.scenario.waste_medium == 'Volume Solid' \
                  and fac_radr_solid_tot_acp is not None:
                     rez_amt = fac_radr_solid_tot_acp;
                     rez_unt = fac_radr_solid_tot_acp_unt;
                     
                  elif self.scenario.waste_type == 'Radioactive: Remote-Handled' and self.scenario.waste_medium == 'Volume Liquid' \
                  and fac_radr_liquid_tot_acp is not None:
                     rez_amt = fac_radr_liquid_tot_acp;
                     rez_unt = fac_radr_liquid_tot_acp_unt; 
                     
                  elif   self.scenario.waste_type == 'Low-Activity Radioactive Waste' and self.scenario.waste_medium == 'Volume Solid' \
                  and fac_larw_solid_tot_acp is not None:
                     rez_amt = fac_larw_solid_tot_acp;
                     rez_unt = fac_larw_solid_tot_acp_unt;
                     
                  elif   self.scenario.waste_type == 'Hazardous' and self.scenario.waste_medium == 'Volume Solid' \
                  and fac_haz_solid_tot_acp is not None:
                     rez_amt = fac_haz_solid_tot_acp;
                     rez_unt = fac_haz_solid_tot_acp_unt;
                     
                  elif self.scenario.waste_type == 'Hazardous' and self.scenario.waste_medium == 'Volume Liquid' \
                  and fac_haz_liquid_tot_acp is not None:
                     rez_amt = fac_haz_liquid_tot_acp;
                     rez_unt = fac_haz_liquid_tot_acp_unt;
                     
                  elif   self.scenario.waste_type == 'Municipal Solid Waste (MSW)' and self.scenario.waste_medium == 'Volume Solid' \
                  and fac_msw_solid_tot_acp is not None:
                     rez_amt = fac_msw_solid_tot_acp;
                     rez_unt = fac_msw_solid_tot_acp_unt;
                     
                  elif   self.scenario.waste_type == 'Construction and Demolition' and self.scenario.waste_medium == 'Volume Solid' \
                  and fac_cad_solid_tot_acp is not None:
                     rez_amt = fac_cad_solid_tot_acp;
                     rez_unt = fac_cad_solid_tot_acp_unt;
                     
                  elif self.scenario.waste_type == 'Non-Hazardous Aqueous Waste' and self.scenario.waste_medium == 'Volume Liquid' \
                  and fac_nhaq_liquid_tot_acp is not None:
                     rez_amt = fac_nhaq_liquid_tot_acp;
                     rez_unt = fac_nhaq_liquid_tot_acp_unt;
                     
                  else:
                     rez_cap = self.facilityCapacity(
                        facility_subtypeids = facility_subtypeids
                     );
                     rez_amt = rez_cap['facility_qty_acpt'];
                     rez_unt = rez_cap['facility_qty_acpt_unit'];
                  
               (rez_amt,rez_unt) = source.util.converter(
                   in_unit     = rez_unt
                  ,in_value    = rez_amt
                  ,unit_system = unit_system
               );
               
               count_facility_qty_accepted += 1;
               
               if rez_cap['facility_qty_acpt'] is not None:
                  total_facility_qty_accepted += rez_amt
               
            if count_facility_qty_accepted == 0:
               average_fac_amt_accepted = 0;
               percent_fac_of_waste     = 0;
               
            else:
               average_fac_amt_accepted = total_facility_qty_accepted / count_facility_qty_accepted;
               
               if self.scenario is None or self.scenario.waste_amount is None:
                  percent_fac_of_waste = None;
                  
               else:
                  if total_facility_qty_accepted == 0:
                     percent_fac_of_waste = None;
                  else:
                     percent_fac_of_waste = self.scenario.waste_amount / total_facility_qty_accepted;
                  
                     if percent_fac_of_waste > 1:
                        percent_fac_of_waste = 1;

      ret = {}
      ret["total_facility_qty_accepted"] = total_facility_qty_accepted;
      ret["average_fac_amt_accepted"]    = average_fac_amt_accepted;
      ret["percent_fac_of_waste"]        = percent_fac_of_waste;
      ret["maximum_facilities_to_find"]  = self.system_cache.maximum_facilities_to_find;
      
      return SimpleNamespace(**ret);
      
   #...........................................................................
   def get_settings_vintage(self):
   
      project_settings_last_updated_date = self.system_cache.settings_last_updated_date;
      project_settings_last_updated_by   = self.system_cache.settings_last_updated_by;
      
      jd = source.util.load_settings();
      
      if jd is None or 'LastUpdatedDate' not in jd:
         file_settings_last_updated_date = None;       
      else:
         file_settings_last_updated_date = jd["LastUpdatedDate"]; 
      
      if jd is None or 'LastUpdatedBy' not in jd:
         file_settings_last_updated_by = None;       
      else:
         file_settings_last_updated_by = jd["LastUpdatedBy"]; 
         
      return {
          'ProjectUnitSystem'             : self.system_cache.current_unit_system
         ,'ProjectSettingsLastUpdatedDate': project_settings_last_updated_date
         ,'ProjectSettingsLastUpdatedBy'  : project_settings_last_updated_by
         ,'FileSettingsLastUpdatedDate'   : file_settings_last_updated_date
         ,'FileSettingsLastUpdatedBy'     : file_settings_last_updated_by
      }
         
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
         
      if self.system_cache is None or self.system_cache.current_facilityattributesid is None:
         current_facilityattributesid = '';
      else:
         current_facilityattributesid = self.system_cache.current_facilityattributesid;
         
      if self.system_cache is None or self.system_cache.current_road_transporter is None:
         current_road_transporter = '';
      else:
         current_road_transporter = self.system_cache.current_road_transporter;
         
      if self.system_cache is None or self.system_cache.current_rail_transporter is None:
         current_rail_transporter = '';
      else:
         current_rail_transporter = self.system_cache.current_rail_transporter;
         
      wstat = self.facility_amt_accepted_stats(
         unit_system = self.system_cache.current_unit_system
      );
      
      if wstat is None or wstat.average_fac_amt_accepted is None:
         average_fac_amt_accepted = '';
      else:
         average_fac_amt_accepted = str(round(wstat.average_fac_amt_accepted,4));
         
      if wstat is None or wstat.total_facility_qty_accepted is None:
         tfqa = '';
      else:
         tfqa = str(round(wstat.total_facility_qty_accepted,4)); 
         
      if waste_medium is None:
         waste_medium = '';
      
      value = "\"Scenario ID\" \""            + scenarioid   + "\";"                        \
            + "\"Waste Type\" \""             + waste_type   + "\";"                        \
            + "\"Waste Medium\" \""           + waste_medium + "\";"                        \
            + "\"Waste Amount\" \""           + waste_amount + " " + waste_unit + "\";"     \
            + "\"Total Estimated Facility Capacity\" \"" + tfqa + " " + waste_unit + "\";"  \
            + "\"Condition ID\" \""           + conditionid  + "\";"                        \
            + "\"Factor ID\" \""              + factorid     + "\";"                        \
            + "\"Facility Attributes ID\" \"" + current_facilityattributesid + "\";"        \
            + "\"Road Transporter\" \""       + current_road_transporter + "\";"            \
            + "\"Rail Transporter\" \""       + current_rail_transporter + "\";";

      return (columns,value);
      
   #...........................................................................
   def fetchTransportationAttributesIDs(self,
       mode         = None
      ,waste_type   = None
      ,waste_medium = None
   ):

      output = [];
      
      if self.transporters_layer.dataSource is not None:
         with arcpy.da.SearchCursor(
             in_table     = self.transporters_layer.dataSource
            ,field_names  = (
                'transporterattrid'
               ,'mode'
               ,'wastetype'
               ,'wastemedium'
             )
            ,where_clause = None
         ) as rows:

            for row in rows:
               row_transporterattrid = row[0];
               row_mode              = row[1];
               row_waste_type        = row[2];
               row_waste_medium      = row[3];
               
               if  ( mode         is None or mode         == row_mode       )  \
               and ( waste_type   is None or waste_type   == row_waste_type )  \
               and ( waste_medium is None or waste_medium == row_waste_medium )\
               and row_transporterattrid not in output:
                  output.append(row_transporterattrid);

      return output;

   #...........................................................................
   def upsertTransportationAttributes(self,
       transporterattrid
      ,mode
      ,waste_type
      ,waste_medium
      ,containercapacity
      ,containercapacityunit
      ,containercountpertransporter  
      ,transportersavailable
      ,transportersprocessedperday
      ,unit_system = None
   ):
   
      flds = [
          'transporterattrid'
         ,'mode'
         ,'wastetype'
         ,'wastemedium'
         ,'containercapacity'
         ,'containercapacityunit'
         ,'containercountpertransporter'
         ,'transportersavailable'
         ,'transportersprocessedperday'
      ];
         
      existing_ids = self.fetchTransportationAttributesIDs(
          mode         = mode
         ,waste_type   = waste_type
         ,waste_medium = waste_medium
      );
      
      if unit_system is None:
         unit_system = self.system_cache.current_unit_system;

      if transporterattrid in existing_ids:
      
         whr = "transporterattrid = " + source.util.sql_quote(transporterattrid) + " and " \
             + "mode              = " + source.util.sql_quote(mode)              + " and " \
             + "wastetype         = " + source.util.sql_quote(waste_type)        + " and " \
             + "wastemedium       = " + source.util.sql_quote(waste_medium)      + " ";

         with arcpy.da.UpdateCursor(
             in_table     = self.transporters_layer.dataSource
            ,field_names  = flds
            ,where_clause = whr
         ) as cursor:
         
            (container_cap,container_cap_unit) = source.util.converter(
                in_unit     = containercapacityunit
               ,in_value    = containercapacity
               ,unit_system = unit_system
            );
               
            for row in cursor:
               row[4] = container_cap;             
               row[5] = container_cap_unit;
               row[6] = containercountpertransporter;          
               row[7] = transportersavailable;
               row[8] = transportersprocessedperday;
       
               cursor.updateRow(row);

      else:

         with arcpy.da.InsertCursor(
             in_table    = self.transporters_layer.dataSource
            ,field_names = flds
         ) as cursor:
         
            (container_cap,container_cap_unit) = source.util.converter(
                in_unit     = containercapacityunit
               ,in_value    = containercapacity
               ,unit_system = unit_system
            );
            
            cursor.insertRow(
               (
                   transporterattrid
                  ,mode
                  ,waste_type
                  ,waste_medium
                  ,container_cap
                  ,container_cap_unit
                  ,containercountpertransporter
                  ,transportersavailable
                  ,transportersprocessedperday
               )
            );
   