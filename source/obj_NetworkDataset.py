import arcpy,os,json,requests;

import source.util;

###############################################################################
import importlib
importlib.reload(source.util);

###############################################################################
def convertDataTypes(pin):

   if pin.lower() in ['double','esrinadtdouble']:
      return 'double';
      
   elif pin.lower() in ['integer','esrinadtinteger']:
      return 'integer';
      
   elif pin.lower() in ['boolean','esrinadtboolean']:
      return 'boolean';
      
   else:
      return pin;
      
###############################################################################
def convertUnits(pin):

   if pin.lower() in ["esrinauminutes","minutes"]:
      return ("min","time");
      
   elif pin.lower() in ["esrinaumeters","meters"]:
      return ("m","distance");
      
   elif pin.lower() in ["esrinaukilometers","kilometers"]:
      return ("km","distance");
      
   elif pin.lower() in ["esrinaumiles","miles"]:
      return ("mi","distance");
      
   else:
      return (pin,None);
         
###############################################################################
def describeRemoteNetworkDataset(url):

   value = {
       'networkDatasetName'  : None
      ,'defaultTravelMode'   : None
      ,'travelModeNames'     : []
      ,'supportedTravelModes': {}
      ,'networkDatasetCosts' : {}
      ,'allCostNames'        : []
      ,'distanceCostNames'   : []
      ,'timeCostNames'       : []
      ,'integerCostNames'    : []
   }
   
   unitHash = {};
   
   try:
      token = arcpy.GetSigninToken();
   except:
      token = None;
   
   if token is not None:
      url = url + '?f=json&token=' + token['token'];
   else:
      url = url + '?f=json';
   
   response = requests.get(url);
   rj       = response.json();
   
   if rj is None or 'supportedTravelModes' not in rj:
      source.util.dzlog(str(rj));
      source.util.dzlog('portal network dataset has no travel modes');
      return rj;
   
   value['networkDatasetName'] = rj['networkDataset']['name'];
   
   for item in rj['networkDataset']['networkAttributes']:
      if item["usageType"] == "esriNAUTCost":
         unit,utype = convertUnits(item['units']);
         
         value['allCostNames'].append(item['name']);
         if utype == 'distance':
            value['distanceCostNames'].append(item['name']);
         elif utype == 'time':
            value['timeCostNames'].append(item['name']);
            
         dt = convertDataTypes(item['dataType']);
         value['networkDatasetCosts'][item['name']] = {
             "name"                  : item['name']
            ,"dataType"              : dt
            ,"unit"                  : unit
            ,"utype"                 : utype
         };
         unitHash[item['name']] = unit;
         
         if dt == 'integer':
            value['integerCostNames'].append(item['name']);
         
   for item in rj['supportedTravelModes']:
      value['travelModeNames'].append(item['name']);
      value['supportedTravelModes'][item['name']] = {
         "name"                  : item['name']
         ,"impedanceAttributeName": item['impedanceAttributeName']
         ,"impedanceAttributeUnit": unitHash[item['impedanceAttributeName']]
         ,"distanceAttributeName" : item['distanceAttributeName']
         ,"distanceAttributeUnit" : unitHash[item['distanceAttributeName']]
         ,"timeAttributeName"     : item['timeAttributeName']
         ,"timeAttributeUnit"     : unitHash[item['timeAttributeName']]                   
      }
      if rj['defaultTravelMode'] == item['itemId']:
         value['defaultTravelMode'] = item['name'];
         
   return value;

###############################################################################
def describePortalHelperNetworkDataset():

   portal_desc = arcpy.GetPortalDescription();
   
   if portal_desc is None or 'helperServices' not in portal_desc:
      raise Exception('portal is not valid');
   
   url = portal_desc['helperServices']['closestFacility']['url'];
   
   return describeRemoteNetworkDataset(url);

###############################################################################
def describeFileNetworkDataset(dataset):

   value = {
       'networkDatasetName'  : None
      ,'defaultTravelMode'   : None
      ,'travelModeNames'     : []
      ,'supportedTravelModes': {}
      ,'networkDatasetCosts' : {}
      ,'allCostNames'        : []
      ,'distanceCostNames'   : []
      ,'timeCostNames'       : []
      ,'integerCostNames'    : []
   }
   
   dataset = dataset.rstrip('/').lower();
   
   unitHash = {};
   
   if not arcpy.Exists(dataset):
      raise Exception('file network dataset not found: ' + dataset);
   
   des = arcpy.Describe(dataset);
   value['networkDatasetName'] = 'File Network Dataset'; 
   value['defaultTravelMode']  = des.defaultTravelModeName;
   
   for item in des.attributes:
      if item.usageType == 'Cost':
         unit,utype = convertUnits(item.units);
         
         value['allCostNames'].append(item.name);
         if utype == 'distance':
            value['distanceCostNames'].append(item.name);
         elif utype == 'time':
            value['timeCostNames'].append(item.name);
            
         dt = convertDataTypes(item.dataType);
         value['networkDatasetCosts'][item.name] = {
             "name"                  : item.name
            ,"dataType"              : dt
            ,"unit"                  : unit 
            ,"utype"                 : utype            
         };
         unitHash[item.name] = unit;
         
         if dt == 'integer':
            value['integerCostNames'].append(item.name);
         
   tm = arcpy.na.GetTravelModes(dataset);
   
   for key,val in tm.items():
      value['travelModeNames'].append(key);

      value['supportedTravelModes'][key] = {
          "name"                  : key
         ,"impedanceAttributeName": val.impedance
         ,"impedanceAttributeUnit": unitHash[val.impedance]
         ,"distanceAttributeName" : val.distanceAttributeName
         ,"distanceAttributeUnit" : unitHash[val.distanceAttributeName]
         ,"timeAttributeName"     : val.timeAttributeName
         ,"timeAttributeUnit"     : unitHash[val.timeAttributeName]                   
      };
   
   return value;

###############################################################################
class NetworkDataset:

   #...........................................................................
   def __init__(self
      ,network_dataset
      ,network_dataset_type     = None
      ,current                  = None
   ):
   
      #////////////////////////////////////////////////////////////////////////
      self.network_dataset             = None;
      self.network_dataset_type        = None;
      # 'PortalHelper'
      # 'FileNetworkDataset'
      # 'RemoteNetworkDataset'
      self.describe                    = None;
      self.current_travel_mode         = None;
      #////////////////////////////////////////////////////////////////////////
   
      if network_dataset is None:
         return;
         
      network_dataset = network_dataset.rstrip('/').lower();
      
      if network_dataset_type is None:
         network_dataset_type = 'PortalHelper';
         
      #////////////////////////////////////////////////////////////////////////
      self.network_dataset             = network_dataset;
      self.network_dataset_type        = network_dataset_type;
      self.current_travel_mode         = current;
      
      if self.network_dataset_type == 'PortalHelper':
         self.describe = describePortalHelperNetworkDataset();
         
      elif self.network_dataset_type == 'RemoteNetworkDataset':
         self.describe = describeRemoteNetworkDataset(self.network_dataset);
         
      elif self.network_dataset_type == 'FileNetworkDataset':
         self.describe = describeFileNetworkDataset(self.network_dataset);
         
      else:
         raise Exception('err');
      
      if 'error' in self.describe:
         self.network_dataset = None;
         
      else:
      
         if current is not None and current != self.describe['defaultTravelMode'] \
         and current in self.describe['supportedTravelModes']:
            self.current_travel_mode = current;
            
         else:
            self.current_travel_mode = self.bestTravelMode(); 
         
   #...........................................................................
   def setCurrentTravelMode(self
      ,current
   ):
      if current in self.describe['travelModeNames']:
         self.current_travel_mode = current;
      else:
         raise Exception('unknown travel mode: ' + current);
         
   #...........................................................................
   def getCurrentTravelMode(self):
   
      if self.describe is None or 'supportedTravelModes' not in self.describe \
      or self.current_travel_mode not in self.describe['supportedTravelModes']:
         return None;
      
      return self.describe['supportedTravelModes'][self.current_travel_mode];
      
   #...........................................................................
   def getCurrentTravelModeImpedanceAttributeName(self):
   
      if self.describe is None or 'supportedTravelModes' not in self.describe \
      or self.current_travel_mode not in self.describe['supportedTravelModes'] \
      or 'impedanceAttributeName' not in self.describe['supportedTravelModes'][self.current_travel_mode]:
         return None;
      
      return self.describe['supportedTravelModes'][self.current_travel_mode]['impedanceAttributeName'];
         
   #...........................................................................
   def getTravelModeNames(self):
   
      if self.describe is None or 'travelModeNames' not in self.describe:
         return [" "];
      
      return self.describe['travelModeNames'];
      
   #...........................................................................
   def getAllCostNames(self,add_empty=False):
   
      if add_empty:
         return [" "] + self.describe['allCostNames']
         
      else:
         return self.describe['allCostNames'];
      
   #...........................................................................
   def getDistanceCostNames(self,add_empty=False):
   
      if self.describe is None or 'distanceCostNames' not in self.describe:
         return [" "];
         
      elif add_empty:
         return [" "] + self.describe['distanceCostNames'];
         
      else:
         return self.describe['distanceCostNames'];
      
   #...........................................................................
   def getTimeCostNames(self,add_empty=False):
   
      if self.describe is None or 'timeCostNames' not in self.describe:
         return [" "];
         
      elif add_empty:
         return [" "] + self.describe['timeCostNames'];
         
      else:
         return self.describe['timeCostNames'];
      
   #...........................................................................
   def getIntegerCostNames(self,add_empty=False):
   
      if self.describe is None or 'integerCostNames' not in self.describe:
         return [" "];
         
      elif add_empty:
         return [" "] + self.describe['integerCostNames'];
         
      else:
         return self.describe['integerCostNames'];
           
   #...........................................................................
   def bestTravelMode(self,ptype='distance'):

      if self.describe is None or 'supportedTravelModes' not in self.describe \
      or len(self.describe['supportedTravelModes']) == 0:
         return None;
             
      weights = {}

      i = 1;
      for key,item in self.describe['supportedTravelModes'].items():
      
         if key == self.current_travel_mode:
            weights[key] = 0;
         elif key == 'Trucking Distance':
            weights[key] = 2;
         elif key == 'Trucking Time':
            weights[key] = 10;
            if ptype == 'time':
               weights[key] = 1;
         elif key[0:5] == 'Truck':
            weights[key] = 20;
         elif key[0:4] == 'Rail':
            weights[key] = 20;
         elif i == 1:
            weights[key] = 100;
         else:
            weights[key] = 500;
            
         i += 1;
      
      for k,v in sorted(weights.items(), key=lambda kv: kv[1]):
         rez = k;
         break
         
      return rez;
      
   #...........................................................................
   def bestOverallCost(self,ptype='distance'):

      if self.describe is None or 'networkDatasetCosts' not in self.describe \
      or len(self.describe['networkDatasetCosts']) == 0:
         return None;
         
      weights = {}
 
      i = 1;
      for key,item in self.describe['networkDatasetCosts'].items():
      
         if (ptype == 'distance' and item['utype'] == 'distance') \
         or (ptype == 'time'     and item['utype'] == 'time'):
         
            if key.lower()[0:16]   == 'overall_distance':
               weights[key] = 2;
            elif key.lower()[0:16] == 'overall_timeoftr':
               weights[key] = 3;
               if ptype == 'time':
                  weights[key] = 1;
                  
            elif self.network_dataset == 'https://www.arcgis.com' and key == 'Kilometers':
               weights[key] = 20;
            elif self.network_dataset == 'https://www.arcgis.com' and key == 'TruckTravelTime':
               weights[key] = 30;
               if ptype == 'time':
                  weights[key] = 10;
            
            elif i == 1:
               weights[key] = 1000;
            else:
               weights[key] = 5000;
               
         i += 1;

      rez = None;
      for k,v in sorted(weights.items(), key=lambda kv: kv[1]):
         rez = k;
         wgt = v;
         break;
         
      return rez;
      
   #...........................................................................
   def bestRoadCost(self,ptype='distance'):

      if self.describe is None or 'networkDatasetCosts' not in self.describe \
      or len(self.describe['networkDatasetCosts']) == 0:
         return None;
         
      weights = {}
      
      i = 1;
      for key,item in self.describe['networkDatasetCosts'].items():
      
         if (ptype == 'distance' and item['utype'] == 'distance') \
         or (ptype == 'time'     and item['utype'] == 'time'):
            
            if key.lower()[0:14] == 'truck_distance':
               weights[key] = 2;
            elif key.lower()[0:14] == 'truck_timeoftr':
               weights[key] = 3;
               if ptype == 'time':
                  weights[key] = 1;
                  
            elif self.network_dataset == 'https://www.arcgis.com' and key == 'Kilometers':
               weights[key] = 20;
            elif self.network_dataset == 'https://www.arcgis.com' and key == 'TruckTravelTime':
               weights[key] = 30;
               if ptype == 'time':
                  weights[key] = 10;
            
            elif key[0:5] == 'Truck':
               weights[key] = 200;
            elif key[0:4] == 'Rail':
               weights[key] = 900;
            
            elif i == 1:
               weights[key] = 1000;
            else:
               weights[key] = 5000;
               
         i += 1;
      
      rez = None;
      for k,v in sorted(weights.items(), key=lambda kv: kv[1]):
         rez = k;
         wgt = v;
         break
      
      return rez;
      
   #...........................................................................
   def bestRailCost(self,ptype='distance'):

      if self.describe is None or 'networkDatasetCosts' not in self.describe \
      or len(self.describe['networkDatasetCosts']) == 0:
         return None;
         
      if self.network_dataset[-10:].lower() == 'arcgis.com':
         return None;
         
      weights = {}
         
      i = 1;
      for key,item in self.describe['networkDatasetCosts'].items():
      
         if (ptype == 'distance' and item['utype'] == 'distance') \
         or (ptype == 'time'     and item['utype'] == 'time'):
      
            if key.lower()[0:13] == 'rail_distance':
               weights[key] = 2;
            elif key.lower()[0:13] == 'rail_timeoftr':
               weights[key] = 3;
               if ptype == 'time':
                  weights[key] = 1;
                  
            elif key[0:4] == 'Rail':
               weights[key] = 20;
            
            elif i == 1:
               weights[key] = 1000;
            else:
               weights[key] = 5000;
               
         i += 1;
      
      rez = None;
      for k,v in sorted(weights.items(), key=lambda kv: kv[1]):
         rez = k;
         wgt = v;
         break;
         
      return rez;
      
   #...........................................................................
   def bestStationCost(self):

      if self.describe is None or 'networkDatasetCosts' not in self.describe \
      or len(self.describe['networkDatasetCosts']) == 0:
         return None;
         
      if self.network_dataset[-10:].lower() == 'arcgis.com':
         return None;
         
      weights = {}
         
      i = 1;
      for key,item in self.describe['networkDatasetCosts'].items():
      
         if key.lower()[0:13] == 'station_count':
            weights[key] = 2;
         
         elif i == 1:
            weights[key] = 100;
         else:
            weights[key] = 500;
            
         i += 1;
      
      for k,v in sorted(weights.items(), key=lambda kv: kv[1]):
         rez = k;
         wgt = v;
         break
         
      if wgt > 10:
         return None;
      else:   
         return rez;
         
   #...........................................................................
   def costUnit(self,cost):
   
      if self.describe is None or 'networkDatasetCosts' not in self.describe \
      or cost not in self.describe['networkDatasetCosts'] \
      or 'unit' not in self.describe['networkDatasetCosts'][cost]:
         return None;
      
      if cost is None or cost == "" or cost == " ":
         return None;
         
      return self.describe['networkDatasetCosts'][cost]["unit"];
      
   