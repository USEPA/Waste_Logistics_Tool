import arcpy,os,json;

###############################################################################
class NetworkDataset:

   dataset                    = None;
   travel_modes               = None;
   travel_modes_keys          = [];
   current_travel_mode        = None;
   current_distance_fieldname = None;
   current_distance_unit      = None;
   current_time_fieldname     = None;
   current_time_unit          = None;
   
   #...........................................................................
   def __init__(self
      ,dataset
      ,current = None
   ):
   
      if dataset is None:
         return;
      
      self.dataset = dataset.rstrip('/').lower();
      self.travel_modes = arcpy.na.GetTravelModes(self.dataset);
      
      if self.travel_modes is None or not self.travel_modes:
         return;
      
      weights = {}
      
      i = 1;
      self.travel_modes_keys = [];
      for travel_mode_name in self.travel_modes:
         travel_mode = self.travel_modes[travel_mode_name];
         
         self.travel_modes_keys.append(travel_mode.name);
   
         if travel_mode.name == current:
            weights[travel_mode.name] = 0;
         elif travel_mode.name == 'Trucking Distance':
            weights[travel_mode.name] = 1;
         elif travel_mode.name == 'Trucking Time':
            weights[travel_mode.name] = 10;
         elif travel_mode.name[0:5] == 'Truck':
            weights[travel_mode.name] = 20;
         elif i == 1:
            weights[travel_mode.name] = 100;
         else:
            weights[travel_mode.name] = 500;
            
         i += 1;
      
      for k,v in sorted(weights.items(), key=lambda kv: kv[1]):
         self.setCurrent(k);
         break;
         
   #...........................................................................
   def setCurrent(self
      ,current
   ):
      
      if current != self.current_travel_mode:
      
         self.current_travel_mode = current;
         
         travel_dict = json.loads(str(self.travel_modes[self.current_travel_mode]));
         
         if 'distanceAttributeName' in travel_dict:
            self.current_distance_fieldname = 'Total_' + travel_dict['distanceAttributeName']
            
            if self.current_distance_fieldname == 'Total_Miles':
               self.current_distance_unit = 'mi';
            elif self.current_distance_fieldname == 'Total_Meters':
               self.current_distance_unit = 'm';
            elif self.current_distance_fieldname == 'Total_Kilometers':
               self.current_distance_unit = 'km';
         
         if 'timeAttributeName' in travel_dict:
            self.current_time_fieldname = 'Total_' + travel_dict['timeAttributeName'];
            
            if self.dataset == 'https://www.arcgis.com' and self.current_time_fieldname == 'Total_TruckTravelTime':
               self.current_time_unit = 'min';
            elif self.current_time_fieldname == 'Total_Minutes':
               self.current_time_unit = 'min';
            elif self.current_time_fieldname == 'Total_Hours':
               self.current_time_unit = 'hr';
  
   