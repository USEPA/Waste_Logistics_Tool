import arcpy,os,math;
import util;

###############################################################################
class FaciltyCalc:

   haz                             = None;
   scenarioid                      = None;
   conditionid                     = None;
   factorid                        = None;
   facility_identifier             = None;
   facility_rank                   = None;
   total_distance                  = None;
   distance_unit                   = None;
   total_trucktraveltime           = None;
   time_unit                       = None;
   average_speed                   = None;
   speed_unit                      = None;
   facility_name                   = None;
   facility_address                = None;
   facility_city                   = None;
   facility_state                  = None;
   facility_zip                    = None;
   facility_telephone              = None;
   facility_waste_mgt              = None;
   facility_capacity_trucks_perday = None;
   facility_qty_accepted           = None;
   facility_qty_accepted_unit      = None;
   shape                           = None;
   allocated_amount                = None;
   allocated_amount_unit           = None;
   number_of_shipments             = None;
   cplm_cost_usd                   = None;
   fixed_cost_usd_per_shipment     = None;
   fixed_cost_usd_per_hour         = None;
   tolls_usd                       = None;
   misc_trans_cost_usd             = None;
   trans_cost_usd                  = None;
   staging_site_cost_usd           = None;
   disposal_cost_usd               = None;
   labor_cost_usd                  = None;
   vehicle_decon_cost_usd          = None;
   cost_multiplier_usd             = None;
   cost_usd                        = None;
   trucks_time_to_comp_days        = None;
   dest_time_to_comp_days          = None;
   time_days                       = None;
   username                        = None;
   creationtime                    = None;

   #...........................................................................
   def __init__(self
      ,haz
      ,scenarioid
      ,conditionid
      ,factorid
      ,facility_identifier
      ,facility_rank
      ,total_distance
      ,total_distance_unit
      ,total_traveltime
      ,total_traveltime_unit
      ,facility_name
      ,facility_address
      ,facility_city
      ,facility_state
      ,facility_zip
      ,facility_telephone
      ,facility_waste_mgt
      ,facility_capacity_trucks_perday
      ,facility_qty_accepted
      ,facility_qty_accepted_unit
      ,shape
      ,unit_system
      ,waste_type
      ,waste_medium
      ,waste_amount
      ,waste_unit
   ):
      self.haz                             = haz;
      self.scenarioid                      = scenarioid;
      self.conditionid                     = conditionid;
      self.factorid                        = factorid;
      self.facility_identifier             = facility_identifier;
      self.facility_rank                   = facility_rank;

      (self.total_distance,self.distance_unit) = util.converter(
          total_distance_unit
         ,total_distance
         ,unit_system
      );

      (self.total_trucktraveltime,self.time_unit) = util.converter(
          total_traveltime_unit
         ,total_traveltime
         ,'hr'
      );

      self.average_speed                   = self.total_distance / self.total_trucktraveltime;
      self.speed_unit                      = self.distance_unit + "/h";

      self.facility_name                   = facility_name;
      self.facility_address                = facility_address;
      self.facility_city                   = facility_city;
      self.facility_state                  = facility_state;
      self.facility_zip                    = facility_zip;
      self.facility_telephone              = facility_telephone;
      self.facility_waste_mgt              = facility_waste_mgt;
      self.facility_capacity_trucks_perday = facility_capacity_trucks_perday;
      self.facility_qty_accepted           = facility_qty_accepted;
      self.facility_qty_accepted_unit      = facility_qty_accepted_unit;
      self.shape                           = shape;

      self.unit_system                     = unit_system;

   #...........................................................................
   def calc(self,running_total):

      if running_total > self.facility_qty_accepted:
         self.allocated_amount = self.facility_qty_accepted;
      else:
         self.allocated_amount = running_total;

      self.allocated_amount_unit = self.facility_qty_accepted_unit;

      #*** calculate the number of shipments ***#
      (loading_rate,unit) = self.haz.factors.shipmentLoadingRate(
          vehicle      = "Truck"
         ,waste_type   = self.haz.scenario.waste_type
         ,waste_medium = self.haz.scenario.waste_medium
         ,unit_system  = self.unit_system
      );
      arcpy.AddMessage(".....");
      arcpy.AddMessage("number_of_shipments");
      arcpy.AddMessage(".   loading_rate for " + self.haz.scenario.waste_type + " " + self.haz.scenario.waste_medium + " = " + str(loading_rate) + " per " + unit);
      arcpy.AddMessage(".   = ceil(allocated amount (" + str(self.allocated_amount) + " " + self.allocated_amount_unit + ") / loading rate (" + str(loading_rate) + "))");
      if loading_rate is None:
         shipments = 0;
      else:
         shipments = self.allocated_amount / loading_rate;
      self.number_of_shipments = math.ceil(shipments) or 0;
      arcpy.AddMessage(".   = " + str(self.number_of_shipments));

      #*** trucks_time_to_comp_days ***#
      nos = self.number_of_shipments;
      tds = self.total_distance;
      spd = self.average_speed;
      nta = self.haz.conditions.numberoftrucksavailable;
      dhr = self.haz.conditions.drivinghours;

      arcpy.AddMessage(".....");
      arcpy.AddMessage("trucks_time_to_complete");
      arcpy.AddMessage(".   = ceil(total distance (" + str(tds) + ") * 2 / average speed(" + str(spd) + ") / driving hours (" + str(dhr) + ") * number of shipments (" + str(nos) + ") / available trucks (" + str(nta) + "))");
      self.trucks_time_to_comp_days = math.ceil(
         tds * 2 / spd / dhr * nos / nta
      ) or 0;
      arcpy.AddMessage(".   = " + str(self.trucks_time_to_comp_days));

      #*** dest_time_to_comp_days ***#
      self.dest_time_to_comp_days = math.ceil(
         nos / self.facility_capacity_trucks_perday
      );
      arcpy.AddMessage(".....");
      arcpy.AddMessage("dest_time_to_comp_days");
      arcpy.AddMessage(".   = ceil(number of shipments (" + str(nos) + ") / facility capacity trucks per day (" + str(self.facility_capacity_trucks_perday) + "))");
      arcpy.AddMessage(".   = " + str(self.dest_time_to_comp_days));

      #*** time_days ***#
      self.time_days = max(self.trucks_time_to_comp_days,self.dest_time_to_comp_days);
      arcpy.AddMessage(".....");
      arcpy.AddMessage("time_days");
      arcpy.AddMessage(".   = max(trucks_time_to_complete_days (" + str(self.trucks_time_to_comp_days) + "), dest_time_to_comp_days (" + str(self.dest_time_to_comp_days) + "))");
      arcpy.AddMessage(".   = " + str(self.time_days));

      #*** cplm_cost_usd ***#
      (cplm_rate,unit) = self.haz.factors.CPLMUnitRate(
          vehicle      = "Truck"
         ,waste_type   = self.haz.scenario.waste_type
         ,waste_medium = self.haz.scenario.waste_medium
         ,distance     = self.total_distance
         ,unit_system  = self.unit_system
      );
      arcpy.AddMessage(".....");
      arcpy.AddMessage("cplm_cost_usd");
      arcpy.AddMessage(".   rate for " + self.haz.scenario.waste_type + " " + self.haz.scenario.waste_medium + " at " + str(tds) + " " + self.distance_unit + " = " + str(cplm_rate) + " " + unit);
      arcpy.AddMessage(".   = total distance (" + str(tds) + " " + self.distance_unit + ") * cplm rate (" + str(cplm_rate) + ") * number of shipments (" + str(nos) + ")");
      self.cplm_cost_usd = self.total_distance * cplm_rate * nos;
      arcpy.AddMessage(".   = " + str(self.cplm_cost_usd));

      #*** fixed_cost_usd_per_shipment ***#
      (pership_fixed_rate,unit) = self.haz.factors.fixedTransCost(
          vehicle      = "Truck"
         ,waste_type   = self.haz.scenario.waste_type
         ,waste_medium = self.haz.scenario.waste_medium
         ,cost_type    = "Per shipment"
         ,unit_system  = self.unit_system
      );
      arcpy.AddMessage(".....");
      arcpy.AddMessage("fixed_cost_usd_per_shipment");
      arcpy.AddMessage(".   rate for " + self.haz.scenario.waste_type + " " + self.haz.scenario.waste_medium + " = " + str(pership_fixed_rate) + " per shipment");
      arcpy.AddMessage(".   = number of shipments (" + str(nos) + ") * shipment fixed rate (" + str(pership_fixed_rate) + ")");
      self.fixed_cost_usd_per_shipment = nos * pership_fixed_rate;
      arcpy.AddMessage(".   = " + str(self.fixed_cost_usd_per_shipment));

      #*** fixed_cost_usd_per_hour ***#
      (hourly_fixed_rate,unit) = self.haz.factors.fixedTransCost(
          vehicle      = "Truck"
         ,waste_type   = self.haz.scenario.waste_type
         ,waste_medium = self.haz.scenario.waste_medium
         ,cost_type    = "Per hour"
         ,unit_system  = self.unit_system
      );
      arcpy.AddMessage(".....");
      arcpy.AddMessage("fixed_cost_usd_per_hour");
      arcpy.AddMessage(".   rate for " + self.haz.scenario.waste_type + " " + self.haz.scenario.waste_medium + " = " + str(hourly_fixed_rate) + " per hour");
      arcpy.AddMessage(".   = number of shipments (" + str(nos) + ") * total distance (" + str(tds) + ") * 2 / average speed (" + str(spd) + ") * hourly fixed rate (" + str(hourly_fixed_rate) + ")");
      self.fixed_cost_usd_per_hour = nos * tds * 2 / spd * hourly_fixed_rate;
      arcpy.AddMessage(".   = " + str(self.fixed_cost_usd_per_hour));

      #*** tolls_usd ***#
      self.tolls_usd = nos * self.haz.conditions.roadtolls * 2;
      arcpy.AddMessage(".....");
      arcpy.AddMessage("toll_usd");
      arcpy.AddMessage(".   = number of shipments (" + str(nos) + ") * road tolls (" + str(self.haz.conditions.roadtolls) + ") * 2")
      arcpy.AddMessage(".   = " + str(self.tolls_usd));

      #*** misc_trans_cost_usd ***#
      self.misc_trans_cost_usd = nos * self.haz.conditions.misccost;
      arcpy.AddMessage(".....");
      arcpy.AddMessage("misc cost");
      arcpy.AddMessage(".   = number of shipments (" + str(nos) + ") * misc cost (" + str(self.haz.conditions.misccost) + ")");
      arcpy.AddMessage(".   = " + str(self.misc_trans_cost_usd));

      #*** trans_cost_usd ***#
      self.trans_cost_usd = self.cplm_cost_usd                \
                          + self.fixed_cost_usd_per_shipment  \
                          + self.fixed_cost_usd_per_hour      \
                          + self.tolls_usd                    \
                          + self.misc_trans_cost_usd;
      arcpy.AddMessage(".....");
      arcpy.AddMessage("total trans cost");
      arcpy.AddMessage(".   = cplm_cost_usd (" + str(self.cplm_cost_usd) + ") + fixed_cost_usd_per_shipment (" + str(self.fixed_cost_usd_per_shipment) + ") + fixed_cost_usd_per_hour (" + str(self.fixed_cost_usd_per_hour) + ") + tolls_usd (" + str(self.tolls_usd) + ") + misc_trans_cost_usd (" + str(self.misc_trans_cost_usd) + ")");
      arcpy.AddMessage(".   = " + str(self.trans_cost_usd));

      #*** staging_site_cost_usd ***#
      arcpy.AddMessage(".....");
      arcpy.AddMessage("staging_site_cost_usd");
      arcpy.AddMessage(".   = time_days (" + str(self.time_days) + " * staging site cost (" + str(self.haz.conditions.stagingsitecost) + ")");
      if self.facility_waste_mgt == "Staging":
         self.staging_site_cost_usd = self.time_days * self.haz.conditions.stagingsitecost;
      else:
         self.staging_site_cost_usd = 0;
         arcpy.AddMessage(".   Not a staging site facility. Zeroed out.");

      arcpy.AddMessage(".   = " + str(self.staging_site_cost_usd));

      #*** disposal_cost_usd ***#
      arcpy.AddMessage(".....");
      arcpy.AddMessage("disposal_cost_usd");
      if self.facility_waste_mgt == "Staging":
         self.disposal_cost_usd = 0;
         arcpy.AddMessage(".   Not a disposal site facility. Zeroed out.");
      else:
         (disposal_cost,unit) = self.haz.factors.disposalFees(
             waste_type   = self.haz.scenario.waste_type
            ,waste_medium = self.haz.scenario.waste_medium
            ,unit_system  = self.unit_system
         );
         arcpy.AddMessage(".   rate for " + self.haz.scenario.waste_type + " " + self.haz.scenario.waste_medium + " = " + str(disposal_cost) + " per " + str(unit));
         arcpy.AddMessage(".   = allocated amount (" + str(self.allocated_amount) + " " + self.allocated_amount_unit + ") * disposal cost rate (" + str(disposal_cost) + ")");
         self.disposal_cost_usd = self.allocated_amount * disposal_cost;

      arcpy.AddMessage(".   = " + str(self.disposal_cost_usd));

      #*** labor_cost_usd ***#
      arcpy.AddMessage(".....");
      arcpy.AddMessage("labor_cost_usd");
      (lbrhr,dummy) = self.haz.factors.laborCosts(
          labor_category = "Heavy and Tractor-Trailer Truck Drivers"
         ,unit_system    = self.unit_system
      );
      arcpy.AddMessage(".   rate for Heavy and Tractor-Trailer Truck Drivers = " + str(lbrhr) + " per hour");
      self.labor_cost_usd = ( nos / nta ) * tds * 2 / spd * lbrhr * nta;
      arcpy.AddMessage(".   = ( number of shipments (" + str(nos) + ") / number of trucks available (" + str(nta) + ") ) * total distance (" + str(tds) + " " + self.distance_unit + ") * 2 / average speed (" + str(spd) + " per hour) * labor rate (" + str(lbrhr) + ") * number of trucks available (" + str(nta) + ")")
      arcpy.AddMessage(".   = " + str(self.labor_cost_usd));

      #*** vehicle_decon_cost_usd ***#
      arcpy.AddMessage(".....");
      arcpy.AddMessage("vehicle_decon_cost_usd");
      arcpy.AddMessage(".   = number of shipments (" + str(nos) + ") * vehicle decon cost (" + str(self.haz.conditions.vehicledeconcost) + ")");
      self.vehicle_decon_cost_usd = nos * self.haz.conditions.vehicledeconcost;
      arcpy.AddMessage(".   = " + str(self.vehicle_decon_cost_usd));

      #*** initial total cost usd ***#
      arcpy.AddMessage(".....");
      initial_total_cost = (              \
         self.trans_cost_usd              \
       + self.staging_site_cost_usd       \
       + self.disposal_cost_usd           \
       + self.labor_cost_usd              \
       + self.vehicle_decon_cost_usd      \
      );
      arcpy.AddMessage("initial total cost");
      arcpy.AddMessage(".   = ( self.trans_cost_usd (" + str(self.trans_cost_usd) + ") + staging site cost (" + str(self.staging_site_cost_usd) \
       + ") + disposal site cost (" + str(self.disposal_cost_usd) + ") + labor cost (" + str(self.labor_cost_usd) + ") + vehicle decon cost ("  \
       + str(self.vehicle_decon_cost_usd) + "))");
      arcpy.AddMessage(".   = " + str(initial_total_cost));
       
      #*** cost multiplier usd ***#
      arcpy.AddMessage(".....");
      self.cost_multiplier_usd = initial_total_cost * self.haz.conditions.totalcostmultiplier;      
      arcpy.AddMessage("cost_multiplier_usd");
      arcpy.AddMessage(".   = initial total cost (" + str(initial_total_cost) + ") * total cost multiplier (" + str(self.haz.conditions.totalcostmultiplier) + ")");
      arcpy.AddMessage(".   = " + str(self.cost_multiplier_usd));      
      
      #*** total_cost_usd ***#
      arcpy.AddMessage(".....");
      self.cost_usd = initial_total_cost + self.cost_multiplier_usd;
      arcpy.AddMessage("total_cost_usd");
      arcpy.AddMessage(".   = total cost usd (" + str(initial_total_cost) + ") + cost multiplier usd (" + str(self.cost_multiplier_usd) + ")");  
      arcpy.AddMessage(".   = " + str(self.cost_usd)); 

   #...........................................................................
   def output(self):
      return (
          self.scenarioid
         ,self.conditionid
         ,self.factorid
         ,self.facility_identifier
         ,self.facility_rank
         ,self.total_distance
         ,self.distance_unit
         ,self.total_trucktraveltime
         ,self.time_unit
         ,self.average_speed
         ,self.speed_unit
         ,self.facility_name
         ,self.facility_address
         ,self.facility_city
         ,self.facility_state
         ,self.facility_zip
         ,self.facility_telephone
         ,self.facility_waste_mgt
         ,self.facility_capacity_trucks_perday
         ,self.facility_qty_accepted
         ,self.facility_qty_accepted_unit
         ,self.shape
         ,self.allocated_amount
         ,self.allocated_amount_unit
         ,self.number_of_shipments
         ,self.cplm_cost_usd
         ,self.fixed_cost_usd_per_shipment
         ,self.fixed_cost_usd_per_hour
         ,self.tolls_usd
         ,self.misc_trans_cost_usd
         ,self.trans_cost_usd
         ,self.staging_site_cost_usd
         ,self.disposal_cost_usd
         ,self.labor_cost_usd
         ,self.vehicle_decon_cost_usd
         ,self.cost_multiplier_usd
         ,self.cost_usd
         ,self.trucks_time_to_comp_days
         ,self.dest_time_to_comp_days
         ,self.time_days
      );
