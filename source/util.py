import arcpy,os,sys;
import json,zipfile;
import logging,inspect,traceback;

g_prj     = "CURRENT";
g_mapname = "AllHazardsWasteLogisticsMap";
g_aprx    = None;
g_logging = logging.DEBUG;
g_pn      = os.path.dirname(os.path.dirname(os.path.realpath(__file__)));

###############################################################################
def str2ary(pin):

   if pin is None:
      return [];
      
   if pin.find(',') > 0:
      return list(map(int,pin.split(',')));
   
   return [int(pin)];
   
###############################################################################
def ary2str(pin):

   lst = [str(e) for e in pin];
   return ",".join(lst);
   
###############################################################################
def mediumMap(pin):

   medium_map = {
       "solid":        "Volume Solid"
      ,"Volume Solid": "Volume Solid"
      ,"liquid":       "Volume Liquid"
      ,"Volume Liquid":"Volume Liquid"
   }  
   
   if pin is None or pin == "" or pin == " ":
      return None;
      
   else:
   
      if pin in medium_map:
         return medium_map[pin];

      else:
         raise Exception('err: ' + str(pin));
         
###############################################################################
def modeMap(pin):

   medium_map = {
       "road":      "Road"
      ,"Road":      "Road"
      ,"rail":      "Rail"
      ,"Rail":      "Rail"
   }  
   
   if pin is None or pin == "" or pin == " ":
      return None;
      
   else:
   
      if pin in medium_map:
         return medium_map[pin];

      else:
         raise Exception('err: ' + str(pin));
         
###############################################################################
def fetch_lyr(lyrname):
   global g_aprx;
   
   if g_aprx is not None:
      aprx = g_aprx;
      
   else:
      try:
         g_aprx = arcpy.mp.ArcGISProject(g_prj);
         aprx = g_aprx;         
      except Exception as e:
         dzlog_e(sys.exc_info(),'ERROR');
      raise;
      
   map = aprx.listMaps(g_mapname)[0];

   for lyr in map.listLayers():

      if lyr.supports("name") and lyr.name == lyrname:
         return lyr;
         
   return None;

###############################################################################
def polygons_to_points(in_features,out_feature_class):

   pt = os.path.dirname(out_feature_class);
   fc = os.path.basename(out_feature_class);
   ds = arcpy.Describe(in_features);
   sr = ds.spatialReference;

   if arcpy.Exists(out_feature_class):
      arcpy.Delete(out_feature_class);

   arcpy.CreateFeatureclass_management(pt,fc,"POINT",template=in_features,spatial_reference=sr);
   fds = ['SHAPE@'] + [f.name for f in arcpy.ListFields(out_feature_class) if f.type not in ('OID','Geometry')];

   with arcpy.da.InsertCursor(out_feature_class,fds) as insert_rows:
      with arcpy.da.SearchCursor(in_features,fds) as read_rows:

         for row in read_rows:
            insert_rows.insertRow(
               (arcpy.PointGeometry(row[0].centroid),) + row[1:]
            );

   return out_feature_class;

###############################################################################
def converter(in_unit,in_value,unit_system):

   if in_value is None:
      return (None,None);
      
   if in_unit == 'zeroed':
      return (0,"zeroed");
   
   if unit_system == "hr":

      if in_unit == "hr":
         return (in_value,"hr");

      elif in_unit == "min":
         return ((in_value / 60),"hr");

   elif unit_system == "Metric":

      # Volume Liquid = L
      # Volume Solid  = m3
      # Area          = sq m
      # Mass          = kg
      # Length        = km

      if in_unit == "L"           \
      or in_unit == "m3"          \
      or in_unit == "sq m"        \
      or in_unit == "kg"          \
      or in_unit == "km"          \
      or in_unit == "cost_per_km" \
      or in_unit == "cost_per_m3" \
      or in_unit == "cost_per_L":
         return (in_value,in_unit);

      elif in_unit == "gal":
         return (converto(in_unit,in_value,"L"),"L");

      elif in_unit == "yd3":
         return (converto(in_unit,in_value,"m3"),"m3");

      elif in_unit == "sq yd":
         return (converto(in_unit,in_value,"sq m"),"sq m");

      elif in_unit == "lbs":
         return (converto(in_unit,in_value,"kg"),"kg");

      elif in_unit == "mi" \
      or   in_unit == "m":
         return (converto(in_unit,in_value,"km"),"km");

      elif in_unit == "cost_per_mi":
         return (converto(in_unit,in_value,"cost_per_km"),"cost_per_km");

      elif in_unit == "cost_per_yd3":
         return (converto(in_unit,in_value,"cost_per_m3"),"cost_per_m3");

      elif in_unit == "cost_per_gal":
         return (converto(in_unit,in_value,"cost_per_L"),"cost_per_L");

   elif unit_system == "US Customary":

      # Volume Liquid = gal
      # Volume Solid  = yd3
      # Area          = sq yd
      # Mass          = lbs
      # Length        = mi

      if in_unit == "gal"          \
      or in_unit == "yd3"          \
      or in_unit == "sq yd"        \
      or in_unit == "lbs"          \
      or in_unit == "mi"           \
      or in_unit == "cost_per_mi"  \
      or in_unit == "cost_per_yd3" \
      or in_unit == "cost_per_gal":
         return (in_value,in_unit);

      elif in_unit == "L":
         return (converto(in_unit,in_value,"gal"),"gal");

      elif in_unit == "m3":
         return (converto(in_unit,in_value,"yd3"),"yd3");

      elif in_unit == "sq m":
         return (converto(in_unit,in_value,"sq yd"),"sq yd");

      elif in_unit == "kg":
         return (converto(in_unit,in_value,"lbs"),"lbs");

      elif in_unit == "km" \
      or   in_unit == "m":
         return (converto(in_unit,in_value,"mi"),"mi");

      elif in_unit == "cost_per_km":
         return (converto(in_unit,in_value,"cost_per_mi"),"cost_per_mi");

      elif in_unit == "cost_per_m3":
         return (converto(in_unit,in_value,"cost_per_yd3"),"cost_per_yd3");

      elif in_unit == "cost_per_L":
         return (converto(in_unit,in_value,"cost_per_gal"),"cost_per_gal");

   raise arcpy.ExecuteError("Error. unimplemented units <" + str(in_unit) + " " + str(unit_system) + ">");

###############################################################################
def converto(in_unit,in_value,out_unit):

   if in_unit == out_unit:
      return in_value;

   # Volume Liquid
   elif in_unit == "L" and out_unit == "gal":
      return in_value * 0.264172;

   elif in_unit == "gal" and out_unit == "L":
      return in_value * 3.78541;

   # Volume Solid
   if in_unit == "m3" and out_unit == "yd3":
      return in_value * 1.30795;

   if in_unit == "yd3" and out_unit == "m3":
      return in_value * 0.764555;

   # Area
   if in_unit == "sq m" and out_unit == "sq yd":
      return in_value * 1.19599;

   elif in_unit == "sq yd" and out_unit == "sq m":
      return in_value * 0.836127;

   # Mass
   if in_unit == "kg" and out_unit == "lbs":
      return in_value * 2.20462;

   elif in_unit == "lbs" and out_unit == "kg":
      return in_value * 0.453592;

   # Length
   elif in_unit == "km" and out_unit == "mi":
      return in_value * 0.621371;

   elif in_unit == "m"  and out_unit == "mi":
      return in_value * 0.000621371;

   elif in_unit == "mi" and out_unit == "km":
      return in_value * 1.60934;

   elif in_unit == "m"  and out_unit == "km":
      return in_value * 0.001;

   # Cost per Distance
   elif in_unit == "cost_per_mi" and out_unit == "cost_per_km":
      return in_value / 1.60934;

   elif in_unit == "cost_per_km" and out_unit == "cost_per_mi":
      return in_value / 0.621371;

   # Cost per Volume
   elif in_unit == "cost_per_m3" and out_unit == "cost_per_yd3":
      return in_value / 1.30795;

   elif in_unit == "cost_per_yd3" and out_unit == "cost_per_m3":
      return in_value / 0.764555;

   elif in_unit == "cost_per_L" and out_unit == "cost_per_gal":
      return in_value / 0.264172;

   elif in_unit == "cost_per_gal" and out_unit == "cost_per_L":
      return in_value / 3.78541;

   raise arcpy.ExecuteError("Error. unimplemented units");

###############################################################################
def buffer_extent(extent,percent):

   xsize = int(abs(extent.lowerLeft.X - extent.lowerRight.X));
   ysize = int(abs(extent.lowerLeft.Y - extent.upperLeft.Y));

   if xsize > ysize:
      extBuffDist = xsize * percent;
   else:
      extBuffDist = ysize * percent;

   origExtentPts = arcpy.Array();
   origExtentPts.add(extent.lowerLeft);
   origExtentPts.add(extent.lowerRight);
   origExtentPts.add(extent.upperRight);
   origExtentPts.add(extent.upperLeft);
   origExtentPts.add(extent.lowerLeft);

   polygonTmp1 = arcpy.Polygon(
       inputs            = origExtentPts
      ,spatial_reference = extent.spatialReference
   );
   polygonTmp2 = polygonTmp1.buffer(extBuffDist);
   new_extent  = polygonTmp2.extent;

   return new_extent;
   
###############################################################################
def load_settings(force_check=True):

   filename = os.path.join(g_pn,"settings.json");

   if not os.path.exists(filename):
      
      if force_check:
         raise arcpy.ExecuteError("Error unable to read settings.json");
         
      else:
         return None;

   with open(filename,"r") as json_f:
      json_d = json.load(json_f);

   return json_d;

###############################################################################
def portal_info():

   rez = {
       'username': None
      ,'portal_url': None
      ,'availableCredits': None
      ,'default_closestFacility': None
      ,'default_closestFacility_url': None
      ,'default_closestFacility_defaultTravelMode': None
      ,'token': None
      ,'isAGO': False
   }
   
   try:
      portal_desc = arcpy.GetPortalDescription();
   except:
      msg = 'describing the portal connection failed, internet may be down.';
      dzlog(msg);
      rez['error'] = msg;
      return rez;
      
   if 'user' in portal_desc:
   
      if 'username' in portal_desc['user']:
         rez['username'] = portal_desc['user']['username'];
         
      if 'availableCredits' in portal_desc['user']:
         rez['availableCredits'] = portal_desc['user']['availableCredits'];

   try:
      rez['portal_url'] = arcpy.GetActivePortalURL();
   except:
      rez['portal_url'] = None;
   
   if rez['portal_url'] is None:
      if 'allSSL' in portal_desc and 'portalHostname' in portal_desc:
      
         if portal_desc['allSSL'] is True:
            rez['portal_url'] = "https://" + portal_desc['portalHostname'];
         else:
            rez['portal_url'] = "http://" + portal_desc['portalHostname'];
      
   if 'helperServices' in portal_desc:
   
      if 'closestFacility' in portal_desc['helperServices']:
      
         rez['default_closestFacility_url'] = portal_desc['helperServices']['closestFacility']['url'];
         rez['default_closestFacility_defaultTravelMode'] = portal_desc['helperServices']['closestFacility']['defaultTravelMode'];
         
         if 'portalHostname' in portal_desc:
         
            if portal_desc['portalHostname'] == 'www.arcgis.com':
               rez['isAGO'] = True;
      
   try:
      rez['token'] = arcpy.GetSigninToken();
   except:
      rez['token'] = None;
   
   return rez;
   
###############################################################################
def clean_string(value):

   if value is None or str(value) == "" or str(value) == " ":
      return None;
      
   return value;
   
###############################################################################
def clean_boo(value):

   if value is None or str(value) == "" or str(value) == " ":
      return None;
      
   elif str(value) in ['True','true','TRUE','1']:
      return True;
      
   elif str(value) in ['False','false','FALSE','0']:
      return False;
      
   else:
      raise Exception('err');
      
###############################################################################
def clean_double(value):

   if value is None or str(value) == "" or str(value) == " ":
      return None;
      
   try:
      v = float(value);

   except ValueError:
      v = None;

   return v;
   
###############################################################################
def clean_id(value):

   if value is None:
      return None;
      
   if len(value) > 255:
      value = value[0:255];
      
   value = value.strip();
   
   value = value.strip("'");
   
   value = value.replace('"','');
   
   value = value.replace(';','');
   
   return value;

###############################################################################
def sql_quote(value):

   if value is None:
      return None;
      
   value = value.replace("'","''");
   
   return "'" + value + "'";

###############################################################################
def sniff_editing_state(workspace=None):

   if workspace is None:
      workspace = arcpy.env.workspace;
    
   boo_check = False;
   
   try:
      z = arcpy.da.Editor(workspace);
      z.startEditing(False,False);
      z.stopEditing(False);
   
   except:
      boo_check = True;
   
   return boo_check;
   
###############################################################################
def recalculate_extent(fc):

   if arcpy.CheckProduct("ArcInfo") == "Available"                            \
   or arcpy.CheckProduct("ArcEditor") == "Available":
      arcpy.RecalculateFeatureClassExtent_management(fc);
      
   else:
      arcpy.CompressFileGeodatabaseData_management(fc);
      arcpy.UncompressFileGeodatabaseData_management(fc);
      
###############################################################################
def dzlog_e(e_info,lvl='info',force=False,reset=False,arcmsg=False):

   exc_type,exc_value,exc_traceback = e_info;
   msg_list = traceback.format_exception(exc_type,exc_value,exc_traceback);
   msg_log = "   ".join(msg_list);
    
   dzlog(
       msg    = msg_log
      ,lvl    = lvl
      ,force  = force
      ,reset  = reset
      ,arcmsg = arcmsg
   );
   
###############################################################################
def dzlog(msg,lvl='info',force=False,reset=False,arcmsg=False):

   callerframerecord = inspect.stack()[1];
   frame   = callerframerecord[0];
   info    = inspect.getframeinfo(frame);
   msg_log = msg + "\n   " + info.function + ": " + str(info.lineno);
   lfmat   = '%(asctime)-15s: %(message)s ';
   
   ##........................................................................##
   if arcmsg:
      arcpy.AddMessage(msg_log);

   ##........................................................................##
   if reset:

      while len(logging.root.handlers) > 0:
         logging.root.removeHandler(logging.root.handlers[-1]);

   ##........................................................................##
   if len(logging.root.handlers) == 0 or reset:

      logging.basicConfig(
          filename = g_pn + os.sep + 'toolbox.log'
         ,format   = lfmat
         ,level    = g_logging
      );

   ##........................................................................##
   if force:

      if lvl.lower() == 'debug':
         level = logging.DEBUG;

      elif lvl.lower() == 'info':
         level = logging.INFO;

      elif lvl.lower() == 'warning':
         level = logging.WARNING;

      elif lvl.lower() == 'error':
         level = logging.ERROR;

      elif lvl.lower() == 'critical':
         level = logging.CRITICAL;

      if not logging.getLogger().isEnabledFor(level):

         while len(logging.root.handlers) > 0:
            logging.root.removeHandler(logging.root.handlers[-1]);

         logging.basicConfig(
             filename = g_pn + os.sep + 'toolbox.log'
            ,format   = lfmat
            ,level    = level
         );

   ##........................................................................##
   if lvl.lower() == 'debug':
      logging.debug(msg_log);

   elif lvl.lower() == 'info':
      logging.info(msg_log);

   elif lvl.lower() == 'warning':
      logging.warning(msg_log);

   elif lvl.lower() == 'error':
      logging.error(msg_log);

   elif lvl.lower() == 'critical':
      logging.critical(msg_log); 

      
  