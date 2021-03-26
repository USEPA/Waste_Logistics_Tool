import arcpy,os;
import json;

import gp_RemoveWorkEnvironment;
import util;
import obj_Condition;
import obj_ShipmentLoading;
import obj_CPLMUnitRates;
import obj_FixedTransCost;
import obj_LaborCosts;
import obj_DisposalFees;
import obj_SystemCache;

###############################################################################
import importlib
importlib.reload(gp_RemoveWorkEnvironment);
importlib.reload(util);
importlib.reload(obj_Condition);
importlib.reload(obj_ShipmentLoading);
importlib.reload(obj_CPLMUnitRates);
importlib.reload(obj_FixedTransCost);
importlib.reload(obj_LaborCosts);
importlib.reload(obj_DisposalFees);
importlib.reload(obj_SystemCache);

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
   unit_system    = parameters[2].valueAsText;

   net_source     = parameters[3].value;
   net_source_str = parameters[3].valueAsText;
   ago_account    = parameters[4].valueAsText;
   travel_mode    = parameters[5].valueAsText;

   if travel_mode is not None and travel_mode.strip() == "":
      travel_mode = None;

   network_distance_field = parameters[6].valueAsText;
   network_distance_unit  = parameters[7].valueAsText;
   network_time_field     = parameters[8].valueAsText;
   network_time_unit      = parameters[9].valueAsText;

   #########################################################################
   # Step 30
   # Verify the default feature class geojson file
   #########################################################################
   pn = os.path.dirname(os.path.realpath(__file__));
   fc = pn + os.sep + r"Resources" + os.sep + r"AllHazardsWasteLogisticsFacilities.json";
   if not os.path.exists(fc):
      raise arcpy.ExecuteError("Error.  AllHazardsWasteLogisticsFacilities.json not found.");

   with open(fc,"r") as json_f:
      json_d = json.load(json_f);

   del json_d;

   arcpy.AddMessage("Facilities verified.");

   #########################################################################
   # Step 40
   # Verify the map
   #########################################################################
   aprx = arcpy.mp.ArcGISProject("CURRENT");
   map = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];

   if map is None:
      raise arcpy.ExecuteError("Error.  Project map not found.");

   #########################################################################
   # Step 50
   # Cleanup preexisting map resources
   #########################################################################
   cleanup = gp_RemoveWorkEnvironment.execute(
       self
      ,parameters
      ,messages
   );

   #########################################################################
   # Step 60
   # Make fresh Closest Facility Analysis Layer
   #########################################################################
   result_object = arcpy.na.MakeClosestFacilityAnalysisLayer(
       network_data_source          = net_source
      ,layer_name                   = "Network"
      ,travel_mode                  = travel_mode
      ,travel_direction             = "TO_FACILITIES"
      ,cutoff                       = None
      ,number_of_facilities_to_find = 3
      ,time_of_day                  = None
      ,time_zone                    = None
      ,time_of_day_usage            = None
      ,line_shape                   = "ALONG_NETWORK"
   );
   lyr_net = result_object.getOutput(0);
   arcpy.AddMessage("Network Analysis Layer created.");

   network_sublayers = arcpy.na.GetNAClassNames(lyr_net);

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_identifier"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Identifier"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_name"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Name"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_address"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Address"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_city"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_City"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_state"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_State"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_zip"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Zip"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_telephone"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Telephone"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_waste_mgt"
      ,field_type                = "TEXT"
      ,field_alias               = "Facility_Waste_Mgt"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_capacity_trucks_perday"
      ,field_type                = "INTEGER"
      ,field_alias               = "Facility_Capacity_Trucks_PerDay"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_qty_accepted_volume_solid"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility_Qty_Accepted_Volume_Solid"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_qty_accepted_volume_solid_unit"
      ,field_type                = "TEXT"
      ,field_alias               = "Facility_Qty_Accepted_Volume_Solid_Unit"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_qty_accepted_volume_liquid"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility_Qty_Accepted_Volume_Liquid"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_qty_accepted_volume_liquid_unit"
      ,field_type                = "TEXT"
      ,field_alias               = "Facility_Qty_Accepted_Volume_Liquid_Unit"
   );

   arcpy.AddMessage("Facilities Layer extended.");

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_identifier"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Identifier"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_name"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Name"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_address"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Address"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_city"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_City"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_state"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_State"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_zip"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Zip"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_telephone"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Telephone"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_waste_mgt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Waste_Mgt"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_capacity_trucks_perday"
      ,field_type                = "INTEGER"
      ,field_alias               = "Facility_Capacity_Trucks_PerDay"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_qty_accepted_volume_solid"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility_Qty_Accepted_Volume_Solid"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_qty_accepted_volume_solid_unit"
      ,field_type                = "TEXT"
      ,field_alias               = "Facility_Qty_Accepted_Volume_Solid_Unit"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_qty_accepted_volume_liquid"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility_Qty_Accepted_Volume_Liquid"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_qty_accepted_volume_liquid_unit"
      ,field_type                = "TEXT"
      ,field_alias               = "Facility_Qty_Accepted_Volume_Liquid_Unit"
   );

   arcpy.AddMessage("Routes Layer extended.");

   #########################################################################
   # Step 70
   # Create Supporting Resources
   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "Conditions"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "Conditions"
      ,[
          ['conditionid'               ,'TEXT'  ,'ConditionID'             ,255, None,'']
         ,['roadtolls'                 ,'DOUBLE','RoadTolls'               ,None,None,'']
         ,['misccost'                  ,'DOUBLE','MiscCost'                ,None,None,'']
         ,['totalcostmultiplier'       ,'DOUBLE','TotalCostMultiplier'     ,None,None,'']
         ,['vehicledeconcost'          ,'DOUBLE','VehicleDeconCost'        ,None,None,'']
         ,['stagingsitecost'           ,'DOUBLE','StagingSiteCost'         ,None,None,'']
         ,['numberoftrucksavailable'   ,'DOUBLE','NumberofTrucksAvailable' ,None,None,'']
         ,['drivinghours'              ,'DOUBLE','DrivingHours'            ,None,None,'']
       ]
   );
   arcpy.AddMessage("Conditions table created.");

   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "ShipmentLoading"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "ShipmentLoading"
      ,[
          ['factorid'                  ,'TEXT'  ,'FactorID'                ,255, None,'']
         ,['vehicle'                   ,'TEXT'  ,'Vehicle'                 ,255, None,'']
         ,['wastetype'                 ,'TEXT'  ,'WasteType'               ,255, None,'']
         ,['wastemedium'               ,'TEXT'  ,'WasteMedium'             ,255, None,'']
         ,['loadingrate'               ,'DOUBLE','LoadingRate'             ,None,None,'']
         ,['unitpershipment'           ,'TEXT'  ,'UnitPerShipment'         ,255, None,'']
       ]
   );
   arcpy.AddMessage("ShipmentLoading table created.")

   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "CPLMUnitRates"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "CPLMUnitRates"
      ,[
          ['factorid'                  ,'TEXT'  ,'FactorID'                ,255, None,'']
         ,['vehicle'                   ,'TEXT'  ,'Vehicle'                 ,255, None,'']
         ,['cplmdist_lower'            ,'DOUBLE','CPLMDist_Lower'          ,None,None,'']
         ,['cplmdist_upper'            ,'DOUBLE','CPLMDist_Upper'          ,None,None,'']
         ,['cplmunit'                  ,'TEXT'  ,'CPLMUnit'                ,255, None,'']
         ,['wastetype'                 ,'TEXT'  ,'WasteType'               ,255, None,'']
         ,['wastemedium'               ,'TEXT'  ,'WasteMedium'             ,255, None,'']
         ,['cplunit_rate'              ,'DOUBLE','CPLMUnit_Rate'           ,None,None,'']
         ,['unit'                      ,'TEXT'  ,'Unit'                    ,255, None,'']
       ]
   );
   arcpy.AddMessage("CPLMUnitRates table created.")

   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "FixedTransCost"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "FixedTransCost"
      ,[
          ['factorid'                  ,'TEXT'  ,'FactorID'                ,255, None,'']
         ,['vehicle'                   ,'TEXT'  ,'Vehicle'                 ,255, None,'']
         ,['fixedcost_type'            ,'TEXT'  ,'FixedCost_Type'          ,255, None,'']
         ,['wastetype'                 ,'TEXT'  ,'WasteType'               ,255, None,'']
         ,['wastemedium'               ,'TEXT'  ,'WasteMedium'             ,255, None,'']
         ,['fixedcost_value'           ,'DOUBLE','FixedCost_Value'         ,None,None,'']
         ,['unit'                      ,'TEXT'  ,'Unit'                    ,255, None,'']
       ]
   );
   arcpy.AddMessage("FixedTransCost table created.");

   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "LaborCosts"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "LaborCosts"
      ,[
          ['factorid'                  ,'TEXT'  ,'FactorID'                ,255, None,'']
         ,['laborcategory'             ,'TEXT'  ,'LaborCategory'           ,255, None,'']
         ,['laborcost'                 ,'DOUBLE','LaborCost'               ,None,None,'']
         ,['unit'                      ,'TEXT'  ,'Unit'                    ,255, None,'']
       ]
   );
   arcpy.AddMessage("LaborCosts table created.");

   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "DisposalFees"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "DisposalFees"
      ,[
          ['factorid'                  ,'TEXT'  ,'FactorID'                ,255, None,'']
         ,['wastetype'                 ,'TEXT'  ,'WasteType'               ,255, None,'']
         ,['wastemedium'               ,'TEXT'  ,'WasteMedium'             ,255, None,'']
         ,['disposalcost'              ,'DOUBLE','DisposalCost'            ,None,None,'']
         ,['unit'                      ,'TEXT'  ,'Unit'                    ,255, None,'']
       ]
   );
   arcpy.AddMessage("DisposalFees table created.");

   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "IncidentArea"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "IncidentArea"
      ,[
          ['name'                          ,'TEXT'  ,'Name'                          ,255, None,'']
         ,['description'                   ,'TEXT'  ,'Description'                   ,2000,None,'']
       ]
   );
   arcpy.AddMessage("IncidentArea feature class created.");

   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "SupportArea"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "SupportArea"
      ,[
          ['name'                          ,'TEXT'  ,'Name'                          ,255, None,'']
         ,['description'                   ,'TEXT'  ,'Description'                   ,2000,None,'']
       ]
   );
   arcpy.AddMessage("SupportArea feature class created.");

   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "ScenarioResults"
      ,geometry_type     = "POLYLINE"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "ScenarioResults"
      ,[
          ['scenarioid'                     ,'TEXT'  ,'ScenarioID'                     ,255, None,'']
         ,['conditionid'                    ,'TEXT'  ,'ConditionID'                    ,255, None,'']
         ,['factorid'                       ,'TEXT'  ,'FactorID'                       ,255, None,'']
         ,['facility_identifier'            ,'TEXT'  ,'Facility_Identifier'            ,255, None,'']
         ,['facility_rank'                  ,'LONG'  ,'Facility_Rank'                  ,None,None,'']
         ,['total_distance'                 ,'DOUBLE','Total_Distance'                 ,None,None,'']
         ,['distance_unit'                  ,'TEXT'  ,'Distance_Unit'                  ,255 ,None,'']
         ,['total_truck_travel_time'        ,'DOUBLE','Total_Truck_Travel_Time'        ,None,None,'']
         ,['time_unit'                      ,'TEXT'  ,'Time_Unit'                      ,255 ,None,'']
         ,['average_speed'                  ,'DOUBLE','Average_Speed'                  ,None,None,'']
         ,['speed_unit'                     ,'TEXT'  ,'Speed_Unit'                     ,255 ,None,'']
         ,['facility_name'                  ,'TEXT'  ,'Facility_Name'                  ,255, None,'']
         ,['facility_address'               ,'TEXT'  ,'Facility_Addres'                ,255, None,'']
         ,['facility_city'                  ,'TEXT'  ,'Facility_City'                  ,255, None,'']
         ,['facility_state'                 ,'TEXT'  ,'Facility_State'                 ,255, None,'']
         ,['facility_zip'                   ,'TEXT'  ,'Facility_Zip'                   ,255, None,'']
         ,['facility_telephone'             ,'TEXT'  ,'Facility_Telephone'             ,255, None,'']
         ,['facility_waste_mgt   '          ,'TEXT'  ,'Facility_Waste_Mgt'             ,255, None,'']
         ,['facility_capacity_trucks_perday','DOUBLE','Facility_Capacity_Trucks_PerDay',None,None,'']
         ,['facility_qty_accepted'          ,'DOUBLE','Facility_Qty_Accepted'          ,None,None,'']
         ,['facility_qty_accepted_unit'     ,'TEXT'  ,'Facility_Qty_Accepted_Unit'     ,255 ,None,'']
         ,['allocated_amount'               ,'DOUBLE','Allocated_Amount'               ,None,None,'']
         ,['allocated_amount_unit'          ,'TEXT'  ,'Allocated_Amount_Unit'          ,255 ,None,'']
         ,['number_of_shipments'            ,'LONG'  ,'Number_Of_Shipments'            ,None,None,'']
         ,['cplm_cost_usd'                  ,'DOUBLE','CPLM_Cost_USD'                  ,None,None,'']
         ,['fixed_cost_usd_per_shipment'    ,'DOUBLE','Fixed_Cost_USD_Per_Shipment'    ,None,None,'']
         ,['fixed_cost_usd_per_hour'        ,'DOUBLE','Fixed_Cost_USD_Per_Hour'        ,None,None,'']
         ,['tolls_usd'                      ,'DOUBLE','Tolls_USD'                      ,None,None,'']
         ,['misc_trans_cost_usd'            ,'DOUBLE','Misc_Trans_Cost_USD'            ,None,None,'']
         ,['trans_cost_usd'                 ,'DOUBLE','Trans_Cost_USD'                 ,None,None,'']
         ,['staging_site_cost_usd'          ,'DOUBLE','Staging_Site_Cost_USD'          ,None,None,'']
         ,['disposal_cost_usd'              ,'DOUBLE','Disposal_Cost_USD'              ,None,None,'']
         ,['labor_cost_usd'                 ,'DOUBLE','Labor_Cost_USD'                 ,None,None,'']
         ,['vehicle_decon_cost_usd'         ,'DOUBLE','Vehicle_Decon_Cost_USD'         ,None,None,'']
         ,['cost_multiplier_usd'            ,'DOUBLE','Cost_Multiplier_USD'            ,None,None,'']
         ,['cost_usd'                       ,'DOUBLE','Cost_USD'                       ,None,None,'']
         ,['trucks_time_to_comp_days'       ,'DOUBLE','Truck_Time_To_Comp_Days'        ,None,None,'']
         ,['dest_time_to_comp_days'         ,'DOUBLE','Dest_Time_To_Comp_Days'         ,None,None,'']
         ,['time_days'                      ,'DOUBLE','Time_Days'                      ,None,None,'']
         ,['username'                       ,'TEXT'  ,'UserName'                       ,None,None,'']
         ,['creationtime'                   ,'DATE'  ,'CreationTime'                   ,None,None,'']
       ]
   );
   arcpy.AddMessage("ScenarioResults feature class created.");

   ############################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "Scenario"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "Scenario"
      ,[
          ['scenarioid'                ,'TEXT'  ,'ScenarioID'                  ,255, None,'']
         ,['waste_type'                ,'TEXT'  ,'Waste_Type'                  ,255, None,'']
         ,['waste_medium'              ,'TEXT'  ,'Waste_Medium'                ,255, None,'']
         ,['waste_amount'              ,'DOUBLE','Waste_Amount'                ,None,None,'']
         ,['waste_unit'                ,'TEXT'  ,'Waste_Unit'                  ,255, None,'']
         ,['numberoffacilitiestofind'  ,'LONG'  ,'NumberOfFacilitiesToFind'    ,None,None,'']
         ,['route_count_requested'     ,'LONG'  ,'Route_Count_Requested'       ,None,None,'']
         ,['route_count_returned'      ,'LONG'  ,'Route_Count_Returned'        ,None,None,'']
         ,['map_image'                 ,'TEXT'  ,'Map_Image'                   ,255, None,'']
         ,['conditionid'               ,'TEXT'  ,'ConditionID'                 ,255, None,'']
         ,['factorid'                  ,'TEXT'  ,'FactorID'                    ,255, None,'']
       ]
   );
   arcpy.AddMessage("Scenario table created.");

   ############################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = arcpy.env.workspace
      ,out_name          = "SystemCache"
      ,geometry_type     = "POLYLINE"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "SystemCache"
      ,[
          ['current_unit_system'                    ,'TEXT'  ,'Current_Unit_System'                    ,None,None,'']
         ,['current_scenarioid'                     ,'TEXT'  ,'Current_ScenarioID'                     ,255, None,'']
         ,['current_conditionid'                    ,'TEXT'  ,'Current_ConditionID'                    ,255, None,'']
         ,['current_factorid'                       ,'TEXT'  ,'Current_FactorID'                       ,255, None,'']
         ,['network_dataset'                        ,'TEXT'  ,'Network_Dataset'                        ,2000,None,'']
         ,['network_distance_fieldname'             ,'TEXT'  ,'Network_Distance_Fieldname'             ,255, None,'']
         ,['network_distance_unit'                  ,'TEXT'  ,'Network_Distance_Unit'                  ,255, None,'']
         ,['network_time_fieldname'                 ,'TEXT'  ,'Network_Time_Fieldname'                 ,255, None,'']
         ,['network_time_unit'                      ,'TEXT'  ,'Network_Time_Unit'                      ,255, None,'']
       ]
   );
   arcpy.AddMessage("SystemCache feature class created.");

   #########################################################################
   # Step 80
   # Load config defaults
   #########################################################################
   json_d = util.load_settings();
   if json_d is None:
      raise arcpy.ExecuteError("Error unable to read Defaults.json");
   else:
      arcpy.AddMessage("Defaults read successfully.");

   if 'Conditions' in json_d:
      cursor = arcpy.da.InsertCursor(
          arcpy.env.workspace + os.sep + "Conditions"
         ,obj_Condition.Condition.fields
      );
      for row in json_d["Conditions"]:
         cursor.insertRow(
            (
                row["ConditionID"]
               ,row["RoadTolls"]
               ,row["MiscCost"]
               ,row["TotalCostMultiplier"]
               ,row["VehicleDeconCost"]
               ,row["StagingSiteCost"]
               ,row["NumberofTrucksAvailable"]
               ,row["DrivingHours"]
            )
         );

      del cursor;
      arcpy.AddMessage("Conditions table loaded.");

   if 'ShipmentLoading' in json_d:
      cursor = arcpy.da.InsertCursor(
          arcpy.env.workspace + os.sep + "ShipmentLoading"
         ,obj_ShipmentLoading.ShipmentLoading.fields
      );
      for cid in json_d["ShipmentLoading"]:
         factorid = cid["FactorID"];

         for row in cid["rows"]:

            (loading_rate,unitpershipment) = util.converter(
                in_unit     = row["UnitPerShipment"]
               ,in_value    = row["LoadingRate"]
               ,unit_system = unit_system
            );

            cursor.insertRow(
               (
                   factorid
                  ,row["Vehicle"]
                  ,row["WasteType"]
                  ,row["WasteMedium"]
                  ,loading_rate
                  ,unitpershipment
               )
            );

      del cursor;
      arcpy.AddMessage("ShipmentLoading table loaded.");

   if 'CPLMUnitRates' in json_d:
      cursor = arcpy.da.InsertCursor(
          arcpy.env.workspace + os.sep + "CPLMUnitRates"
         ,obj_CPLMUnitRates.CPLMUnitRates.fields
      );
      for cid in json_d["CPLMUnitRates"]:
         factorid = cid["FactorID"];

         for row in cid["rows"]:

            (lower_value,cplm_unit) = util.converter(
                in_unit     = row["CPLMUnit"]
               ,in_value    = row["CPLMDist_Lower"]
               ,unit_system = unit_system
            );

            (upper_value,unit) = util.converter(
                in_unit     = row["CPLMUnit"]
               ,in_value    = row["CPLMDist_Upper"]
               ,unit_system = unit_system
            );

            (unit_rate,unit) = util.converter(
                in_unit     = row["Unit"]
               ,in_value    = row["CPLMUnit_Rate"]
               ,unit_system = unit_system
            );

            cursor.insertRow(
               (
                   factorid
                  ,row["Vehicle"]
                  ,lower_value
                  ,upper_value
                  ,cplm_unit
                  ,row["WasteType"]
                  ,row["WasteMedium"]
                  ,unit_rate
                  ,unit
               )
            );

      del cursor;
      arcpy.AddMessage("CPLMUnitRates table loaded.");

   if 'FixedTransCost' in json_d:
      cursor = arcpy.da.InsertCursor(
          arcpy.env.workspace + os.sep + "FixedTransCost"
         ,obj_FixedTransCost.FixedTransCost.fields
      );
      for cid in json_d["FixedTransCost"]:
         factorid = cid["FactorID"];

         for row in cid["rows"]:
            cursor.insertRow(
               (
                   factorid
                  ,row["Vehicle"]
                  ,row["FixedCost_Type"]
                  ,row["WasteType"]
                  ,row["WasteMedium"]
                  ,row["FixedCost_Value"]
                  ,row["Unit"]
               )
            );

      del cursor;
      arcpy.AddMessage("FixedTransCost table loaded.");

   if 'LaborCosts' in json_d:
      cursor = arcpy.da.InsertCursor(
          arcpy.env.workspace + os.sep + "LaborCosts"
         ,obj_LaborCosts.LaborCosts.fields
      );
      for cid in json_d["LaborCosts"]:
         factorid = cid["FactorID"];

         for row in cid["rows"]:
            cursor.insertRow(
               (
                   factorid
                  ,row["LaborCategory"]
                  ,row["LaborCost"]
                  ,row["Unit"]
               )
            );

      del cursor;
      arcpy.AddMessage("LaborCosts table loaded.");

   if 'DisposalFees' in json_d:
      cursor = arcpy.da.InsertCursor(
          arcpy.env.workspace + os.sep + "DisposalFees"
         ,obj_DisposalFees.DisposalFees.fields
      );
      for cid in json_d["DisposalFees"]:
         factorid = cid["FactorID"];

         for row in cid["rows"]:

            (disposal_cost,unit) = util.converter(
                in_unit     = row["Unit"]
               ,in_value    = row["DisposalCost"]
               ,unit_system = unit_system
            );

            cursor.insertRow(
               (
                   factorid
                  ,row["WasteType"]
                  ,row["WasteMedium"]
                  ,disposal_cost
                  ,unit
               )
            );

      del cursor;
      arcpy.AddMessage("DisposalFees table loaded.");

   if 'SystemCache' in json_d:
      cursor = arcpy.da.InsertCursor(
          arcpy.env.workspace + os.sep + "SystemCache"
         ,obj_SystemCache.SystemCache.fields
      );

      cursor.insertRow(
         (
             unit_system
            ,None   # current scenarioid
            ,None   # current conditionid
            ,None   # current factorid
            ,net_source_str
            ,network_distance_field
            ,network_distance_unit
            ,network_time_field
            ,network_time_unit
         )
      );

      del cursor;

   #########################################################################
   # Step 90
   # Create the Folder Group for items and add incident and support area fcs
   #########################################################################
   fld = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","Folder.lyrx"));
   grp = fld.listLayers("Folder")[0];
   grp.name = "AllHazardsWasteLogisticsTool";
   map.addLayer(grp,"TOP");
   grp = map.listLayers("AllHazardsWasteLogisticsTool")[0];

   fld = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","Settings.lyrx"));
   set = fld.listLayers("Folder")[0];
   set.name = "Settings";
   map.addLayerToGroup(grp,set,"TOP");
   set = map.listLayers("Settings")[0];

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","SystemCache.lyrx"));
   map.addLayerToGroup(set,lyr,"TOP");

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","Conditions.lyrx"));
   map.addLayerToGroup(set,lyr,"TOP");

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","Scenario.lyrx"));
   map.addLayerToGroup(set,lyr,"TOP");

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","ShipmentLoading.lyrx"));
   map.addLayerToGroup(set,lyr,"TOP");

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","CPLMUnitRates.lyrx"));
   map.addLayerToGroup(set,lyr,"TOP");

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","FixedTransCost.lyrx"));
   map.addLayerToGroup(set,lyr,"TOP");

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","LaborCosts.lyrx"));
   map.addLayerToGroup(set,lyr,"TOP");

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","DisposalFees.lyrx"));
   map.addLayerToGroup(set,lyr,"TOP");

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","ScenarioResults.lyrx"));
   map.addLayerToGroup(grp,lyr,"TOP");

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","IncidentArea.lyrx"));
   map.addLayerToGroup(grp,lyr,"TOP");

   lyr = arcpy.mp.LayerFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","SupportArea.lyrx"));
   map.addLayerToGroup(grp,lyr,"TOP");

   #########################################################################
   # Step 100
   # Grind up the network layer and add rendering to the new item
   #########################################################################
   lyrx_style  = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Resources","Network.lyrx");
   lyrx_target = arcpy.CreateScratchName(
       "Network.lyrx"
      ,""
      ,"Folder"
      ,arcpy.env.scratchFolder
   );

   arcpy.SaveToLayerFile_management(
       in_layer  = lyr_net
      ,out_layer = lyrx_target
   );

   with open(lyrx_style,"r") as jsonFile_style:
      data_style = json.load(jsonFile_style);

   with open(lyrx_target,"r") as jsonFile_target:
      data_target = json.load(jsonFile_target);

   for item in data_target["layerDefinitions"]:
      if item["name"] == "Facilities":
         for item2 in data_style["layerDefinitions"]:
            if item2["name"] == "Facilities":
               item["renderer"] = item2["renderer"];

      if item["name"] == "Incidents":
         for item2 in data_style["layerDefinitions"]:
            if item2["name"] == "Incidents":
               item["renderer"] = item2["renderer"];

      if item["name"] == "Point Barriers":
         for item2 in data_style["layerDefinitions"]:
            if item2["name"] == "Point Barriers":
               item["renderer"] = item2["renderer"];

      if item["name"] == "Routes":
         for item2 in data_style["layerDefinitions"]:
            if item2["name"] == "Routes":
               item["renderer"] = item2["renderer"];

      if item["name"] == "Line Barriers":
         for item2 in data_style["layerDefinitions"]:
            if item2["name"] == "Line Barriers":
               item["renderer"] = item2["renderer"];

      if item["name"] == "Polygon Barriers":
         for item2 in data_style["layerDefinitions"]:
            if item2["name"] == "Polygon Barriers":
               item["renderer"] = item2["renderer"];

   with open(lyrx_target,"w") as jsonFile:
      json.dump(data_target,jsonFile);

   net = arcpy.mp.LayerFile(lyrx_target);
   map.addLayerToGroup(grp,net,"TOP");

   #########################################################################
   # Step 110
   # Scope is always a problem, try to cleanup manually
   #########################################################################

   del aprx;
   del lyr;
   del lyr_net;
   del net;
   del map;

   return;
