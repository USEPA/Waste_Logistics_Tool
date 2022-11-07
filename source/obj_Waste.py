import arcpy,os

import source.util;

###############################################################################
import importlib
importlib.reload(source.util);

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
      ,('Volume Solid' ,'m3' ,'Low-Activity Radioactive Waste')
      ,('Volume Solid' ,'yd3','Low-Activity Radioactive Waste')
      ,('Volume Solid' ,'m3' ,'Hazardous')
      ,('Volume Solid' ,'yd3','Hazardous')
      ,('Volume Liquid','L'  ,'Hazardous')
      ,('Volume Liquid','gal','Hazardous')
      ,('Volume Solid' ,'m3' ,'Municipal Solid Waste (MSW)')
      ,('Volume Solid' ,'yd3','Municipal Solid Waste (MSW)')
      ,('Volume Solid' ,'m3' ,'Construction and Demolition')
      ,('Volume Solid' ,'yd3','Construction and Demolition')
      ,('Volume Liquid','L'  ,'Non-Hazardous Aqueous Waste')
      ,('Volume Liquid','gal','Non-Hazardous Aqueous Waste')
   ];
   
   facility_types = [
       (1,'Landfill Facilities')
      ,(2,'Combustion Facilities')
      ,(3,'Wastewater Treatment Facilities')
      ,(5,'Other Facilities')
      ,(6,'Government-Owned Land/Facilities')
      ,(7,'Recovery Facilities')
   ];
   
   facility_subtypes = [
       (1 ,'Hazardous Waste Combustion Facilities')
      ,(2 ,'Construction and Demolition (C&D) Landfill')
      ,(3 ,'Municipal Solid Waste (MSW) Combustion Facilities')
      ,(4 ,'Medical/ Biohazardous Waste Incinerators')
      ,(5 ,'Inert or Construction and Demolition (C&D) Landfills')
      ,(6 ,'Municipal Solid Waste (MSW) Landfills')
      ,(8 ,'Centralized Waste Treatment (CWT) Facilities')
      ,(9 ,'Publicly Owned Treatment Works (POTW)')
      ,(10,'Federally Owned Treatment Works (FOTW)')
      ,(11,'Resource Conservation and Recovery Act (RCRA) Subtitle C Hazardous Waste Landfills')
      ,(14,'Commercial Autoclaves')
      ,(16,'Electric Arc Furnaces')
      ,(17,'Transfer Stations')
      ,(19,'Wood-Fired Boilers')
      ,(20,'Government-Owned Land/Facilities')
      ,(21,'Commercial Radioactive Waste Disposal Facilities')
      ,(22,'Federal Radioactive Waste Disposal Facilities')
      ,(23,'RCRA Subtitle C Landfills with Low Activity Radioactive Waste Disposal Authority')
      ,(24,'Rendering Facilities')
      ,(30,'Industrial Waste Landfills')
      ,(31,'Sewage Sludge Incinerators')
      ,(33,'C&D Recyclers')
      ,(34,'Composting')
      ,(35,'Demolition Contractors')
      ,(36,'Electronics Recyclers')
      ,(37,'Household Hazardous Waste Collection')
      ,(38,'Metal Recyclers')
      ,(39,'Tire Recyclers')
      ,(40,'Vehicle Recyclers')
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
   def units(self,
       unit_system = None
      ,medium      = None    
   ):
   
      if unit_system == "Metric":
         return ["m3","sq m","L","km"];
         
      elif unit_system == "US Customary":
         return ["yd3","sq yd","gal","mi"];
         
      if medium == 'Volume Solid':
         return ["m3","yd3"];
         
      elif medium == 'Volume Liquid':
         return ["L","gal"];
         
      return [];
      
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
      waste_medium = source.util.mediumMap(waste_medium);
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
      
   #...........................................................................
   def typeid2txt(self,pin):
   
      if pin is None:
         return None; 
   
      for item in self.facility_types:
      
         if pin == item[0]:
            return item[1];
            
      raise Exception('err');
      
   #...........................................................................
   def subtypeids2txt(self,pin):
   
      if pin is None:
         return None;
        
      rez = None;        
      for id in source.util.str2ary(str(pin)):
   
         for item in self.facility_subtypes:
      
            if id == item[0]:
            
               if rez is None:
                  rez = item[1];
               else:
                  rez = rez + ', ' + item[1];
            
      if rez is None:
         raise Exception('err: ' + str(pin));

      return rez;
      
   #...........................................................................
   def semicolontxt2subtypeids(self,pin):

      if pin is None:
         return [];
         
      rez = [];
      ary_pin = pin.replace("\'","").split(';');
      for txtid in ary_pin:
      
         for item in self.facility_subtypes:
         
            if txtid == item[1]:
            
               rez.append(item[0]);
               
      if len(rez) == 0:
         raise Exception('err: ' + str(pin));
         
      return rez;
       