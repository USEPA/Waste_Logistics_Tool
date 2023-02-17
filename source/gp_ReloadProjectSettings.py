import arcpy,os,sys;
import source.util;
import source.obj_Condition;
import source.obj_Modes;
import source.obj_Transporters;
import source.obj_CPLMUnitRates;
import source.obj_FixedTransCost;
import source.obj_LaborCosts;
import source.obj_DisposalFees;
import source.obj_SystemCache;

###############################################################################
import importlib
importlib.reload(source.util);
importlib.reload(source.obj_Condition);
importlib.reload(source.obj_Modes);
importlib.reload(source.obj_Transporters);
importlib.reload(source.obj_CPLMUnitRates);
importlib.reload(source.obj_FixedTransCost);
importlib.reload(source.obj_LaborCosts);
importlib.reload(source.obj_DisposalFees);
importlib.reload(source.obj_SystemCache);

###############################################################################
def execute(self,parameters,messages):

   #...........................................................................
   haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

   #...........................................................................
   arcpy.TruncateTable_management(haz.aprx.defaultGeodatabase + os.sep + "Conditions");
   arcpy.TruncateTable_management(haz.aprx.defaultGeodatabase + os.sep + "Modes");
   arcpy.TruncateTable_management(haz.aprx.defaultGeodatabase + os.sep + "Transporters");
   arcpy.TruncateTable_management(haz.aprx.defaultGeodatabase + os.sep + "CPLMUnitRates");
   arcpy.TruncateTable_management(haz.aprx.defaultGeodatabase + os.sep + "FixedTransCost");
   arcpy.TruncateTable_management(haz.aprx.defaultGeodatabase + os.sep + "LaborCosts");
   arcpy.TruncateTable_management(haz.aprx.defaultGeodatabase + os.sep + "DisposalFees");
   arcpy.TruncateTable_management(haz.aprx.defaultGeodatabase + os.sep + "SystemCache");
   source.util.dzlog("project settings tables truncated.");
   
   #...........................................................................
   return load_settings(
       haz.aprx
      ,haz.system_cache.current_unit_system
      ,haz.system_cache.network_dataset
      ,haz.system_cache.nd_travel_mode
      ,haz.system_cache.nd_impedance_field
      ,haz.system_cache.nd_overall_distance_field
      ,haz.system_cache.nd_overall_distance_unt
      ,haz.system_cache.nd_overall_time_field
      ,haz.system_cache.nd_overall_time_unt
      ,haz.system_cache.nd_road_distance_field
      ,haz.system_cache.nd_road_distance_unt
      ,haz.system_cache.nd_road_time_field
      ,haz.system_cache.nd_road_time_unt
      ,haz.system_cache.nd_rail_distance_field
      ,haz.system_cache.nd_rail_distance_unt
      ,haz.system_cache.nd_rail_time_field
      ,haz.system_cache.nd_rail_time_unt
      ,haz.system_cache.nd_station_count_field
      ,haz.system_cache.isAGO
      ,haz.system_cache.maximum_facilities_to_find
   );
      
###############################################################################
def load_settings(
    aprx
   ,unit_system
   ,net_source_str
   ,travel_mode
   ,impedance_field
   ,overall_distance_field
   ,overall_distance_unit
   ,overall_time_field
   ,overall_time_unit
   ,road_distance_field
   ,road_distance_unit
   ,road_time_field
   ,road_time_unit
   ,rail_distance_field
   ,rail_distance_unit
   ,rail_time_field
   ,rail_time_unit
   ,station_count_field
   ,isAGO
   ,maximum_facilities_to_find
):

   #########################################################################
   fc = os.path.join(source.util.g_pn,"data","IWasteFacilities.json");
   json_d = source.util.load_settings();
   source.util.dzlog("settings file read successfully.");

   #########################################################################
   if 'Conditions' in json_d:
      with arcpy.da.InsertCursor(
          aprx.defaultGeodatabase + os.sep + "Conditions"
         ,source.obj_Condition.Condition.fields
      ) as cursor:
         for row in json_d["Conditions"]:
            cursor.insertRow(
               (
                   row["ConditionID"]
                   
                  ,row["RoadTollsPerRoadShipment"]
                  
                  ,row["MiscCostPerRoadShipment"]
                  ,row["MiscCostPerRailShipment"]
                  
                  ,row["RoadTransporterDeconCostPerRoadShipment"]
                  ,row["RailTransporterDeconCostPerRailShipment"]
                                    
                  ,row["StagingSiteCost"]
                  
                  ,row["RoadDrivingHoursPerDay"]
                  ,row["RailDrivingHoursPerDay"]
                  
                  ,row["TotalCostMultiplier"]
               )
            );

      arcpy.AddMessage("  Conditions table loaded.");
      
   if 'TransporterAttributes' in json_d:
      transporters = json_d['TransporterAttributes'];
      
      with arcpy.da.InsertCursor(
          aprx.defaultGeodatabase + os.sep + "Transporters"
         ,source.obj_Transporters.Transporters.fields
      ) as transporters_cursor:
      
         for item in transporters:
            transporter_name = item['Name'];
            transporter_mode = item['Mode'];
            transporter_desc = None;
            if 'Description' in item:
               transporter_desc = item['Description'];
               
            for item2 in item['Transporters']:
            
               wastetype                    = item2['WasteType'];
               wastemedium                  = item2['WasteMedium'];
               containercapacity            = item2['ContainerCapacity'];
               containercapacityunit        = item2['ContainerCapacityUnit'];
               containercountpertransporter = item2['ContainerCountPerTransporter'];
               transportersavailable        = item2['TransportersAvailable'];
               transportersprocessedperday  = item2['TransportersProcessedPerDay'];
      
               (container_capacity,container_capacity_unit) = source.util.converter(
                   in_unit     = containercapacityunit
                  ,in_value    = containercapacity
                  ,unit_system = unit_system
               );
               
               transporters_cursor.insertRow(
                  (
                      transporter_name
                     ,transporter_mode
                     ,wastetype
                     ,wastemedium
                     ,container_capacity
                     ,container_capacity_unit
                     ,containercountpertransporter
                     ,transportersavailable
                     ,transportersprocessedperday
                  )
               ); 
  
   if 'Factors' in json_d:
      arcpy.AddMessage("Factors found.");
      
      edit = arcpy.da.Editor(aprx.defaultGeodatabase);
      edit.startEditing(False,False);
      
      factors = json_d["Factors"];
      
      for item in factors:
         factorid = item["FactorID"];
         
         if 'RoutingModes' in item:
            arcpy.AddMessage("Routing Modes found.");
            
            routing_modes = item["RoutingModes"];
            
            modes_cursor = arcpy.da.InsertCursor(
                aprx.defaultGeodatabase + os.sep + "Modes"
               ,source.obj_Modes.Modes.fields
            );
            
            cplm_unit_rates_cursor = arcpy.da.InsertCursor(
                aprx.defaultGeodatabase + os.sep + "CPLMUnitRates"
               ,source.obj_CPLMUnitRates.CPLMUnitRates.fields
            );
            
            fixed_trans_costs_cursor = arcpy.da.InsertCursor(
                aprx.defaultGeodatabase + os.sep + "FixedTransCost"
               ,source.obj_FixedTransCost.FixedTransCost.fields
            );
            
            labor_costs_cursor = arcpy.da.InsertCursor(
                aprx.defaultGeodatabase + os.sep + "LaborCosts"
               ,source.obj_LaborCosts.LaborCosts.fields
            );
            
            for item2 in routing_modes:
               rm_description = None;
               if 'Description' in item2:
                  rm_description = item2["Description"];
               
               modes_cursor.insertRow(
                  (
                      factorid
                     ,item2["Mode"]
                     ,item2["Name"]
                     ,rm_description
                  )
               );                    
                  
               if 'CPLMUnitRates' in item2:
                  arcpy.AddMessage("CPLM Unit Rates found.");
                  
                  cplm_unit_rates = item2["CPLMUnitRates"];
                  
                  for item3 in cplm_unit_rates:
                     
                     (lower_value,cplm_unit) = source.util.converter(
                         in_unit     = item3["CPLMUnit"]
                        ,in_value    = item3["CPLMDist_Lower"]
                        ,unit_system = unit_system
                     );

                     (upper_value,unit) = source.util.converter(
                         in_unit     = item3["CPLMUnit"]
                        ,in_value    = item3["CPLMDist_Upper"]
                        ,unit_system = unit_system
                     );

                     (unit_rate,unit) = source.util.converter(
                         in_unit     = item3["Unit"]
                        ,in_value    = item3["CPLMUnit_Rate"]
                        ,unit_system = unit_system
                     );

                     cplm_unit_rates_cursor.insertRow(
                        (
                            factorid
                           ,item2["Mode"]
                           ,lower_value
                           ,upper_value
                           ,cplm_unit
                           ,item3["WasteType"]
                           ,item3["WasteMedium"]
                           ,unit_rate
                           ,unit
                        )
                     );
                     
               if 'FixedTransCost' in item2:
                  arcpy.AddMessage("Fixed Transportation Costs found.");
                  
                  fixed_trans_costs = item2["FixedTransCost"];
                  
                  for item3 in fixed_trans_costs:
                     
                     fixed_trans_costs_cursor.insertRow(
                        (
                            factorid
                           ,item2["Mode"]
                           ,item3["FixedCost_Type"]
                           ,item3["WasteType"]
                           ,item3["WasteMedium"]
                           ,item3["FixedCost_Value"]
                           ,item3["Unit"]
                        )
                     );
                     
               if 'LaborCosts' in item2:
                  arcpy.AddMessage("Labor Costs found.");
                  
                  laborcosts = item2["LaborCosts"];
                  
                  labor_costs_cursor.insertRow(
                     (
                         factorid
                        ,item2["Mode"]
                        ,laborcosts["LaborCostCategory"]
                        ,laborcosts["LaborCost"]
                        ,laborcosts["Unit"]
                     )
                  );
                  
            del modes_cursor;
            del transporters_cursor;
            del cplm_unit_rates_cursor;
            del fixed_trans_costs_cursor;
            del labor_costs_cursor;
         
      edit.stopEditing(True);
      
   if 'FacilityAttributesBySubtypeID' in json_d:
      arcpy.AddMessage("Facility Attributes found.");
      
      edit = arcpy.da.Editor(aprx.defaultGeodatabase);
      edit.startEditing(False,False);
      
      facility_attributes = json_d["FacilityAttributesBySubtypeID"];
      
      facility_attr_cursor = arcpy.da.InsertCursor(
          aprx.defaultGeodatabase + os.sep + "FacilityCapacities"
         ,source.obj_FacilityCapacities.FacilityCapacities.fields
      );
      
      disposal_fees_cursor = arcpy.da.InsertCursor(
          aprx.defaultGeodatabase + os.sep + "DisposalFees"
         ,source.obj_DisposalFees.DisposalFees.fields
      );
      
      for item in facility_attributes:
      
         facility_attributesid = item['FacilityAttributesID'];
         facility_attributes   = item['FacilityAttributes'];
         
         for item2 in facility_attributes:

            facility_subtypeid  = item2["FacilitySubtypeID"];
            total_accepted_days = item2["TotalAcceptedDays"]
            
            for item3 in item2["DailyThroughput"]:
            
               (volume_per_day,volume_per_day_unit) = source.util.converter(
                   in_unit     = item3["VolumePerDayUnit"]
                  ,in_value    = item3["VolumePerDay"]
                  ,unit_system = unit_system
               );

               facility_attr_cursor.insertRow(
                  (
                      facility_attributesid
                     ,facility_subtypeid
                     ,item3["WasteType"]
                     ,item3["WasteMedium"]
                     ,volume_per_day
                     ,volume_per_day_unit
                     ,total_accepted_days
                  )
               );  
            
            for item3 in item2["DisposalFees"]:
            
               (cost_per_one,cost_per_one_unit) = source.util.converter(
                   in_unit     = item3["CostPerOneUnit"]
                  ,in_value    = item3["CostPerOne"]
                  ,unit_system = unit_system
               );

               disposal_fees_cursor.insertRow(
                  (
                      facility_attributesid
                     ,facility_subtypeid
                     ,item3["WasteType"]
                     ,item3["WasteMedium"]
                     ,cost_per_one
                     ,cost_per_one_unit
                  )
               );
               
      del facility_attr_cursor;
      del disposal_fees_cursor;
                  
      edit.stopEditing(True);
      
   arcpy.AddMessage("  Settings tables loaded.");
      
   if 'LastUpdatedDate' in json_d:
      last_updated_date = json_d["LastUpdatedDate"];
   else:
      last_updated_date = None;
      
   if 'LastUpdatedBy' in json_d:
      last_updated_by = json_d["LastUpdatedBy"];
   else:
      last_updated_by = None;      

   if 'SystemCache' in json_d:
      with arcpy.da.InsertCursor(
          aprx.defaultGeodatabase + os.sep + "SystemCache"
         ,source.obj_SystemCache.SystemCache.fields
      ) as cursor:

         cursor.insertRow(
            (
                unit_system
               ,None   # current scenarioid
               ,None   # current conditionid
               ,None   # current factorid
               ,None   # current_facilityattributesid
               ,None   # current_road_transporter
               ,None   # current_rail_transporter
               ,net_source_str
               ,travel_mode
               ,impedance_field
               ,overall_distance_field
               ,overall_distance_unit
               ,overall_time_field
               ,overall_time_unit
               ,road_distance_field
               ,road_distance_unit
               ,road_time_field
               ,road_time_unit
               ,rail_distance_field
               ,rail_distance_unit
               ,rail_time_field
               ,rail_time_unit
               ,station_count_field
               ,isAGO
               ,maximum_facilities_to_find
               ,last_updated_date
               ,last_updated_by
            )
         );
      
   arcpy.AddMessage("  SystemCache table loaded.");
   
   return None;
   