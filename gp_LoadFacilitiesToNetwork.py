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
   # Abend if edits are pending
   #########################################################################
   if util.sniff_editing_state():
      raise arcpy.ExecuteError("Error.  Pending edits must be saved or cleared before proceeding.");
      
   #########################################################################
   # Step 20
   # Read the parameters
   #########################################################################
   if parameters[2].value is None:
      ary_waste_acceptance = None;
   else:
      ary_waste_acceptance = parameters[2].valueAsText.split(';');

   if parameters[3].valueAsText == "true":
      loadDefaultFacilities = True;
   else:
      loadDefaultFacilities = False;

   if parameters[4].value is None:
      ary_user_defined = None;
      loadUserDefined  = False;
   else:
      ary_user_defined = parameters[4].valueAsText.split(';');
      loadUserDefined  = True;

   if parameters[5].valueAsText == "true":
      limitBySupport = True;
   else:
      limitBySupport = False;

   if parameters[6].valueAsText == "true":
      truncateFacilities = "CLEAR";
   else:
      truncateFacilities = "APPEND";

   #########################################################################
   # Step 30
   # Initialize the haz toc object
   #########################################################################
   haz = obj_AllHazardsWasteLogisticsTool.AllHazardsWasteLogisticsTool();

   (
       scenarioid
      ,unit_system
      ,waste_type
      ,waste_medium
      ,waste_amount
      ,waste_unit
   ) = haz.current_scenario();

   #########################################################################
   # Step 40
   # Generate the waste acceptance where clause
   #########################################################################
   filter_RAD_accepted     = False;
   filter_LARWRad_accepted = False;
   filter_HW_accepted      = False;
   filter_MSW_accepted     = False;
   filter_C_D_accepted     = False;

   if ary_waste_acceptance is None:
      arcpy.AddMessage("No Disposal Facility Types provided.");
      loadDefaultFacilities = False;
      loadUserDefined       = False;
      
   else:
      for item in ary_waste_acceptance:

         if item.strip('\'') == 'Radioactive Waste Facility':
            filter_RAD_accepted = True;

         elif item.strip('\'') == 'RCRA Hazardous Waste Landfill with LARW':
            filter_LARWRad_accepted = True;

         elif item.strip('\'') == 'RCRA Hazardous Waste Landfill':
            filter_HW_accepted = True;

         elif item.strip('\'') == 'Municipal Solid Waste (MSW) Landfill':
            filter_MSW_accepted = True;

         elif item.strip('\'') == 'Construction and Demolition (C&D) Landfill':
            filter_C_D_accepted = True;
            
         else:
            raise arcpy.ExecuteError("Error unknown waste acceptance " + str(item));

   #########################################################################
   # Step 50
   # Check if the Support Area has content
   #########################################################################
   if limitBySupport:
      if haz.support_area.recordCount() == 0:
         limitBySupport = False;

   #########################################################################
   # Step 60
   # Truncate facility layer if requested
   #########################################################################
   if truncateFacilities == "CLEAR":
      arcpy.AddMessage("Truncating Existing Facilities.");
      arcpy.TruncateTable_management(haz.network.facilities.dataSource);

   #########################################################################
   # Step 70
   # Create facility loader fc
   #########################################################################
   if loadDefaultFacilities or                                             \
   (ary_user_defined is not None and len(ary_user_defined) > 0):

      scratch_ldr = arcpy.CreateScratchName(
          "Facility_Loader"
         ,""
         ,"FeatureClass"
         ,arcpy.env.scratchGDB
      );
      scratch_ldr_path,scratch_ldr_name = os.path.split(scratch_ldr);

      arcpy.CreateFeatureclass_management(
          out_path          = scratch_ldr_path
         ,out_name          = scratch_ldr_name
         ,geometry_type     = "POINT"
         ,has_m             = "DISABLED"
         ,has_z             = "DISABLED"
         ,spatial_reference = arcpy.SpatialReference(4326)
         ,config_keyword    = None
      );

      arcpy.management.AddFields(
          scratch_ldr
         ,get_schema("core")
      );
      arcpy.AddMessage("Scratch loading table created.");

   #########################################################################
   # Step 80
   # Load Default Facilities if requested
   #########################################################################
   if loadDefaultFacilities:

      pn = os.path.dirname(os.path.realpath(__file__));
      fc = pn + os.sep + r"Resources" + os.sep + r"AllHazardsWasteLogisticsFacilities.json";
      if not os.path.exists(fc):
         raise arcpy.ExecuteError("Error.  AllHazardsWasteLogisticsFacilities.json not found.");

      scratch_geo = arcpy.CreateScratchName(
          "Load_GeoJSON"
         ,""
         ,"FeatureClass"
         ,arcpy.env.scratchGDB
      );

      arcpy.env.outputMFlag = "Disabled";
      arcpy.env.outputZFlag = "Disabled";

      arcpy.JSONToFeatures_conversion(
          fc
         ,scratch_geo
         ,"POINT"
      );
      arcpy.AddMessage("Default Facilities GeoJSON Loaded.");
      
      scratch_src = arcpy.CreateScratchName(
          "Load_Source"
         ,""
         ,"FeatureClass"
         ,arcpy.env.scratchGDB
      );
      scratch_src_path,scratch_src_name = os.path.split(scratch_src);
      
      arcpy.CreateFeatureclass_management(
          out_path          = scratch_src_path
         ,out_name          = scratch_src_name
         ,geometry_type     = "POINT"
         ,has_m             = "DISABLED"
         ,has_z             = "DISABLED"
         ,spatial_reference = arcpy.SpatialReference(4326)
         ,config_keyword    = None
      );

      arcpy.management.AddFields(
          scratch_src
         ,get_schema("full")
      );

      cursor_in = arcpy.da.SearchCursor(
          in_table     = scratch_geo
         ,field_names  = get_schema("full_fields") + [
            'SHAPE@'
         ]
      );
      
      cursor_out = arcpy.da.InsertCursor(
          in_table    = scratch_src
         ,field_names = get_schema("full_fields") + [
            'SHAPE@'
         ]
      );
      
      for row in cursor_in:
      
         front_gate_longitude = clean_double(row[7]);
         front_gate_latitude  = clean_double(row[8]);
         
         facility_qty_accepted_volume_solid  = clean_double(row[11]);
         facility_qty_accepted_volume_liquid = clean_double(row[13]);
         
         C_D_accepted     = clean_boo(row[15]);
         MSW_accepted     = clean_boo(row[16]);
         HW_accepted      = clean_boo(row[17]);
         LARWRAD_accepted = clean_boo(row[18]);
         RAD_accepted     = clean_boo(row[19]);
         
         cursor_out.insertRow(
            (
                row[0]
               ,row[1]
               ,row[2]
               ,row[3]
               ,row[4]
               ,row[5]
               ,row[6]
               ,front_gate_longitude
               ,front_gate_latitude
               ,row[9]
               ,row[10]
               ,facility_qty_accepted_volume_solid
               ,row[12]
               ,facility_qty_accepted_volume_liquid
               ,row[14]
               ,C_D_accepted
               ,MSW_accepted
               ,HW_accepted
               ,LARWRAD_accepted
               ,RAD_accepted
               ,row[20]
               ,row[21]
               ,row[22]
               ,row[23]
            )
         );
      

      flds = [
          'front_gate_longitude'
         ,'front_gate_latitude'
         ,'C_D_accepted'
         ,'MSW_accepted'
         ,'HW_accepted'
         ,'LARWRAD_accepted'
         ,'RAD_accepted'
         ,'SHAPE@X'
         ,'SHAPE@Y'
      ]
      
      del cursor_in;
      del cursor_out;

      with arcpy.da.UpdateCursor(scratch_src,flds) as cursor:

         for row in cursor:

            if (filter_C_D_accepted     and row[2] == 'True')  \
            or (filter_MSW_accepted     and row[3] == 'True')  \
            or (filter_HW_accepted      and row[4] == 'True')  \
            or (filter_LARWRad_accepted and row[5] == 'True')  \
            or (filter_RAD_accepted     and row[6] == 'True'):

               if row[0] is not None:
                  row[7] = row[0];
                  row[8] = row[1];

                  cursor.updateRow(row);

            else:
               cursor.deleteRow();

      count = int(arcpy.GetCount_management(scratch_src).getOutput(0));

      if limitBySupport and count > 0:

         scratch_clp = arcpy.CreateScratchName(
             "Clip_Facilities"
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );

         arcpy.Clip_analysis(
            in_features        = scratch_src
           ,clip_features      = haz.support_area.dataSource
           ,out_feature_class  = scratch_clp
         );

         scratch_src = scratch_clp;
         count = int(arcpy.GetCount_management(scratch_src).getOutput(0));
         arcpy.AddMessage("Default Facilities Clipped to Support Area.");

      if count > 0:

         cursor_in = arcpy.da.SearchCursor(
             in_table     = scratch_src
            ,field_names  = get_schema("core_fields") + [
               'SHAPE@'
            ]
         );

         cursor_out = arcpy.da.InsertCursor(
             in_table    = scratch_ldr
            ,field_names = get_schema("core_fields") + [
               'SHAPE@'
            ]
         );

         for row in cursor_in:

            if row[11] is not None and row[11] != "":
               (sol,sol_unit) = util.converter(
                   in_unit     = row[12]
                  ,in_value    = row[11]
                  ,unit_system = unit_system
               );

            else:
               sol      = None
               sol_unit = None;

            if row[13] is not None and row[13] != "":
               (liq,liq_unit) = util.converter(
                   in_unit     = row[14]
                  ,in_value    = row[13]
                  ,unit_system = unit_system
               );

            else:
               liq      = None;
               liq_unit = None;

            cursor_out.insertRow(
               (
                   'Facility' + str(row[0])
                  ,row[1]
                  ,row[2]
                  ,row[3]
                  ,row[4]
                  ,row[5]
                  ,row[6]
                  ,row[7]
                  ,row[8]
                  ,row[9]
                  ,row[10]
                  ,sol
                  ,sol_unit
                  ,liq
                  ,liq_unit
                  ,row[15]
               )
            );

         del cursor_in;
         del cursor_out;

         arcpy.AddMessage("Facility Loader Layer loaded.");

   #########################################################################
   # Step 90
   # Load facility loader fc
   #########################################################################
   if loadUserDefined                                                      \
   and ary_user_defined is not None                                        \
   and len(ary_user_defined) > 0:

      for i in range(len(ary_user_defined)):
         boo_stagingsite = False;
         
         scratch_usr = arcpy.CreateScratchName(
             "UserDefined" + str(i)
            ,""
            ,"FeatureClass"
            ,arcpy.env.scratchGDB
         );
         scratch_usr_path,scratch_usr_name = os.path.split(scratch_usr);

         src_input = ary_user_defined[i];

         desc = arcpy.Describe(src_input);

         if desc.shapeType == "Polygon":
            fields = arcpy.ListFields(src_input)
            
            chck = 0;
            for field in fields:
               if field.name == "Name":
                  chck = chck + 1;
               elif field.name == "CENTROID_X":
                  chck = chck + 1;
               elif field.name == "CENTROID_Y":
                  chck = chck + 1;
               elif field.name == "Available_Solid_Waste_Capacity__m3_":
                  chck = chck + 1;
               elif field.name == "Available_Liquid_Waste_Capacity__L_":
                  chck = chck + 1;
            
            if chck != 5:
               raise arcpy.ExecuteError(
                  "Polygon feature class " + str(src_input) 
                  + " does not appear to be a valid staging site tool output file."
               );
            
            boo_stagingsite = True;
            
            scratch_ste = arcpy.CreateScratchName(
                "StagingSite" + str(i)
               ,""
               ,"FeatureClass"
               ,arcpy.env.scratchGDB
            );
            scratch_ste_path,scratch_ste_name = os.path.split(scratch_ste);
            
            arcpy.CreateFeatureclass_management(
                out_path          = scratch_ste_path
               ,out_name          = scratch_ste_name
               ,geometry_type     = "POINT"
               ,has_m             = "DISABLED"
               ,has_z             = "DISABLED"
               ,spatial_reference = arcpy.SpatialReference(4326)
               ,config_keyword    = None
            );

            arcpy.management.AddFields(
                scratch_ste
               ,get_schema("full")
            );
            
            cursor_in = arcpy.da.SearchCursor(
                in_table     = src_input
               ,field_names  = [
                   'Name'
                  ,'CENTROID_X'
                  ,'CENTROID_Y'
                  ,'Available_Solid_Waste_Capacity__m3_'
                  ,'Available_Liquid_Waste_Capacity__L_'
               ]
            );

            cursor_out = arcpy.da.InsertCursor(
                in_table    = scratch_ste
               ,field_names = [
                   'Facility_Identifier'
                  ,'Facility_Name'
                  ,'facility_waste_mgt'                     
                  ,'facility_capacity_trucks_perday'        
                  ,'facility_qty_accepted_volume_solid'     
                  ,'facility_qty_accepted_volume_solid_unit'
                  ,'facility_qty_accepted_volume_liquid'    
                  ,'facility_qty_accepted_volume_liquid_unit'
                  ,'SHAPE@X'
                  ,'SHAPE@Y'
               ]
            );

            for row in cursor_in:

               if row[3] is not None and row[3] != "":
                  (sol,sol_unit) = util.converter(
                      in_unit     = 'm3'
                     ,in_value    = row[3]
                     ,unit_system = unit_system
                  );

               else:
                  sol      = None
                  sol_unit = None;

               if row[4] is not None and row[4] != "":
                  (liq,liq_unit) = util.converter(
                      in_unit     = 'L'
                     ,in_value    = row[4]
                     ,unit_system = unit_system
                  );

               else:
                  liq      = None;
                  liq_unit = None;

               cursor_out.insertRow(
                  (
                      'StagingSiteSelectionTool.' + str(i)
                     ,row[0]
                     ,'Staging'
                     ,30
                     ,sol
                     ,sol_unit
                     ,liq
                     ,liq_unit
                     ,row[1]
                     ,row[2]
                  )
               );

            del cursor_in;
            del cursor_out;
            
            src_input = scratch_ste;            

         if limitBySupport:
            arcpy.Clip_analysis(
               in_features        = src_input
              ,clip_features      = haz.support_area.dataSource
              ,out_feature_class  = scratch_usr
            );

         else:
            arcpy.CopyFeatures_management(
                in_features       = src_input
               ,out_feature_class = scratch_usr
            );

         count = int(arcpy.GetCount_management(scratch_usr).getOutput(0));

         if count > 0:

            cursor_in = arcpy.da.SearchCursor(
                in_table     = scratch_usr
               ,field_names  = get_schema("full_fields") + [
                  'SHAPE@'
               ]
            );

            cursor_out = arcpy.da.InsertCursor(
                in_table    = scratch_ldr
               ,field_names = get_schema("core_fields") + [
                  'SHAPE@'
               ]
            );

            for row in cursor_in:

               if (filter_C_D_accepted     and row[15] == 'True')   \
               or (filter_MSW_accepted     and row[16] == 'True')   \
               or (filter_HW_accepted      and row[17] == 'True')   \
               or (filter_LARWRad_accepted and row[18] == 'True')   \
               or (filter_RAD_accepted     and row[19] == 'True')   \
               or boo_stagingsite:

                  if row[11] is not None and row[11] != "":
                     (sol,sol_unit) = util.converter(
                         in_unit     = row[12]
                        ,in_value    = row[11]
                        ,unit_system = unit_system
                     );

                  else:
                     sol      = None;
                     sol_unit = None;

                  if row[13] is not None and row[13] != "":
                     (liq,liq_unit) = util.converter(
                         in_unit     = row[14]
                        ,in_value    = row[13]
                        ,unit_system = unit_system
                     );

                  else:
                     liq      = None;
                     liq_unit = None;

                  cursor_out.insertRow(
                     (
                         'Facility' + str(row[0])
                        ,row[1]
                        ,row[2]
                        ,row[3]
                        ,row[4]
                        ,row[5]
                        ,row[6]
                        ,row[7]
                        ,row[8]
                        ,row[9]
                        ,row[10]
                        ,sol
                        ,sol_unit
                        ,liq
                        ,liq_unit
                        ,row[23]
                     )
                  );

            del cursor_in;
            del cursor_out;

            arcpy.AddMessage("User Provided Facilities Layer " + str(i) + " loaded.");

   #########################################################################
   # Step 100
   # Load facilities from facility fc
   #########################################################################
   if loadDefaultFacilities or                                             \
   (ary_user_defined is not None and len(ary_user_defined) > 0):
      count = int(arcpy.GetCount_management(scratch_ldr).getOutput(0));

      if count == 0:
         arcpy.AddMessage("No facilities qualify for loading.");

      else:
         str_fm = "Name                                     Facility_Name #;"             \
                + "CurbApproach                             # 0;"                         \
                + "Attr_Minutes                             # 0;"                         \
                + "Attr_TravelTime                          # 0;"                         \
                + "Attr_Miles                               # 0;"                         \
                + "Attr_Kilometers                          # 0;"                         \
                + "Attr_TimeAt1KPH                          # 0;"                         \
                + "Attr_WalkTime                            # 0;"                         \
                + "Attr_TruckMinutes                        # 0;"                         \
                + "Attr_TruckTravelTime                     # 0;"                         \
                + "Cutoff_Minutes                           # #;"                         \
                + "Cutoff_TravelTime                        # #;"                         \
                + "Cutoff_Miles                             # #;"                         \
                + "Cutoff_Kilometers                        # #;"                         \
                + "Cutoff_TimeAt1KPH                        # #;"                         \
                + "Cutoff_WalkTime                          # #;"                         \
                + "Cutoff_TruckMinutes                      # #;"                         \
                + "Cutoff_TruckTravelTime                   # #;"                         \
                + "Facility_Identifier                      Facility_Identifier                      #;" \
                + "Facility_Name                            Facility_Name                            #;" \
                + "Facility_Address                         Facility_Address                         #;" \
                + "Facility_City                            Facility_City                            #;" \
                + "Facility_State                           Facility_State                           #;" \
                + "Facility_Zip                             Facility_Zip                             #;" \
                + "Facility_Telephone                       Facility_Telephone                       #;" \
                + "Facility_Waste_Mgt                       Facility_Waste_Mgt                       #;" \
                + "Facility_Capacity_Trucks_PerDay          Facility_Capacity_Trucks_PerDay          #;" \
                + "Facility_Qty_Accepted_Volume_Solid       Facility_Qty_Accepted_Volume_Solid       #;" \
                + "Facility_Qty_Accepted_Volume_Solid_Unit  Facility_Qty_Accepted_Volume_Solid_Unit  #;" \
                + "Facility_Qty_Accepted_Volume_Liquid      Facility_Qty_Accepted_Volume_Liquid      #;" \
                + "Facility_Qty_Accepted_Volume_Liquid_Unit Facility_Qty_Accepted_Volume_Liquid_Unit #;";

         arcpy.na.AddLocations(
             in_network_analysis_layer      = haz.network.lyr()
            ,sub_layer                      = haz.network.facilities.name
            ,in_table                       = scratch_ldr
            ,field_mappings                 = str_fm
            ,search_tolerance               = None
            ,sort_field                     = None
            ,search_criteria                = None
            ,match_type                     = None
            ,append                         = truncateFacilities
            ,snap_to_position_along_network = None
            ,snap_offset                    = None
            ,exclude_restricted_elements    = None
            ,search_query                   = None
         );

         arcpy.AddMessage("Network Facilities loaded.");

   ############################################################################
   # Step 110
   # Clean up and exit
   ############################################################################
   del haz;

   return;

###############################################################################
def clean_double(value):

   if value is None:
      return None;

   if str(value) == "":
      return None;

   try:
      v = float(value);

   except ValueError:
      v = None;

   return v;

###############################################################################
def clean_boo(value):

   if value is None:
      return None;

   if str(value) == "":
      return None;

   if str(value) in ["-1","1","TRUE","True","true","Y","y","Yes","YES"]:
      return 'True';

   if str(value) in ["0","FALSE","False","false","N","n","No","NO"]:
      return 'False';

   return None;

###############################################################################
def get_schema(keyword):

   core_schema = [
       ['facility_identifier'                     ,'TEXT'  ,'Facility_Identifier'                     ,255, None,'']
      ,['facility_name'                           ,'TEXT'  ,'Facility_Name'                           ,255, None,'']
      ,['facility_address'                        ,'TEXT'  ,'Facility_Addres'                         ,255, None,'']
      ,['facility_city'                           ,'TEXT'  ,'Facility_City'                           ,255, None,'']
      ,['facility_state'                          ,'TEXT'  ,'Facility_State'                          ,255, None,'']
      ,['facility_zip'                            ,'TEXT'  ,'Facility_Zip'                            ,255, None,'']
      ,['facility_telephone'                      ,'TEXT'  ,'Facility_Telephone'                      ,255, None,'']
      ,['front_gate_longitude'                    ,'DOUBLE','Front_Gate_Longitude'                    ,None,None,'']
      ,['front_gate_latitude'                     ,'DOUBLE','Front_Gate_Latitude'                     ,None,None,'']
      ,['facility_waste_mgt'                      ,'TEXT'  ,'Facility_Waste_Mgt'                      ,255 ,None,'']
      ,['facility_capacity_trucks_perday'         ,'DOUBLE','Facility_Capacity_Trucks_PerDay'         ,None,None,'']
      ,['facility_qty_accepted_volume_solid'      ,'DOUBLE','Facility_Qty_Accepted_Volume_Solid'      ,None,None,'']
      ,['facility_qty_accepted_volume_solid_unit' ,'TEXT'  ,'Facility_Qty_Accepted_Volume_Solid_Unit' ,255, None,'']
      ,['facility_qty_accepted_volume_liquid'     ,'DOUBLE','Facility_Qty_Accepted_Volume_Liquid'     ,None,None,'']
      ,['facility_qty_accepted_volume_liquid_unit','TEXT'  ,'Facility_Qty_Accepted_Volume_Liquid_Unit',255, None,'']
   ];  
    
   extended_schema = [
       ['C_D_accepted'                            ,'TEXT'  ,'C_D_Accepted'                            ,255 ,None,'']
      ,['MSW_accepted'                            ,'TEXT'  ,'MSW_Accepted'                            ,255 ,None,'']
      ,['HW_accepted'                             ,'TEXT'  ,'HW_Accepted'                             ,255 ,None,'']
      ,['LARWRad_accepted'                        ,'TEXT'  ,'LARWRad_Accepted'                        ,255 ,None,'']
      ,['RAD_accepted'                            ,'TEXT'  ,'RAD_Accepted'                            ,255 ,None,'']
      ,['date_stamp'                              ,'TEXT'  ,'Date_Stamp'                              ,255 ,None,'']
      ,['source'                                  ,'TEXT'  ,'Source'                                  ,255 ,None,'']
      ,['notes'                                   ,'TEXT'  ,'Notes'                                   ,255 ,None,'']
   ];
   
   if keyword == "full":
      return core_schema + extended_schema;
      
   elif keyword == "core":
      return core_schema;
   
   elif keyword == "full_fields":
      ary_out = [];
      for item in core_schema + extended_schema:
         ary_out.append(item[0]);
      return ary_out;
      
   elif keyword == "core_fields":
      ary_out = [];
      for item in core_schema:
         ary_out.append(item[0]);
      return ary_out;
   
   
