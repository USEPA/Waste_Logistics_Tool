import arcpy,os

import util;
import obj_ShipmentLoading;
import obj_CPLMUnitRates;
import obj_FixedTransCost;
import obj_LaborCosts;
import obj_DisposalFees;

###############################################################################
import importlib
importlib.reload(util);
importlib.reload(obj_ShipmentLoading);
importlib.reload(obj_CPLMUnitRates);
importlib.reload(obj_FixedTransCost);
importlib.reload(obj_LaborCosts);
importlib.reload(obj_DisposalFees);

###############################################################################
class Factors:

   shipment_loading_layer = None;
   cplm_unit_rates_layer  = None;
   fixed_trans_cost_layer = None;
   labor_costs_layer      = None;
   disposal_fees_layer    = None;
   acceptance_rates_layer = None;
   current                = None;

   shipment_loading       = [];
   cplm_unit_rates        = [];
   fixed_trans_cost       = [];
   labor_costs            = [];
   disposal_fees          = [];
   acceptance_rates       = [];

   #...........................................................................
   def __init__(self
      ,shipment_loading_layer
      ,cplm_unit_rates_layer
      ,fixed_trans_cost_layer
      ,labor_costs_layer
      ,disposal_fees_layer
      ,acceptance_rates_layer
   ):

      self.shipment_loading_layer = shipment_loading_layer;
      self.cplm_unit_rates_layer  = cplm_unit_rates_layer;
      self.fixed_trans_cost_layer = fixed_trans_cost_layer;
      self.labor_costs_layer      = labor_costs_layer;
      self.disposal_fees_layer    = disposal_fees_layer;
      self.acceptance_rates_layer = acceptance_rates_layer;

   #...........................................................................
   def fetchFactorIDs(self):

      rows = arcpy.da.SearchCursor(
          in_table     = self.shipment_loading_layer.dataSource
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
   def loadFactorID(self,factorid):

      self.current = factorid;
      
      self.shipment_loading = [];
      self.cplm_unit_rates  = [];
      self.fixed_trans_cost = [];
      self.labor_costs      = [];
      self.disposal_fees    = [];
      self.acceptance_rates = [];

      rows = arcpy.da.SearchCursor(
          in_table     = self.shipment_loading_layer.dataSource
         ,field_names  = obj_ShipmentLoading.ShipmentLoading.fields
         ,where_clause = "factorid = " + util.sql_quote(factorid)
      );

      for row in rows:
         self.shipment_loading.append(
            obj_ShipmentLoading.ShipmentLoading(
                row[0]
               ,row[1]
               ,row[2]
               ,row[3]
               ,row[4]
               ,row[5]
            )
         );

      rows = arcpy.da.SearchCursor(
          in_table     = self.cplm_unit_rates_layer.dataSource
         ,field_names  = obj_CPLMUnitRates.CPLMUnitRates.fields
         ,where_clause = "factorid = " + util.sql_quote(factorid)
      );

      for row in rows:
         self.cplm_unit_rates.append(
            obj_CPLMUnitRates.CPLMUnitRates(
                row[0]
               ,row[1]
               ,row[2]
               ,row[3]
               ,row[4]
               ,row[5]
               ,row[6]
               ,row[7]
               ,row[8]
            )
         );

      rows = arcpy.da.SearchCursor(
          in_table     = self.fixed_trans_cost_layer.dataSource
         ,field_names  = obj_FixedTransCost.FixedTransCost.fields
         ,where_clause = "factorid = " + util.sql_quote(factorid)
      );

      for row in rows:
         self.fixed_trans_cost.append(
            obj_FixedTransCost.FixedTransCost(
                row[0]
               ,row[1]
               ,row[2]
               ,row[3]
               ,row[4]
               ,row[5]
               ,row[6]
            )
         );

      rows = arcpy.da.SearchCursor(
          in_table     = self.labor_costs_layer.dataSource
         ,field_names  = obj_LaborCosts.LaborCosts.fields
         ,where_clause = "factorid = " + util.sql_quote(factorid)
      );

      for row in rows:
         self.labor_costs.append(
            obj_LaborCosts.LaborCosts(
                row[0]
               ,row[1]
               ,row[2]
               ,row[3]
            )
         );

      rows = arcpy.da.SearchCursor(
          in_table     = self.disposal_fees_layer.dataSource
         ,field_names  = obj_DisposalFees.DisposalFees.fields
         ,where_clause = "factorid = " + util.sql_quote(factorid)
      );

      for row in rows:
         self.disposal_fees.append(
            obj_DisposalFees.DisposalFees(
                row[0]
               ,row[1]
               ,row[2]
               ,row[3]
               ,row[4]
            )
         );

   #...........................................................................
   def shipmentLoadingRate(self
      ,vehicle
      ,waste_type
      ,waste_medium
      ,unit_system
   ):
      loadingrate = None;
      unitpershipment = None;

      for obj in self.shipment_loading:
         if  obj.vehicle     == vehicle      \
         and obj.wastetype   == waste_type   \
         and obj.wastemedium == waste_medium:
            
            loadingrate     = obj.loadingrate;
            unitpershipment = obj.unitpershipment;
            break;
      
      if loadingrate is None and unitpershipment is None:
         return (None,None);
         
      return util.converter(
          in_unit     = unitpershipment
         ,in_value    = loadingrate
         ,unit_system = unit_system
      );

   #...........................................................................
   def CPLMUnitRate(self
      ,vehicle
      ,waste_type
      ,waste_medium
      ,distance
      ,unit_system
   ):
      cplunit_rate = None;
      unit         = None;
      
      for obj in self.cplm_unit_rates:
         (cplmdist_lower,dummy) = util.converter(
             obj.unit
            ,obj.cplmdist_lower
            ,unit_system
         );
         
         (cplmdist_upper,dummy) = util.converter(
             obj.unit
            ,obj.cplmdist_upper
            ,unit_system
         );
         
         if  obj.vehicle     == vehicle        \
         and obj.wastetype   == waste_type     \
         and obj.wastemedium == waste_medium   \
         and distance >= cplmdist_lower        \
         and distance  < cplmdist_upper:
            cplunit_rate = obj.cplunit_rate;
            unit         = obj.unit;
            break;

      if cplunit_rate is None and unit is None:
         return (None,None);
         
      return util.converter(
          in_unit     = unit
         ,in_value    = cplunit_rate
         ,unit_system = unit_system
      );

   #...........................................................................
   def fixedTransCost(self
      ,vehicle
      ,waste_type
      ,waste_medium
      ,cost_type
      ,unit_system
   ):
      fixedcost_value = None;
      unit            = None;
      
      for obj in self.fixed_trans_cost:
         if  obj.vehicle     == vehicle      \
         and obj.wastetype   == waste_type   \
         and obj.wastemedium == waste_medium \
         and obj.fixedcost_type == cost_type:

            if obj.fixedcost_value is None:
               fixedcost_value = 0;
               unit            = obj.unit;
            else:
               fixedcost_value = obj.fixedcost_value;
               unit            = obj.unit;
               
            break;
            
      if fixedcost_value is None and unit is None:
         return (None,None);
         
      # No need to change units as unit is per shipment cost
      return (fixedcost_value,unit);

   #...........................................................................
   # Labor Costs are by the hour
   def laborCosts(self
      ,labor_category
      ,unit_system
   ):

      for obj in self.labor_costs:
         if obj.laborcategory == labor_category:
            return (obj.laborcost,obj.unit);

      return (None,None);

   #...........................................................................
   def disposalFees(self
      ,waste_type
      ,waste_medium
      ,unit_system
   ):
      disposalcost = None;
      unit         = None;
      
      for obj in self.disposal_fees:
         if  obj.wastetype   == waste_type   \
         and obj.wastemedium == waste_medium:
            disposalcost = obj.disposalcost
            unit         = obj.unit;
            break;
            
      if disposalcost is None and unit is None:
         return (None,None);

      return util.converter(
          in_unit     = unit
         ,in_value    = disposalcost
         ,unit_system = unit_system
      );
      
