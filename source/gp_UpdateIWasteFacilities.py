import arcpy,os,sys;
import requests,json,csv;
from urllib3.exceptions import InsecureRequestWarning;
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning);
import source.util;
import source.gp_QueryIWasteFacilities;

###############################################################################
import importlib
importlib.reload(source.util);
importlib.reload(source.gp_QueryIWasteFacilities);

def execute(self,parameters,messages):

   json_d = source.util.load_settings();
   source.util.dzlog("settings read successfully.");
   
   #########################################################################
   vintage = source.gp_QueryIWasteFacilities.fetch_json(json_d=json_d);
   
   #########################################################################
   iwasteq           = json_d["IWasteImport"]["IWasteFacilitiesExport"];
   acceptedMaps      = json_d["IWasteImport"]["acceptedMaps"];
   
   geojson = {
       "type" : "FeatureCollection"
      ,"features" : []
   };
   with requests.get(
       iwasteq
      ,stream = True
      ,verify = False
   ) as r:
      lines = (line.decode('utf-8') for line in r.iter_lines())
      for row in csv.reader(lines):
         
         if row[0] == '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">':
            arcpy.AddMessage("I-Waste API not responding, try again later.");
            raise Exception("I-Waste API not responding, try again later.");
         
         if row[0] != 'id' and len(row) > 1:
            
            record_id     = str(row[0]);
            name          = row[1];
            streetAddress = row[2];
            city          = row[3];
            county        = row[4];
            stateCode     = row[5];
            epaRegion     = row[6]
            zipCode       = row[7];
            
            latitude      = row[8];
            longitude     = row[9];
            
            contactName   = row[10];
            contactPhone  = row[11];
            sourceId      = row[12];
            
            facilitySubtypeIDs = str(row[14]);
            facilityType  = int(row[16]);
            
            if longitude is None or latitude is None \
            or longitude == ""   or latitude == ""   \
            or float(longitude)  > 180  or float(longitude) < -180 \
            or float(latitude)   > 90   or float(latitude)  < -90:
               None;
               
            else:

               coor = [float(longitude),float(latitude)];
               prop = {
                   "facility_identifier"                      : record_id
                  ,"facility_typeid"                          : facilityType
                  ,"facility_subtypeids"                      : facilitySubtypeIDs
                  ,"facility_name"                            : name
                  ,"facility_address"                         : streetAddress
                  ,"facility_city"                            : city
                  ,"facility_state"                           : stateCode
                  ,"facility_zip"                             : zipCode
                  ,"facility_telephone"                       : contactPhone
                  ,"front_gate_longitude"                     : None
                  ,"front_gate_latitude"                      : None
                  ,"facility_waste_mgt"                       : None
                  
                  ,"facility_accepts_no_waste"                : None
                  ,"fac_radc_solid_dly_cap"                   : None
                  ,"fac_radc_solid_dly_cap_unt"               : None
                  ,"fac_radc_liquid_dly_cap"                  : None
                  ,"fac_radc_liquid_dly_cap_unt"              : None
                  ,"fac_radr_solid_dly_cap"                   : None
                  ,"fac_radr_solid_dly_cap_unt"               : None
                  ,"fac_radr_liquid_dly_cap"                  : None
                  ,"fac_radr_liquid_dly_cap_unt"              : None
                  ,"fac_larw_solid_dly_cap"                   : None
                  ,"fac_larw_solid_dly_cap_unt"               : None
                  ,"fac_haz_solid_dly_cap"                    : None
                  ,"fac_haz_solid_dly_cap_unt"                : None
                  ,"fac_haz_liquid_dly_cap"                   : None
                  ,"fac_haz_liquid_dly_cap_unt"               : None
                  ,"fac_msw_solid_dly_cap"                    : None
                  ,"fac_msw_solid_dly_cap_unt"                : None
                  ,"fac_cad_solid_dly_cap"                    : None
                  ,"fac_cad_solid_dly_cap_unt"                : None
                  ,"fac_nhaq_liquid_dly_cap"                  : None
                  ,"fac_nhaq_liquid_dly_cap_unt"              : None
                  ,"fac_radc_solid_tot_acp"                   : None
                  ,"fac_radc_solid_tot_acp_unt"               : None
                  ,"fac_radc_liquid_tot_acp"                  : None
                  ,"fac_radc_liquid_tot_acp_unt"              : None
                  ,"fac_radr_solid_tot_acp"                   : None
                  ,"fac_radr_solid_tot_acp_unt"               : None
                  ,"fac_radr_liquid_tot_acp"                  : None
                  ,"fac_radr_liquid_tot_acp_unt"              : None
                  ,"fac_larw_solid_tot_acp"                   : None
                  ,"fac_larw_solid_tot_acp_unt"               : None
                  ,"fac_haz_solid_tot_acp"                    : None
                  ,"fac_haz_solid_tot_acp_unt"                : None
                  ,"fac_haz_liquid_tot_acp"                   : None
                  ,"fac_haz_liquid_tot_acp_unt"               : None
                  ,"fac_msw_solid_tot_acp"                    : None
                  ,"fac_msw_solid_tot_acp_unt"                : None
                  ,"fac_cad_solid_tot_acp"                    : None
                  ,"fac_cad_solid_tot_acp_unt"                : None
                  ,"fac_nhaq_liquid_tot_acp"                  : None
                  ,"fac_nhaq_liquid_tot_acp_unt"              : None
                  ,"fac_radc_solid_dis_fee"                   : None
                  ,"fac_radc_solid_dis_fee_unt"               : None
                  ,"fac_radc_liquid_dis_fee"                  : None
                  ,"fac_radc_liquid_dis_fee_unt"              : None
                  ,"fac_radr_solid_dis_fee"                   : None
                  ,"fac_radr_solid_dis_fee_unt"               : None
                  ,"fac_radr_liquid_dis_fee"                  : None
                  ,"fac_radr_liquid_dis_fee_unt"              : None
                  ,"fac_larw_solid_dis_fee"                   : None
                  ,"fac_larw_solid_dis_fee_unt"               : None
                  ,"fac_haz_solid_dis_fee"                    : None
                  ,"fac_haz_solid_dis_fee_unt"                : None
                  ,"fac_haz_liquid_dis_fee"                   : None
                  ,"fac_haz_liquid_dis_fee_unt"               : None
                  ,"fac_msw_solid_dis_fee"                    : None
                  ,"fac_msw_solid_dis_fee_unt"                : None
                  ,"fac_cad_solid_dis_fee"                    : None
                  ,"fac_cad_solid_dis_fee_unt"                : None
                  ,"fac_nhaq_liquid_dis_fee"                  : None
                  ,"fac_nhaq_liquid_dis_fee_unt"              : None
                  
                  ,"C_D_accepted"                             : False
                  ,"MSW_accepted"                             : False
                  ,"HW_accepted"                              : False
                  ,"LARWRad_accepted"                         : False
                  ,"RAD_accepted"                             : False
                  ,"NHAW_accepted"                            : False
                  
                  ,"date_stamp"                               : None
                  ,"source"                                   : "I-Waste: " + sourceId
                  ,"notes"                                    : None
               }
               
               boo_write = False;
               for item in source.util.str2ary(facilitySubtypeIDs):
                  for wts in acceptedMaps:
                     if item in wts["facilitySubtypeIDs"]:
                        prop[wts["accepted"]] = True;
                        boo_write = True;
               
               if boo_write:
                  geojson["features"].append(
                     {
                         "type" : "Feature"
                        ,"geometry" : {
                            "type"       : "Point"
                           ,"coordinates": coor
                         }
                        ,"properties": prop  
                     }
                  );
            
   #########################################################################
   fc = os.path.join(source.util.g_pn,"data","IWasteFacilities.json");
   with open(fc,'w') as file:
      json.dump(geojson,file,indent=3);
   
   #########################################################################
   fc = os.path.join(source.util.g_pn,"data","IWasteVintage_Remote.json");
   if arcpy.Exists(fc):
      arcpy.Delete_management(fc);
   
   fc = os.path.join(source.util.g_pn,"data","IWasteVintage_Local.json");
   with open(fc,'w') as file:
      json.dump(vintage,file,indent=3);
   
   arcpy.AddMessage("I-Waste updated successfully.");
   
   return None;
   