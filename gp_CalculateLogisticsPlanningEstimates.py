import arcpy,os,sys;
import json;

import util;
import obj_AllHazardsWasteLogisticsTool;
import obj_FacilityCalc;

###############################################################################
import importlib
importlib.reload(util);
importlib.reload(obj_AllHazardsWasteLogisticsTool);
importlib.reload(obj_FacilityCalc);

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
   scenarioid               = parameters[2].valueAsText;
   conditionid              = parameters[3].valueAsText;
   factorid                 = parameters[4].valueAsText;

   map_settings             = parameters[5].value;
   
   stashed_scenarioid       = parameters[6].valueAsText;
   stashed_conditionid      = parameters[7].valueAsText;
   stashed_factorid         = parameters[8].valueAsText;

   #########################################################################
   # Step 30
   # Initialize the haz toc object
   #########################################################################
   haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

   if scenarioid != stashed_scenarioid:
      haz.system_cache.set_current_scenarioid(scenarioid);
      
   if conditionid != stashed_conditionid:
      haz.system_cache.set_current_conditionid(conditionid);
      
   if factorid != stashed_factorid:
      haz.system_cache.set_current_factorid(factorid);
   
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

   arcpy.AddMessage("Conditions and Factors loaded.");

   #########################################################################
   # Step 40
   # Delete any preexisting records under the scenarioid
   #########################################################################
   with arcpy.da.UpdateCursor(
       in_table    = haz.scenario_results.dataSource
      ,field_names = ["scenarioid"]
   ) as cursor:
      for row in cursor:
         if row[0] == scenarioid:
            cursor.deleteRow();

   arcpy.AddMessage("Clearing any preexisting data.");

   #########################################################################
   # Step 60
   # Check for results
   #########################################################################
   if haz.network.routes.recordCount() == 0:
      arcpy.AddMessage("Warning, no results returned from network solve.");
      return;

   #########################################################################
   # Step 70
   # Load the Results featureclass
   #########################################################################
   cursor_in = arcpy.da.SearchCursor(
       in_table     = haz.network.routes.dataSource
      ,field_names  = (
          'facility_identifier'
         ,'FacilityRank'
         ,haz.system_cache.network_distance_fieldname
         ,haz.system_cache.network_time_fieldname
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
         ,'SHAPE@'
       )
      ,sql_clause=(None,'ORDER BY FacilityRank ASC')
   );

   cursor_out = arcpy.da.InsertCursor(
       in_table    = haz.scenario_results.dataSource
      ,field_names = (
          'scenarioid'
         ,'conditionid'
         ,'factorid'
         ,'facility_identifier'
         ,'facility_rank'
         ,'total_distance'
         ,'distance_unit'
         ,'total_truck_travel_time'
         ,'time_unit'
         ,'average_speed'
         ,'speed_unit'
         ,'facility_name'
         ,'facility_address'
         ,'facility_city'
         ,'facility_state'
         ,'facility_zip'
         ,'facility_telephone'
         ,'facility_waste_mgt'
         ,'facility_capacity_trucks_perday'
         ,'facility_qty_accepted'
         ,'facility_qty_accepted_unit'
         ,'SHAPE@'
         ,'allocated_amount'
         ,'allocated_amount_unit'
         ,'number_of_shipments'
         ,'cplm_cost_usd'
         ,'fixed_cost_usd_per_shipment'
         ,'fixed_cost_usd_per_hour'
         ,'tolls_usd'
         ,'misc_trans_cost_usd'
         ,'trans_cost_usd'
         ,'staging_site_cost_usd'
         ,'disposal_cost_usd'
         ,'labor_cost_usd'
         ,'vehicle_decon_cost_usd'
         ,'cost_multiplier_usd'
         ,'cost_usd'
         ,'trucks_time_to_comp_days'
         ,'dest_time_to_comp_days'
         ,'time_days'
       )
   );

   running_total = haz.scenario.waste_amount;

   for row in cursor_in:

      if running_total > 0:

         if waste_medium == 'Volume Liquid':
            facility_qty_accepted      = row[14];
            facility_qty_accepted_unit = row[15];

         elif waste_medium == 'Volume Solid':
            facility_qty_accepted      = row[12];
            facility_qty_accepted_unit = row[13];
            
         else:
            raise arcpy.ExecuteError("Error");

         if  facility_qty_accepted is not None                                 \
         and facility_qty_accepted > 0:
         
            obj = obj_FacilityCalc.FaciltyCalc(
                haz                             = haz
               ,scenarioid                      = scenarioid
               ,conditionid                     = conditionid
               ,factorid                        = factorid
               ,facility_identifier             = row[0]
               ,facility_rank                   = row[1]
               ,total_distance                  = row[2]
               ,total_distance_unit             = haz.system_cache.network_distance_unit
               ,total_traveltime                = row[3]
               ,total_traveltime_unit           = haz.system_cache.network_time_unit
               ,facility_name                   = row[4]
               ,facility_address                = row[5]
               ,facility_city                   = row[6]
               ,facility_state                  = row[7]
               ,facility_zip                    = row[8]
               ,facility_telephone              = row[9]
               ,facility_waste_mgt              = row[10]
               ,facility_capacity_trucks_perday = row[11]
               ,facility_qty_accepted           = facility_qty_accepted
               ,facility_qty_accepted_unit      = facility_qty_accepted_unit
               ,shape                           = row[16]
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
            ,'Unallocated' #facility_identifier
            ,None #facility_rank
            ,None #total_distance
            ,None #distance_unit
            ,None #total_trucktraveltime
            ,None #time_unit
            ,None #average_speed
            ,None #speed_unit
            ,None #facility_name
            ,None #facility_address
            ,None #facility_city
            ,None #facility_state
            ,None #facility_zip
            ,None #facility_telephone
            ,None #facility_waste_mgt
            ,None #facility_capacity_trucks_perday
            ,None #facility_qty_accepted
            ,None #facility_qty_accepted_unit
            ,None #shape
            ,running_total #allocated_amount
            ,waste_unit #allocated_amount_unit
            ,None #number_of_shipments
            ,None #cplm_cost_usd
            ,None #fixed_cost_usd_per_shipment
            ,None #fixed_cost_usd_per_hour
            ,None #tolls_usd
            ,None #misc_trans_cost_usd
            ,None #trans_cost_usd
            ,None #staging_site_cost_usd
            ,None #disposal_cost_usd
            ,None #labor_cost_usd
            ,None #vehicle_decon_cost_usd
            ,None #cost_multiplier_usd
            ,None #cost_usd
            ,None #trucks_time_to_comp_days
            ,None #dest_time_to_comp_days
            ,None #time_days
         )
      )

   arcpy.AddMessage("Scenario persisted into results feature class under " + scenarioid + ".");

   del cursor_out;
   del cursor_in;

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
      aprx = arcpy.mp.ArcGISProject("CURRENT");
      map = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];
      lyt = aprx.listLayouts("AllHazardsWasteLogisticsLayout")[0];
      mf = lyt.listElements("mapframe_element","AllHazardsWasteLogisticsMapFrame")[0]

      map_image = arcpy.env.scratchFolder + os.sep + 'z' + scenarioid + '.png';

      util.recalculate_extent(haz.scenario_results.dataSource);

      if map_settings == 'Zoom to Routes':
         lyr = map.listLayers("ScenarioResults")[0];
         ext = mf.getLayerExtent(lyr,False,True);
         ext2 = util.buffer_extent(ext,0.025);
         mf.camera.setExtent(ext2);

      elif map_settings == 'Zoom to Support Area':
         lyr = map.listLayers("SupportArea")[0];
         ext = mf.getLayerExtent(lyr,False,True);
         ext2 = util.buffer_extent(ext,0.025);
         mf.camera.setExtent(ext2);

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

   #########################################################################
   # Step 100
   #
   #########################################################################
   del haz;

   return;
