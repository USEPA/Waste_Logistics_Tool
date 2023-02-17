import arcpy,os,sys;
import json;

import source.util;
import source.obj_AllHazardsWasteLogisticsTool;
import source.obj_FacilityCalc;
import source.obj_QuerySet;

###############################################################################
import importlib
importlib.reload(source.util);
importlib.reload(source.obj_AllHazardsWasteLogisticsTool);
importlib.reload(source.obj_FacilityCalc);
importlib.reload(source.obj_QuerySet);

def execute(self, parameters, messages):

   #########################################################################
   # Step 10
   # Abend if edits are pending
   #########################################################################
   if source.util.sniff_editing_state():
      raise arcpy.ExecuteError("Error.  Pending edits must be saved or cleared before proceeding.");
      
   #########################################################################
   # Step 20
   # Read the parameters
   #########################################################################
   scenarioid                   = parameters[2].valueAsText;
   conditionid                  = parameters[3].valueAsText;
   factorid                     = parameters[4].valueAsText;
   facilityattributesid         = parameters[5].valueAsText;
   map_settings                 = parameters[6].value;
   
   stashed_scenarioid           = parameters[7].valueAsText;
   stashed_conditionid          = parameters[8].valueAsText;
   stashed_factorid             = parameters[9].valueAsText;
   stashed_facilityattributesid = parameters[10].valueAsText;
   stashed_road_transporter     = parameters[11].valueAsText;
   stashed_rail_transporter     = parameters[12].valueAsText;
   
   #########################################################################
   # Step 30
   # Initialize the haz toc object
   #########################################################################
   haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

   if scenarioid != stashed_scenarioid:
      haz.system_cache.set_current_scenarioid(scenarioid);
      
   if conditionid != stashed_conditionid:
      haz.system_cache.set_current_conditionid(conditionid);
      
   if factorid != stashed_factorid:
      haz.system_cache.set_current_factorid(factorid);
      
   if facilityattributesid != stashed_facilityattributesid:
      haz.system_cache.set_current_facilityattributesid(facilityattributesid);
   
   haz.scenario.loadScenarioID(scenarioid);
   haz.conditions.loadConditionID(conditionid);
   haz.factors.loadFactorID(factorid);

   (
       scenarioid
      ,unit_system
      ,waste_type
      ,waste_medium
      ,waste_amount
      ,waste_unit
   ) = haz.current_scenario();
   
   arcpy.AddMessage(".   Conditions and Factors loaded.");
   
   #########################################################################
   # Step 40
   # Bump the scenario to make sure all ids up-to-date
   #########################################################################
   if haz.system_cache.current_scenarioid is not None:
      haz.scenario.updateLinkageIDs(
          scenarioid                  = haz.system_cache.current_scenarioid
         ,conditionid                 = haz.system_cache.current_conditionid
         ,factorid                    = haz.system_cache.current_factorid
         ,facilityattributesid        = haz.system_cache.current_facilityattributesid
         ,road_transporter_attributes = haz.system_cache.current_road_transporter
         ,rail_transporter_attributes = haz.system_cache.current_rail_transporter
      );

   #########################################################################
   # Step 50
   # Delete any preexisting records under the scenarioid
   #########################################################################
   with arcpy.da.UpdateCursor(
       in_table    = haz.scenario_results.dataSource
      ,field_names = ["scenarioid"]
   ) as cursor:
      for row in cursor:
         if row[0] == scenarioid:
            cursor.deleteRow();

   arcpy.AddMessage(".   Clearing any preexisting data.");

   #########################################################################
   # Step 60
   # Check for results
   #########################################################################
   if haz.network.routes.recordCount() == 0:
      arcpy.AddMessage("  Warning, no results returned from network solve.");
      return;

   #########################################################################
   # Step 70
   # Load the Results featureclass
   #########################################################################
   qryset = source.obj_QuerySet.QuerySet({
       "facility_identifier"             : 'facility_identifier'
      ,"facility_rank"                   : 'FacilityRank'
      ,"network_impedance_field"         : haz.system_cache.total_nd_impedance_field()
      ,"overall_distance_field"          : haz.system_cache.total_nd_overall_distance_field()
      ,"overall_time_field"              : haz.system_cache.total_nd_overall_time_field()
      ,"road_distance_field"             : haz.system_cache.total_nd_road_distance_field()
      ,"road_time_field"                 : haz.system_cache.total_nd_road_time_field()
      ,"rail_distance_field"             : haz.system_cache.total_nd_rail_distance_field()
      ,"rail_time_field"                 : haz.system_cache.total_nd_rail_time_field()
      ,"station_count_field"             : haz.system_cache.total_nd_station_count_field()
      
      ,"facility_typeid"                 : 'facility_typeid'
      ,"facility_subtypeids"             : 'facility_subtypeids'
      ,"facility_name"                   : 'facility_name'
      ,"facility_address"                : 'facility_address'
      ,"facility_city"                   : 'facility_city'
      ,"facility_state"                  : 'facility_state'
      ,"facility_zip"                    : 'facility_zip'
      ,"facility_telephone"              : 'facility_telephone'
      ,"facility_waste_mgt"              : 'facility_waste_mgt'
      
      ,'facility_accepts_no_waste'       : 'facility_accepts_no_waste'
      ,'fac_radc_solid_dly_cap'          : 'fac_radc_solid_dly_cap'
      ,'fac_radc_solid_dly_cap_unt'      : 'fac_radc_solid_dly_cap_unt'
      ,'fac_radc_liquid_dly_cap'         : 'fac_radc_liquid_dly_cap'
      ,'fac_radc_liquid_dly_cap_unt'     : 'fac_radc_liquid_dly_cap_unt'
      ,'fac_radr_solid_dly_cap'          : 'fac_radr_solid_dly_cap'
      ,'fac_radr_solid_dly_cap_unt'      : 'fac_radr_solid_dly_cap_unt'
      ,'fac_radr_liquid_dly_cap'         : 'fac_radr_liquid_dly_cap'
      ,'fac_radr_liquid_dly_cap_unt'     : 'fac_radr_liquid_dly_cap_unt'
      ,'fac_larw_solid_dly_cap'          : 'fac_larw_solid_dly_cap'
      ,'fac_larw_solid_dly_cap_unt'      : 'fac_larw_solid_dly_cap_unt'
      ,'fac_haz_solid_dly_cap'           : 'fac_haz_solid_dly_cap'
      ,'fac_haz_solid_dly_cap_unt'       : 'fac_haz_solid_dly_cap_unt'
      ,'fac_haz_liquid_dly_cap'          : 'fac_haz_liquid_dly_cap'
      ,'fac_haz_liquid_dly_cap_unt'      : 'fac_haz_liquid_dly_cap_unt'
      ,'fac_msw_solid_dly_cap'           : 'fac_msw_solid_dly_cap'
      ,'fac_msw_solid_dly_cap_unt'       : 'fac_msw_solid_dly_cap_unt'
      ,'fac_cad_solid_dly_cap'           : 'fac_cad_solid_dly_cap'
      ,'fac_cad_solid_dly_cap_unt'       : 'fac_cad_solid_dly_cap_unt'
      ,'fac_nhaq_liquid_dly_cap'         : 'fac_nhaq_liquid_dly_cap'
      ,'fac_nhaq_liquid_dly_cap_unt'     : 'fac_nhaq_liquid_dly_cap_unt'
      ,'fac_radc_solid_tot_acp'          : 'fac_radc_solid_tot_acp'
      ,'fac_radc_solid_tot_acp_unt'      : 'fac_radc_solid_tot_acp_unt'
      ,'fac_radc_liquid_tot_acp'         : 'fac_radc_liquid_tot_acp'
      ,'fac_radc_liquid_tot_acp_unt'     : 'fac_radc_liquid_tot_acp_unt'
      ,'fac_radr_solid_tot_acp'          : 'fac_radr_solid_tot_acp'
      ,'fac_radr_solid_tot_acp_unt'      : 'fac_radr_solid_tot_acp_unt'
      ,'fac_radr_liquid_tot_acp'         : 'fac_radr_liquid_tot_acp'
      ,'fac_radr_liquid_tot_acp_unt'     : 'fac_radr_liquid_tot_acp_unt'
      ,'fac_larw_solid_tot_acp'          : 'fac_larw_solid_tot_acp'
      ,'fac_larw_solid_tot_acp_unt'      : 'fac_larw_solid_tot_acp_unt'
      ,'fac_haz_solid_tot_acp'           : 'fac_haz_solid_tot_acp'
      ,'fac_haz_solid_tot_acp_unt'       : 'fac_haz_solid_tot_acp_unt'
      ,'fac_haz_liquid_tot_acp'          : 'fac_haz_liquid_tot_acp'
      ,'fac_haz_liquid_tot_acp_unt'      : 'fac_haz_liquid_tot_acp_unt'
      ,'fac_msw_solid_tot_acp'           : 'fac_msw_solid_tot_acp'
      ,'fac_msw_solid_tot_acp_unt'       : 'fac_msw_solid_tot_acp_unt'
      ,'fac_cad_solid_tot_acp'           : 'fac_cad_solid_tot_acp'
      ,'fac_cad_solid_tot_acp_unt'       : 'fac_cad_solid_tot_acp_unt'
      ,'fac_nhaq_liquid_tot_acp'         : 'fac_nhaq_liquid_tot_acp'
      ,'fac_nhaq_liquid_tot_acp_unt'     : 'fac_nhaq_liquid_tot_acp_unt'
      ,'fac_radc_solid_dis_fee'          : 'fac_radc_solid_dis_fee'
      ,'fac_radc_solid_dis_fee_unt'      : 'fac_radc_solid_dis_fee_unt'
      ,'fac_radc_liquid_dis_fee'         : 'fac_radc_liquid_dis_fee'
      ,'fac_radc_liquid_dis_fee_unt'     : 'fac_radc_liquid_dis_fee_unt'
      ,'fac_radr_solid_dis_fee'          : 'fac_radr_solid_dis_fee'
      ,'fac_radr_solid_dis_fee_unt'      : 'fac_radr_solid_dis_fee_unt'
      ,'fac_radr_liquid_dis_fee'         : 'fac_radr_liquid_dis_fee'
      ,'fac_radr_liquid_dis_fee_unt'     : 'fac_radr_liquid_dis_fee_unt'
      ,'fac_larw_solid_dis_fee'          : 'fac_larw_solid_dis_fee'
      ,'fac_larw_solid_dis_fee_unt'      : 'fac_larw_solid_dis_fee_unt'
      ,'fac_haz_solid_dis_fee'           : 'fac_haz_solid_dis_fee'
      ,'fac_haz_solid_dis_fee_unt'       : 'fac_haz_solid_dis_fee_unt'
      ,'fac_haz_liquid_dis_fee'          : 'fac_haz_liquid_dis_fee'
      ,'fac_haz_liquid_dis_fee_unt'      : 'fac_haz_liquid_dis_fee_unt'
      ,'fac_msw_solid_dis_fee'           : 'fac_msw_solid_dis_fee'
      ,'fac_msw_solid_dis_fee_unt'       : 'fac_msw_solid_dis_fee_unt'
      ,'fac_cad_solid_dis_fee'           : 'fac_cad_solid_dis_fee'
      ,'fac_cad_solid_dis_fee_unt'       : 'fac_cad_solid_dis_fee_unt'
      ,'fac_nhaq_liquid_dis_fee'         : 'fac_nhaq_liquid_dis_fee'
      ,'fac_nhaq_liquid_dis_fee_unt'     : 'fac_nhaq_liquid_dis_fee_unt'
      
      ,"shape"                           : 'SHAPE@'
   });
   
   with arcpy.da.SearchCursor(
       in_table     = haz.network.routes.dataSource
      ,field_names  = qryset.flds
      ,sql_clause=(None,'ORDER BY FacilityRank ASC')
   ) as cursor_in:

      with arcpy.da.InsertCursor(
          in_table    = haz.scenario_results.dataSource
         ,field_names = (
             'scenarioid'
            ,'conditionid'
            ,'factorid'
            ,'facilityattributesid'
            ,'road_transporter_attributes'
            ,'rail_transporter_attributes'
            ,'facility_identifier'
            ,'facility_rank'
            
            ,'total_overall_distance'
            ,'total_overall_distance_unt'
            ,'total_overall_time'
            ,'total_overall_time_unt'
            
            ,'total_road_distance'
            ,'total_road_distance_unt'
            ,'total_road_time'
            ,'total_road_time_unt'
            
            ,'total_rail_distance'
            ,'total_rail_distance_unt'
            ,'total_rail_time'
            ,'total_rail_time_unt'
            
            ,'total_station_count'
            
            ,'average_overall_speed'
            ,'average_road_speed'
            ,'average_rail_speed'
            ,'speed_unit'
            
            ,'facility_typeid'
            ,'facility_subtypeids'
            ,'facility_name'
            ,'facility_address'
            ,'facility_city'
            ,'facility_state'
            ,'facility_zip'
            ,'facility_telephone'
            ,'facility_waste_mgt'
            
            ,'facility_dly_cap'
            ,'facility_dly_cap_unt'
            
            ,'facility_qty_accepted'
            ,'facility_qty_accepted_unt'
            
            ,'SHAPE@'
            
            ,'allocated_amount'
            ,'allocated_amount_unt'
            
            ,'number_of_road_shipments'
            ,'number_of_rail_shipments'
            
            ,'road_cplm_cost_usd'
            ,'rail_cplm_cost_usd'
            
            ,'road_fixed_cost_usd_per_contnr'
            ,'rail_fixed_cost_usd_per_contnr'
            
            ,'road_fixed_cost_usd_per_hour'
            ,'rail_fixed_cost_usd_per_hour'
            
            ,'road_fixed_cost_usd_by_volume'
            ,'rail_fixed_cost_usd_by_volume'
            
            ,'road_tolls_usd_per_shipment'
            
            ,'road_misc_trans_cost_usd'
            ,'rail_misc_trans_cost_usd'
            
            ,'road_trans_cost_usd'
            ,'rail_trans_cost_usd'
            
            ,'staging_site_cost_usd'
            
            ,'disposal_cost_usd'
            
            ,'road_labor_cost_usd'
            ,'rail_labor_cost_usd'
            
            ,'road_transp_decon_cost_usd'
            ,'rail_transp_decon_cost_usd'
            
            ,'cost_multiplier_usd'
            
            ,'total_cost_usd'
            
            ,'road_transp_time_to_comp_days'
            ,'rail_transp_time_to_comp_days'
            ,'total_transp_time_to_comp_days'
            
            ,'road_dest_time_to_comp_days'
            ,'rail_dest_time_to_comp_days'
            ,'total_dest_time_to_comp_days'
            
            ,'time_days'
          )
      ) as cursor_out:

         running_total = haz.scenario.waste_amount;
         
         arcpy.AddMessage(".   Seeking to route " + str(haz.scenario.waste_amount) + " " + haz.scenario.waste_unit + ".");

         for row in cursor_in:
         
            facility_accepts_no_waste = qryset.idx_clean_boo(row,'facility_accepts_no_waste');
            if facility_accepts_no_waste is None:
               facility_accepts_no_waste = False;

            if running_total > 0 and not facility_accepts_no_waste:
            
               facility_waste_mgt = qryset.idx_clean_string(row,'facility_waste_mgt');
               
               facility_dly_cap_src      = None;
               facility_dly_cap_err      = None;
               facility_qty_accepted_src = None;
               facility_qty_accepted_err = None;
               facility_disposal_fee_src = None;
               facility_disposal_fee_err = None;
               
               facility_subtypeids = qryset.idx_clean_string(row,'facility_subtypeids');
               if facility_subtypeids is not None:
                  cap_rez = haz.facilityCapacity(facility_subtypeids);
                  dis_rez = haz.disposalFees(facility_subtypeids);
               else:
                  # Set values to None but assume if no overrides, this will turn bad
                  cap_rez = {};
                  cap_rez['facility_dly_cap']       = None;
                  cap_rez['facility_dly_cap_unit']  = None;
                  cap_rez['facility_qty_acpt']      = None;
                  cap_rez['facility_qty_acpt_unit'] = None;
                  
                  dis_rez = {};
                  dis_rez['costperone']             = None;
                  dis_rez['costperoneunit']         = None;
                  
                  facility_dly_cap_err      = "facility has no subtype, using individual values";
                  facility_qty_accepted_err = "facility has no subtype, using individual values";
                  facility_disposal_fee_err = "facility has no subtype, using individual values";
               
               boo_facility_accepts_no_waste = qryset.idx_clean_boo(row,'facility_accepts_no_waste');
               if boo_facility_accepts_no_waste:
                  facility_dly_cap          = 0;
                  facility_dly_cap_unt      = 'm3';
                  facility_dly_cap_src      = "accepts no waste";
                  facility_dly_cap_err      = "facility is marked to accept no waste";
                  
                  facility_qty_accepted     = 0;
                  facility_qty_accepted_unt = 'm3';
                  facility_qty_accepted_src = "accepts no waste";
                  facility_qty_accepted_err = "facility is marked to accept no waste";
                  
                  facility_disposal_fee     = 0;
                  facility_disposal_fee_unt = 'm3';
                  facility_disposal_fee_src = "accepts no waste";
                  facility_disposal_fee_err = "facility is marked to accept no waste";
               
               else:
               
                  fac_radc_solid_dly_cap      = qryset.idx_clean_double(row,'fac_radc_solid_dly_cap');
                  fac_radc_solid_dly_cap_unt  = qryset.idx_clean_string(row,'fac_radc_solid_dly_cap_unt');
                  fac_radc_liquid_dly_cap     = qryset.idx_clean_double(row,'fac_radc_liquid_dly_cap');
                  fac_radc_liquid_dly_cap_unt = qryset.idx_clean_string(row,'fac_radc_liquid_dly_cap_unt');
                  fac_radr_solid_dly_cap      = qryset.idx_clean_double(row,'fac_radr_solid_dly_cap');
                  fac_radr_solid_dly_cap_unt  = qryset.idx_clean_string(row,'fac_radr_solid_dly_cap_unt');
                  fac_radr_liquid_dly_cap     = qryset.idx_clean_double(row,'fac_radr_liquid_dly_cap');
                  fac_radr_liquid_dly_cap_unt = qryset.idx_clean_string(row,'fac_radr_liquid_dly_cap_unt');
                  fac_larw_solid_dly_cap      = qryset.idx_clean_double(row,'fac_larw_solid_dly_cap');
                  fac_larw_solid_dly_cap_unt  = qryset.idx_clean_string(row,'fac_larw_solid_dly_cap_unt');
                  fac_haz_solid_dly_cap       = qryset.idx_clean_double(row,'fac_haz_solid_dly_cap');
                  fac_haz_solid_dly_cap_unt   = qryset.idx_clean_string(row,'fac_haz_solid_dly_cap_unt');
                  fac_haz_liquid_dly_cap      = qryset.idx_clean_double(row,'fac_haz_liquid_dly_cap');
                  fac_haz_liquid_dly_cap_unt  = qryset.idx_clean_string(row,'fac_haz_liquid_dly_cap_unt');
                  fac_msw_solid_dly_cap       = qryset.idx_clean_double(row,'fac_msw_solid_dly_cap');
                  fac_msw_solid_dly_cap_unt   = qryset.idx_clean_string(row,'fac_msw_solid_dly_cap_unt');
                  fac_cad_solid_dly_cap       = qryset.idx_clean_double(row,'fac_cad_solid_dly_cap');
                  fac_cad_solid_dly_cap_unt   = qryset.idx_clean_string(row,'fac_cad_solid_dly_cap_unt');
                  fac_nhaq_liquid_dly_cap     = qryset.idx_clean_double(row,'fac_nhaq_liquid_dly_cap');
                  fac_nhaq_liquid_dly_cap_unt = qryset.idx_clean_string(row,'fac_nhaq_liquid_dly_cap_unt');
                  fac_radc_solid_tot_acp      = qryset.idx_clean_double(row,'fac_radc_solid_tot_acp');
                  fac_radc_solid_tot_acp_unt  = qryset.idx_clean_string(row,'fac_radc_solid_tot_acp_unt');
                  fac_radc_liquid_tot_acp     = qryset.idx_clean_double(row,'fac_radc_liquid_tot_acp');
                  fac_radc_liquid_tot_acp_unt = qryset.idx_clean_string(row,'fac_radc_liquid_tot_acp_unt');
                  fac_radr_solid_tot_acp      = qryset.idx_clean_double(row,'fac_radr_solid_tot_acp');
                  fac_radr_solid_tot_acp_unt  = qryset.idx_clean_string(row,'fac_radr_solid_tot_acp_unt');
                  fac_radr_liquid_tot_acp     = qryset.idx_clean_double(row,'fac_radr_liquid_tot_acp');
                  fac_radr_liquid_tot_acp_unt = qryset.idx_clean_string(row,'fac_radr_liquid_tot_acp_unt');
                  fac_larw_solid_tot_acp      = qryset.idx_clean_double(row,'fac_larw_solid_tot_acp');
                  fac_larw_solid_tot_acp_unt  = qryset.idx_clean_string(row,'fac_larw_solid_tot_acp_unt');
                  fac_haz_solid_tot_acp       = qryset.idx_clean_double(row,'fac_haz_solid_tot_acp');
                  fac_haz_solid_tot_acp_unt   = qryset.idx_clean_string(row,'fac_haz_solid_tot_acp_unt');
                  fac_haz_liquid_tot_acp      = qryset.idx_clean_double(row,'fac_haz_liquid_tot_acp');
                  fac_haz_liquid_tot_acp_unt  = qryset.idx_clean_string(row,'fac_haz_liquid_tot_acp_unt');
                  fac_msw_solid_tot_acp       = qryset.idx_clean_double(row,'fac_msw_solid_tot_acp');
                  fac_msw_solid_tot_acp_unt   = qryset.idx_clean_string(row,'fac_msw_solid_tot_acp_unt');
                  fac_cad_solid_tot_acp       = qryset.idx_clean_double(row,'fac_cad_solid_tot_acp');
                  fac_cad_solid_tot_acp_unt   = qryset.idx_clean_string(row,'fac_cad_solid_tot_acp_unt');
                  fac_nhaq_liquid_tot_acp     = qryset.idx_clean_double(row,'fac_nhaq_liquid_tot_acp');
                  fac_nhaq_liquid_tot_acp_unt = qryset.idx_clean_string(row,'fac_nhaq_liquid_tot_acp_unt');
                  fac_radc_solid_dis_fee      = qryset.idx_clean_double(row,'fac_radc_solid_dis_fee');
                  fac_radc_solid_dis_fee_unt  = qryset.idx_clean_string(row,'fac_radc_solid_dis_fee_unt');
                  fac_radc_liquid_dis_fee     = qryset.idx_clean_double(row,'fac_radc_liquid_dis_fee');
                  fac_radc_liquid_dis_fee_unt = qryset.idx_clean_string(row,'fac_radc_liquid_dis_fee_unt');
                  fac_radr_solid_dis_fee      = qryset.idx_clean_double(row,'fac_radr_solid_dis_fee');
                  fac_radr_solid_dis_fee_unt  = qryset.idx_clean_string(row,'fac_radr_solid_dis_fee_unt');
                  fac_radr_liquid_dis_fee     = qryset.idx_clean_double(row,'fac_radr_liquid_dis_fee');
                  fac_radr_liquid_dis_fee_unt = qryset.idx_clean_string(row,'fac_radr_liquid_dis_fee_unt');
                  fac_larw_solid_dis_fee      = qryset.idx_clean_double(row,'fac_larw_solid_dis_fee');
                  fac_larw_solid_dis_fee_unt  = qryset.idx_clean_string(row,'fac_larw_solid_dis_fee_unt');
                  fac_haz_solid_dis_fee       = qryset.idx_clean_double(row,'fac_haz_solid_dis_fee');
                  fac_haz_solid_dis_fee_unt   = qryset.idx_clean_string(row,'fac_haz_solid_dis_fee_unt');
                  fac_haz_liquid_dis_fee      = qryset.idx_clean_double(row,'fac_haz_liquid_dis_fee');
                  fac_haz_liquid_dis_fee_unt  = qryset.idx_clean_string(row,'fac_haz_liquid_dis_fee_unt');
                  fac_msw_solid_dis_fee       = qryset.idx_clean_double(row,'fac_msw_solid_dis_fee');
                  fac_msw_solid_dis_fee_unt   = qryset.idx_clean_string(row,'fac_msw_solid_dis_fee_unt');
                  fac_cad_solid_dis_fee       = qryset.idx_clean_double(row,'fac_cad_solid_dis_fee');
                  fac_cad_solid_dis_fee_unt   = qryset.idx_clean_string(row,'fac_cad_solid_dis_fee_unt');
                  fac_nhaq_liquid_dis_fee     = qryset.idx_clean_double(row,'fac_nhaq_liquid_dis_fee');
                  fac_nhaq_liquid_dis_fee_unt = qryset.idx_clean_string(row,'fac_nhaq_liquid_dis_fee_unt');
                  
                  if  waste_type == 'Radioactive: Contact-Handled' and waste_medium == 'Volume Solid':
                     
                     if fac_radc_solid_dly_cap is not None:
                        facility_dly_cap          = fac_radc_solid_dly_cap;
                        facility_dly_cap_unt      = fac_radc_solid_dly_cap_unt;
                        facility_dly_cap_src      = "facility fac_radc_solid_dly_cap";
                     else:
                        if facility_subtypeids is not None:
                           facility_dly_cap       = cap_rez['facility_dly_cap'];
                           facility_dly_cap_unt   = cap_rez['facility_dly_cap_unit'];
                           facility_dly_cap_src   = "subtypes " + facility_subtypeids;
                        else:
                           facility_dly_cap       = 0;
                           facility_dly_cap_unt   = 'zeroed';
                           facility_dly_cap_src   = 'defaulting to zero';
                           facility_dly_cap_err   = 'unable to determine proper facility daily cap!';
                     
                     if fac_radc_solid_tot_acp is not None:
                        facility_qty_accepted     = fac_radc_solid_tot_acp;
                        facility_qty_accepted_unt = fac_radc_solid_tot_acp_unt;
                        facility_qty_accepted_src = "facility fac_radc_solid_tot_acp";
                     else:
                        if facility_subtypeids is not None:
                           facility_qty_accepted     = cap_rez['facility_qty_acpt'];
                           facility_qty_accepted_unt = cap_rez['facility_qty_acpt_unit'];
                           facility_qty_accepted_src = "subtypes " + facility_subtypeids;
                        else:
                           facility_qty_accepted       = 0;
                           facility_qty_accepted_unt   = 'zeroed';
                           facility_qty_accepted_src   = 'defaulting to zero';
                           facility_qty_accepted_err   = 'unable to determine proper facility quantity accepted!';
                        
                     if fac_radc_solid_dis_fee is not None:
                        facility_disposal_fee     = fac_radc_solid_dis_fee;
                        facility_disposal_fee_unt = fac_radc_solid_dis_fee_unt;
                        facility_disposal_fee_src = 'facility fac_radc_solid_dis_fee';
                     else:
                        if facility_subtypeids is not None:
                           facility_disposal_fee     = dis_rez['costperone'];
                           facility_disposal_fee_unt = dis_rez['costperoneunit'];
                           facility_disposal_fee_src = "subtypes " + facility_subtypeids;
                        elif facility_waste_mgt == 'Staging':
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'facility is staging location';
                        else:
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'defaulting to zero';
                           facility_disposal_fee_err   = 'unable to determine proper facility disposal fees!';
                        
                  elif waste_type == 'Radioactive: Contact-Handled' and waste_medium == 'Volume Liquid':
                  
                     if fac_radc_liquid_dly_cap is not None:
                        facility_dly_cap          = fac_radc_liquid_dly_cap;
                        facility_dly_cap_unt      = fac_radc_liquid_dly_cap_unt;
                        facility_dly_cap_src      = "facility fac_radc_liquid_dly_cap";
                     else:
                        if facility_subtypeids is not None:
                           facility_dly_cap          = cap_rez['facility_dly_cap'];
                           facility_dly_cap_unt      = cap_rez['facility_dly_cap_unit'];
                           facility_dly_cap_src      = "subtypes " + facility_subtypeids;
                        else:
                           facility_dly_cap       = 0;
                           facility_dly_cap_unt   = 'zeroed';
                           facility_dly_cap_src   = 'defaulting to zero';
                           facility_dly_cap_err   = 'unable to determine proper facility daily cap!';
                     
                     if fac_radc_liquid_tot_acp is not None:
                        facility_qty_accepted     = fac_radc_liquid_tot_acp;
                        facility_qty_accepted_unt = fac_radc_liquid_tot_acp_unt;
                        facility_qty_accepted_src = "facility fac_radc_liquid_tot_acp";
                     else:
                        if facility_subtypeids is not None:
                           facility_qty_accepted     = cap_rez['facility_qty_acpt'];
                           facility_qty_accepted_unt = cap_rez['facility_qty_acpt_unit'];
                           facility_qty_accepted_src = "subtypes " + facility_subtypeids;
                        else:
                           facility_qty_accepted       = 0;
                           facility_qty_accepted_unt   = 'zeroed';
                           facility_qty_accepted_src   = 'defaulting to zero';
                           facility_qty_accepted_err   = 'unable to determine proper facility quantity accepted!';
                        
                     if fac_radc_liquid_dis_fee is not None:
                        facility_disposal_fee     = fac_radc_liquid_dis_fee;
                        facility_disposal_fee_unt = fac_radc_liquid_dis_fee_unt;
                        facility_disposal_fee_src = 'facility fac_radc_liquid_dis_fee';
                     else:
                        if facility_subtypeids is not None:
                           facility_disposal_fee     = dis_rez['costperone'];
                           facility_disposal_fee_unt = dis_rez['costperoneunit'];
                           facility_disposal_fee_src = "subtypes " + facility_subtypeids;
                        elif facility_waste_mgt == 'Staging':
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'facility is staging location';
                        else:
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'defaulting to zero';
                           facility_disposal_fee_err   = 'unable to determine proper facility disposal fees!';
                        
                  elif  waste_type == 'Radioactive: Remote-Handled' and waste_medium == 'Volume Solid':
                     
                     if fac_radr_solid_dly_cap is not None:
                        facility_dly_cap          = fac_radr_solid_dly_cap;
                        facility_dly_cap_unt      = fac_radr_solid_dly_cap_unt;
                        facility_dly_cap_src      = "facility fac_radr_solid_dly_cap";
                     else:
                        if facility_subtypeids is not None:
                           facility_dly_cap          = cap_rez['facility_dly_cap'];
                           facility_dly_cap_unt      = cap_rez['facility_dly_cap_unit'];
                           facility_dly_cap_src      = "subtypes " + facility_subtypeids;
                        else:
                           facility_dly_cap       = 0;
                           facility_dly_cap_unt   = 'zeroed';
                           facility_dly_cap_src   = 'defaulting to zero';
                           facility_dly_cap_err   = 'unable to determine proper facility daily cap!';
                     
                     if fac_radr_solid_tot_acp is not None:
                        facility_qty_accepted     = fac_radr_solid_tot_acp;
                        facility_qty_accepted_unt = fac_radr_solid_tot_acp_unt;
                        facility_qty_accepted_src = "facility fac_radr_solid_tot_acp";
                     else:
                        if facility_subtypeids is not None:
                           facility_qty_accepted     = cap_rez['facility_qty_acpt'];
                           facility_qty_accepted_unt = cap_rez['facility_qty_acpt_unit'];
                           facility_qty_accepted_src = "subtypes " + facility_subtypeids;
                        else:
                           facility_qty_accepted       = 0;
                           facility_qty_accepted_unt   = 'zeroed';
                           facility_qty_accepted_src   = 'defaulting to zero';
                           facility_qty_accepted_err   = 'unable to determine proper facility quantity accepted!';
                        
                     if fac_radr_solid_dis_fee is not None:
                        facility_disposal_fee     = fac_radr_solid_dis_fee;
                        facility_disposal_fee_unt = fac_radr_solid_dis_fee_unt;
                        facility_disposal_fee_src = 'facility fac_radr_solid_dis_fee';
                     else:
                        if facility_subtypeids is not None:
                           facility_disposal_fee     = dis_rez['costperone'];
                           facility_disposal_fee_unt = dis_rez['costperoneunit'];
                           facility_disposal_fee_src = "subtypes " + facility_subtypeids;
                        elif facility_waste_mgt == 'Staging':
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'facility is staging location';
                        else:
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'defaulting to zero';
                           facility_disposal_fee_err   = 'unable to determine proper facility disposal fees!';
                        
                  elif waste_type == 'Radioactive: Remote-Handled' and waste_medium == 'Volume Liquid':
                  
                     if fac_radr_liquid_dly_cap is not None:
                        facility_dly_cap          = fac_radr_liquid_dly_cap;
                        facility_dly_cap_unt      = fac_radr_liquid_dly_cap_unt;
                        facility_dly_cap_src      = "facility fac_radr_liquid_dly_cap";
                     else:
                        if facility_subtypeids is not None:
                           facility_dly_cap          = cap_rez['facility_dly_cap'];
                           facility_dly_cap_unt      = cap_rez['facility_dly_cap_unit'];
                           facility_dly_cap_src      = "subtypes " + facility_subtypeids;
                        else:
                           facility_dly_cap       = 0;
                           facility_dly_cap_unt   = 'zeroed';
                           facility_dly_cap_src   = 'defaulting to zero';
                           facility_dly_cap_err   = 'unable to determine proper facility daily cap!';
                     
                     if fac_radr_liquid_tot_acp is not None:
                        facility_qty_accepted     = fac_radr_liquid_tot_acp;
                        facility_qty_accepted_unt = fac_radr_liquid_tot_acp_unt;
                        facility_qty_accepted_src = "facility fac_radr_liquid_tot_acp";
                     else:
                        if facility_subtypeids is not None:
                           facility_qty_accepted     = cap_rez['facility_qty_acpt'];
                           facility_qty_accepted_unt = cap_rez['facility_qty_acpt_unit'];
                           facility_qty_accepted_src = "subtypes " + facility_subtypeids;
                        else:
                           facility_qty_accepted       = 0;
                           facility_qty_accepted_unt   = 'zeroed';
                           facility_qty_accepted_src   = 'defaulting to zero';
                           facility_qty_accepted_err   = 'unable to determine proper facility quantity accepted!';
                        
                     if fac_radr_liquid_dis_fee is not None:
                        facility_disposal_fee     = fac_radr_liquid_dis_fee;
                        facility_disposal_fee_unt = fac_radr_liquid_dis_fee_unt;
                        facility_disposal_fee_src = 'facility fac_radr_liquid_dis_fee';
                     else:
                        if facility_subtypeids is not None:
                           facility_disposal_fee     = dis_rez['costperone'];
                           facility_disposal_fee_unt = dis_rez['costperoneunit'];
                           facility_disposal_fee_src = "subtypes " + facility_subtypeids;
                        elif facility_waste_mgt == 'Staging':
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'facility is staging location';
                        else:
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'defaulting to zero';
                           facility_disposal_fee_err   = 'unable to determine proper facility disposal fees!';
                        
                  elif  waste_type == 'Low-Activity Radioactive Waste' and waste_medium == 'Volume Solid':
                     
                     if fac_larw_solid_dly_cap is not None:
                        facility_dly_cap          = fac_larw_solid_dly_cap;
                        facility_dly_cap_unt      = fac_larw_solid_dly_cap_unt;
                        facility_dly_cap_src      = "facility fac_larw_solid_dly_cap";
                     else:
                        if facility_subtypeids is not None:
                           facility_dly_cap          = cap_rez['facility_dly_cap'];
                           facility_dly_cap_unt      = cap_rez['facility_dly_cap_unit'];
                           facility_dly_cap_src      = "subtypes " + facility_subtypeids;
                        else:
                           facility_dly_cap       = 0;
                           facility_dly_cap_unt   = 'zeroed';
                           facility_dly_cap_src   = 'defaulting to zero';
                           facility_dly_cap_err   = 'unable to determine proper facility daily cap!';
                     
                     if fac_larw_solid_tot_acp is not None:
                        facility_qty_accepted     = fac_larw_solid_tot_acp;
                        facility_qty_accepted_unt = fac_larw_solid_tot_acp_unt;
                        facility_qty_accepted_src = "facility fac_larw_solid_tot_acp";
                     else:
                        if facility_subtypeids is not None:
                           facility_qty_accepted     = cap_rez['facility_qty_acpt'];
                           facility_qty_accepted_unt = cap_rez['facility_qty_acpt_unit'];
                           facility_qty_accepted_src = "subtypes " + facility_subtypeids;
                        else:
                           facility_qty_accepted       = 0;
                           facility_qty_accepted_unt   = 'zeroed';
                           facility_qty_accepted_src   = 'defaulting to zero';
                           facility_qty_accepted_err   = 'unable to determine proper facility quantity accepted!';
                        
                     if fac_larw_solid_dis_fee is not None:
                        facility_disposal_fee     = fac_larw_solid_dis_fee;
                        facility_disposal_fee_unt = fac_larw_solid_dis_fee_unt;
                        facility_disposal_fee_src = 'facility fac_larw_solid_dis_fee';
                     else:
                        if facility_subtypeids is not None:
                           facility_disposal_fee     = dis_rez['costperone'];
                           facility_disposal_fee_unt = dis_rez['costperoneunit'];
                           facility_disposal_fee_src = "subtypes " + facility_subtypeids;
                        elif facility_waste_mgt == 'Staging':
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'facility is staging location';
                        else:
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'defaulting to zero';
                           facility_disposal_fee_err   = 'unable to determine proper facility disposal fees!';
                        
                  elif  waste_type == 'Hazardous' and waste_medium == 'Volume Solid':
                     
                     if fac_haz_solid_dly_cap is not None:
                        facility_dly_cap          = fac_haz_solid_dly_cap;
                        facility_dly_cap_unt      = fac_haz_solid_dly_cap_unt;
                        facility_dly_cap_src      = "facility fac_haz_solid_dly_cap";
                     else:
                        if facility_subtypeids is not None:
                           facility_dly_cap          = cap_rez['facility_dly_cap'];
                           facility_dly_cap_unt      = cap_rez['facility_dly_cap_unit'];
                           facility_dly_cap_src      = "subtypes " + facility_subtypeids;
                        else:
                           facility_dly_cap       = 0;
                           facility_dly_cap_unt   = 'zeroed';
                           facility_dly_cap_src   = 'defaulting to zero';
                           facility_dly_cap_err   = 'unable to determine proper facility daily cap!';
                     
                     if fac_haz_solid_tot_acp is not None:
                        facility_qty_accepted     = fac_haz_solid_tot_acp;
                        facility_qty_accepted_unt = fac_haz_solid_tot_acp_unt;
                        facility_qty_accepted_src = "facility fac_haz_solid_tot_acp";
                     else:
                        if facility_subtypeids is not None:
                           facility_qty_accepted     = cap_rez['facility_qty_acpt'];
                           facility_qty_accepted_unt = cap_rez['facility_qty_acpt_unit'];
                           facility_qty_accepted_src = "subtypes " + facility_subtypeids;
                        else:
                           facility_qty_accepted       = 0;
                           facility_qty_accepted_unt   = 'zeroed';
                           facility_qty_accepted_src   = 'defaulting to zero';
                           facility_qty_accepted_err   = 'unable to determine proper facility quantity accepted!';
                        
                     if fac_haz_solid_dis_fee is not None:
                        facility_disposal_fee     = fac_haz_solid_dis_fee;
                        facility_disposal_fee_unt = fac_haz_solid_dis_fee_unt;
                        facility_disposal_fee_src = 'facility fac_haz_solid_dis_fee';
                     else:
                        if facility_subtypeids is not None:
                           facility_disposal_fee     = dis_rez['costperone'];
                           facility_disposal_fee_unt = dis_rez['costperoneunit'];
                           facility_disposal_fee_src = "subtypes " + facility_subtypeids;
                        elif facility_waste_mgt == 'Staging':
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'facility is staging location';
                        else:
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'defaulting to zero';
                           facility_disposal_fee_err   = 'unable to determine proper facility disposal fees!';
                        
                  elif waste_type == 'Hazardous' and waste_medium == 'Volume Liquid':
                  
                     if fac_haz_liquid_dly_cap is not None:
                        facility_dly_cap          = fac_haz_liquid_dly_cap;
                        facility_dly_cap_unt      = fac_haz_liquid_dly_cap_unt;
                        facility_dly_cap_src      = "facility fac_haz_liquid_dly_cap";
                     else:
                        if facility_subtypeids is not None:
                           facility_dly_cap          = cap_rez['facility_dly_cap'];
                           facility_dly_cap_unt      = cap_rez['facility_dly_cap_unit'];
                           facility_dly_cap_src      = "subtypes " + facility_subtypeids;
                        else:
                           facility_dly_cap       = 0;
                           facility_dly_cap_unt   = 'zeroed';
                           facility_dly_cap_src   = 'defaulting to zero';
                           facility_dly_cap_err   = 'unable to determine proper facility daily cap!';
                     
                     if fac_haz_liquid_tot_acp is not None:
                        facility_qty_accepted     = fac_haz_liquid_tot_acp;
                        facility_qty_accepted_unt = fac_haz_liquid_tot_acp_unt;
                        facility_qty_accepted_src = "facility fac_haz_liquid_tot_acp";
                     else:
                        if facility_subtypeids is not None:
                           facility_qty_accepted     = cap_rez['facility_qty_acpt'];
                           facility_qty_accepted_unt = cap_rez['facility_qty_acpt_unit'];
                           facility_qty_accepted_src = "subtypes " + facility_subtypeids;
                        else:
                           facility_qty_accepted       = 0;
                           facility_qty_accepted_unt   = 'zeroed';
                           facility_qty_accepted_src   = 'defaulting to zero';
                           facility_qty_accepted_err   = 'unable to determine proper facility quantity accepted!';
                        
                     if fac_haz_liquid_dis_fee is not None:
                        facility_disposal_fee     = fac_haz_liquid_dis_fee;
                        facility_disposal_fee_unt = fac_haz_liquid_dis_fee_unt;
                        facility_disposal_fee_src = 'facility fac_haz_liquid_dis_fee';
                     else:
                        if facility_subtypeids is not None:
                           facility_disposal_fee     = dis_rez['costperone'];
                           facility_disposal_fee_unt = dis_rez['costperoneunit'];
                           facility_disposal_fee_src = "subtypes " + facility_subtypeids;
                        elif facility_waste_mgt == 'Staging':
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'facility is staging location';
                        else:
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'defaulting to zero';
                           facility_disposal_fee_err   = 'unable to determine proper facility disposal fees!';
                        
                  elif  waste_type == 'Municipal Solid Waste (MSW)' and waste_medium == 'Volume Solid':
                     
                     if fac_msw_solid_dly_cap is not None:
                        facility_dly_cap          = fac_msw_solid_dly_cap;
                        facility_dly_cap_unt      = fac_msw_solid_dly_cap_unt;
                        facility_dly_cap_src      = "facility fac_msw_solid_dly_cap";
                     else:
                        if facility_subtypeids is not None:
                           facility_dly_cap          = cap_rez['facility_dly_cap'];
                           facility_dly_cap_unt      = cap_rez['facility_dly_cap_unit'];
                           facility_dly_cap_src      = "subtypes " + facility_subtypeids;
                        else:
                           facility_dly_cap       = 0;
                           facility_dly_cap_unt   = 'zeroed';
                           facility_dly_cap_src   = 'defaulting to zero';
                           facility_dly_cap_err   = 'unable to determine proper facility daily cap!';
                     
                     if fac_msw_solid_tot_acp is not None:
                        facility_qty_accepted     = fac_msw_solid_tot_acp;
                        facility_qty_accepted_unt = fac_msw_solid_tot_acp_unt;
                        facility_qty_accepted_src = "facility fac_msw_solid_tot_acp";
                     else:
                        if facility_subtypeids is not None:
                           facility_qty_accepted     = cap_rez['facility_qty_acpt'];
                           facility_qty_accepted_unt = cap_rez['facility_qty_acpt_unit'];
                           facility_qty_accepted_src = "subtypes " + facility_subtypeids;
                        else:
                           facility_qty_accepted       = 0;
                           facility_qty_accepted_unt   = 'zeroed';
                           facility_qty_accepted_src   = 'defaulting to zero';
                           facility_qty_accepted_err   = 'unable to determine proper facility quantity accepted!';
                        
                     if fac_msw_solid_dis_fee is not None:
                        facility_disposal_fee     = fac_msw_solid_dis_fee;
                        facility_disposal_fee_unt = fac_msw_solid_dis_fee_unt;
                        facility_disposal_fee_src = 'facility fac_msw_solid_dis_fee';
                     else:
                        if facility_subtypeids is not None:
                           facility_disposal_fee     = dis_rez['costperone'];
                           facility_disposal_fee_unt = dis_rez['costperoneunit'];
                           facility_disposal_fee_src = "subtypes " + facility_subtypeids;
                        elif facility_waste_mgt == 'Staging':
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'facility is staging location';
                        else:
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'defaulting to zero';
                           facility_disposal_fee_err   = 'unable to determine proper facility disposal fees!';
                           
                  elif  waste_type == 'Construction and Demolition' and waste_medium == 'Volume Solid':
                     
                     if fac_cad_solid_dly_cap is not None:
                        facility_dly_cap          = fac_cad_solid_dly_cap;
                        facility_dly_cap_unt      = fac_cad_solid_dly_cap_unt;
                        facility_dly_cap_src      = "facility fac_cad_solid_dly_cap";
                     else:
                        if facility_subtypeids is not None:
                           facility_dly_cap          = cap_rez['facility_dly_cap'];
                           facility_dly_cap_unt      = cap_rez['facility_dly_cap_unit'];
                           facility_dly_cap_src      = "subtypes " + facility_subtypeids;
                        else:
                           facility_dly_cap       = 0;
                           facility_dly_cap_unt   = 'zeroed';
                           facility_dly_cap_src   = 'defaulting to zero';
                           facility_dly_cap_err   = 'unable to determine proper facility daily cap!';
                     
                     if fac_cad_solid_tot_acp is not None:
                        facility_qty_accepted     = fac_cad_solid_tot_acp;
                        facility_qty_accepted_unt = fac_cad_solid_tot_acp_unt;
                        facility_qty_accepted_src = "facility fac_cad_solid_tot_acp";
                     else:
                        if facility_subtypeids is not None:
                           facility_qty_accepted     = cap_rez['facility_qty_acpt'];
                           facility_qty_accepted_unt = cap_rez['facility_qty_acpt_unit'];
                           facility_qty_accepted_src = "subtypes " + facility_subtypeids;
                        else:
                           facility_qty_accepted       = 0;
                           facility_qty_accepted_unt   = 'zeroed';
                           facility_qty_accepted_src   = 'defaulting to zero';
                           facility_qty_accepted_err   = 'unable to determine proper facility quantity accepted!';
                        
                     if fac_cad_solid_dis_fee is not None:
                        facility_disposal_fee     = fac_cad_solid_dis_fee;
                        facility_disposal_fee_unt = fac_cad_solid_dis_fee_unt;
                        facility_disposal_fee_src = 'facility fac_cad_solid_dis_fee';
                     else:
                        if facility_subtypeids is not None:
                           facility_disposal_fee     = dis_rez['costperone'];
                           facility_disposal_fee_unt = dis_rez['costperoneunit'];
                           facility_disposal_fee_src = "subtypes " + facility_subtypeids;
                        elif facility_waste_mgt == 'Staging':
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'facility is staging location';
                        else:
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'defaulting to zero';
                           facility_disposal_fee_err   = 'unable to determine proper facility disposal fees!';
                        
                  elif waste_type == 'Non-Hazardous Aqueous Waste' and waste_medium == 'Volume Liquid':
                  
                     if fac_nhaq_liquid_dly_cap is not None:
                        facility_dly_cap          = fac_nhaq_liquid_dly_cap;
                        facility_dly_cap_unt      = fac_nhaq_liquid_dly_cap_unt;
                        facility_dly_cap_src      = "facility fac_nhaq_liquid_dly_cap";
                     else:
                        if facility_subtypeids is not None:
                           facility_dly_cap          = cap_rez['facility_dly_cap'];
                           facility_dly_cap_unt      = cap_rez['facility_dly_cap_unit'];
                           facility_dly_cap_src      = "subtypes " + facility_subtypeids;
                        else:
                           facility_dly_cap       = 0;
                           facility_dly_cap_unt   = 'zeroed';
                           facility_dly_cap_src   = 'defaulting to zero';
                           facility_dly_cap_err   = 'unable to determine proper facility daily cap!';
                     
                     if fac_nhaq_liquid_tot_acp is not None:
                        facility_qty_accepted     = fac_nhaq_liquid_tot_acp;
                        facility_qty_accepted_unt = fac_nhaq_liquid_tot_acp_unt;
                        facility_qty_accepted_src = "facility fac_nhaq_liquid_tot_acp";
                     else:
                        if facility_subtypeids is not None:
                           facility_qty_accepted     = cap_rez['facility_qty_acpt'];
                           facility_qty_accepted_unt = cap_rez['facility_qty_acpt_unit'];
                           facility_qty_accepted_src = "subtypes " + facility_subtypeids;
                        else:
                           facility_qty_accepted       = 0;
                           facility_qty_accepted_unt   = 'zeroed';
                           facility_qty_accepted_src   = 'defaulting to zero';
                           facility_qty_accepted_err   = 'unable to determine proper facility quantity accepted!';
                        
                     if fac_nhaq_liquid_dis_fee is not None:
                        facility_disposal_fee     = fac_nhaq_liquid_dis_fee;
                        facility_disposal_fee_unt = fac_nhaq_liquid_dis_fee_unt;
                        facility_disposal_fee_src = 'facility fac_nhaq_liquid_dis_fee';
                     else:
                        if facility_subtypeids is not None:
                           facility_disposal_fee     = dis_rez['costperone'];
                           facility_disposal_fee_unt = dis_rez['costperoneunit'];
                           facility_disposal_fee_src = "subtypes " + facility_subtypeids;
                        elif facility_waste_mgt == 'Staging':
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'facility is staging location';
                        else:
                           facility_disposal_fee       = 0;
                           facility_disposal_fee_unt   = 'zeroed';
                           facility_disposal_fee_src   = 'defaulting to zero';
                           facility_disposal_fee_err   = 'unable to determine proper facility disposal fees!';
                        
                  else:
                     raise Exception('err');

               if  facility_qty_accepted is not None \
               and facility_qty_accepted > 0:
               
                  (facility_dly_cap,facility_dly_cap_unt) = source.util.converter(
                      in_unit     = facility_dly_cap_unt
                     ,in_value    = facility_dly_cap
                     ,unit_system = unit_system
                  );
                  
                  (facility_qty_accepted,facility_qty_accepted_unt) = source.util.converter(
                      in_unit     = facility_qty_accepted_unt
                     ,in_value    = facility_qty_accepted
                     ,unit_system = unit_system
                  );
                  
                  (facility_disposal_fee,facility_disposal_fee_unt) = source.util.converter(
                      in_unit     = facility_disposal_fee_unt
                     ,in_value    = facility_disposal_fee
                     ,unit_system = unit_system
                  );
                  
                  obj = source.obj_FacilityCalc.FaciltyCalc(
                      haz                             = haz
                     ,scenarioid                      = scenarioid
                     ,conditionid                     = conditionid
                     ,factorid                        = factorid
                     ,facilityattributesid            = stashed_facilityattributesid
                     ,road_transporter                = stashed_road_transporter
                     ,rail_transporter                = stashed_rail_transporter
                     ,facility_identifier             = qryset.idx(row,'facility_identifier')
                     ,facility_rank                   = qryset.idx(row,'facility_rank')
                     
                     ,total_network_impedance         = qryset.idx(row,'network_impedance_field')
            
                     ,total_overall_distance          = qryset.idx(row,'overall_distance_field')
                     ,total_overall_distance_unt      = haz.system_cache.nd_overall_distance_unt
                     ,total_overall_time              = qryset.idx(row,'overall_time_field')
                     ,total_overall_time_unt          = haz.system_cache.nd_overall_time_unt
                     
                     ,total_road_distance             = qryset.idx(row,'road_distance_field')
                     ,total_road_distance_unt         = haz.system_cache.nd_road_distance_unt
                     ,total_road_time                 = qryset.idx(row,'road_time_field')
                     ,total_road_time_unt             = haz.system_cache.nd_road_time_unt
                     
                     ,total_rail_distance             = qryset.idx(row,'rail_distance_field')
                     ,total_rail_distance_unt         = haz.system_cache.nd_rail_distance_unt
                     ,total_rail_time                 = qryset.idx(row,'rail_time_field')
                     ,total_rail_time_unt             = haz.system_cache.nd_rail_time_unt
                     
                     ,total_station_count             = qryset.idx(row,'station_count_field')
                     
                     ,facility_typeid                 = qryset.idx(row,'facility_typeid')
                     ,facility_subtypeids             = qryset.idx(row,'facility_subtypeids')
                     ,facility_name                   = qryset.idx(row,'facility_name')
                     ,facility_address                = qryset.idx(row,'facility_address')
                     ,facility_city                   = qryset.idx(row,'facility_city')
                     ,facility_state                  = qryset.idx(row,'facility_state')
                     ,facility_zip                    = qryset.idx(row,'facility_zip')
                     ,facility_telephone              = qryset.idx(row,'facility_telephone')
                     ,facility_waste_mgt              = qryset.idx(row,'facility_waste_mgt')
                     
                     ,facility_dly_cap                = facility_dly_cap
                     ,facility_dly_cap_unt            = facility_dly_cap_unt
                     ,facility_dly_cap_src            = facility_dly_cap_src
                     ,facility_dly_cap_err            = facility_dly_cap_err
                     
                     ,facility_qty_accepted           = facility_qty_accepted
                     ,facility_qty_accepted_unt       = facility_qty_accepted_unt
                     ,facility_qty_accepted_src       = facility_qty_accepted_src
                     ,facility_qty_accepted_err       = facility_qty_accepted_err
                     
                     ,facility_disposal_fee           = facility_disposal_fee
                     ,facility_disposal_fee_unt       = facility_disposal_fee_unt
                     ,facility_disposal_fee_src       = facility_disposal_fee_src
                     ,facility_disposal_fee_err       = facility_disposal_fee_err
                     
                     ,shape                           = qryset.idx(row,'shape')
                     ,unit_system                     = unit_system
                     ,waste_type                      = waste_type
                     ,waste_medium                    = waste_medium
                     ,waste_amount                    = waste_amount
                     ,waste_unit                      = waste_unit
                  );

                  obj.calc(running_total);

                  running_total = running_total - obj.facility_qty_accepted;

                  cursor_out.insertRow(
                     obj.output()
                  );

         #########################################################################
         # Step 80
         # Look for overflow
         #########################################################################
         if running_total > 0:
            cursor_out.insertRow(
               (
                   scenarioid
                  ,conditionid
                  ,factorid
                  ,stashed_facilityattributesid
                  ,stashed_road_transporter
                  ,stashed_rail_transporter
                  ,'Unallocated' #facility_identifier
                  ,None #facility_rank
                  
                  ,None #total_overall_distance
                  ,None #total_overall_distance_unt
                  ,None #total_overall_time
                  ,None #total_overall_time_unt
                  
                  ,None #total_road_distance
                  ,None #total_road_distance_unt
                  ,None #total_road_time
                  ,None #total_road_time_unt
                  
                  ,None #total_rail_distance
                  ,None #total_rail_distance_unt
                  ,None #total_rail_time
                  ,None #total_rail_time_unt
                  
                  ,None #total_station_count
                  
                  ,None #average_overall_speed
                  ,None #average_road_speed
                  ,None #average_rail_speed
                  ,None #speed_unit
                  
                  ,None #facility_typeid
                  ,None #facility_subtypeids
                  ,None #facility_name
                  ,None #facility_address
                  ,None #facility_city
                  ,None #facility_state
                  ,None #facility_zip
                  ,None #facility_telephone
                  ,None #facility_waste_mgt
                  
                  ,None #facility_dly_cap
                  ,None #facility_dly_cap_unt
                  
                  ,None #facility_qty_accepted
                  ,None #facility_qty_accepted_unt
                  
                  ,None #shape
                  
                  ,running_total #allocated_amount
                  ,waste_unit    #allocated_amount_unt
                  
                  ,None #number_of_road_shipments
                  ,None #number_of_rail_shipments
                  
                  ,None #road_cplm_cost_usd
                  ,None #rail_cplm_cost_usd
                  
                  ,None #road_fixed_cost_usd_per_contnr
                  ,None #rail_fixed_cost_usd_per_contnr
                  
                  ,None #road_fixed_cost_usd_per_hour
                  ,None #rail_fixed_cost_usd_per_hour
                  
                  ,None #road_fixed_cost_usd_by_volume
                  ,None #rail_fixed_cost_usd_by_volume
                  
                  ,None #road_tolls_per_road_shipment_usd
                  
                  ,None #misc_cost_per_road_shipment_usd
                  ,None #misc_cost_per_rail_shipment_usd
                  
                  ,None #road_trans_cost_usd
                  ,None #rail_trans_cost_usd
                  
                  ,None #staging_site_cost_usd
                  
                  ,None #disposal_cost_usd
                  
                  ,None #road_labor_cost_usd
                  ,None #rail_labor_cost_usd
                  
                  ,None #road_transp_decon_cost_usd
                  ,None #rail_transp_decon_cost_usd
                  
                  ,None #cost_multiplier_usd
                  
                  ,None #total_cost_usd
                  
                  ,None #road_transp_time_to_comp_days
                  ,None #rail_transp_time_to_comp_days
                  ,None #total_transp_time_to_comp_days
                  
                  ,None #road_dest_time_to_comp_days
                  ,None #rail_dest_time_to_comp_days
                  ,None #total_dest_time_to_comp_days
                  
                  ,None #time_days
               )
            )

   arcpy.AddMessage("  Scenario persisted into results feature class under " + scenarioid + ".");

   #########################################################################
   # Step 90
   # Turn off the routes layer to only show the results
   #########################################################################
   haz.network.routes.layer.visible   = False;
   haz.scenario_results.layer.visible = False;
   haz.scenario_results.layer.visible = True;

   if map_settings == 'Disable Map':
      haz.scenario.upsertScenarioID(
          scenarioid   = scenarioid
         ,map_image    = 'Disabled'
         ,conditionid  = conditionid
         ,factorid     = factorid
      );

   else:
      if source.util.g_aprx is not None:
         aprx = source.util.g_aprx;
      else:
         try:
            source.util.g_aprx = arcpy.mp.ArcGISProject(source.util.g_prj);
            aprx = source.util.g_aprx;
         except Exception as e:
            source.util.dzlog_e(sys.exc_info(),'ERROR');
            raise;
      
      map = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];
      lyt = aprx.listLayouts("AllHazardsWasteLogisticsLayout")[0];
      mf = lyt.listElements("MAPFRAME_ELEMENT","AllHazardsWasteLogisticsMapFrame")[0]
      arcpy.AddMessage("Referencing frame containing " + mf.map.name);

      map_image = arcpy.env.scratchFolder + os.sep + 'z' + scenarioid + '.png';

      if map_settings == 'Zoom to Routes':
         #source.util.recalculate_extent(haz.scenario_results.dataSource);
      
         lyr = mf.map.listLayers("ScenarioResults")[0];
         arcpy.AddMessage("Referencing " + lyr.name);
         #ext = mf.getLayerExtent(lyr,False,True);
         ext = arcpy.Describe(haz.scenario_results.dataSource).extent;
         arcpy.AddMessage("Getting Layer Extent " + ext.JSON);
         ext2 = source.util.buffer_extent(ext,0.025);
         arcpy.AddMessage("Buffered Extent " + ext2.JSON);
         mf.camera.setExtent(ext2);
         del lyr;
         del ext;
         del ext2;

      elif map_settings == 'Zoom to Support Area':
         #source.util.recalculate_extent(haz.support_area.dataSource);
         
         lyr = mf.map.listLayers("SupportArea")[0];
         arcpy.AddMessage("Referencing " + lyr.name);
         ext = mf.getLayerExtent(lyr,False,True);
         ext = arcpy.Describe(haz.support_area.dataSource).extent;
         arcpy.AddMessage("Getting Layer Extent " + ext.JSON);
         ext2 = source.util.buffer_extent(ext,0.025);
         arcpy.AddMessage("Buffered Extent " + ext2.JSON);
         mf.camera.setExtent(ext2);
         
         ext3 = mf.camera.getExtent();
         arcpy.AddMessage("Camera Extent " + mf.camera.mode + " " + ext3.JSON);
         del lyr;
         del ext;
         del ext2;
         del ext3;
         
      elif map_settings == 'User Zoom':
         None;

      lyt.exportToPNG(
         out_png = map_image
      );

      haz.scenario.upsertScenarioID(
          scenarioid   = scenarioid
         ,map_image    = map_image
         ,conditionid  = conditionid
         ,factorid     = factorid
      );
      
      del map;
      del lyt;
      del mf;

   #########################################################################
   # Step 100
   #
   #########################################################################
   del haz;

   return;
