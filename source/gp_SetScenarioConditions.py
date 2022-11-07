import arcpy,os;

import source.util;
import source.obj_AllHazardsWasteLogisticsTool;

###############################################################################
import importlib
importlib.reload(source.util);
importlib.reload(source.obj_AllHazardsWasteLogisticsTool);

def execute(self, parameters, messages):
   
   #########################################################################
   # Step 10 
   # Read the parameters
   #########################################################################
   conditionid              = parameters[2].valueAsText;
   newconditionid           = source.util.clean_id(parameters[3].valueAsText);

   roadtollsperroadshipment = parameters[4].value;
   
   misccostperroadshipment  = parameters[5].value;
   misccostperrailshipment  = parameters[6].value;
   
   roadtransporterdeconcost = parameters[7].value;
   railtransporterdeconcost = parameters[8].value;
   
   stagingsitecost          = parameters[9].value;
   
   roaddrivinghoursperday   = parameters[10].value;
   raildrivinghoursperday   = parameters[11].value;
   
   totalcostmultiplier      = parameters[12].value;
   
   factorid                 = source.util.clean_string(parameters[13].valueAsText);
   
   facilityattributesid     = source.util.clean_string(parameters[14].valueAsText);
   
   #########################################################################
   # Step 20 
   # Initialize the haz object
   #########################################################################
   haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
   arcpy.AddMessage(".    Current ScenarioID = " + str(haz.system_cache.current_scenarioid));
   
   if  haz is not None and haz.system_cache is not None:
      
      if haz.system_cache.current_factorid is None    \
      or factorid != haz.system_cache.current_factorid:
         haz.system_cache.set_current_factorid(factorid);
         
      if haz.system_cache.current_facilityattributesid is None                \
      or facilityattributesid != haz.system_cache.current_facilityattributesid:
         haz.system_cache.set_current_facilityattributesid(facilityattributesid);
   
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
       
      ,roadtollsperroadshipment
      
      ,misccostperroadshipment
      ,misccostperrailshipment
      
      ,roadtransporterdeconcost
      ,railtransporterdeconcost
      
      ,stagingsitecost
      
      ,roaddrivinghoursperday
      ,raildrivinghoursperday
      
      ,totalcostmultiplier
   );
   
   haz.system_cache.set_current_conditionid(targetconditionid);

   arcpy.AddMessage("  Condition set persisted.");
   
   #########################################################################
   # Step 30
   # Persist the ids into the scenario record
   #########################################################################
   if haz.system_cache.current_scenarioid is not None:
      haz.scenario.updateLinkageIDs(
          scenarioid                  = haz.system_cache.current_scenarioid
         ,conditionid                 = haz.system_cache.current_conditionid
         ,factorid                    = haz.system_cache.current_factorid
         ,facilityattributesid        = haz.system_cache.current_facilityattributesid
         ,road_transporter_attributes = haz.system_cache.current_road_transporter
         ,rail_transporter_attributes = haz.system_cache.current_rail_transporter
      );
   
   del haz;
   
   return;
   
   