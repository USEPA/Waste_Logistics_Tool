import arcpy,os

###############################################################################
class Waste:

   waste_hash = [
       ('Volume Solid' ,'m3' ,'Radioactive: Contact-Handled')
      ,('Volume Solid' ,'yd3','Radioactive: Contact-Handled')
      ,('Volume Liquid','L'  ,'Radioactive: Contact-Handled')
      ,('Volume Liquid','gal','Radioactive: Contact-Handled')
      ,('Volume Solid' ,'m3' ,'Radioactive: Remote-Handled')
      ,('Volume Solid' ,'yd3','Radioactive: Remote-Handled')
      ,('Volume Liquid','L'  ,'Radioactive: Remote-Handled')
      ,('Volume Liquid','gal','Radioactive: Remote-Handled')
      ,('Volume Solid' ,'m3' ,'Hazardous')
      ,('Volume Solid' ,'yd3','Hazardous')
      ,('Volume Liquid','L'  ,'Hazardous')
      ,('Volume Liquid','gal','Hazardous')
      ,('Volume Solid' ,'m3' ,'Municipal Solid Waste (MSW)')
      ,('Volume Solid' ,'yd3','Municipal Solid Waste (MSW)')
      ,('Volume Solid' ,'m3' ,'Construction and Demolition')
      ,('Volume Solid' ,'yd3','Construction and Demolition')
   ];

   #...........................................................................
   def __init__(self):
      None;

   #...........................................................................
   def waste_types(self):
      results = [];

      for item in self.waste_hash:
         (medium,unit,type) = item;
         if type not in results:
            results.append(type);

      return results;
      
   #...........................................................................
   def units(self,unit_system):
   
      if unit_system == "Metric":
         return ["m3","sq m","L","km"];
         
      elif unit_system == "US Customary":
         return ["yd3","sq yd","gal","mi"]; 
         
      raise arcpy.ExecuteError("Error");
      
   #...........................................................................
   def waste_units(self,unit_system):
      results = [];
      
      vry = self.units(unit_system);     
       
      for item in self.waste_hash:
         (medium,unit,type) = item;
         if unit not in results and unit in vry:
            results.append(unit);

      return results;

   #...........................................................................
   def waste_mediums(self):
      results = [];

      for item in self.waste_hash:
         (medium,unit,type) = item;
         if medium not in results:
            results.append(medium);

      return results;

   #...........................................................................
   def filter_medium(self,waste_type,waste_medium):
      results = [];

      for item in self.waste_hash:
         (medium,unit,type) = item;
         if waste_type is None or type == waste_type:
            if waste_medium is None or medium == waste_medium:
               if medium not in results:
                  results.append(medium);

      return results;
      
   #...........................................................................
   def filter_unit(self,waste_type,waste_medium,unit_system):
      results = [];
      
      vry = self.units(unit_system); 

      for item in self.waste_hash:
         (medium,unit,type) = item;
         if waste_type is None or type == waste_type:
            if waste_medium is None or medium == waste_medium:
               if unit not in results and unit in vry:
                  results.append(unit);

      return results;

   #...........................................................................
   def filter_types(self,waste_type,waste_medium):
      results = [];

      for item in self.waste_hash:
         (medium,unit,type) = item;
         if waste_type is None or type == waste_type:
            if waste_medium is None or medium == waste_medium:
               if type not in results:
                  results.append(type);

      return results;
