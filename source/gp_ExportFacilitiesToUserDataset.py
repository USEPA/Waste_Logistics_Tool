import arcpy,os,sys;
import requests,json,csv;
import source.util;

###############################################################################
import importlib
importlib.reload(source.util);

def execute(self,parameters,messages):

   #...........................................................................
   haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

   #...........................................................................
   dest_fc = parameters[1].valueAsText;
   qclause = parameters[2].valueAsText;
   dest_fc_path,dest_fc_name = os.path.split(dest_fc);

   #...........................................................................
   arcpy.env.overwriteOutput = True
   if arcpy.Exists(dest_fc):
      arcpy.Delete_management(dest_fc);

   #...........................................................................
   arcpy.CreateFeatureclass_management(
       out_path          = dest_fc_path
      ,out_name          = dest_fc_name
      ,geometry_type     = "POINT"
      ,has_m             = "DISABLED"
      ,has_z             = "DISABLED"
      ,spatial_reference = arcpy.SpatialReference(4326)
      ,config_keyword    = None
   );

   arcpy.management.AddFields(
       dest_fc
      ,[
          ['facility_identifier'             ,'TEXT'  ,'Facility_Identifier'                          ,255, None,'']
         ,['facility_typeid'                 ,'LONG'  ,'Facility TypeID'                              ,None,None,'']
         ,['facility_subtypeids'             ,'TEXT'  ,'Facility SubtypeIDs'                          ,255, None,'']
         ,['facility_name'                   ,'TEXT'  ,'Facility_Name'                                ,255, None,'']
         ,['facility_address'                ,'TEXT'  ,'Facility_Address'                             ,255, None,'']
         ,['facility_city'                   ,'TEXT'  ,'Facility_City'                                ,255, None,'']
         ,['facility_state'                  ,'TEXT'  ,'Facility_State'                               ,255, None,'']
         ,['facility_zip'                    ,'TEXT'  ,'Facility_Zip'                                 ,255, None,'']
         ,['facility_telephone'              ,'TEXT'  ,'Facility_Telephone'                           ,255, None,'']
         ,['front_gate_longitude'            ,'DOUBLE','Front_Gate_Longitude'                         ,None,None,'']
         ,['front_gate_latitude'             ,'DOUBLE','Front_Gate_Latitude'                          ,None,None,'']
         ,['facility_waste_mgt'              ,'TEXT'  ,'Facility_Waste_Mgt'                           ,255, None,'']
         
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

   arcpy.management.AddIndex(
       in_table   = dest_fc
      ,fields     = 'facility_identifier'
      ,index_name = 'facility_identifier_idx'
   );

   #...........................................................................
   flds = [
       'facility_identifier'
      ,'facility_typeid'
      ,'facility_subtypeids'
      ,'facility_name'
      ,'facility_address'
      ,'facility_city'
      ,'facility_state'
      ,'facility_zip'
      ,'facility_telephone'
      ,'front_gate_longitude'
      ,'front_gate_latitude'
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
      
      ,'date_stamp'
      ,'source'
      ,'notes'
      ,'SHAPE@'
    ];

   with arcpy.da.SearchCursor(
       in_table     = haz.network.facilities.dataSource
      ,field_names  = flds
      ,where_clause = qclause
   ) as cursor_in:

      with arcpy.da.InsertCursor(
          in_table     = dest_fc
         ,field_names  = flds
      ) as cursor_out:

         idx = 0;
         for row in cursor_in:
            cursor_out.insertRow(row);
            idx += 1;

   arcpy.AddMessage("Exported " + str(idx) + " records to " + dest_fc_name);

   #...........................................................................

   return None;
