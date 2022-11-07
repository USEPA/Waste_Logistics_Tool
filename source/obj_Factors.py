import arcpy,os

import source.util;
import source.obj_Modes;
import source.obj_CPLMUnitRates;
import source.obj_FixedTransCost;
import source.obj_LaborCosts;
import source.obj_DisposalFees;
import source.obj_FacilityCapacities;

###############################################################################
import importlib
importlib.reload(source.util);
importlib.reload(source.obj_Modes);
importlib.reload(source.obj_CPLMUnitRates);
importlib.reload(source.obj_FixedTransCost);
importlib.reload(source.obj_LaborCosts);
importlib.reload(source.obj_DisposalFees);
importlib.reload(source.obj_FacilityCapacities);

###############################################################################
class Factors:

   #...........................................................................
   def __init__(self
      ,modes_layer
      ,cplm_unit_rates_layer
      ,fixed_trans_cost_layer
      ,labor_costs_layer
      ,disposal_fees_layer
      ,facility_capacities_layer
   ):
      #////////////////////////////////////////////////////////////////////////
      self.modes_layer               = None;
      self.cplm_unit_rates_layer     = None;
      self.fixed_trans_cost_layer    = None;
      self.labor_costs_layer         = None;
      self.disposal_fees_layer       = None;
      self.facility_capacities_layer = None;
      self.current                   = None;

      self.modes_layer               = [];
      self.cplm_unit_rates           = [];
      self.fixed_trans_cost          = [];
      self.labor_costs               = [];
      self.disposal_fees             = [];
      self.facility_capacities       = [];
      
      #////////////////////////////////////////////////////////////////////////
      self.modes_layer               = modes_layer;
      self.cplm_unit_rates_layer     = cplm_unit_rates_layer;
      self.fixed_trans_cost_layer    = fixed_trans_cost_layer;
      self.labor_costs_layer         = labor_costs_layer;
      self.disposal_fees_layer       = disposal_fees_layer;
      self.facility_capacities_layer = facility_capacities_layer;

   #...........................................................................
   def fetchFactorIDs(self):

      rows = arcpy.da.SearchCursor(
          in_table     = self.modes_layer.dataSource
         ,field_names  = (
             'factorid'
          )
         ,where_clause = None
      );

      output = [];

      for row in rows:
         if row[0] not in output:
            output.append(row[0]);

      del rows;

      return output;

   #...........................................................................
   def loadFactorID(self
      ,factorid
   ):

      self.current = factorid;
      
      self.modes                     = [];
      self.cplm_unit_rates           = [];
      self.fixed_trans_cost          = [];
      self.labor_costs               = [];
      self.disposal_fees             = [];
      self.facility_capacities       = [];
      
      #########################################################################
      with arcpy.da.SearchCursor(
          in_table     = self.modes_layer.dataSource
         ,field_names  = source.obj_Modes.Modes.fields
         ,where_clause = "factorid = " + source.util.sql_quote(factorid)
      ) as cursor:

         for row in cursor:
            self.modes.append(
               source.obj_Modes.Modes(
                   factorid    = row[0]
                  ,mode        = row[1]
                  ,name        = row[2]
                  ,description = row[3]
               )
            );

      #########################################################################
      with arcpy.da.SearchCursor(
          in_table     = self.cplm_unit_rates_layer.dataSource
         ,field_names  = source.obj_CPLMUnitRates.CPLMUnitRates.fields
         ,where_clause = "factorid = " + source.util.sql_quote(factorid)
      ) as cursor:

         for row in cursor:
            self.cplm_unit_rates.append(
               source.obj_CPLMUnitRates.CPLMUnitRates(
                   factorid         = row[0]
                  ,mode             = row[1]
                  ,cplmdist_lower   = row[2]
                  ,cplmdist_upper   = row[3]
                  ,cplmunit         = row[4]
                  ,wastetype        = row[5]
                  ,wastemedium      = row[6]
                  ,cplunit_rate     = row[7]
                  ,cplunit_rateunit = row[8]
               )
            );

      #########################################################################
      with arcpy.da.SearchCursor(
          in_table     = self.fixed_trans_cost_layer.dataSource
         ,field_names  = source.obj_FixedTransCost.FixedTransCost.fields
         ,where_clause = "factorid = " + source.util.sql_quote(factorid)
      ) as cursor:

         for row in cursor:
            self.fixed_trans_cost.append(
               source.obj_FixedTransCost.FixedTransCost(
                   factorid            = row[0]
                  ,mode                = row[1]
                  ,fixedcost_type      = row[2]
                  ,wastetype           = row[3]
                  ,wastemedium         = row[4]
                  ,fixedcost_value     = row[5]
                  ,fixedcost_valueunit = row[6]
               )
            );

      #########################################################################
      with arcpy.da.SearchCursor(
          in_table     = self.labor_costs_layer.dataSource
         ,field_names  = source.obj_LaborCosts.LaborCosts.fields
         ,where_clause = "factorid = " + source.util.sql_quote(factorid)
      ) as cursor:

         for row in cursor:
            self.labor_costs.append(
               source.obj_LaborCosts.LaborCosts(
                   factorid      = row[0]
                  ,mode          = row[1]
                  ,laborcategory = row[2]
                  ,laborcost     = row[3]
                  ,laborcostunit = row[4]
               )
            );

   #...........................................................................
   def CPLMUnitRate(self
      ,mode
      ,distance
      ,distance_unit
      ,waste_type
      ,waste_medium
      ,unit_system
   ):
      mode         = source.util.modeMap(mode);
      waste_medium = source.util.mediumMap(waste_medium);
      
      cplunit_rate     = None;
      cplunit_rateunit = None;
      
      rez = {
          'cplunit_rate'     : 0
         ,'cplunit_rateunit' : 'zeroed'
      }
      
      for obj in self.cplm_unit_rates:
         md = source.util.modeMap(obj.mode);
         wm = source.util.mediumMap(obj.wastemedium);
         
         (cplmdist_lower,dummy) = source.util.converter(
             obj.cplunit_rateunit
            ,obj.cplmdist_lower
            ,unit_system
         );
         
         (cplmdist_upper,dummy) = source.util.converter(
             obj.cplunit_rateunit
            ,obj.cplmdist_upper
            ,unit_system
         );
         
         if  md              == mode           \
         and obj.wastetype   == waste_type     \
         and wm              == waste_medium   \
         and distance  >= cplmdist_lower        \
         and distance  < cplmdist_upper:
            cplunit_rate     = obj.cplunit_rate;
            cplunit_rateunit = obj.cplunit_rateunit;
            break;

      if cplunit_rate is None and cplunit_rateunit is None:
         return rez;
         
      rez = {
          'cplunit_rate'     : cplunit_rate
         ,'cplunit_rateunit' : cplunit_rateunit
      }
         
      return rez;

   #...........................................................................
   def fixedTransCost(self
      ,mode
      ,fixedcost_type
      ,waste_type
      ,waste_medium
      ,unit_system
   ):
      mode         = source.util.modeMap(mode);
      waste_medium = source.util.mediumMap(waste_medium);
      
      fixedcost_value     = None;
      fixedcost_valueunit = None;
      
      rez = {
          'fixedcost_type'      : 'stub'
         ,'fixedcost_value'     : 0
         ,'fixedcost_valueunit' : 'zeroed'
      }
      
      for obj in self.fixed_trans_cost:
         md = source.util.modeMap(obj.mode);
         wm = source.util.mediumMap(obj.wastemedium);
         
         if  md                 == mode         \
         and obj.wastetype      == waste_type   \
         and wm                 == waste_medium \
         and obj.fixedcost_type == fixedcost_type:

            if obj.fixedcost_value is None:
               fixedcost_value     = 0;
               fixedcost_valueunit = obj.fixedcost_valueunit;
            else:
               fixedcost_value     = obj.fixedcost_value;
               fixedcost_valueunit = obj.fixedcost_valueunit;
               
            break;
            
      if fixedcost_value is None and fixedcost_valueunit is None:
         return rez;
         
      rez = {
          'fixedcost_type'      : fixedcost_type
         ,'fixedcost_value'     : fixedcost_value
         ,'fixedcost_valueunit' : fixedcost_valueunit
      }
         
      # No need to change units as unit is per shipment cost
      return rez;

   #...........................................................................
   # Labor Costs are by the hour
   def laborCosts(self
      ,mode
   ):
      mode = source.util.modeMap(mode);
      
      rez = {
          'laborcategory': None
         ,'laborcost'    : 0
         ,'laborcostunit': 'zeroed'
      }
      
      for obj in self.labor_costs:
         md = source.util.modeMap(obj.mode);
         
         if md == mode:
            laborcategory = obj.laborcategory;
            laborcost     = obj.laborcost;
            laborcostunit = obj.laborcostunit;
            
      rez = {
          'laborcategory': laborcategory
         ,'laborcost'    : laborcost
         ,'laborcostunit': laborcostunit
      }

      return rez;
      
   #...........................................................................
   def facilityCapacity(self
      ,facility_subtypeids
      ,waste_type
      ,waste_medium
      ,unit_system
   ):
      waste_medium = source.util.mediumMap(waste_medium);
      
      
      