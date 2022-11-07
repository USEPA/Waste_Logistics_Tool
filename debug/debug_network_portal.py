import json,os,sys;
import copy;
from decimal import Decimal;
import zipfile;
import logging;
import inspect;
import openpyxl;
from types import SimpleNamespace;
import math;

###############################################################################
#
# Usage:
#   Open your ArcGIS Python Command Prompt and cd to the debug folder
#   python debug_network_portal.py > myresults.json
#   Send the myresults.json to EPA for diagnosis
#
###############################################################################

def is_number(s):
   try:
      float(s);
      return True;
   except ValueError:
      return False;
        
def jsonk(k):
   return "\"" + str(k) + "\": ";
   
def jsonv(v):
   if v is None:
      return 'null';
   elif type(v) == bool:
      if v is True:
         return 'true';
      else:
         return 'false';
   elif is_number(v):
      return str(v);
   return "\"" + v.replace('\\','\\\\') + "\"";
   
def jsonkv(k,v):
   return jsonk(k) + jsonv(v);

###############################################################################
message = None;

try:
   import arcpy;
   
except Exception as e:

   if len(e.args) == 1 and e.args[0] == "The Product License has not been initialized.":
      print("{");
      print("    " + jsonkv("arcpy",e.args[0]));
      print("   ," + jsonkv("message","ArcGIS Pro does not appear to be licensed at the moment.  " \
      + "You may need to log into ArcGIS Online (to validate a Named User license) or "            \
      + "access your organization's license server to retrieve a concurrent desktop license."));
      print("{");
      sys.exit(0);
      
   else:
      raise;

###############################################################################
project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)));
sys.path.append(project_root);
import source.util;
source.util.g_prj = source.util.g_pn + os.sep + "AllHazardsWasteLogisticsTool.aprx";

###############################################################################
print("{");
print("    " + jsonkv("arcpy","licensed"));

print("   ," + jsonk("install") + "{")
d = arcpy.GetInstallInfo();
com = " ";
for key,value in d.items():
   print("      " + com + jsonkv(key,value));
   com = ",";
value = arcpy.CheckExtension('Network');
print("      " + com + jsonkv("NetworkAnalyst",value));
print("    }")

###############################################################################
avail_portals = arcpy.ListPortalURLs();
print("   ," + jsonk("availablePortals") + "[");
com = " ";
for item in avail_portals:
   print("      " + com + jsonv(item));
   com = ","
print("   ]")

active_portal = arcpy.GetActivePortalURL();
print("   ," + jsonkv("activePortal",active_portal));

portalinfo = None;
if active_portal is not None:
   portalinfo = arcpy.GetPortalInfo(active_portal);

###############################################################################
portal_desc = arcpy.GetPortalDescription();
username    = None;
credits     = None;
level       = None;
portal_url  = None;
is_portal   = None;
portal_name = None;
loggedin    = False;
   
if 'user' in portal_desc:
   loggedin = True;
   
   if 'username' in portal_desc['user']:
      username = portal_desc['user']['username'];
   
   if 'availableCredits' in portal_desc['user']:
      credits  = portal_desc['user']['availableCredits'];
   else:
      if 'availableCredits' in portal_desc:
         credits  = portal_desc['availableCredits'];
         
   if 'level' in portal_desc['user']:
      level    = portal_desc['user']['level']

else:
   message = "You do not appear to be logged into an active portal.  If you wish to use portal resources please log into and set the desired portal to be active."

if 'allSSL' in portal_desc and 'portalHostname' in portal_desc:
   if portal_desc['allSSL'] is True:
      portal_url = "https://" + portal_desc['portalHostname'];
   else:
      portal_url = "http://" + portal_desc['portalHostname'];
   
   if 'isPortal' in portal_desc:
      is_portal = portal_desc['isPortal'];
   if 'portalName' in portal_desc:
      portal_name = portal_desc['portalName'];  
   
travel_modes = None;
if portal_url is not None:
   portal_url   = portal_url.rstrip('/').lower();
   
   try: 
      travel_modes = arcpy.na.GetTravelModes(active_portal);
   except:
      travel_modes = None;
      loggedin     = False;
   
print("   ," + jsonkv("loggedInActive",loggedin));
print("   ," + jsonkv("portalName",portal_name));
print("   ," + jsonkv("isLocalPortal",is_portal));
print("   ," + jsonkv("username",username));
print("   ," + jsonkv("availableCredits",credits));
print("   ," + jsonkv("agoUserLevel",level));
   
if travel_modes is None:
   print("   ," + jsonkv("travelModes",travel_modes));
else:
   print("   ," + jsonk("travelModes") + "{");
   com = " ";
   for key,value in travel_modes.items():
      print("      " + com + jsonk(key) + "{")
      com2 = " ";
      print("         " + com2 + jsonkv("type",value.name));
      com2 = ",";
      print("         " + com2 + jsonkv("description",value.description));
      com2 = ",";
      print("         " + com2 + jsonkv("impedanceAttributeName",value.impedance));
      com2 = ",";
      print("         " + com2 + jsonkv("timeAttributeName",value.timeAttributeName));
      com2 = ",";
      print("         " + com2 + jsonkv("distanceAttributeName",value.distanceAttributeName));
      com2 = ",";
      print("         " + com2 + jsonk("restrictionAttributeNames") + "[");
      com3 = " ";
      for item in value.restrictions:
         print("            " + com3 + jsonv(item));
         com3 = ","
      print("         ]");
      print("         " + com2 + jsonk("attributeParameterValues") + "[");
      com4 = " ";
      for key2,value2 in value.attributeParameters.items():
         com5 = " ";
         print("            " + com4 + "{");
         print("               " + com5 + jsonkv("attributeName",key2[0]));
         com5 = ",";
         print("               " + com5 + jsonkv("parameterName",key2[1]));
         com5 = ",";
         print("               " + com5 + jsonkv("value",value2));
         com5 = ",";
         com4 = ",";
         print("            }");
      print("         ]");
      print("         " + com2 + jsonkv("useHierarchy",value.useHierarchy));
      com2 = ",";
      print("         " + com2 + jsonkv("uturnAtJunctions",value.uTurns));
      com2 = ",";
      print("         " + com2 + jsonkv("simplificationTolerance",value.simplificationTolerance));
      com2 = ",";
      com = ",";
      print("      }");
   print("   }");

###############################################################################
aprx = arcpy.mp.ArcGISProject(source.util.g_prj);
map  = aprx.listMaps("*")[0];

print("   ," + jsonkv("project",source.util.g_prj));
print("   ," + jsonkv("map",map.name));

###############################################################################
print("   ," + jsonkv("message",message));
print("}");

