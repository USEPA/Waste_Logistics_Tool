import arcpy,os,math;
import source.util;

###############################################################################
class FaciltyCalc:

   #...........................................................................
   def __init__(self
      ,haz
      ,scenarioid
      ,conditionid
      ,factorid
      ,facilityattributesid
      ,road_transporter
      ,rail_transporter
      ,facility_identifier
      ,facility_rank
      
      ,total_network_impedance
      
      ,total_overall_distance
      ,total_overall_distance_unt
      ,total_overall_time
      ,total_overall_time_unt
      
      ,total_road_distance
      ,total_road_distance_unt
      ,total_road_time
      ,total_road_time_unt
      
      ,total_rail_distance
      ,total_rail_distance_unt
      ,total_rail_time
      ,total_rail_time_unt
      
      ,total_station_count
      
      ,facility_typeid
      ,facility_subtypeids
      ,facility_name
      ,facility_address
      ,facility_city
      ,facility_state
      ,facility_zip
      ,facility_telephone
      ,facility_waste_mgt
      
      ,facility_dly_cap
      ,facility_dly_cap_unt
      ,facility_dly_cap_src
      ,facility_dly_cap_err
      
      ,facility_qty_accepted
      ,facility_qty_accepted_unt
      ,facility_qty_accepted_src
      ,facility_qty_accepted_err
      
      ,facility_disposal_fee
      ,facility_disposal_fee_unt
      ,facility_disposal_fee_src
      ,facility_disposal_fee_err
      
      ,shape
      ,unit_system
      ,waste_type
      ,waste_medium
      ,waste_amount
      ,waste_unit
   ):
      #////////////////////////////////////////////////////////////////////////
      self.haz                              = None;
      self.scenarioid                       = None;
      self.conditionid                      = None;
      self.factorid                         = None;
      self.facilityattributesid             = None;
      self.road_transporter                 = None;
      self.rail_transporter                 = None;
      self.facility_identifier              = None;
      self.facility_rank                    = None;
      
      self.total_network_impedance          = None;
      
      self.total_overall_distance           = None;
      self.total_overall_distance_unt       = None;
      self.total_overall_time               = None;
      self.total_overall_time_unt           = None;
      
      self.total_road_distance              = None;
      self.total_road_distance_unt          = None;
      self.total_road_time                  = None;
      self.total_road_time_unt              = None;
      
      self.total_rail_distance              = None;
      self.total_rail_distance_unt          = None;
      self.total_rail_time                  = None;
      self.total_rail_time_unt              = None;
      
      self.total_station_count              = None;
      
      self.average_overall_speed            = None;
      self.average_road_speed               = None;
      self.average_rail_speed               = None;
      self.speed_unit                       = None;
      
      self.facility_typeid                  = None;
      self.facility_subtypeids              = None;
      self.facility_name                    = None;
      self.facility_address                 = None;
      self.facility_city                    = None;
      self.facility_state                   = None;
      self.facility_zip                     = None;
      self.facility_telephone               = None;
      self.facility_waste_mgt               = None;
      
      self.facility_dly_cap                 = None;
      self.facility_dly_cap_unt             = None;
      self.facility_dly_cap_src             = None;
      self.facility_dly_cap_err             = None;
      
      self.facility_qty_accepted            = None;
      self.facility_qty_accepted_unt        = None;
      self.facility_qty_accepted_src        = None;
      self.facility_qty_accepted_err        = None;
      
      self.facility_disposal_fee            = None;
      self.facility_disposal_fee_unt        = None;
      self.facility_disposal_fee_src        = None;
      self.facility_disposal_fee_err        = None;
      
      self.shape                            = None;
      
      self.allocated_amount                 = None;
      self.allocated_amount_unt             = None;
      
      self.number_of_road_shipments         = None;
      self.number_of_road_containers        = None;
      self.number_of_rail_shipments         = None;
      self.number_of_rail_containers        = None;
      
      self.road_cplm_cost_usd               = None;
      self.rail_cplm_cost_usd               = None;
      
      self.road_fixed_cost_usd_per_contnr   = None;
      self.rail_fixed_cost_usd_per_contnr   = None;
      
      self.road_fixed_cost_usd_per_hour     = None;
      self.rail_fixed_cost_usd_per_hour     = None;
      
      self.road_fixed_cost_usd_by_volume    = None;
      self.rail_fixed_cost_usd_by_volume    = None;
      
      self.road_tolls_usd_per_shipment      = None;
      
      self.road_misc_trans_cost_usd         = None;
      self.rail_misc_trans_cost_usd         = None;
      
      self.road_trans_cost_usd              = None;
      self.rail_trans_cost_usd              = None;
      
      self.staging_site_cost_usd            = None;
      
      self.disposal_cost_usd                = None;
      
      self.road_labor_cost_usd              = None;
      self.rail_labor_cost_usd              = None;
      
      self.road_transp_decon_cost_usd       = None;
      self.rail_transp_decon_cost_usd       = None;
      
      self.cost_multiplier_usd              = None;
      
      self.total_cost_usd                   = None;
      
      self.road_transp_time_to_comp_days    = None;
      self.rail_transp_time_to_comp_days    = None;
      self.total_transp_time_to_comp_days   = None;
      
      self.road_dest_time_to_comp_days      = None;
      self.rail_dest_time_to_comp_days      = None;
      self.total_dest_time_to_comp_days     = None;
      
      self.road_time_days                   = None;
      self.rail_time_days                   = None;
      self.time_days                        = None;
      
      self.username                         = None;
      self.creationtime                     = None;
      
      #////////////////////////////////////////////////////////////////////////
      self.haz                              = haz;
      self.scenarioid                       = scenarioid;
      self.conditionid                      = conditionid;
      self.factorid                         = factorid;
      self.facilityattributesid             = facilityattributesid;
      self.road_transporter                 = road_transporter;
      self.rail_transporter                 = rail_transporter;
      self.facility_identifier              = facility_identifier;
      self.facility_rank                    = facility_rank;
      
      self.total_network_impedance          = total_network_impedance;

      (self.total_overall_distance,self.total_overall_distance_unt) = source.util.converter(
          total_overall_distance_unt
         ,total_overall_distance
         ,unit_system
      );

      (self.total_overall_time,self.total_overall_time_unt) = source.util.converter(
          total_overall_time_unt
         ,total_overall_time
         ,'hr'
      );
      
      (self.total_road_distance,self.total_road_distance_unt) = source.util.converter(
          total_road_distance_unt
         ,total_road_distance
         ,unit_system
      );

      (self.total_road_time,self.total_road_time_unt) = source.util.converter(
          total_road_time_unt
         ,total_road_time
         ,'hr'
      );
      
      (self.total_rail_distance,self.total_rail_distance_unt) = source.util.converter(
          total_rail_distance_unt
         ,total_rail_distance
         ,unit_system
      );

      (self.total_rail_time,self.total_rail_time_unt) = source.util.converter(
          total_rail_time_unt
         ,total_rail_time
         ,'hr'
      );
      
      self.total_station_count             = total_station_count;

      self.average_overall_speed           = self.total_overall_distance / self.total_overall_time;
      
      if self.total_road_time is not None and self.total_road_time > 0:
         self.average_road_speed          = self.total_road_distance   / self.total_road_time;
      else:
         self.average_road_speed          = None;
      
      if self.total_rail_time is not None and self.total_rail_time > 0:
         self.average_rail_speed           = self.total_rail_distance    / self.total_rail_time;
      else:
         self.average_rail_speed           = None;
         
      self.speed_unit                      = self.total_overall_distance_unt + "/h";

      self.facility_typeid                 = facility_typeid;
      self.facility_subtypeids             = facility_subtypeids;
      self.facility_name                   = facility_name;
      self.facility_address                = facility_address;
      self.facility_city                   = facility_city;
      self.facility_state                  = facility_state;
      self.facility_zip                    = facility_zip;
      self.facility_telephone              = facility_telephone;
      self.facility_waste_mgt              = facility_waste_mgt;
      
      self.facility_dly_cap                = facility_dly_cap;
      self.facility_dly_cap_unt            = facility_dly_cap_unt;
      self.facility_dly_cap_src            = facility_dly_cap_src;
      self.facility_dly_cap_err            = facility_dly_cap_err;
      
      self.facility_qty_accepted           = facility_qty_accepted;
      self.facility_qty_accepted_unt       = facility_qty_accepted_unt;
      self.facility_qty_accepted_src       = facility_qty_accepted_src;
      self.facility_qty_accepted_err       = facility_qty_accepted_err;
      
      self.facility_disposal_fee           = facility_disposal_fee;
      self.facility_disposal_fee_unt       = facility_disposal_fee_unt;
      self.facility_disposal_fee_src       = facility_disposal_fee_src;
      self.facility_disposal_fee_err       = facility_disposal_fee_err;
      
      self.shape                           = shape;

      self.unit_system                     = unit_system;

   #...........................................................................
   def calc(self,running_total):
      
      #########################################################################
      arcpy.AddMessage(".....");
      wm = source.util.mediumMap(self.haz.scenario.waste_medium);
      wt = self.haz.scenario.waste_type;
      wu = self.haz.scenario.waste_unit;
      arcpy.AddMessage(". Routing " + str(wm) + " " + str(wt) + " " + str(wu) + " to facility " + str(self.facility_identifier) + ".");
      arcpy.AddMessage(".   Facility TypeID " + str(self.facility_typeid) + "; SubtypeIDs " + str(self.facility_subtypeids) + ".");
      arcpy.AddMessage(".   Facility Daily Capacity: " + str(self.facility_dly_cap) + " " + str(self.facility_dly_cap_unt));
      arcpy.AddMessage(".     Source: " + str(self.facility_dly_cap_src) + "; Errors: " + str(self.facility_dly_cap_err));
      arcpy.AddMessage(".   Facility Quantity Accepted: " + str(self.facility_qty_accepted) + " " + str(self.facility_qty_accepted_unt));
      arcpy.AddMessage(".     Source: " + str(self.facility_qty_accepted_src) + "; Errors: " + str(self.facility_qty_accepted_err));
      arcpy.AddMessage(".   Facility Disposal Fees: " + str(self.facility_disposal_fee) + " " + str(self.facility_disposal_fee_unt));
      arcpy.AddMessage(".     Source: " + str(self.facility_disposal_fee_src) + "; Errors: " + str(self.facility_disposal_fee_err));
      
      #########################################################################
      arcpy.AddMessage(".....");
      self.allocated_amount_unt = self.facility_qty_accepted_unt;
      if running_total > self.facility_qty_accepted:
         self.allocated_amount = self.facility_qty_accepted;
         arcpy.AddMessage(". Assigning full amount (" + str(self.allocated_amount) + " " + str(self.allocated_amount_unt) + ") to facility."); 
      else:
         self.allocated_amount = running_total;
         arcpy.AddMessage(". Assigning partial amount (" + str(self.allocated_amount) + " " + str(self.allocated_amount_unt) + ") to facility."); 
      
      #########################################################################
      #
      # Calculate road vs rail percentage
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Overall Route Distance: " + str(self.total_overall_distance) + " " + str(self.total_overall_distance_unt));
      arcpy.AddMessage(". Overall Route Time: "     + str(self.total_overall_time)     + " " + str(self.total_overall_time_unt));

      hasRoad = False;
      hasRail = False;
      if self.total_road_distance is None or self.total_road_distance == 0:
         road_ratio = 0;
      else:
         road_ratio = self.total_road_distance / self.total_overall_distance;
         hasRoad = True;
         arcpy.AddMessage(". Road Route Distance: " + str(self.total_road_distance) + " " + str(self.total_road_distance_unt));
         arcpy.AddMessage(". Road Route Time: "     + str(self.total_road_time)     + " " + str(self.total_road_time_unt));
         arcpy.AddMessage(". Road Average Speed: "  + str(self.average_road_speed)     + " " + str(self.speed_unit));
      arcpy.AddMessage(". Road percentage for route is " + str(road_ratio) + "");
      
      if self.total_rail_distance is None or self.total_rail_distance == 0:
         rail_ratio = 0;
      else:
         rail_ratio = self.total_rail_distance / self.total_overall_distance;
         hasRail = True;
         arcpy.AddMessage(". Rail Route Distance: " + str(self.total_rail_distance) + " " + str(self.total_rail_distance_unt));
         arcpy.AddMessage(". Rail Route Time: "     + str(self.total_rail_time)     + " " + str(self.total_rail_time_unt));
         arcpy.AddMessage(". Rail Average Speed: "  + str(self.average_rail_speed)     + " " + str(self.speed_unit));
      arcpy.AddMessage(". Rail percentage for route is " + str(rail_ratio) + ".");
         
      #########################################################################
      #
      # Define Transporter Capacities
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Define transporter capacities");
      
      if hasRoad:
         road_transporter_rez  = self.haz.transporterCapacity(
             mode              = 'Road'
            ,transporterattrid = self.road_transporter
         );
         road_transportercapacity          = road_transporter_rez['transportercapacity'];
         road_transportercapacityunit      = road_transporter_rez['transportercapacityunit'];
         road_transportersavailable        = road_transporter_rez['transportersavailable'];
         road_transportersprocessedperday  = road_transporter_rez['transportersprocessedperday'];
         road_containercountpertransporter = road_transporter_rez['containercountpertransporter'];
         road_containercapacity            = road_transporter_rez['containercapacity'];
         road_containercapacityunit        = road_transporter_rez['containercapacityunit'];
         
         arcpy.AddMessage(".    Road transporter capacity is " + str(road_transportercapacity) + " " + str(road_transportercapacityunit) + ".");
         arcpy.AddMessage(".    Road transporters available: " + str(road_transportersavailable) + ".");
         arcpy.AddMessage(".    Road transporters processed per day: " + str(road_transportersprocessedperday) + ".");
         arcpy.AddMessage(".    Road containers per transporter: " + str(road_containercountpertransporter) + ".");
         arcpy.AddMessage(".    Road container capacity: " + str(road_containercapacity) + " " + str(road_containercapacityunit) + ".");
      
      if hasRail:
         rail_transporter_rez  = self.haz.transporterCapacity(
             mode              = 'Rail'
            ,transporterattrid = self.rail_transporter
         );
         rail_transportercapacity          = rail_transporter_rez['transportercapacity'];
         rail_transportercapacityunit      = rail_transporter_rez['transportercapacityunit'];
         rail_transportersavailable        = rail_transporter_rez['transportersavailable'];
         rail_transportersprocessedperday  = rail_transporter_rez['transportersprocessedperday'];
         rail_containercountpertransporter = rail_transporter_rez['containercountpertransporter'];
         rail_containercapacity            = rail_transporter_rez['containercapacity'];
         rail_containercapacityunit        = rail_transporter_rez['containercapacityunit'];
         
         arcpy.AddMessage(".    Rail transporter capacity is " + str(rail_transportercapacity) + " " + str(rail_transportercapacityunit) + ".");
         arcpy.AddMessage(".    Rail transporters available: " + str(rail_transportersavailable) + ".");
         arcpy.AddMessage(".    Rail transporters processed per day: " + str(rail_transportersprocessedperday) + ".");
         arcpy.AddMessage(".    Rail containers per transporter: " + str(rail_containercountpertransporter) + ".");
         arcpy.AddMessage(".    Rail container capacity: " + str(rail_containercapacity) + " " + str(rail_containercapacityunit) + ".");
      
      #########################################################################
      #
      # Calculate Number of Waste Shipments and Containers
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate Number of Waste Shipments");
      
      if hasRoad:
         arcpy.AddMessage(". number_of_road_shipments");
         arcpy.AddMessage(".     = ceil(allocated amount (" + str(self.allocated_amount) + " " + str(self.allocated_amount_unt) + ") / (container capacity (" + str(road_containercapacity) + " " + str(road_containercapacityunit) + ") * container count per transporter (" + str(road_containercountpertransporter) + "))");
         if road_transportercapacity is None:
            road_shipments  = 0;
            road_containers = 0;
         else:
            road_shipments = math.ceil(self.allocated_amount / (road_containercapacity * road_containercountpertransporter));
         self.number_of_road_shipments  = road_shipments or 0;
         self.number_of_road_containers = self.number_of_road_shipments * road_containercountpertransporter;
      else:
         self.number_of_road_shipments  = 0;
         self.number_of_road_containers = 0;
      arcpy.AddMessage(".     number_of_road_shipments  = " + str(self.number_of_road_shipments));
      arcpy.AddMessage(".     number_of_road_containers = " + str(self.number_of_road_containers));
      
      if hasRail:
         arcpy.AddMessage(". number_of_rail_shipments");
         arcpy.AddMessage(".     = ceil(allocated amount (" + str(self.allocated_amount) + " " + str(self.allocated_amount_unt) + ") / (container capacity (" + str(rail_containercapacity) + " " + str(rail_containercapacityunit) + ") * container count per transporter (" + str(rail_containercountpertransporter) + "))");
         if rail_transportercapacity is None:
            rail_shipments  = 0;
            rail_containers = 0;
         else:
            rail_shipments = math.ceil(self.allocated_amount / (rail_containercapacity * rail_containercountpertransporter));
         self.number_of_rail_shipments = rail_shipments or 0;
         self.number_of_rail_containers = self.number_of_rail_shipments * rail_containercountpertransporter;
      else:
         self.number_of_rail_shipments  = 0;
         self.number_of_rail_containers = 0;
      arcpy.AddMessage(".     number_of_rail_shipments  = " + str(self.number_of_rail_shipments));
      arcpy.AddMessage(".     number_of_rail_containers = " + str(self.number_of_rail_containers));
      
      #########################################################################
      #
      # Calculate the Transportation CPLM Cost
      # as is calculated with distance, ratio is not applied
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate Cost Per Unit Miles (CPLM)");
      
      if hasRoad:
         road_cplm_rez = self.haz.CPLMUnitRate(
             mode          = 'Road'
            ,distance      = self.total_road_distance
            ,distance_unit = self.total_road_distance_unt
         );
         road_cplunit_rate     = road_cplm_rez['cplunit_rate'];
         road_cplunit_rateunit = road_cplm_rez['cplunit_rateunit'];
         arcpy.AddMessage(". road_cplm_cost_usd");
         arcpy.AddMessage(".     rate for " + str(wt) + " " + str(wm) + " at " + str(self.total_road_distance) + " " + str(self.total_road_distance_unt) + " = " + str(road_cplunit_rate) + " " + str(road_cplunit_rateunit));
         arcpy.AddMessage(".     = total road distance (" + str(self.total_road_distance) + " " + str(self.total_road_distance_unt) + ") * road cplm rate (" + str(road_cplunit_rate) + ") * number of road shipments (" + str(self.number_of_road_shipments) + ")");
         self.road_cplm_cost_usd = self.total_road_distance * road_cplunit_rate * self.number_of_road_shipments;
      else:
         self.road_cplm_cost_usd = 0;
      arcpy.AddMessage(".     road_cplm_cost_usd = " + str(self.road_cplm_cost_usd));
         
      if hasRail:
         rail_cplm_rez = self.haz.CPLMUnitRate(
             mode          = 'Rail'
            ,distance      = self.total_rail_distance
            ,distance_unit = self.total_rail_distance_unt
         );
         rail_cplunit_rate     = rail_cplm_rez['cplunit_rate'];
         rail_cplunit_rateunit = rail_cplm_rez['cplunit_rateunit'];
         arcpy.AddMessage(". rail_cplm_cost_usd");
         arcpy.AddMessage(".     rate for " + str(wt) + " " + str(wm) + " at " + str(self.total_rail_distance) + " " + str(self.total_rail_distance_unt) + " = " + str(rail_cplunit_rate) + " " + str(rail_cplunit_rateunit));
         arcpy.AddMessage(".     = total rail distance (" + str(self.total_rail_distance) + " " + str(self.total_rail_distance_unt) + ") * rail cplm rate (" + str(rail_cplunit_rate) + ") * number of rail shipments (" + str(self.number_of_rail_shipments) + ")");
         self.rail_cplm_cost_usd = self.total_rail_distance * rail_cplunit_rate * self.number_of_rail_shipments;
      else:
         self.rail_cplm_cost_usd = 0;
      arcpy.AddMessage(".     rail_cplm_cost_usd = " + str(self.rail_cplm_cost_usd));
      
      #########################################################################
      #
      # Calculate Fixed Costs per shipment container with mode ratio
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate the Fixed Cost Per Shipment Container");
      
      if hasRoad:
         road_per_contnr_fixed_cost_rez = self.haz.fixedTransCost(
             mode           = 'Road'
            ,fixedcost_type = 'Per container'
         );
         road_per_contnr_fixedcost_value     = road_per_contnr_fixed_cost_rez['fixedcost_value'];
         road_per_contnr_fixedcost_valueunit = road_per_contnr_fixed_cost_rez['fixedcost_valueunit'];
         arcpy.AddMessage(". road_per_contnr_fixedcost_value = " + str(road_per_contnr_fixedcost_value) + " per container");
         arcpy.AddMessage(". road_fixed_cost_usd_per_contnr");     
         arcpy.AddMessage(".     = number of road containers (" + str(self.number_of_road_containers) + ") * road_per_contnr_fixedcost_value (" + str(road_per_contnr_fixedcost_value) + ") * road_ratio (" + str(road_ratio) + ")");
         self.road_fixed_cost_usd_per_contnr = self.number_of_road_containers * road_per_contnr_fixedcost_value * road_ratio;
      else:
         self.road_fixed_cost_usd_per_contnr = 0;
      arcpy.AddMessage(".     road_fixed_cost_usd_per_contnr = " + str(self.road_fixed_cost_usd_per_contnr));

      if hasRail:
         rail_per_contnr_fixed_cost_rez = self.haz.fixedTransCost(
             mode           = 'Rail'
            ,fixedcost_type = 'Per container'
         );
         rail_per_contnr_fixedcost_value     = rail_per_contnr_fixed_cost_rez['fixedcost_value'];
         rail_per_contnr_fixedcost_valueunit = rail_per_contnr_fixed_cost_rez['fixedcost_valueunit'];
         arcpy.AddMessage(". rail_fixed_cost_usd_per_contnr");
         arcpy.AddMessage(".     rate for " + wt + " " + wm + " = " + str(rail_per_contnr_fixedcost_value) + " per container");
         arcpy.AddMessage(".     = number of rail containers (" + str(self.number_of_rail_containers) + ") * rail_per_contnr_fixedcost_value (" + str(rail_per_contnr_fixedcost_value) + ") * rail_ratio (" + str(rail_ratio) + ")");
         self.rail_fixed_cost_usd_per_contnr = self.number_of_rail_containers * rail_per_contnr_fixedcost_value * rail_ratio;
      else:
         self.rail_fixed_cost_usd_per_contnr = 0;
      arcpy.AddMessage(".     rail_fixed_cost_usd_per_container = " + str(self.rail_fixed_cost_usd_per_contnr));
      
      #########################################################################
      #
      # Calculate Fixed Costs per hour
      # as is calculated with distance, ratio is not applied
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate the Fixed Cost Per Hour");
      
      if hasRoad:
         road_per_hour_fixed_cost_rez = self.haz.fixedTransCost(
             mode           = 'Road'
            ,fixedcost_type = 'Per hour'
         );
         road_per_hour_fixedcost_value     = road_per_hour_fixed_cost_rez['fixedcost_value'];
         road_per_hour_fixedcost_valueunit = road_per_hour_fixed_cost_rez['fixedcost_valueunit'];
         nos = self.number_of_road_shipments;
         tds = self.total_road_distance;
         tdu = self.total_road_distance_unt;
         spd = self.average_road_speed;
         spu = self.speed_unit;
         arcpy.AddMessage(". road_fixed_cost_usd_per_hour");
         arcpy.AddMessage(".     road_per_hour_fixedcost_value = " + str(road_per_hour_fixedcost_value) + " per hour");
         arcpy.AddMessage(".     = number of shipments (" + str(nos) + ") * total distance (" + str(tds) + " " + str(tdu) + ") * 2 / average speed (" + str(spd) + " " + str(spu) + ") * road_per_hour_fixedcost_value (" + str(road_per_hour_fixedcost_value) + ")");
         self.road_fixed_cost_usd_per_hour = nos * tds * 2 / spd * road_per_hour_fixedcost_value;
      else:
         self.road_fixed_cost_usd_per_hour = 0;
      arcpy.AddMessage(".     road_fixed_cost_usd_per_hour = " + str(self.road_fixed_cost_usd_per_hour));

      if hasRail:
         rail_per_hour_fixed_cost_rez = self.haz.fixedTransCost(
             mode           = 'Rail'
            ,fixedcost_type = 'Per hour'
         );
         rail_per_hour_fixedcost_value     = rail_per_hour_fixed_cost_rez['fixedcost_value'];
         rail_per_hour_fixedcost_valueunit = rail_per_hour_fixed_cost_rez['fixedcost_valueunit'];
         nos = self.number_of_rail_shipments;
         tds = self.total_rail_distance;
         tdu = self.total_rail_distance_unt;
         spd = self.average_rail_speed;
         spu = self.speed_unit;
         arcpy.AddMessage(". rail_fixed_cost_usd_per_hour");
         arcpy.AddMessage(".     rail_per_hour_fixedcost_value = " + str(rail_per_hour_fixedcost_value) + " per hour");
         arcpy.AddMessage(".     = number of shipments (" + str(nos) + ") * total distance (" + str(tds) + " " + str(tdu) + ") * 2 / average speed (" + str(spd) + " " + str(spu) +  ") * rail_per_hour_fixedcost_value (" + str(rail_per_hour_fixedcost_value) + ")");
         self.rail_fixed_cost_usd_per_hour = nos * tds * 2 / spd * rail_per_hour_fixedcost_value;
      else:
         self.rail_fixed_cost_usd_per_hour = 0;
      arcpy.AddMessage(".     rail_per_hour_fixedcost_value = " + str(self.rail_fixed_cost_usd_per_hour));

      #########################################################################
      #
      # Calculate Fixed Costs by Volume
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate the Fixed Cost By Volume");
      
      if hasRoad:
         road_by_volume_fixed_cost_rez = self.haz.fixedTransCost(
             mode           = 'Road'
            ,fixedcost_type = 'By Volume'
         );
         road_by_volume_fixedcost_value     = road_by_volume_fixed_cost_rez['fixedcost_value'];
         road_by_volume_fixedcost_valueunit = road_by_volume_fixed_cost_rez['fixedcost_valueunit'];

         arcpy.AddMessage(". road_fixed_cost_usd_by_volume");
         arcpy.AddMessage(".     road_by_volume_fixedcost_value = " + str(road_by_volume_fixedcost_value) + " " + str(road_by_volume_fixedcost_valueunit));
         arcpy.AddMessage(".     = waste allocated (" + str(self.allocated_amount) + " " + str(self.haz.scenario.waste_unit) + ") * road_by_volume_fixedcost_value ($" + str(road_by_volume_fixedcost_value) + ")");
         self.road_fixed_cost_usd_by_volume = self.allocated_amount * road_by_volume_fixedcost_value;
      else:
         self.road_fixed_cost_usd_by_volume = 0;
      arcpy.AddMessage(".     road_by_volume_fixedcost_value = " + str(self.road_fixed_cost_usd_by_volume));

      if hasRail:
         rail_by_volume_fixed_cost_rez = self.haz.fixedTransCost(
             mode           = 'Rail'
            ,fixedcost_type = 'By Volume'
         );
         rail_by_volume_fixedcost_value     = rail_by_volume_fixed_cost_rez['fixedcost_value'];
         rail_by_volume_fixedcost_valueunit = rail_by_volume_fixed_cost_rez['fixedcost_valueunit'];

         arcpy.AddMessage(". rail_fixed_cost_usd_by_volume");
         arcpy.AddMessage(".     rail_by_volume_fixedcost_value = " + str(rail_by_volume_fixedcost_value) + " " + str(rail_by_volume_fixedcost_valueunit));
         arcpy.AddMessage(".     = waste allocated (" + str(self.allocated_amount) + " " + str(self.haz.scenario.waste_unit) + ") * rail_by_volume_fixedcost_value ($" + str(rail_by_volume_fixedcost_value) + ")");
         self.rail_fixed_cost_usd_by_volume = self.allocated_amount * rail_by_volume_fixedcost_value;
      else:
         self.rail_fixed_cost_usd_by_volume = 0;
      arcpy.AddMessage(".     rail_by_volume_fixedcost_value = " + str(self.rail_fixed_cost_usd_by_volume));
          
      #########################################################################
      #
      # Calculate the Road Tolls Per Shipment
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate the Road Tolls Per Shipment");

      if hasRoad:
         nos = self.number_of_road_shipments;
         arcpy.AddMessage(". road_tolls_usd_per_shipment");
         arcpy.AddMessage(".     = number of shipments (" + str(nos) + ") * road tolls (" + str(self.haz.conditions.roadtollsperroadshipment) + ") * 2")
         self.road_tolls_usd_per_shipment = nos * self.haz.conditions.roadtollsperroadshipment * 2;
      else:
         self.road_tolls_usd_per_shipment = 0;
      arcpy.AddMessage(".     road_tolls_usd_per_shipment = " + str(self.road_tolls_usd_per_shipment));

      #########################################################################
      #
      # Calculate Misc Costs Per Shipment
      # including mode ratio
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate Misc Costs Per Shipment");
      
      if hasRoad:
         nos = self.number_of_road_shipments;
         arcpy.AddMessage(". road misc cost");
         arcpy.AddMessage(".     = number of road shipments (" + str(nos) + ") * misc cost (" + str(self.haz.conditions.misccostperroadshipment) + ")");
         self.road_misc_trans_cost_usd = nos * self.haz.conditions.misccostperroadshipment;
      else:
         self.road_misc_trans_cost_usd = 0;
      arcpy.AddMessage(".     road_misc_trans_cost_usd = " + str(self.road_misc_trans_cost_usd)); 
      
      if hasRail:
         nos = self.number_of_rail_shipments;
         arcpy.AddMessage(". rail misc cost");
         arcpy.AddMessage(".     = number of rail shipments (" + str(nos) + ") * misc cost (" + str(self.haz.conditions.misccostperrailshipment) + ")");
         self.rail_misc_trans_cost_usd = nos * self.haz.conditions.misccostperrailshipment;
      else:
         self.rail_misc_trans_cost_usd = 0;
      arcpy.AddMessage(".     rail_misc_trans_cost_usd = " + str(self.rail_misc_trans_cost_usd));
      
      #########################################################################
      #
      # Calculate the Transportion Time to Complete Transportation of Waste (days)
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate the Transportion Time to Complete Transportation of Waste ");
      
      if hasRoad:
         nos = self.number_of_road_shipments;
         tds = self.total_road_distance;
         tdu = self.total_road_distance_unt;
         spd = self.average_road_speed;
         spu = self.speed_unit;
         nta = road_transportersavailable;
         dhr = self.haz.conditions.roaddrivinghoursperday; 
         arcpy.AddMessage(". road_time_to_complete");
         arcpy.AddMessage(".     = ceil(((((road distance (" + str(tds) + " " + str(tdu) + ") * 2 ) / average road speed(" + str(spd) + " " + str(spu) + ")) / road driving hours (" + str(dhr) + ")) * number of road shipments (" + str(nos) + ")) / available road transporters (" + str(nta) + "))");
         self.road_transp_time_to_comp_days = math.ceil(
            ((((tds * 2) / spd) / dhr) * nos) / nta
         ) or 0;
      else:
         self.road_transp_time_to_comp_days = 0;
      arcpy.AddMessage(".     road_transp_time_to_comp_days = " + str(self.road_transp_time_to_comp_days));
         
      if hasRail:
         nos = self.number_of_rail_shipments;
         tds = self.total_rail_distance;
         tdu = self.total_rail_distance_unt;
         spd = self.average_rail_speed;
         spu = self.speed_unit;
         nta = rail_transportersavailable;
         dhr = self.haz.conditions.raildrivinghoursperday; 
         arcpy.AddMessage(". rail_time_to_complete");
         arcpy.AddMessage(".     = ceil(((((rail distance (" + str(tds) + " " + str(tdu) + ") * 2) / average rail speed(" + str(spd) + " " + str(spu) + ")) / rail driving hours (" + str(dhr) + ")) * number of rail shipments (" + str(nos) + ")) / available rail transporters (" + str(nta) + "))");
         self.rail_transp_time_to_comp_days = math.ceil(
            ((((tds * 2) / spd) / dhr) * nos) / nta
         ) or 0;
      else:
         self.rail_transp_time_to_comp_days = 0;
      arcpy.AddMessage(".     rail_transp_time_to_comp_days = " + str(self.rail_transp_time_to_comp_days));
      
      self.total_transp_time_to_comp_days = self.road_transp_time_to_comp_days + self.rail_transp_time_to_comp_days;
      
      #########################################################################
      #
      # Calculate the Destination Time to Complete Transportation (days) 
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate Destination Time to Complete in Days");
      
      if hasRoad:
         self.road_dest_time_to_comp_days = math.ceil(
            self.number_of_road_shipments / road_transportersprocessedperday
         );
      else:
         self.road_dest_time_to_comp_days = 0;
      arcpy.AddMessage(".    road_dest_time_to_comp_days = " + str(self.road_dest_time_to_comp_days));
      
      if hasRail:
         self.rail_dest_time_to_comp_days = math.ceil(
            self.number_of_rail_shipments / rail_transportersprocessedperday
         );
      else:
         self.rail_dest_time_to_comp_days = 0;
      arcpy.AddMessage(".    rail_dest_time_to_comp_days = " + str(self.rail_dest_time_to_comp_days));
      
      self.total_dest_time_to_comp_days = self.road_dest_time_to_comp_days + self.rail_dest_time_to_comp_days;
      
      #########################################################################
      #
      # Calculate Total Transportation Time (days) 
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate Total Transportation Time (days) ");
      
      if hasRoad:
         arcpy.AddMessage(". road time_days");
         arcpy.AddMessage(".     = max(road_transp_time_to_comp_days (" + str(self.road_transp_time_to_comp_days) + "), road_dest_time_to_comp_days (" + str(self.road_dest_time_to_comp_days) + "))");
         self.road_time_days = max(self.road_transp_time_to_comp_days,self.road_dest_time_to_comp_days);
      else:
         self.road_time_days = 0;
      arcpy.AddMessage(".     road time_days = " + str(self.road_time_days));
      
      if hasRail:
         arcpy.AddMessage(". rail time_days");
         arcpy.AddMessage(".     = max(rail_transp_time_to_comp_days (" + str(self.rail_transp_time_to_comp_days) + "), rail_dest_time_to_comp_days (" + str(self.rail_dest_time_to_comp_days) + "))");
         self.rail_time_days = max(self.rail_transp_time_to_comp_days,self.rail_dest_time_to_comp_days);
      else:
         self.rail_time_days = 0;
      arcpy.AddMessage(".     rail time_days = " + str(self.rail_time_days));
      
      self.time_days = self.road_time_days + self.rail_time_days;       
       
      #########################################################################
      #
      # Calculate Waste Staging Site Cost ($) 
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate Waste Staging Site Cost ($)");

      if self.facility_waste_mgt == "Staging":
         arcpy.AddMessage(". staging_site_cost_usd");
         arcpy.AddMessage(".     = time_days (" + str(self.time_days) + " * staging site cost (" + str(self.haz.conditions.stagingsitecost) + ")");
         self.staging_site_cost_usd = self.time_days * self.haz.conditions.stagingsitecost;
         arcpy.AddMessage(".     = " + str(self.staging_site_cost_usd));
      else:
         self.staging_site_cost_usd = 0;
         arcpy.AddMessage(".     Not a staging site facility. Zeroed out.");
      arcpy.AddMessage(".     staging_site_cost_usd = " + str(self.staging_site_cost_usd));       

      #########################################################################
      #
      # Calculate Waste Disposal Cost ($)
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate Waste Disposal Cost ($)");
      
      if self.facility_waste_mgt == "Staging":
         self.disposal_cost_usd = 0;
         arcpy.AddMessage(".     Not a disposal site facility. Zeroed out.");
      else:
         disposal_fees_costperone     = self.facility_disposal_fee;
         disposal_fees_costperoneunit = self.facility_disposal_fee_unt; 
         arcpy.AddMessage(".     disposal_fees_costperone = " + str(disposal_fees_costperone) + " per " + str(disposal_fees_costperoneunit));
         arcpy.AddMessage(".     = allocated amount (" + str(self.allocated_amount) + " " + self.allocated_amount_unt + ") * disposal cost rate (" + str(disposal_fees_costperone) + " " + str(disposal_fees_costperoneunit) + ")");
         self.disposal_cost_usd = round(self.allocated_amount * disposal_fees_costperone,2);
      arcpy.AddMessage(".     disposal_cost_usd = " + str(self.disposal_cost_usd));
         
      #########################################################################
      #
      # Calculate Labor Costs
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate Labor Costs");

      if hasRoad:
         road_labor_costs_rez            = self.haz.laborCosts('Road');
         road_labor_costs_laborcost      = road_labor_costs_rez['laborcost'];
         road_labor_costs_laborcost_unit = road_labor_costs_rez['laborcostunit'];
         arcpy.AddMessage(".     rate for road transporter drivers = " + str(road_labor_costs_laborcost) + " per hour");
         nos = self.number_of_road_shipments;
         tds = self.total_road_distance;
         spd = self.average_road_speed;
         nta = road_transportersavailable;
         arcpy.AddMessage(".     = ( number of road shipments (" + str(nos) + ") / number of road transporters available (" + str(nta) + ") ) * total distance (" + str(tds) + " " + str(self.total_road_distance_unt) + ") * 2 / average road speed (" + str(spd) + " per hour) * labor rate (" + str(road_labor_costs_laborcost) + ") * number of road transporters available (" + str(nta) + ")")
         self.road_labor_cost_usd = ( nos / nta ) * tds * 2 / spd * road_labor_costs_laborcost * nta;
      else:
         self.road_labor_cost_usd = 0;
      arcpy.AddMessage(".     road_labor_cost_usd = " + str(self.road_labor_cost_usd));
         
      if hasRail:
         rail_labor_costs_rez            = self.haz.laborCosts('Rail');
         rail_labor_costs_laborcost      = rail_labor_costs_rez['laborcost'];
         rail_labor_costs_laborcost_unit = rail_labor_costs_rez['laborcostunit'];
         arcpy.AddMessage(".     rate for rail transporter drivers = " + str(rail_labor_costs_laborcost) + " per hour");
         nos = self.number_of_rail_shipments;
         tds = self.total_rail_distance;
         spd = self.average_rail_speed;
         nta = rail_transportersavailable;
         arcpy.AddMessage(".     = ( number of rail shipments (" + str(nos) + ") / number of rail transporters available (" + str(nta) + ") ) * total distance (" + str(tds) + " " + str(self.total_rail_distance_unt) + ") * 2 / average rail speed (" + str(spd) + " per hour) * labor rate (" + str(rail_labor_costs_laborcost) + ") * number of rail transporters available (" + str(nta) + ")")
         self.rail_labor_cost_usd = ( nos / nta ) * tds * 2 / spd * rail_labor_costs_laborcost * nta;
      else:
         self.rail_labor_cost_usd = 0;
      arcpy.AddMessage(".     rail_labor_cost_usd = " + str(self.rail_labor_cost_usd));
      
      #########################################################################
      #
      # Calculate Vehicle Decontamination Cost ($) 
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate Vehicle Decontamination Cost ($)");
      
      if hasRoad:
         arcpy.AddMessage(". road_transp_decon_cost_usd");
         arcpy.AddMessage(".     = number of road shipments (" + str(self.number_of_road_shipments) + ") * vehicle decon cost (" + str(self.haz.conditions.roadtransporterdeconcost) + ")");
         self.road_transp_decon_cost_usd = self.number_of_road_shipments * self.haz.conditions.roadtransporterdeconcost;
      else:
         self.road_transp_decon_cost_usd = 0;
      arcpy.AddMessage(".     road_transp_decon_cost_usd = " + str(self.road_transp_decon_cost_usd));
      
      if hasRail:
         arcpy.AddMessage(". rail_transp_decon_cost_usd");
         arcpy.AddMessage(".     = number of rail shipments (" + str(self.number_of_rail_shipments) + ") * vehicle decon cost (" + str(self.haz.conditions.railtransporterdeconcost) + ")");
         self.rail_transp_decon_cost_usd = self.number_of_rail_shipments * self.haz.conditions.railtransporterdeconcost;
      else:
         self.rail_transp_decon_cost_usd = 0;
      arcpy.AddMessage(".     rail_transp_decon_cost_usd = " + str(self.rail_transp_decon_cost_usd));
 
      #########################################################################
      #
      # Sum Total Transportation Cost 
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Sum Total Transportation Cost");
      
      if hasRoad:
         arcpy.AddMessage(". road total trans cost");
         arcpy.AddMessage(".     = road_cplm_cost_usd (" + str(self.road_cplm_cost_usd) + ") + road_fixed_cost_usd_per_contnr (" + str(self.road_fixed_cost_usd_per_contnr) \
         + ") + road_fixed_cost_usd_per_hour (" + str(self.road_fixed_cost_usd_per_hour) + ") + road_fixed_cost_usd_by_volume (" + str(self.road_fixed_cost_usd_by_volume)  \
         + ") + road_tolls_usd_per_shipment (" + str(self.road_tolls_usd_per_shipment) + ") + road_misc_trans_cost_usd (" + str(self.road_misc_trans_cost_usd) + ")");
         self.road_trans_cost_usd = (           \
           self.road_cplm_cost_usd              \
         + self.road_fixed_cost_usd_per_contnr  \
         + self.road_fixed_cost_usd_per_hour    \
         + self.road_fixed_cost_usd_by_volume   \
         + self.road_tolls_usd_per_shipment     \
         + self.road_misc_trans_cost_usd        \
         );
      else:
         self.road_trans_cost_usd = 0;
      arcpy.AddMessage(".     road_trans_cost_usd = " + str(self.road_trans_cost_usd)); 
                          
      if hasRail:
         arcpy.AddMessage(". rail total trans cost");
         arcpy.AddMessage(".     = rail_cplm_cost_usd (" + str(self.rail_cplm_cost_usd) + ") + rail_fixed_cost_usd_per_contnr (" + str(self.rail_fixed_cost_usd_per_contnr) \
         + ") + rail_fixed_cost_usd_per_hour (" + str(self.rail_fixed_cost_usd_per_hour) + ") + rail_fixed_cost_usd_by_volume (" + str(self.rail_fixed_cost_usd_by_volume)  \
         + ") + rail_misc_trans_cost_usd (" + str(self.rail_misc_trans_cost_usd) + ")");
         self.rail_trans_cost_usd = (           \
           self.rail_cplm_cost_usd              \
         + self.rail_fixed_cost_usd_per_contnr  \
         + self.rail_fixed_cost_usd_per_hour    \
         + self.rail_fixed_cost_usd_by_volume   \
         + self.rail_misc_trans_cost_usd        \
         );
      else:
         self.rail_trans_cost_usd = 0;
      arcpy.AddMessage(".     rail_trans_cost_usd = " + str(self.rail_trans_cost_usd)); 
      
      #########################################################################
      #
      # Subtotal Road and Rail Transportation Results 
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Subtotal Road and Rail Transportation Results");
      
      if hasRoad:
         arcpy.AddMessage(". subtotal_road_cost_usd");
         arcpy.AddMessage(".     = ( self.road_trans_cost_usd (" + str(self.road_trans_cost_usd) + ") + road_labor_cost_usd (" + str(self.road_labor_cost_usd) \
          + ") + road transporter decon cost ("  + str(self.road_transp_decon_cost_usd) + "))");
         subtotal_road_cost_usd = (                   \
            self.road_trans_cost_usd              \
          + self.road_labor_cost_usd              \
          + self.road_transp_decon_cost_usd       \
         );
      else:
         subtotal_road_cost_usd = 0;
      arcpy.AddMessage(".     subtotal_road_cost_usd = " + str(subtotal_road_cost_usd));
         
      if hasRail:
         arcpy.AddMessage(". subtotal_rail_cost_usd");
         arcpy.AddMessage(".     = ( self.rail_trans_cost_usd (" + str(self.rail_trans_cost_usd) + ") + rail_labor_cost_usd (" + str(self.rail_labor_cost_usd) \
          + ") + rail transporter decon cost ("  + str(self.rail_transp_decon_cost_usd) + "))");
         subtotal_rail_cost_usd = (               \
            self.rail_trans_cost_usd              \
          + self.rail_labor_cost_usd              \
          + self.rail_transp_decon_cost_usd       \
         );
      else:
         subtotal_rail_cost_usd = 0;
      arcpy.AddMessage(".     subtotal_rail_cost_usd = " + str(subtotal_rail_cost_usd));
      
      #########################################################################
      #
      # Subtotal Transportation and Facility Costs
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Subtotal Transportation and Facility Costs");
      
      arcpy.AddMessage(". subtotal_trans_fac_costs");
      arcpy.AddMessage(".     = subtotal_road_cost_usd (" + str(subtotal_road_cost_usd) + ") + "
      + "subtotal_rail_cost_usd (" + str(subtotal_rail_cost_usd) + ") + "
      + "disposal_cost_usd (" + str(self.disposal_cost_usd) + ") + "
      + "staging_site_cost_usd (" + str(self.staging_site_cost_usd)  + ") + "
      + "road_labor_cost_usd (" + str(self.road_labor_cost_usd) + ") + "
      + "rail_labor_cost_usd (" + str(self.rail_labor_cost_usd) + ") + "
      + "road_transp_decon_cost_usd (" + str(self.road_transp_decon_cost_usd) + ") + "
      + "rail_transp_decon_cost_usd (" + str(self.rail_transp_decon_cost_usd) + ") ");
      
      subtotal_trans_fac_costs = (                                        \
        subtotal_road_cost_usd + subtotal_rail_cost_usd                   \
      + self.disposal_cost_usd + self.staging_site_cost_usd               \
      ); 
      arcpy.AddMessage(".   subtotal_trans_fac_costs = " + str(subtotal_trans_fac_costs));
      
      #########################################################################
      #
      # Calculate Multiplier Amount
      #
      #########################################################################
      arcpy.AddMessage(".....");
      arcpy.AddMessage(". Calculate Additional Cost Due to Multiplier ($)");
      
      if self.haz.conditions.totalcostmultiplier is None or self.haz.conditions.totalcostmultiplier == 0:
         self.cost_multiplier_usd = 0;
      else:
         self.cost_multiplier_usd = subtotal_trans_fac_costs * self.haz.conditions.totalcostmultiplier;
      arcpy.AddMessage(".   cost_multiplier_usd = " + str(self.cost_multiplier_usd));
      
      #########################################################################
      #
      # Calculate Total Cost ($)
      #
      #########################################################################
      arcpy.AddMessage("....."); 
      arcpy.AddMessage(". Calculate Total Cost ($) ");
      
      arcpy.AddMessage(". total cost");
      arcpy.AddMessage(".     = subtotal_trans_fac_costs (" + str(subtotal_trans_fac_costs) + ") + cost_multiplier_usd (" + str(self.cost_multiplier_usd) + ")");
      self.total_cost_usd = subtotal_trans_fac_costs + self.cost_multiplier_usd;
      arcpy.AddMessage(".     total_cost_usd = " + str(self.total_cost_usd));

   #...........................................................................
   def output(self):
      return (
          self.scenarioid
         ,self.conditionid
         ,self.factorid
         ,self.facilityattributesid
         ,self.road_transporter
         ,self.rail_transporter
         ,self.facility_identifier
         ,self.facility_rank
         
         ,self.total_overall_distance
         ,self.total_overall_distance_unt
         ,self.total_overall_time
         ,self.total_overall_time_unt
         
         ,self.total_road_distance
         ,self.total_road_distance_unt
         ,self.total_road_time
         ,self.total_road_time_unt
         
         ,self.total_rail_distance
         ,self.total_rail_distance_unt
         ,self.total_rail_time
         ,self.total_rail_time_unt
         
         ,self.total_station_count
         
         ,self.average_overall_speed
         ,self.average_road_speed
         ,self.average_rail_speed
         ,self.speed_unit
         
         ,self.facility_typeid
         ,self.facility_subtypeids
         ,self.facility_name
         ,self.facility_address
         ,self.facility_city
         ,self.facility_state
         ,self.facility_zip
         ,self.facility_telephone
         ,self.facility_waste_mgt
         
         ,self.facility_dly_cap
         ,self.facility_dly_cap_unt
         
         ,self.facility_qty_accepted
         ,self.facility_qty_accepted_unt
         
         ,self.shape
         
         ,self.allocated_amount
         ,self.allocated_amount_unt
         
         ,self.number_of_road_shipments
         ,self.number_of_rail_shipments 
         
         ,self.road_cplm_cost_usd
         ,self.rail_cplm_cost_usd
         
         ,self.road_fixed_cost_usd_per_contnr
         ,self.rail_fixed_cost_usd_per_contnr
         
         ,self.road_fixed_cost_usd_per_hour
         ,self.rail_fixed_cost_usd_per_hour
         
         ,self.road_fixed_cost_usd_by_volume
         ,self.rail_fixed_cost_usd_by_volume
         
         ,self.road_tolls_usd_per_shipment
         
         ,self.road_misc_trans_cost_usd
         ,self.rail_misc_trans_cost_usd
         
         ,self.road_trans_cost_usd
         ,self.rail_trans_cost_usd
         
         ,self.staging_site_cost_usd
         
         ,self.disposal_cost_usd
         
         ,self.road_labor_cost_usd
         ,self.rail_labor_cost_usd
         
         ,self.road_transp_decon_cost_usd
         ,self.rail_transp_decon_cost_usd
         
         ,self.cost_multiplier_usd
         
         ,self.total_cost_usd
         
         ,self.road_transp_time_to_comp_days
         ,self.rail_transp_time_to_comp_days
         ,self.total_transp_time_to_comp_days
         
         ,self.road_dest_time_to_comp_days
         ,self.rail_dest_time_to_comp_days
         ,self.total_dest_time_to_comp_days
         
         ,self.time_days
      );
