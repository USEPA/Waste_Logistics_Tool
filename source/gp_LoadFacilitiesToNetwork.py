import arcpy,os,sys;

import source.util;
import source.obj_AllHazardsWasteLogisticsTool;
import source.obj_QuerySet;

###############################################################################
import importlib
importlib.reload(source.util);
importlib.reload(source.obj_AllHazardsWasteLogisticsTool);
importlib.reload(source.obj_QuerySet);

def execute(self,parameters,messages):

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
   subtype_text = parameters[2].valueAsText;
   
   if parameters[3].valueAsText == "true":
      loadDefaultFacilities = True;
   else:
      loadDefaultFacilities = False;

   if parameters[4].value is None:
      ary_user_defined = None;
      loadUserDefined  = False;
   else:
      a = parameters[4].valueAsText;
      b = a.split(';');
      ary_user_defined = [i.replace("'","") for i in b ]
      loadUserDefined  = True;

   if parameters[5].valueAsText == "true":
      limitBySupport = True;
   else:
      limitBySupport = False;

   if parameters[6].valueAsText == "true":
      truncateFacilities = "CLEAR";
   else:
      truncateFacilities = "APPEND";
      
   override_incident_search_tolerance = parameters[7].value;
   override_facility_search_tolerance = parameters[8].value;
      
   #########################################################################
   # Step 30
   # Initialize the haz toc object
   #########################################################################
   haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

   (
       scenarioid
      ,unit_system
      ,waste_type
      ,waste_medium
      ,waste_amount
      ,waste_unit
   ) = haz.current_scenario();
   
   subtype_list = haz.waste.semicolontxt2subtypeids(subtype_text);
   
   #########################################################################
   # Step 40 
   # Load the incidents as requested
   #########################################################################
   incident_temp = arcpy.CreateScratchName(
       "Incident_Centroid"
      ,""
      ,"FeatureClass"
      ,arcpy.env.scratchGDB
   );
   
   source.util.polygons_to_points(
       in_features       = haz.incident_area.dataSource
      ,out_feature_class = incident_temp
   );
   
   str_fm = "Name Name #;"              \
          + "CurbApproach # 0;"         \
          + "Attr_Minutes # 0;"         \
          + "Attr_TravelTime # 0;"      \
          + "Attr_Miles # 0;"           \
          + "Attr_Kilometers # 0;"      \
          + "Attr_TimeAt1KPH # 0;"      \
          + "Attr_WalkTime # 0;"        \
          + "Attr_TruckMinutes # 0;"    \
          + "Attr_TruckTravelTime # 0;" \
          + "Cutoff_Minutes # #;"       \
          + "Cutoff_TravelTime # #;"    \
          + "Cutoff_Miles # #;"         \
          + "Cutoff_Kilometers # #;"    \
          + "Cutoff_TimeAt1KPH # #;"    \
          + "Cutoff_WalkTime # #;"      \
          + "Cutoff_TruckMinutes # #;"  \
          + "Cutoff_TruckTravelTime # #";               
   
   arcpy.na.AddLocations(
       in_network_analysis_layer      = haz.network.lyr()
      ,sub_layer                      = haz.network.incidents.name
      ,in_table                       = incident_temp
      ,field_mappings                 = str_fm
      ,search_tolerance               = override_incident_search_tolerance
      ,sort_field                     = None
      ,search_criteria                = None
      ,match_type                     = None
      ,append                         = False
      ,snap_to_position_along_network = None
      ,snap_offset                    = None
      ,exclude_restricted_elements    = None
      ,search_query                   = None
   );
   
   arcpy.AddMessage("  Network Incidents Layer loaded.");

   #########################################################################
   # Step 40
   # Generate the waste acceptance where clause
   #########################################################################
   filter_RAD_accepted     = False;
   filter_LARWRad_accepted = False;
   filter_HW_accepted      = False;
   filter_MSW_accepted     = False;
   filter_C_D_accepted     = False;
   filter_NHAW_accepted    = False;
   
   if  waste_type in ['Radioactive: Contact-Handled','Radioactive: Remote-Handled']:
      filter_RAD_accepted     = True;
   elif waste_type == 'Low-Activity Radioactive Waste':
      filter_LARWRad_accepted = True;
   elif waste_type == 'Hazardous':
      filter_HW_accepted      = True;
   elif waste_type == 'Municipal Solid Waste (MSW)':
      filter_MSW_accepted     = True;
   elif waste_type == 'Construction and Demolition':
      filter_C_D_accepted     = True;
   elif waste_type == 'Non-Hazardous Aqueous Waste':
      filter_NHAW_accepted    = True;
   else:
      raise Exception('err: ' + str(waste_type));

   #########################################################################
   # Step 50
   # Check if the Support Area has content
   #########################################################################
   if limitBySupport:
      if haz.support_area.recordCount() == 0:
         limitBySupport = False;

   #########################################################################
   # Step 60
   # Truncate facility layer if requested
   #########################################################################
   if truncateFacilities == "CLEAR":
      arcpy.AddMessage("Truncating Existing Facilities.");
      arcpy.TruncateTable_management(haz.network.facilities.dataSource);

   #########################################################################
   # Step 70
   # Create facility loader scratch fc
   #########################################################################
   if loadDefaultFacilities or                                             \
   (ary_user_defined is not None and len(ary_user_defined) > 0):

      scratch_ldr = arcpy.CreateScratchName(
          "Facility_Loader"
         ,""
         ,"FeatureClass"
         ,arcpy.env.scratchGDB
      );
      scratch_ldr_path,scratch_ldr_name = os.path.split(scratch_ldr);

      arcpy.CreateFeatureclass_management(
          out_path          = scratch_ldr_path
         ,out_name          = scratch_ldr_name
         ,geometry_type     = "POINT"
         ,has_m             = "DISABLED"
         ,has_z             = "DISABLED"
         ,spatial_reference = arcpy.SpatialReference(4326)
         ,config_keyword    = None
      );

      arcpy.management.AddFields(
          scratch_ldr
         ,[
             ['facility_identifier'             ,'TEXT'  ,'Facility_Identifier'                          ,255, None,'']
            ,['facility_typeid'                 ,'LONG'  ,'Facility Type ID'                             ,None,None,'']
            ,['facility_subtypeids'             ,'TEXT'  ,'Facility_SubtypeIDs'                          ,255, None,'']
            ,['facility_name'                   ,'TEXT'  ,'Facility_Name'                                ,255, None,'']
            ,['facility_address'                ,'TEXT'  ,'Facility_Addres'                              ,255, None,'']
            ,['facility_city'                   ,'TEXT'  ,'Facility_City'                                ,255, None,'']
            ,['facility_state'                  ,'TEXT'  ,'Facility_State'                               ,255, None,'']
            ,['facility_zip'                    ,'TEXT'  ,'Facility_Zip'                                 ,255, None,'']
            ,['facility_telephone'              ,'TEXT'  ,'Facility_Telephone'                           ,255, None,'']
            ,['front_gate_longitude'            ,'DOUBLE','Front_Gate_Longitude'                         ,None,None,'']
            ,['front_gate_latitude'             ,'DOUBLE','Front_Gate_Latitude'                          ,None,None,'']
            ,['facility_waste_mgt'              ,'TEXT'  ,'Facility_Waste_Mgt'                           ,255 ,None,'']
            
            ,['facility_accepts_no_waste'       ,'TEXT'  ,'Facility Accepts No Waste Flag'                                             ,255 ,None,'']
            ,['fac_radc_solid_dly_cap'          ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Solid Daily Capacity'          ,None,None,'']
            ,['fac_radc_solid_dly_cap_unt'      ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Solid Daily Capacity Unit'     ,255 ,None,'']
            ,['fac_radc_liquid_dly_cap'         ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Liquid Daily Capacity'         ,None,None,'']
            ,['fac_radc_liquid_dly_cap_unt'     ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Liquid Daily Capacity Unit'    ,255 ,None,'']
            ,['fac_radr_solid_dly_cap'          ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Solid Daily Capacity'           ,None,None,'']
            ,['fac_radr_solid_dly_cap_unt'      ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Solid Daily Capacity Unit'      ,255 ,None,'']
            ,['fac_radr_liquid_dly_cap'         ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Liquid Daily Capacity'          ,None,None,'']
            ,['fac_radr_liquid_dly_cap_unt'     ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Liquid Daily Capacity Unit'     ,255 ,None,'']
            ,['fac_larw_solid_dly_cap'          ,'DOUBLE','Facility Low-Activity Radioactive Waste Volume Solid Daily Capacity'        ,None,None,'']
            ,['fac_larw_solid_dly_cap_unt'      ,'TEXT'  ,'Facility Low-Activity Radioactive Waste Volume Solid Daily Capacity Unit'   ,255 ,None,'']
            ,['fac_haz_solid_dly_cap'           ,'DOUBLE','Facility Hazardous Volume Solid Daily Capacity'                             ,None,None,'']
            ,['fac_haz_solid_dly_cap_unt'       ,'TEXT'  ,'Facility Hazardous Volume Solid Daily Capacity Unit'                        ,255 ,None,'']
            ,['fac_haz_liquid_dly_cap'          ,'DOUBLE','Facility Hazardous Volume Liquid Daily Capacity'                            ,None,None,'']
            ,['fac_haz_liquid_dly_cap_unt'      ,'TEXT'  ,'Facility Hazardous Volume Liquid Daily Capacity Unit'                       ,255 ,None,'']
            ,['fac_msw_solid_dly_cap'           ,'DOUBLE','Facility Municipal Solid Waste (MSW) Volume Solid Daily Capacity'           ,None,None,'']
            ,['fac_msw_solid_dly_cap_unt'       ,'TEXT'  ,'Facility Municipal Solid Waste (MSW) Volume Solid Daily Capacity Unit'      ,255 ,None,'']
            ,['fac_cad_solid_dly_cap'           ,'DOUBLE','Facility Construction and Demolition Volume Solid Daily Capacity'           ,None,None,'']
            ,['fac_cad_solid_dly_cap_unt'       ,'TEXT'  ,'Facility Construction and Demolition Volume Solid Daily Capacity Unit'      ,255 ,None,'']
            ,['fac_nhaq_liquid_dly_cap'         ,'DOUBLE','Facility Non-Hazardous Aqueous Waste Volume Liquid Daily Capacity'          ,None,None,'']
            ,['fac_nhaq_liquid_dly_cap_unt'     ,'TEXT'  ,'Facility Non-Hazardous Aqueous Waste Volume Liquid Daily Capacity Unit'     ,255 ,None,'']
            ,['fac_radc_solid_tot_acp'          ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Solid Total Acceptance'        ,None,None,'']
            ,['fac_radc_solid_tot_acp_unt'      ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Solid Total Acceptance Unit'   ,255 ,None,'']
            ,['fac_radc_liquid_tot_acp'         ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Liquid Total Acceptance'       ,None,None,'']
            ,['fac_radc_liquid_tot_acp_unt'     ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Liquid Total Acceptance Unit'  ,255 ,None,'']
            ,['fac_radr_solid_tot_acp'          ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Solid Total Acceptance'         ,None,None,'']
            ,['fac_radr_solid_tot_acp_unt'      ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Solid Total Acceptance Unit'    ,255 ,None,'']
            ,['fac_radr_liquid_tot_acp'         ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Liquid Total Acceptance'        ,None,None,'']
            ,['fac_radr_liquid_tot_acp_unt'     ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Liquid Total Acceptance Unit'   ,255 ,None,'']
            ,['fac_larw_solid_tot_acp'          ,'DOUBLE','Facility Low-Activity Radioactive Waste Volume Solid Total Acceptance'     ,None,None,'']
            ,['fac_larw_solid_tot_acp_unt'      ,'TEXT'  ,'Facility Low-Activity Radioactive Waste Volume Solid Total Acceptance Unit',255 ,None,'']
            ,['fac_haz_solid_tot_acp'           ,'DOUBLE','Facility Hazardous Volume Solid Total Acceptance'                           ,None,None,'']
            ,['fac_haz_solid_tot_acp_unt'       ,'TEXT'  ,'Facility Hazardous Volume Solid Total Acceptance Unit'                      ,255 ,None,'']
            ,['fac_haz_liquid_tot_acp'          ,'DOUBLE','Facility Hazardous Volume Liquid Total Acceptance'                          ,None,None,'']
            ,['fac_haz_liquid_tot_acp_unt'      ,'TEXT'  ,'Facility Hazardous Volume Liquid Total Acceptance Unit'                     ,255 ,None,'']
            ,['fac_msw_solid_tot_acp'           ,'DOUBLE','Facility Municipal Solid Waste (MSW) Volume Solid Total Acceptance'         ,None,None,'']
            ,['fac_msw_solid_tot_acp_unt'       ,'TEXT'  ,'Facility Municipal Solid Waste (MSW) Volume Solid Total Acceptance Unit'    ,255 ,None,'']
            ,['fac_cad_solid_tot_acp'           ,'DOUBLE','Facility Construction and Demolition Volume Solid Total Acceptance'         ,None,None,'']
            ,['fac_cad_solid_tot_acp_unt'       ,'TEXT'  ,'Facility Construction and Demolition Volume Solid Total Acceptance Unit'    ,255 ,None,'']
            ,['fac_nhaq_liquid_tot_acp'         ,'DOUBLE','Facility Non-Hazardous Aqueous Waste Volume Liquid Total Acceptance'        ,None,None,'']
            ,['fac_nhaq_liquid_tot_acp_unt'     ,'TEXT'  ,'Facility Non-Hazardous Aqueous Waste Volume Liquid Total Acceptance Unit'   ,255 ,None,'']
            ,['fac_radc_solid_dis_fee'          ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Solid Disposal Fees'           ,None,None,'']
            ,['fac_radc_solid_dis_fee_unt'      ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Solid Disposal Fees Unit'      ,255 ,None,'']
            ,['fac_radc_liquid_dis_fee'         ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Liquid Disposal Fees'          ,None,None,'']
            ,['fac_radc_liquid_dis_fee_unt'     ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Liquid Disposal Fees Unit'     ,255 ,None,'']
            ,['fac_radr_solid_dis_fee'          ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Solid Disposal Fees'            ,None,None,'']
            ,['fac_radr_solid_dis_fee_unt'      ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Solid Disposal Fees Unit'       ,255 ,None,'']
            ,['fac_radr_liquid_dis_fee'         ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Liquid Disposal Fees'           ,None,None,'']
            ,['fac_radr_liquid_dis_fee_unt'     ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Liquid Disposal Fees Unit'      ,255 ,None,'']
            ,['fac_larw_solid_dis_fee'          ,'DOUBLE','Facility Low-Activity Radioactive Waste Volume Solid Disposal Fees'         ,None,None,'']
            ,['fac_larw_solid_dis_fee_unt'      ,'TEXT'  ,'Facility Low-Activity Radioactive Waste Volume Solid Disposal Fees Unit'    ,255 ,None,'']
            ,['fac_haz_solid_dis_fee'           ,'DOUBLE','Facility Hazardous Volume Solid Disposal Fees'                              ,None,None,'']
            ,['fac_haz_solid_dis_fee_unt'       ,'TEXT'  ,'Facility Hazardous Volume Solid Disposal Fees Unit'                         ,255 ,None,'']
            ,['fac_haz_liquid_dis_fee'          ,'DOUBLE','Facility Hazardous Volume Liquid Disposal Fees'                             ,None,None,'']
            ,['fac_haz_liquid_dis_fee_unt'      ,'TEXT'  ,'Facility Hazardous Volume Liquid Disposal Fees Unit'                        ,255 ,None,'']
            ,['fac_msw_solid_dis_fee'           ,'DOUBLE','Facility Municipal Solid Waste (MSW) Volume Solid Disposal Fees'            ,None,None,'']
            ,['fac_msw_solid_dis_fee_unt'       ,'TEXT'  ,'Facility Municipal Solid Waste (MSW) Volume Solid Disposal Fees Unit'       ,255 ,None,'']
            ,['fac_cad_solid_dis_fee'           ,'DOUBLE','Facility Construction and Demolition Volume Solid Disposal Fees'            ,None,None,'']
            ,['fac_cad_solid_dis_fee_unt'       ,'TEXT'  ,'Facility Construction and Demolition Volume Solid Disposal Fees Unit'       ,255 ,None,'']
            ,['fac_nhaq_liquid_dis_fee'         ,'DOUBLE','Facility Non-Hazardous Aqueous Waste Volume Liquid Disposal Fees'           ,None,None,'']
            ,['fac_nhaq_liquid_dis_fee_unt'     ,'TEXT'  ,'Facility Non-Hazardous Aqueous Waste Volume Liquid Disposal Fees Unit'      ,255 ,None,'']
 
            ,['C_D_accepted'                    ,'TEXT'  ,'C_D_Accepted'                                 ,255 ,None,'']
            ,['MSW_accepted'                    ,'TEXT'  ,'MSW_Accepted'                                 ,255 ,None,'']
            ,['HW_accepted'                     ,'TEXT'  ,'HW_Accepted'                                  ,255 ,None,'']
            ,['LARWRad_accepted'                ,'TEXT'  ,'LARWRad_Accepted'                             ,255 ,None,'']
            ,['RAD_accepted'                    ,'TEXT'  ,'RAD_Accepted'                                 ,255 ,None,'']
            ,['NHAW_accepted'                   ,'TEXT'  ,'NHAW_Accepted'                                ,255 ,None,'']
            
            ,['date_stamp'                      ,'TEXT'  ,'Date_Stamp'                                   ,255 ,None,'']
            ,['source'                          ,'TEXT'  ,'Source'                                       ,255 ,None,'']
            ,['notes'                           ,'TEXT'  ,'Notes'                                        ,255 ,None,'']
         ]
      );
      arcpy.AddMessage("  Scratch loading table created.");

   #########################################################################
   # Step 80
   # Load I-Waste Facilities if requested
   #########################################################################
   if loadDefaultFacilities:
      fc = os.path.join(source.util.g_pn,"data","IWasteFacilities.json");
      if not os.path.exists(fc):
         raise arcpy.ExecuteError("Error.  IWasteFacilities.json not found.");

      scratch_geo = arcpy.CreateScratchName(
          "Load_GeoJSON"
         ,""
         ,"FeatureClass"
         ,arcpy.env.scratchGDB
      );

      arcpy.env.outputMFlag = "Disabled";
      arcpy.env.outputZFlag = "Disabled";

      arcpy.JSONToFeatures_conversion(
          fc
         ,scratch_geo
         ,"POINT"
      );
      count = int(arcpy.GetCount_management(scratch_geo).getOutput(0));
      arcpy.AddMessage("  Total I-Waste Facilities loaded from GeoJSON: " + str(count));

      scratch_src = arcpy.CreateScratchName(
          "Load_Source"
         ,""
         ,"FeatureClass"
         ,arcpy.env.scratchGDB
      );
      scratch_src_path,scratch_src_name = os.path.split(scratch_src);

      arcpy.CreateFeatureclass_management(
          out_path          = scratch_src_path
         ,out_name          = scratch_src_name
         ,geometry_type     = "POINT"
         ,has_m             = "DISABLED"
         ,has_z             = "DISABLED"
         ,spatial_reference = arcpy.SpatialReference(4326)
         ,config_keyword    = None
      );

      arcpy.management.AddFields(
          scratch_src
         ,[
             ['facility_identifier'             ,'TEXT'  ,'Facility_Identifier'                          ,255, None,'']
            ,['facility_typeid'                 ,'LONG'  ,'Facility Type ID'                             ,None,None,'']
            ,['facility_subtypeids'             ,'TEXT'  ,'Facility_SubtypeIDs'                          ,255, None,'']
            ,['facility_name'                   ,'TEXT'  ,'Facility_Name'                                ,255, None,'']
            ,['facility_address'                ,'TEXT'  ,'Facility_Addres'                              ,255, None,'']
            ,['facility_city'                   ,'TEXT'  ,'Facility_City'                                ,255, None,'']
            ,['facility_state'                  ,'TEXT'  ,'Facility_State'                               ,255, None,'']
            ,['facility_zip'                    ,'TEXT'  ,'Facility_Zip'                                 ,255, None,'']
            ,['facility_telephone'              ,'TEXT'  ,'Facility_Telephone'                           ,255, None,'']
            ,['front_gate_longitude'            ,'DOUBLE','Front_Gate_Longitude'                         ,None,None,'']
            ,['front_gate_latitude'             ,'DOUBLE','Front_Gate_Latitude'                          ,None,None,'']
            ,['facility_waste_mgt'              ,'TEXT'  ,'Facility_Waste_Mgt'                           ,255 ,None,'']

            ,['facility_accepts_no_waste'       ,'TEXT'  ,'Facility Accepts No Waste Flag'                                             ,255 ,None,'']
            ,['fac_radc_solid_dly_cap'          ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Solid Daily Capacity'          ,None,None,'']
            ,['fac_radc_solid_dly_cap_unt'      ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Solid Daily Capacity Unit'     ,255 ,None,'']
            ,['fac_radc_liquid_dly_cap'         ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Liquid Daily Capacity'         ,None,None,'']
            ,['fac_radc_liquid_dly_cap_unt'     ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Liquid Daily Capacity Unit'    ,255 ,None,'']
            ,['fac_radr_solid_dly_cap'          ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Solid Daily Capacity'           ,None,None,'']
            ,['fac_radr_solid_dly_cap_unt'      ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Solid Daily Capacity Unit'      ,255 ,None,'']
            ,['fac_radr_liquid_dly_cap'         ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Liquid Daily Capacity'          ,None,None,'']
            ,['fac_radr_liquid_dly_cap_unt'     ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Liquid Daily Capacity Unit'     ,255 ,None,'']
            ,['fac_larw_solid_dly_cap'          ,'DOUBLE','Facility Low-Activity Radioactive Waste Volume Solid Daily Capacity'        ,None,None,'']
            ,['fac_larw_solid_dly_cap_unt'      ,'TEXT'  ,'Facility Low-Activity Radioactive Waste Volume Solid Daily Capacity Unit'   ,255 ,None,'']
            ,['fac_haz_solid_dly_cap'           ,'DOUBLE','Facility Hazardous Volume Solid Daily Capacity'                             ,None,None,'']
            ,['fac_haz_solid_dly_cap_unt'       ,'TEXT'  ,'Facility Hazardous Volume Solid Daily Capacity Unit'                        ,255 ,None,'']
            ,['fac_haz_liquid_dly_cap'          ,'DOUBLE','Facility Hazardous Volume Liquid Daily Capacity'                            ,None,None,'']
            ,['fac_haz_liquid_dly_cap_unt'      ,'TEXT'  ,'Facility Hazardous Volume Liquid Daily Capacity Unit'                       ,255 ,None,'']
            ,['fac_msw_solid_dly_cap'           ,'DOUBLE','Facility Municipal Solid Waste (MSW) Volume Solid Daily Capacity'           ,None,None,'']
            ,['fac_msw_solid_dly_cap_unt'       ,'TEXT'  ,'Facility Municipal Solid Waste (MSW) Volume Solid Daily Capacity Unit'      ,255 ,None,'']
            ,['fac_cad_solid_dly_cap'           ,'DOUBLE','Facility Construction and Demolition Volume Solid Daily Capacity'           ,None,None,'']
            ,['fac_cad_solid_dly_cap_unt'       ,'TEXT'  ,'Facility Construction and Demolition Volume Solid Daily Capacity Unit'      ,255 ,None,'']
            ,['fac_nhaq_liquid_dly_cap'         ,'DOUBLE','Facility Non-Hazardous Aqueous Waste Volume Liquid Daily Capacity'          ,None,None,'']
            ,['fac_nhaq_liquid_dly_cap_unt'     ,'TEXT'  ,'Facility Non-Hazardous Aqueous Waste Volume Liquid Daily Capacity Unit'     ,255 ,None,'']
            ,['fac_radc_solid_tot_acp'          ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Solid Total Acceptance'        ,None,None,'']
            ,['fac_radc_solid_tot_acp_unt'      ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Solid Total Acceptance Unit'   ,255 ,None,'']
            ,['fac_radc_liquid_tot_acp'         ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Liquid Total Acceptance'       ,None,None,'']
            ,['fac_radc_liquid_tot_acp_unt'     ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Liquid Total Acceptance Unit'  ,255 ,None,'']
            ,['fac_radr_solid_tot_acp'          ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Solid Total Acceptance'         ,None,None,'']
            ,['fac_radr_solid_tot_acp_unt'      ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Solid Total Acceptance Unit'    ,255 ,None,'']
            ,['fac_radr_liquid_tot_acp'         ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Liquid Total Acceptance'        ,None,None,'']
            ,['fac_radr_liquid_tot_acp_unt'     ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Liquid Total Acceptance Unit'   ,255 ,None,'']
            ,['fac_larw_solid_tot_acp'          ,'DOUBLE','Facility Low-Activity Radioactive Waste Volume Solid Total Acceptance'      ,None,None,'']
            ,['fac_larw_solid_tot_acp_unt'      ,'TEXT'  ,'Facility Low-Activity Radioactive Waste Volume Solid Total Acceptance Unit' ,255 ,None,'']
            ,['fac_haz_solid_tot_acp'           ,'DOUBLE','Facility Hazardous Volume Solid Total Acceptance'                           ,None,None,'']
            ,['fac_haz_solid_tot_acp_unt'       ,'TEXT'  ,'Facility Hazardous Volume Solid Total Acceptance Unit'                      ,255 ,None,'']
            ,['fac_haz_liquid_tot_acp'          ,'DOUBLE','Facility Hazardous Volume Liquid Total Acceptance'                          ,None,None,'']
            ,['fac_haz_liquid_tot_acp_unt'      ,'TEXT'  ,'Facility Hazardous Volume Liquid Total Acceptance Unit'                     ,255 ,None,'']
            ,['fac_msw_solid_tot_acp'           ,'DOUBLE','Facility Municipal Solid Waste (MSW) Volume Solid Total Acceptance'         ,None,None,'']
            ,['fac_msw_solid_tot_acp_unt'       ,'TEXT'  ,'Facility Municipal Solid Waste (MSW) Volume Solid Total Acceptance Unit'    ,255 ,None,'']
            ,['fac_cad_solid_tot_acp'           ,'DOUBLE','Facility Construction and Demolition Volume Solid Total Acceptance'         ,None,None,'']
            ,['fac_cad_solid_tot_acp_unt'       ,'TEXT'  ,'Facility Construction and Demolition Volume Solid Total Acceptance Unit'    ,255 ,None,'']
            ,['fac_nhaq_liquid_tot_acp'         ,'DOUBLE','Facility Non-Hazardous Aqueous Waste Volume Liquid Total Acceptance'        ,None,None,'']
            ,['fac_nhaq_liquid_tot_acp_unt'     ,'TEXT'  ,'Facility Non-Hazardous Aqueous Waste Volume Liquid Total Acceptance Unit'   ,255 ,None,'']
            ,['fac_radc_solid_dis_fee'          ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Solid Disposal Fees'           ,None,None,'']
            ,['fac_radc_solid_dis_fee_unt'      ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Solid Disposal Fees Unit'      ,255 ,None,'']
            ,['fac_radc_liquid_dis_fee'         ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Liquid Disposal Fees'          ,None,None,'']
            ,['fac_radc_liquid_dis_fee_unt'     ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Liquid Disposal Fees Unit'     ,255 ,None,'']
            ,['fac_radr_solid_dis_fee'          ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Solid Disposal Fees'            ,None,None,'']
            ,['fac_radr_solid_dis_fee_unt'      ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Solid Disposal Fees Unit'       ,255 ,None,'']
            ,['fac_radr_liquid_dis_fee'         ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Liquid Disposal Fees'           ,None,None,'']
            ,['fac_radr_liquid_dis_fee_unt'     ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Liquid Disposal Fees Unit'      ,255 ,None,'']
            ,['fac_larw_solid_dis_fee'          ,'DOUBLE','Facility Low-Activity Radioactive Waste Volume Solid Disposal Fees'         ,None,None,'']
            ,['fac_larw_solid_dis_fee_unt'      ,'TEXT'  ,'Facility Low-Activity Radioactive Waste Volume Solid Disposal Fees Unit'    ,255 ,None,'']
            ,['fac_haz_solid_dis_fee'           ,'DOUBLE','Facility Hazardous Volume Solid Disposal Fees'                              ,None,None,'']
            ,['fac_haz_solid_dis_fee_unt'       ,'TEXT'  ,'Facility Hazardous Volume Solid Disposal Fees Unit'                         ,255 ,None,'']
            ,['fac_haz_liquid_dis_fee'          ,'DOUBLE','Facility Hazardous Volume Liquid Disposal Fees'                             ,None,None,'']
            ,['fac_haz_liquid_dis_fee_unt'      ,'TEXT'  ,'Facility Hazardous Volume Liquid Disposal Fees Unit'                        ,255 ,None,'']
            ,['fac_msw_solid_dis_fee'           ,'DOUBLE','Facility Municipal Solid Waste (MSW) Volume Solid Disposal Fees'            ,None,None,'']
            ,['fac_msw_solid_dis_fee_unt'       ,'TEXT'  ,'Facility Municipal Solid Waste (MSW) Volume Solid Disposal Fees Unit'       ,255 ,None,'']
            ,['fac_cad_solid_dis_fee'           ,'DOUBLE','Facility Construction and Demolition Volume Solid Disposal Fees'            ,None,None,'']
            ,['fac_cad_solid_dis_fee_unt'       ,'TEXT'  ,'Facility Construction and Demolition Volume Solid Disposal Fees Unit'       ,255 ,None,'']
            ,['fac_nhaq_liquid_dis_fee'         ,'DOUBLE','Facility Non-Hazardous Aqueous Waste Volume Liquid Disposal Fees'           ,None,None,'']
            ,['fac_nhaq_liquid_dis_fee_unt'     ,'TEXT'  ,'Facility Non-Hazardous Aqueous Waste Volume Liquid Disposal Fees Unit'      ,255 ,None,'']
 
            ,['C_D_accepted'                    ,'TEXT'  ,'C_D_Accepted'                                 ,255 ,None,'']
            ,['MSW_accepted'                    ,'TEXT'  ,'MSW_Accepted'                                 ,255 ,None,'']
            ,['HW_accepted'                     ,'TEXT'  ,'HW_Accepted'                                  ,255 ,None,'']
            ,['LARWRad_accepted'                ,'TEXT'  ,'LARWRad_Accepted'                             ,255 ,None,'']
            ,['RAD_accepted'                    ,'TEXT'  ,'RAD_Accepted'                                 ,255 ,None,'']
            ,['NHAW_accepted'                   ,'TEXT'  ,'NHAW_Accepted'                                ,255 ,None,'']
            
            ,['date_stamp'                      ,'TEXT'  ,'Date_Stamp'                                   ,255 ,None,'']
            ,['source'                          ,'TEXT'  ,'Source'                                       ,255 ,None,'']
            ,['notes'                           ,'TEXT'  ,'Notes'                                        ,255 ,None,'']
         ]
      );

      qryset = source.obj_QuerySet.QuerySet({
          'facility_identifier'             : 'facility_identifier'
         ,'facility_typeid'                 : 'facility_typeid'
         ,'facility_subtypeids'             : 'facility_subtypeids'
         ,'facility_name'                   : 'facility_name'
         ,'facility_address'                : 'facility_address'
         ,'facility_city'                   : 'facility_city'
         ,'facility_state'                  : 'facility_state'
         ,'facility_zip'                    : 'facility_zip'
         ,'facility_telephone'              : 'facility_telephone'
         ,'front_gate_longitude'            : 'front_gate_longitude'
         ,'front_gate_latitude'             : 'front_gate_latitude'
         ,'facility_waste_mgt'              : 'facility_waste_mgt'
         
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

         ,'C_D_accepted'                    : 'C_D_accepted'
         ,'MSW_accepted'                    : 'MSW_accepted'
         ,'HW_accepted'                     : 'HW_accepted'
         ,'LARWRad_accepted'                : 'LARWRad_accepted'
         ,'RAD_accepted'                    : 'RAD_accepted'
         ,'NHAW_accepted'                   : 'NHAW_accepted'
         
         ,'date_stamp'                      : 'date_stamp'
         ,'source'                          : 'source'
         ,'notes'                           : 'notes'
         ,'SHAPE@'                          : 'SHAPE@'
      });

      with arcpy.da.SearchCursor(
          in_table     = scratch_geo
         ,field_names  = qryset.flds
      ) as cursor_in:

         with arcpy.da.InsertCursor(
             in_table     = scratch_src
            ,field_names  = qryset.flds
         ) as cursor_out:

            #########################################################################
            idx = 0;
            for row in cursor_in:

               cursor_out.insertRow(
                  (
                      qryset.idx(row,'facility_identifier')
                     ,qryset.idx(row,'facility_typeid')
                     ,qryset.idx(row,'facility_subtypeids')
                     ,qryset.idx(row,'facility_name')
                     ,qryset.idx(row,'facility_address')
                     ,qryset.idx(row,'facility_city')
                     ,qryset.idx(row,'facility_state')
                     ,qryset.idx(row,'facility_zip')
                     ,qryset.idx(row,'facility_telephone')
                     ,qryset.idx_clean_double(row,'front_gate_longitude')
                     ,qryset.idx_clean_double(row,'front_gate_latitude')
                     ,qryset.idx_clean_string(row,'facility_waste_mgt')
                     
                     ,qryset.idx_clean_string(row,'facility_accepts_no_waste')
                     ,qryset.idx_clean_double(row,'fac_radc_solid_dly_cap')
                     ,qryset.idx_clean_string(row,'fac_radc_solid_dly_cap_unt')
                     ,qryset.idx_clean_double(row,'fac_radc_liquid_dly_cap')
                     ,qryset.idx_clean_string(row,'fac_radc_liquid_dly_cap_unt')
                     ,qryset.idx_clean_double(row,'fac_radr_solid_dly_cap')
                     ,qryset.idx_clean_string(row,'fac_radr_solid_dly_cap_unt')
                     ,qryset.idx_clean_double(row,'fac_radr_liquid_dly_cap')
                     ,qryset.idx_clean_string(row,'fac_radr_liquid_dly_cap_unt')
                     ,qryset.idx_clean_double(row,'fac_larw_solid_dly_cap')
                     ,qryset.idx_clean_string(row,'fac_larw_solid_dly_cap_unt')
                     ,qryset.idx_clean_double(row,'fac_haz_solid_dly_cap')
                     ,qryset.idx_clean_string(row,'fac_haz_solid_dly_cap_unt')
                     ,qryset.idx_clean_double(row,'fac_haz_liquid_dly_cap')
                     ,qryset.idx_clean_string(row,'fac_haz_liquid_dly_cap_unt')
                     ,qryset.idx_clean_double(row,'fac_msw_solid_dly_cap')
                     ,qryset.idx_clean_string(row,'fac_msw_solid_dly_cap_unt')
                     ,qryset.idx_clean_double(row,'fac_cad_solid_dly_cap')
                     ,qryset.idx_clean_string(row,'fac_cad_solid_dly_cap_unt')
                     ,qryset.idx_clean_double(row,'fac_nhaq_liquid_dly_cap')
                     ,qryset.idx_clean_string(row,'fac_nhaq_liquid_dly_cap_unt')
                     ,qryset.idx_clean_double(row,'fac_radc_solid_tot_acp')
                     ,qryset.idx_clean_string(row,'fac_radc_solid_tot_acp_unt')
                     ,qryset.idx_clean_double(row,'fac_radc_liquid_tot_acp')
                     ,qryset.idx_clean_string(row,'fac_radc_liquid_tot_acp_unt')
                     ,qryset.idx_clean_double(row,'fac_radr_solid_tot_acp')
                     ,qryset.idx_clean_string(row,'fac_radr_solid_tot_acp_unt')
                     ,qryset.idx_clean_double(row,'fac_radr_liquid_tot_acp')
                     ,qryset.idx_clean_string(row,'fac_radr_liquid_tot_acp_unt')
                     ,qryset.idx_clean_double(row,'fac_larw_solid_tot_acp')
                     ,qryset.idx_clean_string(row,'fac_larw_solid_tot_acp_unt')
                     ,qryset.idx_clean_double(row,'fac_haz_solid_tot_acp')
                     ,qryset.idx_clean_string(row,'fac_haz_solid_tot_acp_unt')
                     ,qryset.idx_clean_double(row,'fac_haz_liquid_tot_acp')
                     ,qryset.idx_clean_string(row,'fac_haz_liquid_tot_acp_unt')
                     ,qryset.idx_clean_double(row,'fac_msw_solid_tot_acp')
                     ,qryset.idx_clean_string(row,'fac_msw_solid_tot_acp_unt')
                     ,qryset.idx_clean_double(row,'fac_cad_solid_tot_acp')
                     ,qryset.idx_clean_string(row,'fac_cad_solid_tot_acp_unt')
                     ,qryset.idx_clean_double(row,'fac_nhaq_liquid_tot_acp')
                     ,qryset.idx_clean_string(row,'fac_nhaq_liquid_tot_acp_unt')
                     ,qryset.idx_clean_double(row,'fac_radc_solid_dis_fee')
                     ,qryset.idx_clean_string(row,'fac_radc_solid_dis_fee_unt')
                     ,qryset.idx_clean_double(row,'fac_radc_liquid_dis_fee')
                     ,qryset.idx_clean_string(row,'fac_radc_liquid_dis_fee_unt')
                     ,qryset.idx_clean_double(row,'fac_radr_solid_dis_fee')
                     ,qryset.idx_clean_string(row,'fac_radr_solid_dis_fee_unt')
                     ,qryset.idx_clean_double(row,'fac_radr_liquid_dis_fee')
                     ,qryset.idx_clean_string(row,'fac_radr_liquid_dis_fee_unt')
                     ,qryset.idx_clean_double(row,'fac_larw_solid_dis_fee')
                     ,qryset.idx_clean_string(row,'fac_larw_solid_dis_fee_unt')
                     ,qryset.idx_clean_double(row,'fac_haz_solid_dis_fee')
                     ,qryset.idx_clean_string(row,'fac_haz_solid_dis_fee_unt')
                     ,qryset.idx_clean_double(row,'fac_haz_liquid_dis_fee')
                     ,qryset.idx_clean_string(row,'fac_haz_liquid_dis_fee_unt')
                     ,qryset.idx_clean_double(row,'fac_msw_solid_dis_fee')
                     ,qryset.idx_clean_string(row,'fac_msw_solid_dis_fee_unt')
                     ,qryset.idx_clean_double(row,'fac_cad_solid_dis_fee')
                     ,qryset.idx_clean_string(row,'fac_cad_solid_dis_fee_unt')
                     ,qryset.idx_clean_double(row,'fac_nhaq_liquid_dis_fee')
                     ,qryset.idx_clean_string(row,'fac_nhaq_liquid_dis_fee_unt')

                     ,qryset.idx_clean_boo(row,'C_D_accepted')
                     ,qryset.idx_clean_boo(row,'MSW_accepted')
                     ,qryset.idx_clean_boo(row,'HW_accepted')
                     ,qryset.idx_clean_boo(row,'LARWRad_accepted')
                     ,qryset.idx_clean_boo(row,'RAD_accepted')
                     ,qryset.idx_clean_boo(row,'NHAW_accepted')

                     ,qryset.idx(row,'date_stamp')
                     ,qryset.idx(row,'source')
                     ,qryset.idx_clean_string(row,'notes')
                     ,qryset.idx(row,'SHAPE@')
                  )
               );

               idx += 1;

      count = int(arcpy.GetCount_management(scratch_src).getOutput(0));
      arcpy.AddMessage("  Total I-Waste Facilities converted from GeoJSON: " + str(count));

      #########################################################################
      # Swap in front gate coordinate and filter by acceptance and subtype
      #########################################################################
      qryset2 = source.obj_QuerySet.QuerySet({
          'facility_subtypeids'  : 'facility_subtypeids'
         ,'front_gate_longitude' : 'front_gate_longitude'
         ,'front_gate_latitude'  : 'front_gate_latitude'
         ,'C_D_accepted'         : 'C_D_accepted'
         ,'MSW_accepted'         : 'MSW_accepted'
         ,'HW_accepted'          : 'HW_accepted'
         ,'LARWRad_accepted'     : 'LARWRad_accepted'
         ,'RAD_accepted'         : 'RAD_accepted'
         ,'NHAW_accepted'        : 'NHAW_accepted'
         ,'SHAPE@X'              : 'SHAPE@X'
         ,'SHAPE@Y'              : 'SHAPE@Y'
      });

      with arcpy.da.UpdateCursor(
          in_table    = scratch_src
         ,field_names = qryset2.flds
      ) as cursor:

         for row in cursor:

            if (filter_C_D_accepted     and qryset2.idx(row,'C_D_accepted')     == 'True')  \
            or (filter_MSW_accepted     and qryset2.idx(row,'MSW_accepted')     == 'True')  \
            or (filter_HW_accepted      and qryset2.idx(row,'HW_accepted')      == 'True')  \
            or (filter_LARWRad_accepted and qryset2.idx(row,'LARWRad_accepted') == 'True')  \
            or (filter_RAD_accepted     and qryset2.idx(row,'RAD_accepted')     == 'True')  \
            or (filter_NHAW_accepted    and qryset2.idx(row,'NHAW_accepted')    == 'True'):

               row_subtypes = qryset2.idx_clean_string(row,'facility_subtypeids');
               if row_subtypes is not None:
                  
                  if len(subtype_list) > 0:
                     boo_write = False;
                     for id in source.util.str2ary(row_subtypes):
                        if id in subtype_list:
                           boo_write = True;
                     
                     if boo_write:
                        if qryset2.idx(row,'front_gate_longitude') is not None:
                           row[qryset2.lkup['SHAPE@X']] = qryset2.idx(row,'front_gate_longitude');
                           row[qryset2.lkup['SHAPE@Y']] = qryset2.idx(row,'front_gate_latitude');
                           cursor.updateRow(row);
                     else:
                        cursor.deleteRow();
                  
                  else:
                     cursor.deleteRow();
                  
               else:                  
                  if qryset2.idx(row,'front_gate_longitude') is not None:
                     row[qryset2.lkup['SHAPE@X']] = qryset2.idx(row,'front_gate_longitude');
                     row[qryset2.lkup['SHAPE@Y']] = qryset2.idx(row,'front_gate_latitude');
                     cursor.updateRow(row);

            else:
               cursor.deleteRow();

      count = int(arcpy.GetCount_management(scratch_src).getOutput(0));
      arcpy.AddMessage("  Total I-Waste Facilities after waste acceptance types reductions: " + str(count));

      #########################################################################
      # Clip by support area if requested
      #########################################################################
      if limitBySupport and count > 0:

         scratch_clp = arcpy.CreateScratchName(
             prefix    = "Clip_Facilities"
            ,suffix    = ""
            ,data_type = "FeatureClass"
            ,workspace = arcpy.env.scratchGDB
         );

         arcpy.Clip_analysis(
            in_features        = scratch_src
           ,clip_features      = haz.support_area.dataSource
           ,out_feature_class  = scratch_clp
         );

         scratch_src = scratch_clp;
         count = int(arcpy.GetCount_management(scratch_src).getOutput(0));
         arcpy.AddMessage("  Total I-Waste Facilities after clip by support area: " + str(count));

      #########################################################################
      # Copy results into final feature class
      #########################################################################
      if count > 0:

         with arcpy.da.SearchCursor(
             in_table     = scratch_src
            ,field_names  = qryset.flds
         ) as cursor_in:

            with arcpy.da.InsertCursor(
                in_table    = scratch_ldr
               ,field_names = qryset.flds
            ) as cursor_out:

               for row in cursor_in:

                  cursor_out.insertRow(
                     (
                         'Facility' + qryset.idx_clean_string(row,'facility_identifier')
                        ,qryset.idx(row,'facility_typeid')
                        ,qryset.idx(row,'facility_subtypeids')
                        ,qryset.idx(row,'facility_name')
                        ,qryset.idx(row,'facility_address')
                        ,qryset.idx(row,'facility_city')
                        ,qryset.idx(row,'facility_state')
                        ,qryset.idx(row,'facility_zip')
                        ,qryset.idx(row,'facility_telephone')
                        ,qryset.idx(row,'front_gate_longitude')
                        ,qryset.idx(row,'front_gate_latitude')
                        ,qryset.idx(row,'facility_waste_mgt')
                        
                        ,qryset.idx_clean_string(row,'facility_accepts_no_waste')
                        ,qryset.idx_clean_double(row,'fac_radc_solid_dly_cap')
                        ,qryset.idx_clean_string(row,'fac_radc_solid_dly_cap_unt')
                        ,qryset.idx_clean_double(row,'fac_radc_liquid_dly_cap')
                        ,qryset.idx_clean_string(row,'fac_radc_liquid_dly_cap_unt')
                        ,qryset.idx_clean_double(row,'fac_radr_solid_dly_cap')
                        ,qryset.idx_clean_string(row,'fac_radr_solid_dly_cap_unt')
                        ,qryset.idx_clean_double(row,'fac_radr_liquid_dly_cap')
                        ,qryset.idx_clean_string(row,'fac_radr_liquid_dly_cap_unt')
                        ,qryset.idx_clean_double(row,'fac_larw_solid_dly_cap')
                        ,qryset.idx_clean_string(row,'fac_larw_solid_dly_cap_unt')
                        ,qryset.idx_clean_double(row,'fac_haz_solid_dly_cap')
                        ,qryset.idx_clean_string(row,'fac_haz_solid_dly_cap_unt')
                        ,qryset.idx_clean_double(row,'fac_haz_liquid_dly_cap')
                        ,qryset.idx_clean_string(row,'fac_haz_liquid_dly_cap_unt')
                        ,qryset.idx_clean_double(row,'fac_msw_solid_dly_cap')
                        ,qryset.idx_clean_string(row,'fac_msw_solid_dly_cap_unt')
                        ,qryset.idx_clean_double(row,'fac_cad_solid_dly_cap')
                        ,qryset.idx_clean_string(row,'fac_cad_solid_dly_cap_unt')
                        ,qryset.idx_clean_double(row,'fac_nhaq_liquid_dly_cap')
                        ,qryset.idx_clean_string(row,'fac_nhaq_liquid_dly_cap_unt')
                        ,qryset.idx_clean_double(row,'fac_radc_solid_tot_acp')
                        ,qryset.idx_clean_string(row,'fac_radc_solid_tot_acp_unt')
                        ,qryset.idx_clean_double(row,'fac_radc_liquid_tot_acp')
                        ,qryset.idx_clean_string(row,'fac_radc_liquid_tot_acp_unt')
                        ,qryset.idx_clean_double(row,'fac_radr_solid_tot_acp')
                        ,qryset.idx_clean_string(row,'fac_radr_solid_tot_acp_unt')
                        ,qryset.idx_clean_double(row,'fac_radr_liquid_tot_acp')
                        ,qryset.idx_clean_string(row,'fac_radr_liquid_tot_acp_unt')
                        ,qryset.idx_clean_double(row,'fac_larw_solid_tot_acp')
                        ,qryset.idx_clean_string(row,'fac_larw_solid_tot_acp_unt')
                        ,qryset.idx_clean_double(row,'fac_haz_solid_tot_acp')
                        ,qryset.idx_clean_string(row,'fac_haz_solid_tot_acp_unt')
                        ,qryset.idx_clean_double(row,'fac_haz_liquid_tot_acp')
                        ,qryset.idx_clean_string(row,'fac_haz_liquid_tot_acp_unt')
                        ,qryset.idx_clean_double(row,'fac_msw_solid_tot_acp')
                        ,qryset.idx_clean_string(row,'fac_msw_solid_tot_acp_unt')
                        ,qryset.idx_clean_double(row,'fac_cad_solid_tot_acp')
                        ,qryset.idx_clean_string(row,'fac_cad_solid_tot_acp_unt')
                        ,qryset.idx_clean_double(row,'fac_nhaq_liquid_tot_acp')
                        ,qryset.idx_clean_string(row,'fac_nhaq_liquid_tot_acp_unt')
                        ,qryset.idx_clean_double(row,'fac_radc_solid_dis_fee')
                        ,qryset.idx_clean_string(row,'fac_radc_solid_dis_fee_unt')
                        ,qryset.idx_clean_double(row,'fac_radc_liquid_dis_fee')
                        ,qryset.idx_clean_string(row,'fac_radc_liquid_dis_fee_unt')
                        ,qryset.idx_clean_double(row,'fac_radr_solid_dis_fee')
                        ,qryset.idx_clean_string(row,'fac_radr_solid_dis_fee_unt')
                        ,qryset.idx_clean_double(row,'fac_radr_liquid_dis_fee')
                        ,qryset.idx_clean_string(row,'fac_radr_liquid_dis_fee_unt')
                        ,qryset.idx_clean_double(row,'fac_larw_solid_dis_fee')
                        ,qryset.idx_clean_string(row,'fac_larw_solid_dis_fee_unt')
                        ,qryset.idx_clean_double(row,'fac_haz_solid_dis_fee')
                        ,qryset.idx_clean_string(row,'fac_haz_solid_dis_fee_unt')
                        ,qryset.idx_clean_double(row,'fac_haz_liquid_dis_fee')
                        ,qryset.idx_clean_string(row,'fac_haz_liquid_dis_fee_unt')
                        ,qryset.idx_clean_double(row,'fac_msw_solid_dis_fee')
                        ,qryset.idx_clean_string(row,'fac_msw_solid_dis_fee_unt')
                        ,qryset.idx_clean_double(row,'fac_cad_solid_dis_fee')
                        ,qryset.idx_clean_string(row,'fac_cad_solid_dis_fee_unt')
                        ,qryset.idx_clean_double(row,'fac_nhaq_liquid_dis_fee')
                        ,qryset.idx_clean_string(row,'fac_nhaq_liquid_dis_fee_unt')
                        
                        ,qryset.idx(row,'C_D_accepted')
                        ,qryset.idx(row,'MSW_accepted')
                        ,qryset.idx(row,'HW_accepted')
                        ,qryset.idx(row,'LARWRad_accepted')
                        ,qryset.idx(row,'RAD_accepted')
                        ,qryset.idx(row,'NHAW_accepted')
                        
                        ,qryset.idx(row,'date_stamp')
                        ,qryset.idx(row,'source')
                        ,qryset.idx(row,'notes')
                        
                        ,qryset.idx(row,'SHAPE@')
                     )
                  );

         arcpy.AddMessage("  Facility Loader Layer loaded.");

   #########################################################################
   # Step 90
   # Load User-defined facilities
   #########################################################################
   if loadUserDefined                                                      \
   and ary_user_defined is not None                                        \
   and len(ary_user_defined) > 0:

      # Spin through each incoming user file
      for i in range(len(ary_user_defined)):

         boo_stagingsite = False;

         # define a scratch fc for the user file
         scratch_usr = arcpy.CreateScratchName(
             "UserDefined" + str(i)
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_usr_path,scratch_usr_name = os.path.split(scratch_usr);

         src_input = ary_user_defined[i];

         # Describe the incoming feature set
         desc = arcpy.Describe(src_input);

         # If polygon, then search for centroid information in the fc
         if desc.shapeType == "Polygon":

            fields = arcpy.ListFields(src_input)

            chck = 0;
            for field in fields:
               if field.name == "Name":
                  chck = chck + 1;
               elif field.name == "CENTROID_X":
                  chck = chck + 1;
               elif field.name == "CENTROID_Y":
                  chck = chck + 1;
               elif field.name == "Available_Solid_Waste_Capacity__m3_":
                  chck = chck + 1;
               elif field.name == "Available_Liquid_Waste_Capacity__L_":
                  chck = chck + 1;

            # Note we don't have a fallback for when its not a staging tool file
            if chck != 5:
               raise arcpy.ExecuteError(
                  "Polygon feature class " + str(src_input)
                  + " does not appear to be a valid staging site tool output file."
               );

            boo_stagingsite = True;

            scratch_ste = arcpy.CreateScratchName(
                "StagingSite" + str(i)
               ,""
               ,"FeatureClass"
               ,arcpy.env.scratchGDB
            );
            scratch_ste_path,scratch_ste_name = os.path.split(scratch_ste);

            arcpy.CreateFeatureclass_management(
                out_path          = scratch_ste_path
               ,out_name          = scratch_ste_name
               ,geometry_type     = "POINT"
               ,has_m             = "DISABLED"
               ,has_z             = "DISABLED"
               ,spatial_reference = arcpy.SpatialReference(4326)
               ,config_keyword    = None
            );

            arcpy.management.AddFields(
                scratch_ste
               ,[
                   ['facility_identifier'             ,'TEXT'  ,'Facility_Identifier'                          ,255, None,'']
                  ,['facility_typeid'                 ,'LONG'  ,'Facility TypeID'                              ,None,None,'']
                  ,['facility_subtypeids'             ,'TEXT'  ,'Facility SubtypeIDs'                          ,255, None,'']
                  ,['facility_name'                   ,'TEXT'  ,'Facility_Name'                                ,255, None,'']
                  ,['facility_address'                ,'TEXT'  ,'Facility_Addres'                              ,255, None,'']
                  ,['facility_city'                   ,'TEXT'  ,'Facility_City'                                ,255, None,'']
                  ,['facility_state'                  ,'TEXT'  ,'Facility_State'                               ,255, None,'']
                  ,['facility_zip'                    ,'TEXT'  ,'Facility_Zip'                                 ,255, None,'']
                  ,['facility_telephone'              ,'TEXT'  ,'Facility_Telephone'                           ,255, None,'']
                  ,['front_gate_longitude'            ,'DOUBLE','Front_Gate_Longitude'                         ,None,None,'']
                  ,['front_gate_latitude'             ,'DOUBLE','Front_Gate_Latitude'                          ,None,None,'']
                  ,['facility_waste_mgt'              ,'TEXT'  ,'Facility_Waste_Mgt'                           ,255 ,None,'']
                  
                  ,['facility_accepts_no_waste'       ,'TEXT'  ,'Facility Accepts No Waste Flag'                                             ,255 ,None,'']
                  ,['fac_radc_solid_dly_cap'          ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Solid Daily Capacity'          ,None,None,'']
                  ,['fac_radc_solid_dly_cap_unt'      ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Solid Daily Capacity Unit'     ,255 ,None,'']
                  ,['fac_radc_liquid_dly_cap'         ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Liquid Daily Capacity'         ,None,None,'']
                  ,['fac_radc_liquid_dly_cap_unt'     ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Liquid Daily Capacity Unit'    ,255 ,None,'']
                  ,['fac_radr_solid_dly_cap'          ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Solid Daily Capacity'           ,None,None,'']
                  ,['fac_radr_solid_dly_cap_unt'      ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Solid Daily Capacity Unit'      ,255 ,None,'']
                  ,['fac_radr_liquid_dly_cap'         ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Liquid Daily Capacity'          ,None,None,'']
                  ,['fac_radr_liquid_dly_cap_unt'     ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Liquid Daily Capacity Unit'     ,255 ,None,'']
                  ,['fac_larw_solid_dly_cap'          ,'DOUBLE','Facility Low-Activity Radioactive Waste Volume Solid Daily Capacity'        ,None,None,'']
                  ,['fac_larw_solid_dly_cap_unt'      ,'TEXT'  ,'Facility Low-Activity Radioactive Waste Volume Solid Daily Capacity Unit'   ,255 ,None,'']
                  ,['fac_haz_solid_dly_cap'           ,'DOUBLE','Facility Hazardous Volume Solid Daily Capacity'                             ,None,None,'']
                  ,['fac_haz_solid_dly_cap_unt'       ,'TEXT'  ,'Facility Hazardous Volume Solid Daily Capacity Unit'                        ,255 ,None,'']
                  ,['fac_haz_liquid_dly_cap'          ,'DOUBLE','Facility Hazardous Volume Liquid Daily Capacity'                            ,None,None,'']
                  ,['fac_haz_liquid_dly_cap_unt'      ,'TEXT'  ,'Facility Hazardous Volume Liquid Daily Capacity Unit'                       ,255 ,None,'']
                  ,['fac_msw_solid_dly_cap'           ,'DOUBLE','Facility Municipal Solid Waste (MSW) Volume Solid Daily Capacity'           ,None,None,'']
                  ,['fac_msw_solid_dly_cap_unt'       ,'TEXT'  ,'Facility Municipal Solid Waste (MSW) Volume Solid Daily Capacity Unit'      ,255 ,None,'']
                  ,['fac_cad_solid_dly_cap'           ,'DOUBLE','Facility Construction and Demolition Volume Solid Daily Capacity'           ,None,None,'']
                  ,['fac_cad_solid_dly_cap_unt'       ,'TEXT'  ,'Facility Construction and Demolition Volume Solid Daily Capacity Unit'      ,255 ,None,'']
                  ,['fac_nhaq_liquid_dly_cap'         ,'DOUBLE','Facility Non-Hazardous Aqueous Waste Volume Liquid Daily Capacity'          ,None,None,'']
                  ,['fac_nhaq_liquid_dly_cap_unt'     ,'TEXT'  ,'Facility Non-Hazardous Aqueous Waste Volume Liquid Daily Capacity Unit'     ,255 ,None,'']
                  ,['fac_radc_solid_tot_acp'          ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Solid Total Acceptance'        ,None,None,'']
                  ,['fac_radc_solid_tot_acp_unt'      ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Solid Total Acceptance Unit'   ,255 ,None,'']
                  ,['fac_radc_liquid_tot_acp'         ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Liquid Total Acceptance'       ,None,None,'']
                  ,['fac_radc_liquid_tot_acp_unt'     ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Liquid Total Acceptance Unit'  ,255 ,None,'']
                  ,['fac_radr_solid_tot_acp'          ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Solid Total Acceptance'         ,None,None,'']
                  ,['fac_radr_solid_tot_acp_unt'      ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Solid Total Acceptance Unit'    ,255 ,None,'']
                  ,['fac_radr_liquid_tot_acp'         ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Liquid Total Acceptance'        ,None,None,'']
                  ,['fac_radr_liquid_tot_acp_unt'     ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Liquid Total Acceptance Unit'   ,255 ,None,'']
                  ,['fac_larw_solid_tot_acp'          ,'DOUBLE','Facility Low-Activity Radioactive Waste Volume Solid Total Acceptance'      ,None,None,'']
                  ,['fac_larw_solid_tot_acp_unt'      ,'TEXT'  ,'Facility Low-Activity Radioactive Waste Volume Solid Total Acceptance Unit' ,255 ,None,'']
                  ,['fac_haz_solid_tot_acp'           ,'DOUBLE','Facility Hazardous Volume Solid Total Acceptance'                           ,None,None,'']
                  ,['fac_haz_solid_tot_acp_unt'       ,'TEXT'  ,'Facility Hazardous Volume Solid Total Acceptance Unit'                      ,255 ,None,'']
                  ,['fac_haz_liquid_tot_acp'          ,'DOUBLE','Facility Hazardous Volume Liquid Total Acceptance'                          ,None,None,'']
                  ,['fac_haz_liquid_tot_acp_unt'      ,'TEXT'  ,'Facility Hazardous Volume Liquid Total Acceptance Unit'                     ,255 ,None,'']
                  ,['fac_msw_solid_tot_acp'           ,'DOUBLE','Facility Municipal Solid Waste (MSW) Volume Solid Total Acceptance'         ,None,None,'']
                  ,['fac_msw_solid_tot_acp_unt'       ,'TEXT'  ,'Facility Municipal Solid Waste (MSW) Volume Solid Total Acceptance Unit'    ,255 ,None,'']
                  ,['fac_cad_solid_tot_acp'           ,'DOUBLE','Facility Construction and Demolition Volume Solid Total Acceptance'         ,None,None,'']
                  ,['fac_cad_solid_tot_acp_unt'       ,'TEXT'  ,'Facility Construction and Demolition Volume Solid Total Acceptance Unit'    ,255 ,None,'']
                  ,['fac_nhaq_liquid_tot_acp'         ,'DOUBLE','Facility Non-Hazardous Aqueous Waste Volume Liquid Total Acceptance'        ,None,None,'']
                  ,['fac_nhaq_liquid_tot_acp_unt'     ,'TEXT'  ,'Facility Non-Hazardous Aqueous Waste Volume Liquid Total Acceptance Unit'   ,255 ,None,'']
                  ,['fac_radc_solid_dis_fee'          ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Solid Disposal Fees'           ,None,None,'']
                  ,['fac_radc_solid_dis_fee_unt'      ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Solid Disposal Fees Unit'      ,255 ,None,'']
                  ,['fac_radc_liquid_dis_fee'         ,'DOUBLE','Facility Radioactive: Contact-Handled Volume Liquid Disposal Fees'          ,None,None,'']
                  ,['fac_radc_liquid_dis_fee_unt'     ,'TEXT'  ,'Facility Radioactive: Contact-Handled Volume Liquid Disposal Fees Unit'     ,255 ,None,'']
                  ,['fac_radr_solid_dis_fee'          ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Solid Disposal Fees'            ,None,None,'']
                  ,['fac_radr_solid_dis_fee_unt'      ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Solid Disposal Fees Unit'       ,255 ,None,'']
                  ,['fac_radr_liquid_dis_fee'         ,'DOUBLE','Facility Radioactive: Remote-Handled Volume Liquid Disposal Fees'           ,None,None,'']
                  ,['fac_radr_liquid_dis_fee_unt'     ,'TEXT'  ,'Facility Radioactive: Remote-Handled Volume Liquid Disposal Fees Unit'      ,255 ,None,'']
                  ,['fac_larw_solid_dis_fee'          ,'DOUBLE','Facility Low-Activity Radioactive Waste Volume Solid Disposal Fees'         ,None,None,'']
                  ,['fac_larw_solid_dis_fee_unt'      ,'TEXT'  ,'Facility Low-Activity Radioactive Waste Volume Solid Disposal Fees Unit'    ,255 ,None,'']
                  ,['fac_haz_solid_dis_fee'           ,'DOUBLE','Facility Hazardous Volume Solid Disposal Fees'                              ,None,None,'']
                  ,['fac_haz_solid_dis_fee_unt'       ,'TEXT'  ,'Facility Hazardous Volume Solid Disposal Fees Unit'                         ,255 ,None,'']
                  ,['fac_haz_liquid_dis_fee'          ,'DOUBLE','Facility Hazardous Volume Liquid Disposal Fees'                             ,None,None,'']
                  ,['fac_haz_liquid_dis_fee_unt'      ,'TEXT'  ,'Facility Hazardous Volume Liquid Disposal Fees Unit'                        ,255 ,None,'']
                  ,['fac_msw_solid_dis_fee'           ,'DOUBLE','Facility Municipal Solid Waste (MSW) Volume Solid Disposal Fees'            ,None,None,'']
                  ,['fac_msw_solid_dis_fee_unt'       ,'TEXT'  ,'Facility Municipal Solid Waste (MSW) Volume Solid Disposal Fees Unit'       ,255 ,None,'']
                  ,['fac_cad_solid_dis_fee'           ,'DOUBLE','Facility Construction and Demolition Volume Solid Disposal Fees'            ,None,None,'']
                  ,['fac_cad_solid_dis_fee_unt'       ,'TEXT'  ,'Facility Construction and Demolition Volume Solid Disposal Fees Unit'       ,255 ,None,'']
                  ,['fac_nhaq_liquid_dis_fee'         ,'DOUBLE','Facility Non-Hazardous Aqueous Waste Volume Liquid Disposal Fees'           ,None,None,'']
                  ,['fac_nhaq_liquid_dis_fee_unt'     ,'TEXT'  ,'Facility Non-Hazardous Aqueous Waste Volume Liquid Disposal Fees Unit'      ,255 ,None,'']
       
                  ,['C_D_accepted'                    ,'TEXT'  ,'C_D_Accepted'                                 ,255 ,None,'']
                  ,['MSW_accepted'                    ,'TEXT'  ,'MSW_Accepted'                                 ,255 ,None,'']
                  ,['HW_accepted'                     ,'TEXT'  ,'HW_Accepted'                                  ,255 ,None,'']
                  ,['LARWRad_accepted'                ,'TEXT'  ,'LARWRad_Accepted'                             ,255 ,None,'']
                  ,['RAD_accepted'                    ,'TEXT'  ,'RAD_Accepted'                                 ,255 ,None,'']
                  ,['NHAW_accepted'                   ,'TEXT'  ,'NHAW_Accepted'                                ,255 ,None,'']
                  
                  ,['date_stamp'                      ,'TEXT'  ,'Date_Stamp'                                   ,255 ,None,'']
                  ,['source'                          ,'TEXT'  ,'Source'                                       ,255 ,None,'']
                  ,['notes'                           ,'TEXT'  ,'Notes'                                        ,255 ,None,'']
               ]
            );

            with arcpy.da.SearchCursor(
                in_table     = src_input
               ,field_names  = [
                   'Name'
                  ,'CENTROID_X'
                  ,'CENTROID_Y'
                  ,'Available_Solid_Waste_Capacity__m3_'
                  ,'Available_Liquid_Waste_Capacity__L_'
               ]
            ) as cursor_in:

               with arcpy.da.InsertCursor(
                   in_table    = scratch_ste
                  ,field_names = [
                      'facility_identifier'
                     ,'facility_name'
                     ,'facility_waste_mgt'
                     
                     ,'facility_accepts_no_waste'
                     ,'fac_radc_solid_dly_cap'
                     ,'fac_radc_solid_dly_cap_unt'
                     ,'fac_radc_liquid_dly_cap'
                     ,'fac_radc_liquid_dly_cap_unt'
                     ,'fac_radr_solid_dly_cap'
                     ,'fac_radr_solid_dly_cap_unt'
                     ,'fac_radr_liquid_dly_cap'
                     ,'fac_radr_liquid_dly_cap_unt'
                     ,'fac_larw_solid_dly_cap'
                     ,'fac_larw_solid_dly_cap_unt'
                     ,'fac_haz_solid_dly_cap'
                     ,'fac_haz_solid_dly_cap_unt'
                     ,'fac_haz_liquid_dly_cap'
                     ,'fac_haz_liquid_dly_cap_unt'
                     ,'fac_msw_solid_dly_cap'
                     ,'fac_msw_solid_dly_cap_unt'
                     ,'fac_cad_solid_dly_cap'
                     ,'fac_cad_solid_dly_cap_unt'
                     ,'fac_nhaq_liquid_dly_cap'
                     ,'fac_nhaq_liquid_dly_cap_unt'
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
                     ,'fac_radc_solid_dis_fee'
                     ,'fac_radc_solid_dis_fee_unt'
                     ,'fac_radc_liquid_dis_fee'
                     ,'fac_radc_liquid_dis_fee_unt'
                     ,'fac_radr_solid_dis_fee'
                     ,'fac_radr_solid_dis_fee_unt'
                     ,'fac_radr_liquid_dis_fee'
                     ,'fac_radr_liquid_dis_fee_unt'
                     ,'fac_larw_solid_dis_fee'
                     ,'fac_larw_solid_dis_fee_unt'
                     ,'fac_haz_solid_dis_fee'
                     ,'fac_haz_solid_dis_fee_unt'
                     ,'fac_haz_liquid_dis_fee'
                     ,'fac_haz_liquid_dis_fee_unt'
                     ,'fac_msw_solid_dis_fee'
                     ,'fac_msw_solid_dis_fee_unt'
                     ,'fac_cad_solid_dis_fee'
                     ,'fac_cad_solid_dis_fee_unt'
                     ,'fac_nhaq_liquid_dis_fee'
                     ,'fac_nhaq_liquid_dis_fee_unt'
                     
                     ,'C_D_accepted'    
                     ,'MSW_accepted'    
                     ,'HW_accepted'     
                     ,'LARWRad_accepted'
                     ,'RAD_accepted'    
                     ,'NHAW_accepted'   
                     
                     ,'source'                             
                     ,'SHAPE@X'
                     ,'SHAPE@Y'
                  ]
               ) as cursor_out:

                  for row in cursor_in:
                  
                     ssst_name           = row[0];
                     ssst_cenX           = row[1];
                     ssst_cenY           = row[2];
                     ssst_solid_waste_m3 = row[3];
                     ssst_liquid_waste_L = row[4];

                     cursor_out.insertRow(
                        (
                            'StagingSiteSelectionTool.' + str(i)
                           ,ssst_name
                           ,'Staging'
                           
                           ,'False'
                           
                           ,ssst_solid_waste_m3 / 90
                           ,'m3'
                           ,ssst_liquid_waste_L / 90
                           ,'L'
                           
                           ,ssst_solid_waste_m3 / 90
                           ,'m3'
                           ,ssst_liquid_waste_L / 90
                           ,'L'
                           
                           ,ssst_solid_waste_m3 / 90
                           ,'m3'
                           
                           ,ssst_solid_waste_m3 / 90
                           ,'m3'
                           ,ssst_liquid_waste_L / 90
                           ,'L'
                           
                           ,ssst_solid_waste_m3 / 90
                           ,'m3'
                           
                           ,ssst_solid_waste_m3 / 90
                           ,'m3'
                           
                           ,ssst_liquid_waste_L / 90
                           ,'L'
                           
                           
                           ,ssst_solid_waste_m3
                           ,'m3'
                           ,ssst_liquid_waste_L
                           ,'L'
                           
                           ,ssst_solid_waste_m3
                           ,'m3'
                           ,ssst_liquid_waste_L
                           ,'L'
                           
                           ,ssst_solid_waste_m3
                           ,'m3'
                           
                           ,ssst_solid_waste_m3
                           ,'m3'
                           ,ssst_liquid_waste_L
                           ,'L'
                           
                           ,ssst_solid_waste_m3
                           ,'m3'
                           
                           ,ssst_solid_waste_m3
                           ,'m3'
                           
                           ,ssst_liquid_waste_L
                           ,'L'
                           
                           ,None
                           ,None
                           ,None
                           ,None
                           
                           ,None
                           ,None
                           ,None
                           ,None
                           
                           ,None
                           ,None
                           
                           ,None
                           ,None
                           ,None
                           ,None
                           
                           ,None
                           ,None
                           
                           ,None
                           ,None
                           
                           ,None
                           ,None
                           
                           ,'True'
                           ,'True'
                           ,'True'
                           ,'True'
                           ,'True'
                           ,'True'
                           
                           ,'StagingSiteSelectionTool'
                           ,ssst_cenX
                           ,ssst_cenY
                        )
                     );
                     
            src_input = scratch_ste;
            
         count = int(arcpy.GetCount_management(src_input).getOutput(0));
         arcpy.AddMessage("  Total User-Defined Facilities loaded: " + str(count));

         ######################################################################
         # Limit user records by support area if requested
         ######################################################################
         if limitBySupport:
            arcpy.Clip_analysis(
               in_features        = src_input
              ,clip_features      = haz.support_area.dataSource
              ,out_feature_class  = scratch_usr
            );

         else:
            arcpy.CopyFeatures_management(
                in_features       = src_input
               ,out_feature_class = scratch_usr
            );

         count = int(arcpy.GetCount_management(scratch_usr).getOutput(0));
         arcpy.AddMessage("  Total User-Defined Facilities after support area limiting: " + str(count));

         ######################################################################
         # Append user records into scratch loader fc
         ######################################################################
         if count > 0:
         
            qryset = source.obj_QuerySet.QuerySet({
                'facility_identifier'             : 'facility_identifier'
               ,'facility_typeid'                 : 'facility_typeid'
               ,'facility_subtypeids'             : 'facility_subtypeids'
               ,'facility_name'                   : 'facility_name'
               ,'facility_address'                : 'facility_address'
               ,'facility_city'                   : 'facility_city'
               ,'facility_state'                  : 'facility_state'
               ,'facility_zip'                    : 'facility_zip'
               ,'facility_telephone'              : 'facility_telephone'
               ,'front_gate_longitude'            : 'front_gate_longitude'
               ,'front_gate_latitude'             : 'front_gate_latitude'
               ,'facility_waste_mgt'              : 'facility_waste_mgt'
               
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

               ,'C_D_accepted'                    : 'C_D_accepted'
               ,'MSW_accepted'                    : 'MSW_accepted'
               ,'HW_accepted'                     : 'HW_accepted'
               ,'LARWRad_accepted'                : 'LARWRad_accepted'
               ,'RAD_accepted'                    : 'RAD_accepted'
               ,'NHAW_accepted'                   : 'NHAW_accepted'
               
               ,'date_stamp'                      : 'date_stamp'
               ,'source'                          : 'source'
               ,'notes'                           : 'notes'
               
               ,'SHAPE@'                          : 'SHAPE@'
            });

            with arcpy.da.SearchCursor(
                in_table     = scratch_usr
               ,field_names  = qryset.flds
            ) as cursor_in:

               with arcpy.da.InsertCursor(
                   in_table    = scratch_ldr
                  ,field_names = qryset.flds
               ) as cursor_out:

                  idx = 0;
                  for row in cursor_in:
                     idx += 1;

                     if (filter_C_D_accepted     and qryset.idx(row,'C_D_accepted')     == 'True')   \
                     or (filter_MSW_accepted     and qryset.idx(row,'MSW_accepted')     == 'True')   \
                     or (filter_HW_accepted      and qryset.idx(row,'HW_accepted')      == 'True')   \
                     or (filter_LARWRad_accepted and qryset.idx(row,'LARWRad_accepted') == 'True')   \
                     or (filter_RAD_accepted     and qryset.idx(row,'RAD_accepted')     == 'True')   \
                     or (filter_NHAW_accepted    and qryset.idx(row,'NHAW_accepted')    == 'True')   \
                     or boo_stagingsite:
                     
                        fi = qryset.idx_clean_string(row,'facility_identifier');
                        if fi is None:
                           facility_identifier = 'Facility' + str(idx);
                        else:
                           if fi[:1].isnumeric():
                              facility_identifier = 'Facility' + str(fi);
                           else:
                              facility_identifier = str(fi);

                        cursor_out.insertRow(
                           (
                               facility_identifier
                              ,qryset.idx(row,'facility_typeid')
                              ,qryset.idx(row,'facility_subtypeids')
                              ,qryset.idx(row,'facility_name')
                              ,qryset.idx(row,'facility_address')
                              ,qryset.idx(row,'facility_city')
                              ,qryset.idx(row,'facility_state')
                              ,qryset.idx(row,'facility_zip')
                              ,qryset.idx(row,'facility_telephone')
                              ,qryset.idx_clean_double(row,'front_gate_longitude')
                              ,qryset.idx_clean_double(row,'front_gate_latitude')
                              ,qryset.idx(row,'facility_waste_mgt')
                              
                              ,qryset.idx_clean_string(row,'facility_accepts_no_waste')
                              ,qryset.idx_clean_double(row,'fac_radc_solid_dly_cap')
                              ,qryset.idx_clean_string(row,'fac_radc_solid_dly_cap_unt')
                              ,qryset.idx_clean_double(row,'fac_radc_liquid_dly_cap')
                              ,qryset.idx_clean_string(row,'fac_radc_liquid_dly_cap_unt')
                              ,qryset.idx_clean_double(row,'fac_radr_solid_dly_cap')
                              ,qryset.idx_clean_string(row,'fac_radr_solid_dly_cap_unt')
                              ,qryset.idx_clean_double(row,'fac_radr_liquid_dly_cap')
                              ,qryset.idx_clean_string(row,'fac_radr_liquid_dly_cap_unt')
                              ,qryset.idx_clean_double(row,'fac_larw_solid_dly_cap')
                              ,qryset.idx_clean_string(row,'fac_larw_solid_dly_cap_unt')
                              ,qryset.idx_clean_double(row,'fac_haz_solid_dly_cap')
                              ,qryset.idx_clean_string(row,'fac_haz_solid_dly_cap_unt')
                              ,qryset.idx_clean_double(row,'fac_haz_liquid_dly_cap')
                              ,qryset.idx_clean_string(row,'fac_haz_liquid_dly_cap_unt')
                              ,qryset.idx_clean_double(row,'fac_msw_solid_dly_cap')
                              ,qryset.idx_clean_string(row,'fac_msw_solid_dly_cap_unt')
                              ,qryset.idx_clean_double(row,'fac_cad_solid_dly_cap')
                              ,qryset.idx_clean_string(row,'fac_cad_solid_dly_cap_unt')
                              ,qryset.idx_clean_double(row,'fac_nhaq_liquid_dly_cap')
                              ,qryset.idx_clean_string(row,'fac_nhaq_liquid_dly_cap_unt')
                              ,qryset.idx_clean_double(row,'fac_radc_solid_tot_acp')
                              ,qryset.idx_clean_string(row,'fac_radc_solid_tot_acp_unt')
                              ,qryset.idx_clean_double(row,'fac_radc_liquid_tot_acp')
                              ,qryset.idx_clean_string(row,'fac_radc_liquid_tot_acp_unt')
                              ,qryset.idx_clean_double(row,'fac_radr_solid_tot_acp')
                              ,qryset.idx_clean_string(row,'fac_radr_solid_tot_acp_unt')
                              ,qryset.idx_clean_double(row,'fac_radr_liquid_tot_acp')
                              ,qryset.idx_clean_string(row,'fac_radr_liquid_tot_acp_unt')
                              ,qryset.idx_clean_double(row,'fac_larw_solid_tot_acp')
                              ,qryset.idx_clean_string(row,'fac_larw_solid_tot_acp_unt')
                              ,qryset.idx_clean_double(row,'fac_haz_solid_tot_acp')
                              ,qryset.idx_clean_string(row,'fac_haz_solid_tot_acp_unt')
                              ,qryset.idx_clean_double(row,'fac_haz_liquid_tot_acp')
                              ,qryset.idx_clean_string(row,'fac_haz_liquid_tot_acp_unt')
                              ,qryset.idx_clean_double(row,'fac_msw_solid_tot_acp')
                              ,qryset.idx_clean_string(row,'fac_msw_solid_tot_acp_unt')
                              ,qryset.idx_clean_double(row,'fac_cad_solid_tot_acp')
                              ,qryset.idx_clean_string(row,'fac_cad_solid_tot_acp_unt')
                              ,qryset.idx_clean_double(row,'fac_nhaq_liquid_tot_acp')
                              ,qryset.idx_clean_string(row,'fac_nhaq_liquid_tot_acp_unt')
                              ,qryset.idx_clean_double(row,'fac_radc_solid_dis_fee')
                              ,qryset.idx_clean_string(row,'fac_radc_solid_dis_fee_unt')
                              ,qryset.idx_clean_double(row,'fac_radc_liquid_dis_fee')
                              ,qryset.idx_clean_string(row,'fac_radc_liquid_dis_fee_unt')
                              ,qryset.idx_clean_double(row,'fac_radr_solid_dis_fee')
                              ,qryset.idx_clean_string(row,'fac_radr_solid_dis_fee_unt')
                              ,qryset.idx_clean_double(row,'fac_radr_liquid_dis_fee')
                              ,qryset.idx_clean_string(row,'fac_radr_liquid_dis_fee_unt')
                              ,qryset.idx_clean_double(row,'fac_larw_solid_dis_fee')
                              ,qryset.idx_clean_string(row,'fac_larw_solid_dis_fee_unt')
                              ,qryset.idx_clean_double(row,'fac_haz_solid_dis_fee')
                              ,qryset.idx_clean_string(row,'fac_haz_solid_dis_fee_unt')
                              ,qryset.idx_clean_double(row,'fac_haz_liquid_dis_fee')
                              ,qryset.idx_clean_string(row,'fac_haz_liquid_dis_fee_unt')
                              ,qryset.idx_clean_double(row,'fac_msw_solid_dis_fee')
                              ,qryset.idx_clean_string(row,'fac_msw_solid_dis_fee_unt')
                              ,qryset.idx_clean_double(row,'fac_cad_solid_dis_fee')
                              ,qryset.idx_clean_string(row,'fac_cad_solid_dis_fee_unt')
                              ,qryset.idx_clean_double(row,'fac_nhaq_liquid_dis_fee')
                              ,qryset.idx_clean_string(row,'fac_nhaq_liquid_dis_fee_unt')
                              
                              ,qryset.idx(row,'C_D_accepted')
                              ,qryset.idx(row,'MSW_accepted')
                              ,qryset.idx(row,'HW_accepted')
                              ,qryset.idx(row,'LARWRad_accepted')
                              ,qryset.idx(row,'RAD_accepted')
                              ,qryset.idx(row,'NHAW_accepted')
                              
                              ,qryset.idx(row,'date_stamp')
                              ,qryset.idx(row,'source')
                              ,qryset.idx(row,'notes')
                              
                              ,qryset.idx(row,'SHAPE@')
                           )
                        );

            arcpy.AddMessage("User Provided Facilities Layer " + str(i) + " loaded.");

   #########################################################################
   # Step 100
   # Hash ids to load
   #########################################################################
   facility_ids = {}
   count = int(arcpy.GetCount_management(
      haz.network.facilities.dataSource
   ).getOutput(0));

   if count > 0:

      with arcpy.da.SearchCursor(
          in_table    = scratch_ldr
         ,field_names = ['facility_identifier']
      ) as cursor:
         for row in cursor:
            facility_ids[row[0]] = 1;

      arcpy.AddMessage('. hashed ' + str(len(facility_ids)) + ' facility ids');

      int_count = 0;
      with arcpy.da.UpdateCursor(
          in_table    = haz.network.facilities.dataSource
         ,field_names = ['facility_identifier']
      ) as cursor:
         for row in cursor:
            if row[0] in facility_ids:
               cursor.deleteRow();
               int_count += 1;

      arcpy.AddMessage('. updating ' + str(int_count) + ' facility ids');

   #########################################################################
   # Step 110
   # Load facilities from facility fc
   #########################################################################
   if loadDefaultFacilities or                                             \
   (ary_user_defined is not None and len(ary_user_defined) > 0):
      count = int(arcpy.GetCount_management(scratch_ldr).getOutput(0));

      if count == 0:
         arcpy.AddMessage("No facilities qualify for loading.");

      else:
         str_fm = "Name                                     Facility_Name #;"             \
                + "CurbApproach                             # 0;"                         \
                + "Attr_Minutes                             # 0;"                         \
                + "Attr_TravelTime                          # 0;"                         \
                + "Attr_Miles                               # 0;"                         \
                + "Attr_Kilometers                          # 0;"                         \
                + "Attr_TimeAt1KPH                          # 0;"                         \
                + "Attr_WalkTime                            # 0;"                         \
                + "Attr_TruckMinutes                        # 0;"                         \
                + "Attr_TruckTravelTime                     # 0;"                         \
                + "Cutoff_Minutes                           # #;"                         \
                + "Cutoff_TravelTime                        # #;"                         \
                + "Cutoff_Miles                             # #;"                         \
                + "Cutoff_Kilometers                        # #;"                         \
                + "Cutoff_TimeAt1KPH                        # #;"                         \
                + "Cutoff_WalkTime                          # #;"                         \
                + "Cutoff_TruckMinutes                      # #;"                         \
                + "Cutoff_TruckTravelTime                   # #;"                         \
                + "Facility_Identifier                      Facility_Identifier                      #;" \
                + "Facility_TypeID                          Facility_TypeID                          #;" \
                + "Facility_SubtypeIDs                      Facility_SubtypeIDs                      #;" \
                + "Facility_Name                            Facility_Name                            #;" \
                + "Facility_Address                         Facility_Address                         #;" \
                + "Facility_City                            Facility_City                            #;" \
                + "Facility_State                           Facility_State                           #;" \
                + "Facility_Zip                             Facility_Zip                             #;" \
                + "Facility_Telephone                       Facility_Telephone                       #;" \
                + "front_gate_longitude                     front_gate_longitude                     #;" \
                + "front_gate_latitude                      front_gate_latitude                      #;" \
                + "Facility_Waste_Mgt                       Facility_Waste_Mgt                       #;" \
                + "facility_accepts_no_waste                facility_accepts_no_waste                #;" \
                + "fac_radc_solid_dly_cap                   fac_radc_solid_dly_cap                   #;" \
                + "fac_radc_solid_dly_cap_unt               fac_radc_solid_dly_cap_unt               #;" \
                + "fac_radc_liquid_dly_cap                  fac_radc_liquid_dly_cap                  #;" \
                + "fac_radc_liquid_dly_cap_unt              fac_radc_liquid_dly_cap_unt              #;" \
                + "fac_radr_solid_dly_cap                   fac_radr_solid_dly_cap                   #;" \
                + "fac_radr_solid_dly_cap_unt               fac_radr_solid_dly_cap_unt               #;" \
                + "fac_radr_liquid_dly_cap                  fac_radr_liquid_dly_cap                  #;" \
                + "fac_radr_liquid_dly_cap_unt              fac_radr_liquid_dly_cap_unt              #;" \
                + "fac_larw_solid_dly_cap                   fac_larw_solid_dly_cap                   #;" \
                + "fac_larw_solid_dly_cap_unt               fac_larw_solid_dly_cap_unt               #;" \
                + "fac_haz_solid_dly_cap                    fac_haz_solid_dly_cap                    #;" \
                + "fac_haz_solid_dly_cap_unt                fac_haz_solid_dly_cap_unt                #;" \
                + "fac_haz_liquid_dly_cap                   fac_haz_liquid_dly_cap                   #;" \
                + "fac_haz_liquid_dly_cap_unt               fac_haz_liquid_dly_cap_unt               #;" \
                + "fac_msw_solid_dly_cap                    fac_msw_solid_dly_cap                    #;" \
                + "fac_msw_solid_dly_cap_unt                fac_msw_solid_dly_cap_unt                #;" \
                + "fac_cad_solid_dly_cap                    fac_cad_solid_dly_cap                    #;" \
                + "fac_cad_solid_dly_cap_unt                fac_cad_solid_dly_cap_unt                #;" \
                + "fac_nhaq_liquid_dly_cap                  fac_nhaq_liquid_dly_cap                  #;" \
                + "fac_nhaq_liquid_dly_cap_unt              fac_nhaq_liquid_dly_cap_unt              #;" \
                + "fac_radc_solid_tot_acp                   fac_radc_solid_tot_acp                   #;" \
                + "fac_radc_solid_tot_acp_unt               fac_radc_solid_tot_acp_unt               #;" \
                + "fac_radc_liquid_tot_acp                  fac_radc_liquid_tot_acp                  #;" \
                + "fac_radc_liquid_tot_acp_unt              fac_radc_liquid_tot_acp_unt              #;" \
                + "fac_radr_solid_tot_acp                   fac_radr_solid_tot_acp                   #;" \
                + "fac_radr_solid_tot_acp_unt               fac_radr_solid_tot_acp_unt               #;" \
                + "fac_radr_liquid_tot_acp                  fac_radr_liquid_tot_acp                  #;" \
                + "fac_radr_liquid_tot_acp_unt              fac_radr_liquid_tot_acp_unt              #;" \
                + "fac_larw_solid_tot_acp                   fac_larw_solid_tot_acp                   #;" \
                + "fac_larw_solid_tot_acp_unt               fac_larw_solid_tot_acp_unt               #;" \
                + "fac_haz_solid_tot_acp                    fac_haz_solid_tot_acp                    #;" \
                + "fac_haz_solid_tot_acp_unt                fac_haz_solid_tot_acp_unt                #;" \
                + "fac_haz_liquid_tot_acp                   fac_haz_liquid_tot_acp                   #;" \
                + "fac_haz_liquid_tot_acp_unt               fac_haz_liquid_tot_acp_unt               #;" \
                + "fac_msw_solid_tot_acp                    fac_msw_solid_tot_acp                    #;" \
                + "fac_msw_solid_tot_acp_unt                fac_msw_solid_tot_acp_unt                #;" \
                + "fac_cad_solid_tot_acp                    fac_cad_solid_tot_acp                    #;" \
                + "fac_cad_solid_tot_acp_unt                fac_cad_solid_tot_acp_unt                #;" \
                + "fac_nhaq_liquid_tot_acp                  fac_nhaq_liquid_tot_acp                  #;" \
                + "fac_nhaq_liquid_tot_acp_unt              fac_nhaq_liquid_tot_acp_unt              #;" \
                + "fac_radc_solid_dis_fee                   fac_radc_solid_dis_fee                   #;" \
                + "fac_radc_solid_dis_fee_unt               fac_radc_solid_dis_fee_unt               #;" \
                + "fac_radc_liquid_dis_fee                  fac_radc_liquid_dis_fee                  #;" \
                + "fac_radc_liquid_dis_fee_unt              fac_radc_liquid_dis_fee_unt              #;" \
                + "fac_radr_solid_dis_fee                   fac_radr_solid_dis_fee                   #;" \
                + "fac_radr_solid_dis_fee_unt               fac_radr_solid_dis_fee_unt               #;" \
                + "fac_radr_liquid_dis_fee                  fac_radr_liquid_dis_fee                  #;" \
                + "fac_radr_liquid_dis_fee_unt              fac_radr_liquid_dis_fee_unt              #;" \
                + "fac_larw_solid_dis_fee                   fac_larw_solid_dis_fee                   #;" \
                + "fac_larw_solid_dis_fee_unt               fac_larw_solid_dis_fee_unt               #;" \
                + "fac_haz_solid_dis_fee                    fac_haz_solid_dis_fee                    #;" \
                + "fac_haz_solid_dis_fee_unt                fac_haz_solid_dis_fee_unt                #;" \
                + "fac_haz_liquid_dis_fee                   fac_haz_liquid_dis_fee                   #;" \
                + "fac_haz_liquid_dis_fee_unt               fac_haz_liquid_dis_fee_unt               #;" \
                + "fac_msw_solid_dis_fee                    fac_msw_solid_dis_fee                    #;" \
                + "fac_msw_solid_dis_fee_unt                fac_msw_solid_dis_fee_unt                #;" \
                + "fac_cad_solid_dis_fee                    fac_cad_solid_dis_fee                    #;" \
                + "fac_cad_solid_dis_fee_unt                fac_cad_solid_dis_fee_unt                #;" \
                + "fac_nhaq_liquid_dis_fee                  fac_nhaq_liquid_dis_fee                  #;" \
                + "fac_nhaq_liquid_dis_fee_unt              fac_nhaq_liquid_dis_fee_unt              #;" \
                + "C_D_accepted                             C_D_accepted                             #;" \
                + "MSW_accepted                             MSW_accepted                             #;" \
                + "HW_accepted                              HW_accepted                              #;" \
                + "LARWRad_accepted                         LARWRad_accepted                         #;" \
                + "RAD_accepted                             RAD_accepted                             #;" \
                + "NHAW_accepted                            NHAW_accepted                            #;" \
                + "date_stamp                               date_stamp                               #;" \
                + "source                                   source                                   #;" \
                + "notes                                    notes                                    #";

         arcpy.na.AddLocations(
             in_network_analysis_layer      = haz.network.lyr()
            ,sub_layer                      = haz.network.facilities.name
            ,in_table                       = scratch_ldr
            ,field_mappings                 = str_fm
            ,search_tolerance               = override_facility_search_tolerance
            ,sort_field                     = None
            ,search_criteria                = None
            ,match_type                     = None
            ,append                         = truncateFacilities
            ,snap_to_position_along_network = None
            ,snap_offset                    = None
            ,exclude_restricted_elements    = None
            ,search_query                   = None
         );

         arcpy.AddMessage("  Network Facilities loaded.");

   ############################################################################
   # Step 120
   # Clean up and exit
   ############################################################################
   del haz;

   return;


