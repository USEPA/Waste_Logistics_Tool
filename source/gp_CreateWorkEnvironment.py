import arcpy,os,sys;
import json;

import source.gp_RemoveWorkEnvironment;
import source.util;

###############################################################################
import importlib
importlib.reload(source.gp_RemoveWorkEnvironment);
importlib.reload(source.util);

###############################################################################
def execute(self,parameters,messages):

   source.util.dzlog("Running gp_CreateWorkEnvironment.");
   #########################################################################
   # Step 10
   # Abend if edits are pending
   #########################################################################
   if source.util.sniff_editing_state():
      err = "Error.  Pending edits must be saved or cleared before proceeding.";
      source.util.dzlog(err);
      raise arcpy.ExecuteError(err);
      
   #########################################################################
   # Step 20
   # Read the parameters
   #########################################################################
   unit_system      = parameters[1].valueAsText;
   
   nd_type          = parameters[2].valueAsText;
   nd_file          = parameters[3].value;
   nd_file_str      = parameters[3].valueAsText;
   nd_remote        = parameters[4].value;
   nd_remote_str    = parameters[4].valueAsText;
   nd_portal        = parameters[5].value;
   nd_portal_str    = parameters[5].valueAsText;
   
   portal_username  = parameters[6].valueAsText;
   portal_credits   = parameters[7].value;
   
   travel_mode      = parameters[8].valueAsText;
   impedance_field  = parameters[9].valueAsText;
   
   overall_dist_fld = parameters[10].valueAsText;
   overall_dist_unt = parameters[11].valueAsText; 
   overall_time_fld = parameters[12].valueAsText;
   overall_time_unt = parameters[13].valueAsText;
   
   road_dist_fld    = parameters[14].valueAsText;
   road_dist_unt    = parameters[15].valueAsText; 
   road_time_fld    = parameters[16].valueAsText;
   road_time_unt    = parameters[17].valueAsText;
   
   rail_dist_fld    = parameters[18].valueAsText;
   rail_dist_unt    = parameters[19].valueAsText; 
   rail_time_fld    = parameters[20].valueAsText;
   rail_time_unt    = parameters[21].valueAsText;
   
   station_cnt_fld  = parameters[22].valueAsText;
   
   isAGO            = source.util.clean_boo(parameters[23].valueAsText);
   
   if isAGO:
      maximum_facilities_to_find = 100;
   else:
      maximum_facilities_to_find = None;
   
   if nd_type == 'Portal Helper':
      net_source     = nd_portal.rstrip('/').lower();
      net_source_str = nd_portal_str.rstrip('/').lower();
      
   elif nd_type == 'File Network Dataset':
      net_source     = nd_file;
      net_source_str = nd_file_str;
      
   elif nd_type == 'Remote Network Dataset':
      net_source     = nd_remote;
      net_source_str = nd_remote_str;
      
   else:
      raise Exception('err');
   
   ago_account = portal_username;

   if travel_mode is not None and travel_mode.strip() == "":
      travel_mode = None;
   
   accumulate_attributes = [];
   accumulate_attributes.append(overall_dist_fld);
   accumulate_attributes.append(overall_time_fld);
   
   if road_dist_fld is None or road_dist_fld == "" or road_dist_fld == " ":
      road_dist_fld = None;
   else:
      accumulate_attributes.append(road_dist_fld);
      
   if road_dist_unt == "" or road_dist_unt == " ":
      road_dist_unt   = None;
      
   if road_time_fld is None or road_time_fld == "" or road_time_fld == " ":
      road_time_fld = None;
   else:
      accumulate_attributes.append(road_time_fld);
   
   if road_time_unt == "" or road_time_unt == " ":
      road_time_unt = None;
      
   if rail_dist_fld is None or rail_dist_fld == "" or rail_dist_fld == " ":
      rail_dist_fld = None;
   else:
      accumulate_attributes.append(rail_dist_fld);
   
   if rail_dist_unt == "" or rail_dist_unt == " ":
      rail_dist_unt = None;
   
   if rail_time_fld is None or rail_time_fld == "" or rail_time_fld == " ":
      rail_time_fld = None;
   else:
      accumulate_attributes.append(rail_time_fld);

   if rail_time_unt == "" or rail_time_unt == " ":
      rail_time_unt = None;
      
   if station_cnt_fld is None or station_cnt_fld == "" or station_cnt_fld == " ":
      station_cnt_fld = None;
   else:
      accumulate_attributes.append(station_cnt_fld);
      
   accumulate_attributes = list(set(accumulate_attributes));
      
   #########################################################################
   # Step 30
   # Verify the default IWasteFacilities geojson file
   #########################################################################
   arcpy.AddMessage("  Verifying default IWaste facilities file.");
   fc = os.path.join(source.util.g_pn,"data","IWasteFacilities.json");
   if not os.path.exists(fc):
      err = "Error.  IWasteFacilities.json not found.";
      source.util.dzlog(err);
      raise arcpy.ExecuteError(err);

   with open(fc,"r") as json_f:
      json_d = json.load(json_f);

   del json_d;

   arcpy.AddMessage("  IWaste Facilities verified.");
   
   arcpy.AddMessage("  Verifying default IWaste local vintage file.");
   fc = os.path.join(source.util.g_pn,"data","IWasteVintage_Local.json");
   if not os.path.exists(fc):
      err = "Error.  IWasteVintage_Local.json not found.";
      source.util.dzlog(err);
      raise arcpy.ExecuteError(err);

   with open(fc,"r") as json_f:
      json_d = json.load(json_f);

   del json_d;

   arcpy.AddMessage("  IWaste Local Vintage verified.");

   #########################################################################
   # Step 40
   # Verify the map
   #########################################################################
   if source.util.g_aprx is None:
      aprx = arcpy.mp.ArcGISProject(source.util.g_prj);
   else:
      aprx = source.util.g_aprx;
   
   map = aprx.listMaps("AllHazardsWasteLogisticsMap")[0];

   if map is None:
      raise arcpy.ExecuteError("Error.  Project map not found.");

   #########################################################################
   # Step 50
   # Cleanup preexisting map resources
   #########################################################################
   cleanup = source.gp_RemoveWorkEnvironment.execute(
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
      ,accumulate_attributes        = accumulate_attributes
   );
   lyr_net = result_object.getOutput(0);
   arcpy.AddMessage("  Network Analysis Layer created.");

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
      ,field_name                = "facility_typeid"
      ,field_type                = "LONG"
      ,field_alias               = "Facility_TypeID"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_subtypeids"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_SubtypeIDs"
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
      ,field_name                = "front_gate_longitude"
      ,field_type                = "DOUBLE"
      ,field_alias               = "front_gate_longitude"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "front_gate_latitude"
      ,field_type                = "DOUBLE"
      ,field_alias               = "front_gate_latitude"
   );

   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_waste_mgt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_Waste_Mgt"
   );
   
   ## No waste flag
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "facility_accepts_no_waste"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Accepts No Waste Flag"
   );
   
   ############################################################################
   # Daily Caps
   ############################################################################
   # Radioactive: Contact-Handled
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Daily Capacity Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_liquid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_liquid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Daily Capacity Unit"
   );
   
   # Radioactive: Remote-Handled
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Daily Capacity Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_liquid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_liquid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Daily Capacity Unit"
   );
   
   # Low-Activity Radioactive Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_larw_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_larw_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Daily Capacity Unit"
   );
   
   # Hazardous
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Solid Daily Capacity Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_liquid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Liquid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_liquid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Liquid Daily Capacity Unit"
   );
   
   # Municipal Solid Waste (MSW)
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_msw_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_msw_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Daily Capacity Unit"
   );
   
   # Construction and Demolition
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_cad_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Construction and Demolition Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_cad_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Construction and Demolition Volume Solid Daily Capacity Unit"
   );
   
   # Non-Hazardous Aqueous Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_nhaq_liquid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_nhaq_liquid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Daily Capacity Unit"
   );
   
   ############################################################################
   # Total Acceptance
   ############################################################################
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Total Acceptance Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_liquid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_liquid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Total Acceptance Unit"
   );
   
   # Radioactive: Remote-Handled
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Total Acceptance Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_liquid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_liquid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Total Acceptance Unit"
   );
   
   # Low-Activity Radioactive Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_larw_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_larw_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Total Acceptance Unit"
   );
   
   # Hazardous
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Solid Total Acceptance Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_liquid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Liquid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_liquid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Liquid Total Acceptance Unit"
   );
   
   # Municipal Solid Waste (MSW)
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_msw_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_msw_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Total Acceptance Unit"
   );
   
   # Construction and Demolition
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_cad_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Construction and Demolition Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_cad_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Construction and Demolition Volume Solid Total Acceptance Unit"
   );
   
   # Non-Hazardous Aqueous Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_nhaq_liquid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_nhaq_liquid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Total Acceptance Unit"
   );
   
   ############################################################################
   # Disposal Fees
   ############################################################################
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Disposal Fees Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_liquid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radc_liquid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Disposal Fees Unit"
   );
   
   # Radioactive: Remote-Handled
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Disposal Fees Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_liquid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_radr_liquid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Disposal Fees Unit"
   );
   
   # Low-Activity Radioactive Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_larw_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_larw_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Disposal Fees Unit"
   );
   
   # Hazardous
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Solid Disposal Fees Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_liquid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Liquid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_haz_liquid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Liquid Disposal Fees Unit"
   );
   
   # Municipal Solid Waste (MSW)
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_msw_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_msw_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Disposal Fees Unit"
   );
   
   # Construction and Demolition
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_cad_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Construction and Demolition Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_cad_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Construction and Demolition Volume Solid Disposal Fees Unit"
   );
   
   # Non-Hazardous Aqueous Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_nhaq_liquid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "fac_nhaq_liquid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Disposal Fees Unit"
   );

   ############################################################################
   # Acceptance type flags
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "C_D_accepted"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Construction and Demolition Waste Accepted"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "MSW_accepted"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Municipal Solid Waste (MSW) Accepted"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "HW_accepted"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Hazardous Waste Accepted"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "LARWRad_accepted"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Low-Activity Radioactive Waste Accepted"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "RAD_accepted"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Radioactive Waste Accepted"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "NHAW_accepted"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Non-Hazardous Aqueous Waste Volume Accepted"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "date_stamp"
      ,field_type                = "DATE"
      ,field_length              = 255
      ,field_alias               = "Last Altered Date Stamp"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "source"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Source"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["Facilities"]
      ,field_name                = "notes"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Additional Notes"
   );

   arcpy.AddMessage("  Facilities Layer extended.");

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
      ,field_name                = "facility_typeid"
      ,field_type                = "LONG"
      ,field_alias               = "Facility_TypeID"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_subtypeids"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility_SubtypeIDs"
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
   
   ## No waste flag
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "facility_accepts_no_waste"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Accepts No Waste Flag"
   );
   
   ############################################################################
   # Daily Caps
   ############################################################################
   # Radioactive: Contact-Handled
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Daily Capacity Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_liquid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_liquid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Daily Capacity Unit"
   );
   
   # Radioactive: Remote-Handled
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Daily Capacity Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_liquid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_liquid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Daily Capacity Unit"
   );
   
   # Low-Activity Radioactive Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_larw_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_larw_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Daily Capacity Unit"
   );
   
   # Hazardous
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Solid Daily Capacity Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_liquid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Liquid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_liquid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Liquid Daily Capacity Unit"
   );
   
   # Municipal Solid Waste (MSW)
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_msw_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_msw_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Daily Capacity Unit"
   );
   
   # Construction and Demolition
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_cad_solid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Construction and Demolition Volume Solid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_cad_solid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Construction and Demolition Volume Solid Daily Capacity Unit"
   );
   
   # Non-Hazardous Aqueous Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_nhaq_liquid_dly_cap"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Daily Capacity"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_nhaq_liquid_dly_cap_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Daily Capacity Unit"
   );
   
   ############################################################################
   # Total Acceptance
   ############################################################################
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Total Acceptance Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_liquid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_liquid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Total Acceptance Unit"
   );
   
   # Radioactive: Remote-Handled
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Total Acceptance Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_liquid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_liquid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Total Acceptance Unit"
   );
   
   # Low-Activity Radioactive Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_larw_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_larw_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Total Acceptance Unit"
   );
   
   # Hazardous
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Solid Total Acceptance Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_liquid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Liquid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_liquid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Liquid Total Acceptance Unit"
   );
   
   # Municipal Solid Waste (MSW)
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_msw_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_msw_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Total Acceptance Unit"
   );
   
   # Construction and Demolition
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_cad_solid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Construction and Demolition Volume Solid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_cad_solid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Construction and Demolition Volume Solid Total Acceptance Unit"
   );
   
   # Non-Hazardous Aqueous Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_nhaq_liquid_tot_acp"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Total Acceptance"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_nhaq_liquid_tot_acp_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Total Acceptance Unit"
   );
   
   ############################################################################
   # Disposal Fees
   ############################################################################
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Solid Disposal Fees Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_liquid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radc_liquid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Contact-Handled Volume Liquid Disposal Fees Unit"
   );
   
   # Radioactive: Remote-Handled
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Solid Disposal Fees Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_liquid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_radr_liquid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Radioactive: Remote-Handled Volume Liquid Disposal Fees Unit"
   );
   
   # Low-Activity Radioactive Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_larw_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_larw_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Low-Activity Radioactive Waste Volume Solid Disposal Fees Unit"
   );
   
   # Hazardous
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Solid Disposal Fees Unit"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_liquid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Hazardous Volume Liquid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_haz_liquid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Hazardous Volume Liquid Disposal Fees Unit"
   );
   
   # Municipal Solid Waste (MSW)
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_msw_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_msw_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Municipal Solid Waste (MSW) Volume Solid Disposal Fees Unit"
   );
   
   # Construction and Demolition
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_cad_solid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Construction and Demolition Volume Solid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_cad_solid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Construction and Demolition Volume Solid Disposal Fees Unit"
   );
   
   # Non-Hazardous Aqueous Waste
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_nhaq_liquid_dis_fee"
      ,field_type                = "DOUBLE"
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Disposal Fees"
   );
   
   arcpy.na.AddFieldToAnalysisLayer(
       in_network_analysis_layer = lyr_net
      ,sub_layer                 = network_sublayers["CFRoutes"]
      ,field_name                = "fac_nhaq_liquid_dis_fee_unt"
      ,field_type                = "TEXT"
      ,field_length              = 255
      ,field_alias               = "Facility Non-Hazardous Aqueous Waste Volume Liquid Disposal Fees Unit"
   );
   
   arcpy.AddMessage("  Routes Layer extended.");

   #########################################################################
   # Step 70
   # Create Supporting Resources
   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
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
          ['conditionid'               ,'TEXT'  ,'ConditionID'                                  ,255, None,'']
         ,['roadtollsperroadshipment'  ,'DOUBLE','Road Tolls Per Road Shipment'                 ,None,None,'']
         
         ,['misccostperroadshipment'   ,'DOUBLE','Misc Cost Per Road Shipment'                  ,None,None,'']
         ,['misccostperrailshipment'   ,'DOUBLE','Misc Cost Per Rail Shipment'                  ,None,None,'']
         
         ,['roadtransporterdeconcost'  ,'DOUBLE','Road Transporter Decon Cost Per Road Shipment',None,None,'']
         ,['railtransporterdeconcost'  ,'DOUBLE','Rail Transporter Decon Cost Per Rail Shipment',None,None,'']
         
         ,['stagingsitecost'           ,'DOUBLE','Staging Site Cost'                            ,None,None,'']
         
         ,['roaddrivinghoursperday'    ,'DOUBLE','Road Driving Hours Per Day'                   ,None,None,'']
         ,['raildrivinghoursperday'    ,'DOUBLE','Rail Driving Hours Per Day'                   ,None,None,'']
         
         ,['totalcostmultiplier'       ,'DOUBLE','Total Cost Multiplier'                        ,None,None,'']
       ]
   );
   
   arcpy.management.AddIndex(
       in_table   = "Conditions"
      ,fields     = 'conditionid'
      ,index_name = 'conditionid_idx'
   );
   
   arcpy.AddMessage("  Conditions table created.");
   
   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
      ,out_name          = "Modes"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );
   
   arcpy.management.AddFields(
       "Modes"
      ,[
          ['factorid'                  ,'TEXT'  ,'FactorID'                ,255, None,'']
         ,['mode'                      ,'TEXT'  ,'Mode'                    ,255, None,'']
         ,['name'                      ,'TEXT'  ,'Transporter'             ,255, None,'']
         ,['description'               ,'TEXT'  ,'Description'             ,255, None,'']
       ]
   );
   
   arcpy.management.AddIndex(
       in_table   = "Modes"
      ,fields     = 'factorid'
      ,index_name = 'factorid_idx'
   );
   
   arcpy.AddMessage("  Modes table created.");
   
   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
      ,out_name          = "Transporters"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );
   
   arcpy.management.AddFields(
       "Transporters"
      ,[
          ['transporterattrid'           ,'TEXT'  ,'Transporter Attribute ID'       ,255, None,'']
         ,['mode'                        ,'TEXT'  ,'Mode'                           ,255, None,'']
         ,['wastetype'                   ,'TEXT'  ,'WasteType'                      ,255, None,'']
         ,['wastemedium'                 ,'TEXT'  ,'WasteMedium'                    ,255, None,'']
         ,['containercapacity'           ,'DOUBLE','Container Capacity'             ,None,None,'']
         ,['containercapacityunit'       ,'TEXT'  ,'Container Capacity Unit'        ,255, None,'']
         ,['containercountpertransporter','LONG'  ,'Container Count Per Transporter',None,None,'']
         ,['transportersavailable'       ,'LONG'  ,'Transporters Available'         ,None,None,'']
         ,['transportersprocessedperday' ,'LONG'  ,'Transporters Processed Per Day' ,None,None,'']
       ]
   );
   
   arcpy.management.AddIndex(
       in_table   = "Transporters"
      ,fields     = 'transporterattrid'
      ,index_name = 'transporterattrid_idx'
   );
   
   arcpy.AddMessage("  Transporters table created.");

   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
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
         ,['mode'                      ,'TEXT'  ,'Mode'                    ,255, None,'']
         ,['cplmdist_lower'            ,'DOUBLE','CPLMDist_Lower'          ,None,None,'']
         ,['cplmdist_upper'            ,'DOUBLE','CPLMDist_Upper'          ,None,None,'']
         ,['cplmunit'                  ,'TEXT'  ,'CPLMUnit'                ,255, None,'']
         ,['wastetype'                 ,'TEXT'  ,'WasteType'               ,255, None,'']
         ,['wastemedium'               ,'TEXT'  ,'WasteMedium'             ,255, None,'']
         ,['cplunit_rate'              ,'DOUBLE','CPLMUnit_Rate'           ,None,None,'']
         ,['cplunit_rateunit'          ,'TEXT'  ,'CPLMUnit_Rate Unit'      ,255, None,'']
       ]
   );
   
   arcpy.management.AddIndex(
       in_table   = "CPLMUnitRates"
      ,fields     = 'factorid'
      ,index_name = 'factorid_idx'
   );
   
   arcpy.AddMessage("  CPLMUnitRates table created.")

   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
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
         ,['mode'                      ,'TEXT'  ,'Mode'                    ,255, None,'']
         ,['fixedcost_type'            ,'TEXT'  ,'FixedCost_Type'          ,255, None,'']
         ,['wastetype'                 ,'TEXT'  ,'WasteType'               ,255, None,'']
         ,['wastemedium'               ,'TEXT'  ,'WasteMedium'             ,255, None,'']
         ,['fixedcost_value'           ,'DOUBLE','FixedCost_Value'         ,None,None,'']
         ,['fixedcost_valueunit'       ,'TEXT'  ,'FixedCost_Value Unit'    ,255, None,'']
       ]
   );
   
   arcpy.management.AddIndex(
       in_table   = "FixedTransCost"
      ,fields     = 'factorid'
      ,index_name = 'factorid_idx'
   );
   
   arcpy.AddMessage("  FixedTransCost table created.");

   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
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
         ,['mode'                      ,'TEXT'  ,'Mode'                    ,255, None,'']
         ,['laborcategory'             ,'TEXT'  ,'LaborCategory'           ,255, None,'']
         ,['laborcost'                 ,'DOUBLE','LaborCost'               ,None,None,'']
         ,['laborcostunit'             ,'TEXT'  ,'LaborCost Unit'          ,255, None,'']
       ]
   );
   
   arcpy.management.AddIndex(
       in_table   = "LaborCosts"
      ,fields     = 'factorid'
      ,index_name = 'factorid_idx'
   );
   
   arcpy.AddMessage("  LaborCosts table created.");
   
   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
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
          ['facilityattributesid'      ,'TEXT'  ,'Facility Attributes ID'    ,255, None,'']
         ,['facility_subtypeid'        ,'LONG'  ,'Facility_SubtypeID'        ,None,None,'']
         ,['wastetype'                 ,'TEXT'  ,'WasteType'                 ,255, None,'']
         ,['wastemedium'               ,'TEXT'  ,'WasteMedium'               ,255, None,'']
         ,['costperone'                ,'DOUBLE','CostPerOne'                ,None,None,'']
         ,['costperoneunit'            ,'TEXT'  ,'CostPerOneUnit'            ,255, None,'']
       ]
   );
   
   arcpy.management.AddIndex(
       in_table   = "DisposalFees"
      ,fields     = 'facilityattributesid'
      ,index_name = 'facilityattributesid_idx'
   );
   
   arcpy.AddMessage("  DisposalFees table created.");

   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
      ,out_name          = "FacilityCapacities"
      ,geometry_type     = "POLYGON"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       "FacilityCapacities"
      ,[
          ['facilityattributesid'      ,'TEXT'  ,'Facility Attributes ID'    ,255, None,'']
         ,['facility_subtypeid'        ,'LONG'  ,'Facility_SubtypeID'        ,None,None,'']
         ,['wastetype'                 ,'TEXT'  ,'WasteType'                 ,255, None,'']
         ,['wastemedium'               ,'TEXT'  ,'WasteMedium'               ,255, None,'']
         ,['dailyvolumeperday'         ,'DOUBLE','Daily Volume Per Day'      ,None,None,'']
         ,['dailyvolumeperdayunit'     ,'TEXT'  ,'Daily Volume Per Day Unit' ,255, None,'']
         ,['totalaccepted_days'        ,'LONG'  ,'Total Accepted Days'       ,None,None,'']
       ]
   );
   
   arcpy.management.AddIndex(
       in_table   = "FacilityCapacities"
      ,fields     = 'facilityattributesid'
      ,index_name = 'facilityattributesid_idx'
   );
   
   arcpy.AddMessage("  FacilityCapacities table created.");

   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
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
   
   arcpy.AddMessage("  IncidentArea feature class created.");

   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
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
   arcpy.AddMessage("  SupportArea feature class created.");

   #########################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
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
         ,['facilityattributesid'           ,'TEXT'  ,'Facility Attributes ID'         ,255, None,'']
         ,['road_transporter_attributes'    ,'TEXT'  ,'Road Transporter Attributes'    ,255, None,'']
         ,['rail_transporter_attributes'    ,'TEXT'  ,'Rail Transporter Attributes'    ,255, None,'']
         ,['facility_identifier'            ,'TEXT'  ,'Facility_Identifier'            ,255, None,'']
         ,['facility_rank'                  ,'LONG'  ,'Facility_Rank'                  ,None,None,'']
         
         ,['total_overall_distance'         ,'DOUBLE','Total Overall Distance'         ,None,None,'']
         ,['total_overall_distance_unt'     ,'TEXT'  ,'Total Overall Distance Unit'    ,255 ,None,'']
         ,['total_overall_time'             ,'DOUBLE','Total Overall Time'             ,None,None,'']
         ,['total_overall_time_unt'         ,'TEXT'  ,'Total Overall Time Unit'        ,255 ,None,'']
         
         ,['total_road_distance'            ,'DOUBLE','Total Road Distance'            ,None,None,'']
         ,['total_road_distance_unt'        ,'TEXT'  ,'Total Road Distance Unit'       ,255 ,None,'']
         ,['total_road_time'                ,'DOUBLE','Total Road Time'                ,None,None,'']
         ,['total_road_time_unt'            ,'TEXT'  ,'Total Road Time Unit'           ,255 ,None,'']
         
         ,['total_rail_distance'            ,'DOUBLE','Total Rail Distance'            ,None,None,'']
         ,['total_rail_distance_unt'        ,'TEXT'  ,'Total Rail Distance Unit'       ,255 ,None,'']
         ,['total_rail_time'                ,'DOUBLE','Total Rail Time'                ,None,None,'']
         ,['total_rail_time_unt'            ,'TEXT'  ,'Total Rail Time Unit'           ,255 ,None,'']
         
         ,['total_station_count'            ,'LONG'  ,'Total Station Count'            ,None,None,'']
         
         ,['average_overall_speed'          ,'DOUBLE','Average_Overall_Speed'          ,None,None,'']
         ,['average_road_speed'             ,'DOUBLE','Average_Road_Speed'             ,None,None,'']
         ,['average_rail_speed'             ,'DOUBLE','Average_Rail_Speed'             ,None,None,'']
         ,['speed_unit'                     ,'TEXT'  ,'Speed_Unit'                     ,255 ,None,'']
         
         ,['facility_typeid'                ,'LONG'  ,'Facility_TypeID'                ,None,None,'']
         ,['facility_subtypeids'            ,'TEXT'  ,'Facility_SubtypeIDs'            ,255, None,'']
         ,['facility_name'                  ,'TEXT'  ,'Facility_Name'                  ,255, None,'']
         ,['facility_address'               ,'TEXT'  ,'Facility_Addres'                ,255, None,'']
         ,['facility_city'                  ,'TEXT'  ,'Facility_City'                  ,255, None,'']
         ,['facility_state'                 ,'TEXT'  ,'Facility_State'                 ,255, None,'']
         ,['facility_zip'                   ,'TEXT'  ,'Facility_Zip'                   ,255, None,'']
         ,['facility_telephone'             ,'TEXT'  ,'Facility_Telephone'             ,255, None,'']
         ,['facility_waste_mgt'             ,'TEXT'  ,'Facility_Waste_Mgt'             ,255, None,'']
         
         ,['facility_dly_cap'               ,'DOUBLE','Facility Daily Capacity'        ,None,None,'']
         ,['facility_dly_cap_unt'           ,'TEXT'  ,'Facility Daily Capacity Unit'   ,255 ,None,'']
         
         ,['facility_qty_accepted'          ,'DOUBLE','Facility_Qty_Accepted'          ,None,None,'']
         ,['facility_qty_accepted_unt'      ,'TEXT'  ,'Facility_Qty_Accepted_Unit'     ,255 ,None,'']
         
         ,['allocated_amount'               ,'DOUBLE','Allocated_Amount'               ,None,None,'']
         ,['allocated_amount_unt'           ,'TEXT'  ,'Allocated_Amount_Unit'          ,255 ,None,'']
         
         ,['number_of_road_shipments'       ,'LONG'  ,'Number Of Road Shipments'       ,None,None,'']
         ,['number_of_rail_shipments'       ,'LONG'  ,'Number Of Rail Shipments'       ,None,None,'']
         
         ,['road_cplm_cost_usd'             ,'DOUBLE','Road CPLM Cost USD'             ,None,None,'']
         ,['rail_cplm_cost_usd'             ,'DOUBLE','Rail CPLM Cost USD'             ,None,None,'']
         
         ,['road_fixed_cost_usd_per_contnr' ,'DOUBLE','Road Fixed Cost USD Per Container',None,None,'']
         ,['rail_fixed_cost_usd_per_contnr' ,'DOUBLE','Rail Fixed Cost USD Per Container',None,None,'']
         
         ,['road_fixed_cost_usd_per_hour'   ,'DOUBLE','Road Fixed Cost USD Per Hour'   ,None,None,'']
         ,['rail_fixed_cost_usd_per_hour'   ,'DOUBLE','Rail Fixed Cost USD Per Hour'   ,None,None,'']
         
         ,['road_fixed_cost_usd_by_volume'  ,'DOUBLE','Road Fixed Cost USD By Volume'  ,None,None,'']
         ,['rail_fixed_cost_usd_by_volume'  ,'DOUBLE','Rail Fixed Cost USD By Volume'  ,None,None,'']
         
         ,['road_tolls_usd_per_shipment'    ,'DOUBLE','Road Tolls ($)'                 ,None,None,'']
         
         ,['road_misc_trans_cost_usd'       ,'DOUBLE','Road Misc Trans Cost ($)'       ,None,None,'']
         ,['rail_misc_trans_cost_usd'       ,'DOUBLE','Rail Misc Trans Cost ($)'       ,None,None,'']
         
         ,['road_trans_cost_usd'            ,'DOUBLE','Road Trans Cost ($)'            ,None,None,'']
         ,['rail_trans_cost_usd'            ,'DOUBLE','Rail Trans Cost ($)'            ,None,None,'']
         
         ,['staging_site_cost_usd'          ,'DOUBLE','Staging Site Cost ($)'          ,None,None,'']
         
         ,['disposal_cost_usd'              ,'DOUBLE','Disposal Cost ($)'              ,None,None,'']
         
         ,['road_labor_cost_usd'            ,'DOUBLE','Road Labor Cost ($)'            ,None,None,'']
         ,['rail_labor_cost_usd'            ,'DOUBLE','Rail Labor Cost ($)'            ,None,None,'']
         
         ,['road_transp_decon_cost_usd'     ,'DOUBLE','Road Transporter Decon Cost ($)',None,None,'']
         ,['rail_transp_decon_cost_usd'     ,'DOUBLE','Rail Transporter Decon Cost ($)',None,None,'']
         
         ,['cost_multiplier_usd'            ,'DOUBLE','Cost Multiplier ($)'            ,None,None,'']
         
         ,['total_cost_usd'                 ,'DOUBLE','Total Cost ($)'                 ,None,None,'']
         
         ,['road_transp_time_to_comp_days'  ,'DOUBLE','Road Transporter Time To Comp Days' ,None,None,'']
         ,['rail_transp_time_to_comp_days'  ,'DOUBLE','Rail Transporter Time To Comp Days' ,None,None,'']
         ,['total_transp_time_to_comp_days' ,'DOUBLE','Total Transporter Time To Comp Days',None,None,'']
         
         ,['road_dest_time_to_comp_days'    ,'DOUBLE','Road Destination Time To Comp Days' ,None,None,'']
         ,['rail_dest_time_to_comp_days'    ,'DOUBLE','Rail Destination Time To Comp Days' ,None,None,'']
         ,['total_dest_time_to_comp_days'   ,'DOUBLE','Total Destination Time To Comp Days',None,None,'']
         
         ,['time_days'                      ,'DOUBLE','Time Days'                      ,None,None,'']
         
         ,['username'                       ,'TEXT'  ,'UserName'                       ,None,None,'']
         ,['creationtime'                   ,'DATE'  ,'CreationTime'                   ,None,None,'']
       ]
   );
   
   arcpy.management.AddIndex(
       in_table   = "ScenarioResults"
      ,fields     = 'scenarioid'
      ,index_name = 'scenarioid_idx'
   );
   
   arcpy.AddMessage("  ScenarioResults feature class created.");

   ############################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
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
          ['scenarioid'                 ,'TEXT'  ,'ScenarioID'                  ,255, None,'']
         ,['waste_type'                 ,'TEXT'  ,'Waste_Type'                  ,255, None,'']
         ,['waste_medium'               ,'TEXT'  ,'Waste_Medium'                ,255, None,'']
         ,['waste_amount'               ,'DOUBLE','Waste_Amount'                ,None,None,'']
         ,['waste_unit'                 ,'TEXT'  ,'Waste_Unit'                  ,255, None,'']
         ,['numberoffacilitiestofind'   ,'LONG'  ,'NumberOfFacilitiesToFind'    ,None,None,'']
         ,['route_count_requested'      ,'LONG'  ,'Route_Count_Requested'       ,None,None,'']
         ,['route_count_returned'       ,'LONG'  ,'Route_Count_Returned'        ,None,None,'']
         ,['map_image'                  ,'TEXT'  ,'Map_Image'                   ,255, None,'']
         ,['conditionid'                ,'TEXT'  ,'ConditionID'                 ,255, None,'']
         ,['factorid'                   ,'TEXT'  ,'FactorID'                    ,255, None,'']
         ,['facilityattributesid'       ,'TEXT'  ,'Facility Attributes ID'      ,255, None,'']
         ,['road_transporter_attributes','TEXT'  ,'Road Transporter Attributes' ,255, None,'']
         ,['rail_transporter_attributes','TEXT'  ,'Rail Transporter Attributes' ,255, None,'']
       ]
   );
   arcpy.AddMessage("  Scenario table created.");

   ############################################################################
   arcpy.CreateFeatureclass_management(
       out_path          = aprx.defaultGeodatabase
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
          ['current_unit_system'                    ,'TEXT'  ,'Current Unit System'                    ,None,None,'']
         ,['current_scenarioid'                     ,'TEXT'  ,'Current ScenarioID'                     ,255, None,'']
         ,['current_conditionid'                    ,'TEXT'  ,'Current ConditionID'                    ,255, None,'']
         ,['current_factorid'                       ,'TEXT'  ,'Current FactorID'                       ,255, None,'']
         ,['current_facilityattributesid'           ,'TEXT'  ,'Current Facility Attributes ID'         ,255, None,'']
         ,['current_road_transporter'               ,'TEXT'  ,'Current Road Transporter ID'            ,255, None,'']
         ,['current_rail_transporter'               ,'TEXT'  ,'Current Rail Transporter ID'            ,255, None,'']
         ,['network_dataset'                        ,'TEXT'  ,'Network Dataset'                        ,2000,None,'']
         ,['nd_travel_mode'                         ,'TEXT'  ,'Network Travel Mode'                    ,255, None,'']
         ,['nd_impedance_field'                     ,'TEXT'  ,'Network Impedance Field'                ,255, None,'']
         ,['nd_overall_distance_field'              ,'TEXT'  ,'Network Overall Distance Field'         ,255, None,'']
         ,['nd_overall_distance_unt'                ,'TEXT'  ,'Network Overall Distance Unit'          ,255, None,'']
         ,['nd_overall_time_field'                  ,'TEXT'  ,'Network Overall Time Field'             ,255, None,'']
         ,['nd_overall_time_unt'                    ,'TEXT'  ,'Network Overall Time Unit'              ,255, None,'']
         ,['nd_road_distance_field'                 ,'TEXT'  ,'Network Road Distance Field'            ,255, None,'']
         ,['nd_road_distance_unt'                   ,'TEXT'  ,'Network Road Distance Unit'             ,255, None,'']
         ,['nd_road_time_field'                     ,'TEXT'  ,'Network Road Time Field'                ,255, None,'']
         ,['nd_road_time_unt'                       ,'TEXT'  ,'Network Road Time Unit'                 ,255, None,'']
         ,['nd_rail_distance_field'                 ,'TEXT'  ,'Network Rail Distance Field'            ,255, None,'']
         ,['nd_rail_distance_unt'                   ,'TEXT'  ,'Network Rail Distance Unit'             ,255, None,'']
         ,['nd_rail_time_field'                     ,'TEXT'  ,'Network Rail Time Field'                ,255, None,'']
         ,['nd_rail_time_unt'                       ,'TEXT'  ,'Network Rail Time Unit'                 ,255, None,'']
         ,['nd_station_count_field'                 ,'TEXT'  ,'Network Station Count Field'            ,255, None,'']
         ,['isAGO'                                  ,'TEXT'  ,'is ArcGIS Online Routing'               ,255, None,'']
         ,['maximum_facilities_to_find'             ,'LONG'  ,'Maximum Facilities To Find'             ,255, None,'']
         ,['settings_last_updated_date'             ,'TEXT'  ,'Settings Last Updated Date'             ,255, None,'']
         ,['settings_last_updated_by'               ,'TEXT'  ,'Settings Last Updated By'               ,255, None,'']
       ]
   );
   arcpy.AddMessage("  SystemCache feature class created.");

   #########################################################################
   # Step 80
   # Load config defaults
   #########################################################################
   z = source.gp_ReloadProjectSettings.load_settings(
       aprx
      ,unit_system
      ,net_source_str
      ,travel_mode
      ,impedance_field
      ,overall_dist_fld
      ,overall_dist_unt
      ,overall_time_fld
      ,overall_time_unt
      ,road_dist_fld
      ,road_dist_unt
      ,road_time_fld
      ,road_time_unt
      ,rail_dist_fld
      ,rail_dist_unt
      ,rail_time_fld
      ,rail_time_unt
      ,station_cnt_fld
      ,isAGO
      ,maximum_facilities_to_find
   );

   #########################################################################
   # Step 90
   # Create the Folder Group for items and add incident and support area fcs
   #########################################################################
   arcpy.AddMessage("  Adding Folder Layer.");
   fld = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","Folder.lyrx"));
   grp = fld.listLayers("Folder")[0];
   grp.name = "AllHazardsWasteLogisticsTool";
   map.addLayer(grp,"TOP");
   grp = map.listLayers("AllHazardsWasteLogisticsTool")[0];

   arcpy.AddMessage("  Adding Settings Layer.");
   fld = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","Settings.lyrx"));
   stl = fld.listLayers("Folder")[0];
   stl.name = "Settings";
   map.addLayerToGroup(grp,stl,"TOP");
   stl = map.listLayers("Settings")[0];

   arcpy.AddMessage("  Adding SystemCache Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","SystemCache.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(stl,lyr,"TOP");

   arcpy.AddMessage("  Adding Conditions Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","Conditions.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(stl,lyr,"TOP");

   arcpy.AddMessage("  Adding Scenario Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","Scenario.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(stl,lyr,"TOP");
   
   arcpy.AddMessage("  Adding Modes Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","Modes.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(stl,lyr,"TOP");
   
   arcpy.AddMessage("  Adding Transporters Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","Transporters.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(stl,lyr,"TOP");

   arcpy.AddMessage("  Adding CPLMUnitRates Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","CPLMUnitRates.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(stl,lyr,"TOP");

   arcpy.AddMessage("  Adding FixedTransCost Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","FixedTransCost.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(stl,lyr,"TOP");

   arcpy.AddMessage("  Adding LaborCosts Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","LaborCosts.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(stl,lyr,"TOP");

   arcpy.AddMessage("  Adding DisposalFees Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","DisposalFees.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(stl,lyr,"TOP");
   
   arcpy.AddMessage("  Adding FacilityCapacities Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","FacilityCapacities.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(stl,lyr,"TOP");

   arcpy.AddMessage("  Adding ScenarioResults Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","ScenarioResults.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(grp,lyr,"TOP");

   arcpy.AddMessage("  Adding IncidentArea Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","IncidentArea.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(grp,lyr,"TOP");

   arcpy.AddMessage("  Adding SupportArea Layer.");
   lyr = arcpy.mp.LayerFile(os.path.join(source.util.g_pn,"resources","SupportArea.lyrx"));
   lyr.updateConnectionProperties(
       lyr.listLayers('*')[0].connectionProperties['connection_info']['database']
      ,aprx.defaultGeodatabase
   );
   map.addLayerToGroup(grp,lyr,"TOP");

   #########################################################################
   # Step 100
   # Grind up the network layer and add rendering to the new item
   #########################################################################
   arcpy.AddMessage("  Grinding on Network Layer.");
   lyrx_style  = os.path.join(source.util.g_pn,"resources","Network.lyrx");
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
   chk = False;
   for lyr in map.listLayers():
      if lyr.name == "Scenario":
         chk = True;
   
   if not chk:
      raise arcpy.ExecuteError('layers not found');
      
   del net;
   
   return;
