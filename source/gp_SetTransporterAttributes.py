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
   waste_type               = parameters[2].valueAsText;
   waste_medium             = parameters[3].valueAsText;
   
   roadtransporterattributesname               = source.util.clean_string(parameters[4].valueAsText);
   newroadtransporterattributesname            = source.util.clean_string(parameters[5].valueAsText);
   roadtransportercontainercapacity            = parameters[6].valueAsText; 
   roadtransportercontainercapacityunit        = parameters[7].valueAsText;
   roadtransportercontainercountpertransporter = parameters[8].valueAsText; 
   roadtransportersavailable                   = parameters[9].valueAsText;
   roadtransportersprocessedperday             = parameters[10].valueAsText;
   
   railtransporterattributesname               = source.util.clean_string(parameters[11].valueAsText);
   newrailtransporterattributesname            = source.util.clean_string(parameters[12].valueAsText);
   railtransportercontainercapacity            = parameters[13].valueAsText; 
   railtransportercontainercapacityunit        = parameters[14].valueAsText;
   railtransportercontainercountpertransporter = parameters[15].valueAsText; 
   railtransportersavailable                   = parameters[16].valueAsText;
   railtransportersprocessedperday             = parameters[17].valueAsText;
   
   #########################################################################
   # Step 20 
   # Initialize the haz object
   #########################################################################
   haz = source.obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();
   
   if haz is not None and haz.system_cache is not None:
      prev_road_attributes_name = haz.system_cache.current_road_transporter;
      prev_rail_attributes_name = haz.system_cache.current_rail_transporter;
   else:
      prev_road_attributes_name = None;
      prev_rail_attributes_name = None;
      
   if newroadtransporterattributesname is not None:
      road_attributes_name = newroadtransporterattributesname;
      haz.system_cache.set_current_road_transporter(road_attributes_name);
       
   else:
      road_attributes_name = roadtransporterattributesname;
      
      if road_attributes_name != prev_road_attributes_name:
         haz.system_cache.set_current_road_transporter(road_attributes_name);
      
   if newrailtransporterattributesname is not None:
      rail_attributes_name = newrailtransporterattributesname;
      haz.system_cache.set_current_rail_transporter(rail_attributes_name);
       
   else:
      rail_attributes_name = railtransporterattributesname;
      
      if rail_attributes_name != prev_rail_attributes_name:
         haz.system_cache.set_current_rail_transporter(rail_attributes_name);
   
   #########################################################################
   # Step 30
   # Persist the attribute values
   #########################################################################
   if road_attributes_name is not None:
      haz.upsertTransportationAttributes(
          transporterattrid            = road_attributes_name
         ,mode                         = 'Road'
         ,waste_type                   = waste_type
         ,waste_medium                 = waste_medium
         ,containercapacity            = roadtransportercontainercapacity
         ,containercapacityunit        = roadtransportercontainercapacityunit
         ,containercountpertransporter = roadtransportercontainercountpertransporter   
         ,transportersavailable        = roadtransportersavailable
         ,transportersprocessedperday  = roadtransportersprocessedperday
      );
   
   if rail_attributes_name is not None:
      haz.upsertTransportationAttributes(
          transporterattrid            = rail_attributes_name
         ,mode                         = 'Rail'
         ,waste_type                   = waste_type
         ,waste_medium                 = waste_medium
         ,containercapacity            = railtransportercontainercapacity
         ,containercapacityunit        = railtransportercontainercapacityunit
         ,containercountpertransporter = railtransportercontainercountpertransporter   
         ,transportersavailable        = railtransportersavailable
         ,transportersprocessedperday  = railtransportersprocessedperday
      );

   arcpy.AddMessage("  Transportation Attributes persisted.");
   
   #########################################################################
   # Step 40
   # Persist the ids into the scenario record
   #########################################################################
   if haz.system_cache.current_scenarioid is not None:
      haz.scenario.updateLinkageIDs(
          scenarioid                  = haz.system_cache.current_scenarioid
         ,road_transporter_attributes = haz.system_cache.current_road_transporter
         ,rail_transporter_attributes = haz.system_cache.current_rail_transporter
      );
   
   del haz;
   
   return;
   
   