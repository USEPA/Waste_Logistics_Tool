import arcpy,os;

import util;
import obj_AllHazardsWasteLogisticsTool;

###############################################################################
import importlib
importlib.reload(util);
importlib.reload(obj_AllHazardsWasteLogisticsTool);

def execute(self, parameters, messages):
   
   #########################################################################
   # Step 10 
   # Read the parameters
   #########################################################################
   conditionid              = parameters[2].valueAsText;
   newconditionid           = util.clean_id(parameters[3].valueAsText);

   roadtolls                = parameters[4].value;
   misccost                 = parameters[5].value;
   totalcostmultiplier      = parameters[6].value;
   vehicledeconcost         = parameters[7].value;
   stagingsitecost          = parameters[8].value;
   numberoftrucksavailable  = parameters[9].value;
   drivinghours             = parameters[10].value;
   
   #########################################################################
   # Step 20 
   # Initialize the haz object
   #########################################################################
   haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
   
   #########################################################################
   # Step 30
   # Persist the condition
   #########################################################################
   if newconditionid is not None:
      targetconditionid = newconditionid;
   else:
      targetconditionid = conditionid;

   haz.conditions.upsertConditionID(
       targetconditionid
      ,roadtolls
      ,misccost
      ,totalcostmultiplier
      ,vehicledeconcost
      ,stagingsitecost
      ,numberoftrucksavailable
      ,drivinghours
   );
   
   haz.system_cache.set_current_conditionid(targetconditionid);

   arcpy.AddMessage("Condition set persisted.");
   
   del haz;
   
   return;
   
   