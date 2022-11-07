import arcpy,os,sys;
import requests,json;
from datetime import datetime;
from urllib3.exceptions import InsecureRequestWarning;
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning);

import source.util;

###############################################################################
import importlib
importlib.reload(source.util);

def execute(self,parameters,messages):

   fc = os.path.join(source.util.g_pn,"data","IWasteVintage_Remote.json");
 
   #########################################################################
   payload = fetch_json();  
      
   with open(fc,'w') as file:
      json.dump(payload,file,indent=3);
      
   return None;
   
def fetch_json(json_d=None):

   if json_d is None:
      json_d = source.util.load_settings();
   
   source.util.dzlog("settings read successfully.");
   iwasteq = json_d["IWasteImport"]["IWasteDisposalFacilitySubtypes"];
   acceptedMaps = json_d["IWasteImport"]["acceptedMaps"];
   
   response = requests.get(iwasteq,verify=False);
   j_data = response.json();
      
   payload = {
       "timestamp"     : datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
      ,"vintages"      : []
      ,"wasteGroupings": []
   };
   
   for item in j_data:
      payload["vintages"].append(
         {
             "shortName"             : item["shortName"]
            ,"disposalFacilityTypeId": item["disposalFacilityTypeId"]
            ,"facilitySubtypeId"     : item["id"]
            ,"dateLastUpdate"        : item["dateLastUpdate"]
         }
      );
      
   for item in acceptedMaps:
      obj = {
          "wasteType"         : item["WasteType"]
         ,"facilitySubtypeIds": item["facilitySubtypeIDs"]
         ,"dateLastUpdate"    : []
      }
      
      for vtg in payload["vintages"]:
         if vtg["facilitySubtypeId"] in item["facilitySubtypeIDs"]:
            obj["dateLastUpdate"].append(vtg["dateLastUpdate"]);
            
      obj["dateLastUpdate"] = sorted(set(obj["dateLastUpdate"]));
      payload["wasteGroupings"].append(obj); 
      
   return payload;


   