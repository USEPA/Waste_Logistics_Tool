import arcpy;
import source.util;

###############################################################################
import importlib
try:
   importlib.reload(source.util);

except:
   pass;

###############################################################################
class ParmFramework:

   #...........................................................................
   def __init__(self,framework):
      
      self.framework      = framework;   
      self.parmByName     = {};
      self.parmByIndex    = {};
      self.error_code     = 0;
      self.status_message = None;
      
      if 'framework' not in self.framework:
         self.framework["framework"] = {};
      
      if 'error_code' in self.framework:
         self.error_code = self.framework["error_code"];
      else:
         self.framework["error_code"] = 0;      
      
      if 'status_message' in self.framework:
         self.status_message = self.framework["status_message"];
      else:
         self.framework["status_message"] = None;      
      
      if 'parms' not in self.framework \
      or self.framework["parms"] is None:
         self.framework["parms"] = [];
         
      if 'stash' not in self.framework \
      or self.framework["stash"] is None:
         self.framework["stash"] = {};
      
      idx = 1;
      for frmparm in self.framework["framework"]:
         frmparm["index"] = idx;
         self.parmByIndex[idx] = frmparm;
         self.parmByName[frmparm["name"]] = frmparm;
         idx += 1;
         
   #...........................................................................
   def getIndexByName(self,name):
   
      return self.parmByName[name]["index"];
      
   #...........................................................................
   def getParmValueByName(self,name):
   
      return self.parmByName[name]["value"];
      
   #...........................................................................
   def getStash(self,stash):
   
      if stash in self.framework["stash"]:
         return self.framework["stash"][stash];
      else:
         return None;
        
   #...........................................................................
   def getErrorCode(self):
   
      if self.error_code is not None:
         return self.error_code;
         
      if 'error_code' in self.framework:
         return self.framework["error_code"];
      
   #...........................................................................
   def setErrorCode(self,error_code,status_message=None):
   
      self.error_code = error_code;
      self.status_message = status_message;
      
      self.framework["error_code"] = error_code;
      self.framework["status_message"] = status_message;
      
   #...........................................................................
   def setStash(self,stash,value):
   
      self.framework["stash"][stash] = value;
   
   #...........................................................................
   def setParmEnabledByName(self,name,value):
   
      self.parmByName[name]["enabled"] = value;
   
   #...........................................................................
   def setParmValueByName(self,name,value,columns=None,filter_list=None):
   
      self.parmByName[name]["value"] = value;
      
      if columns is not None:
         self.parmByName[name]["columns"] = columns;
         
      if filter_list is not None:
         self.parmByName[name]["filter.list"] = filter_list;
         
   #...........................................................................
   def isAtLeast(self,parameters,name,value=1):
      
      idx = self.parmByName[name]["index"];
      prm = parameters[idx];
      
      if prm.hasBeenValidated:
         if prm.value is None or prm.value < value:
            parameters[idx].value          = value;
            self.parmByName[name]["value"] = value;
         
      return parameters;
   
   #...........................................................................
   def refreshFromParameters(self,parameters):
   
      for idx,prm in enumerate(parameters):
         if idx in self.parmByIndex and 'value' in self.parmByIndex[idx]:
            self.parmByIndex[idx]["value"] = prm.value;         
         
   #...........................................................................
   def getParms(self):

      if self.framework is None:
         return None;
         
      parms = [];
      
      parm0_enabled = False;
      parm0_value   = None;
      if 'error_code' in self.framework and self.framework["error_code"] > 0:
         parm0_enabled = True;
         parm0_value   = self.framework["status_message"];
      
      param0 = arcpy.Parameter(
          displayName   = ""
         ,name          = "error_condition"
         ,datatype      = "GPString"
         ,parameterType = "Optional"
         ,direction     = "Input"
         ,enabled       = parm0_enabled
      );
      param0.value = parm0_value;
      parms.append(param0);

      for item in self.framework["framework"]:
         
         parm = None;
         parm_enabled = True;
         if 'enabled' in item:
            parm_enabled = item["enabled"];
         elif self.framework["error_code"] > 1:
            parm_enabled = False;
            
         parm_category = None;
         if 'category' in item and item["category"] is not None:
            parm_category = item["category"];
            
         parm_multiValue = None;
         if 'multiValue' in item and item["multiValue"] is not None:
            parm_multiValue = item["multiValue"];
         
         parm = arcpy.Parameter(
             displayName   = item["displayName"]
            ,name          = item["name"]
            ,datatype      = item["datatype"]
            ,parameterType = item["parameterType"]
            ,direction     = item["direction"]
            ,enabled       = parm_enabled
            ,category      = parm_category
            ,multiValue    = parm_multiValue
         );
         
         if 'columns' in item:
            parm.columns = item["columns"];
         
         if 'value' in item and item["value"] is not None:          
            parm.value = item["value"];
         
         if 'filter.type' in item:
            parm.filter.type = item["filter.type"];
            
         if 'filter.list' in item:
            if item["filter.list"] is None:
               parm.filter.list = [];
            else:
               parm.filter.list = item["filter.list"];
         
         parms.append(parm);
      
      self.parms = parms;
      
      return parms;
      