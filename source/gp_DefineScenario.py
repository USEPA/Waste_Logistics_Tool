import arcpy,os,sys;
from decimal import Decimal;

import source.util;
import source.obj_AllHazardsWasteLogisticsTool;

###############################################################################
import importlib
importlib.reload(source.util);
importlib.reload(source.obj_AllHazardsWasteLogisticsTool);

def execute(self, parameters, messages):
   
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
   scenarioid   = source.util.clean_id(parameters[2].valueAsText);
   waste_type   = parameters[3].valueAsText;
   waste_medium = parameters[4].valueAsText;
   waste_unit   = parameters[5].valueAsText;
   waste_amount = parameters[6].value;
   
   #########################################################################
   # Step 30 
   # Initialize the haz toc object
   #########################################################################
   haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
   
   unit_system = None;
   if haz is not None and haz.system_cache is not None:
      unit_system = haz.system_cache.current_unit_system;
      
   (waste_amount,waste_unit) = source.util.converter(
       in_unit     = waste_unit
      ,in_value    = waste_amount
      ,unit_system = unit_system
   );
      
   #########################################################################
   # Step 50 
   # Persist the waste amounts
   #########################################################################
   haz.scenario.upsertScenarioID(
       scenarioid   = scenarioid
      ,waste_type   = waste_type
      ,waste_medium = waste_medium
      ,waste_amount = waste_amount
      ,waste_unit   = waste_unit
      ,conditionid  = haz.system_cache.current_conditionid
      ,factorid     = haz.system_cache.current_factorid
   );
   haz.system_cache.set_current_scenarioid(scenarioid);
  
   del haz;
   
   return;
      