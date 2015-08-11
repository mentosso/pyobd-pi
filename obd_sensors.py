#!/usr/bin/env python
###########################################################################
# obd_sensors.py
#
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)
# Copyright 2009 Secons Ltd. (www.obdtester.com)
#
# This file is part of pyOBD.
#
# pyOBD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pyOBD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyOBD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###########################################################################

def hex_to_int(str):
    i = eval("0x" + str, {}, {})
    return i

def maf(code):
    code = hex_to_int(code)
    return code * 0.00132276

def throttle_pos(code):
    code = hex_to_int(code)
    return code * 100.0 / 255.0

def intake_m_pres(code): # in kPa
    code = hex_to_int(code)
    return code / 0.14504
  
def rpm(code):
    code = hex_to_int(code)
    return code / 4

def speed(code):
    code = hex_to_int(code)
    return code / 1.609

def percent_scale(code):
    code = hex_to_int(code)
    return code * 100.0 / 255.0

def timing_advance(code):
    code = hex_to_int(code)
    return (code - 128) / 2.0

def sec_to_min(code):
    code = hex_to_int(code)
    return code / 60

def temp(code):
    code = hex_to_int(code)
    c = code - 40 
    return 32 + (9 * c / 5) 

def cpass(code):
    #fixme
    return code

def fuel_trim_percent(code):
    code = hex_to_int(code)
    #return (code - 128.0) * 100.0 / 128
    return (code - 128) * 100 / 128

def fuel_trim_percent_2(code):
    code = hex_to_int(code[2:4])
    #return (code - 128.0) * 100.0 / 128
    return (code - 128) * 100 / 128

def dtc_decrypt(code):
    #first byte is byte after PID and without spaces
    num = hex_to_int(code[:2]) #A byte
    res = []

    if num & 0x80: # is mil light on
        mil = 1
    else:
        mil = 0
        
    # bit 0-6 are the number of dtc's. 
    num = num & 0x7f
    
    res.append(num)
    res.append(mil)
    
    numB = hex_to_int(code[2:4]) #B byte
      
    for i in range(0,3):
        res.append(((numB>>i)&0x01)+((numB>>(3+i))&0x02))
    
    numC = hex_to_int(code[4:6]) #C byte
    numD = hex_to_int(code[6:8]) #D byte
       
    for i in range(0,7):
        res.append(((numC>>i)&0x01)+(((numD>>i)&0x01)<<1))
    
    res.append(((numD>>7)&0x01)) #EGR SystemC7  bit of different 
    
    #return res
    return "#"

def hex_to_bitstring(str):
    bitstring = ""
    for i in str:
        # silly type safety, we don't want to eval random stuff
        if type(i) == type(''): 
            v = eval("0x%s" % i)
            if v & 8 :
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 4:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 2:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 1:
                bitstring += '1'
            else:
                bitstring += '0'                
    return bitstring

def mil(code):
    numA = hex_to_int(code[0:2])
    numB = hex_to_int(code[2:4])
    return numA * 256 + numB

def rel_fuel_press(code):
    return mil(code) * 0.079

def dir_fuel_press(code):
    return mil(code) * 10

def equivalence_ratio(code):
    numA = hex_to_int(code[0:2])
    numB = hex_to_int(code[2:4])
    return (numA * 256 + numB) * 2 / 65535

def vapor_press(code):
    return mil(code) / 4

def catalyst_temperature(code):
    return mil(code) / 10 - 40

def ctrl_module_vol(code):
    return mil(code) / 1000

def abs_load_val(code):
    return mil(code) / 100 * 255

def amb_air_temp(code):
    code = hex_to_int(code)
    return code - 40

def abs_vapor_press(code):
    return mil(code) / 200

def vapor_press(code):
    return mil(code) - 32767

def fuel_inj_timing(code):
    return (mil(code) - 26880)/128

def fuel_rate(code):
    return mil(code) / 100

def demand_eng(code):
    code = hex_to_int(code)
    return code - 125

def percent_torque_b(code):
    code = hex_to_int(code[2:4])
    return code - 125

def percent_torque_c(code):
    code = hex_to_int(code[4:6])
    return code - 125

def percent_torque_d(code):
    code = hex_to_int(code[6:8])
    return code - 125

def percent_torque_e(code):
    code = hex_to_int(code[8:10])
    return code - 125

def hex_string(code):
    string = "0x"
    for value in code:
        string += value
    return string

class Sensor:
    def __init__(self, shortName, sensorName, sensorcommand, sensorValueFunction, u):
        self.shortname = shortName
        self.name = sensorName
        self.cmd  = sensorcommand
        self.value= sensorValueFunction
        self.unit = u

SENSORS = [
    Sensor("pids"                  , "Supported PIDs"				                                            , "0100" , hex_to_bitstring ,""       ),
    Sensor("dtc_status"            , "S-S DTC Cleared"				                                            , "0101" , dtc_decrypt      ,""       ),
    Sensor("dtc_ff"                , "DTC C-F-F"					                                            , "0102" , cpass            ,""       ),
    Sensor("fuel_status"           , "Fuel System Stat"				                                            , "0103" , cpass            ,""       ),
    Sensor("load"                  , "Calc Load Value"				                                            , "01041", percent_scale    ,""       ),
    Sensor("temp"                  , "Coolant Temp"					                                            , "0105" , temp             ,"F"      ),
    Sensor("short_term_fuel_trim_1", "S-T Fuel Trim"				                                            , "0106" , fuel_trim_percent,"%"      ),
    Sensor("long_term_fuel_trim_1" , "L-T Fuel Trim"				                                            , "0107" , fuel_trim_percent,"%"      ),
    Sensor("short_term_fuel_trim_2", "S-T Fuel Trim"				                                            , "0108" , fuel_trim_percent,"%"      ),
    Sensor("long_term_fuel_trim_2" , "L-T Fuel Trim"				                                            , "0109" , fuel_trim_percent,"%"      ),
    Sensor("fuel_pressure"         , "FuelRail Pressure"			                                            , "010A" , cpass            ,""       ),
    Sensor("manifold_pressure"     , "Intk Manifold"				                                            , "010B" , intake_m_pres    ,"psi"    ),
    Sensor("rpm"                   , "Engine RPM"					                                            , "010C1", rpm              ,""       ),
    Sensor("speed"                 , "Vehicle Speed"				                                            , "010D1", speed            ,"MPH"    ),
    Sensor("timing_advance"        , "Timing Advance"				                                            , "010E" , timing_advance   ,"degrees"),
    Sensor("intake_air_temp"       , "Intake Air Temp"				                                            , "010F" , temp             ,"F"      ),
    Sensor("maf"                   , "AirFlow Rate(MAF)"			                                            , "0110" , maf              ,"lb/min" ),
    Sensor("throttle_pos"          , "Throttle Position"			                                            , "01111", throttle_pos     ,"%"      ),
    Sensor("secondary_air_status"  , "2nd Air Status"				                                            , "0112" , cpass            ,""       ),
    Sensor("o2_sensor_positions"   , "Loc of O2 sensors"			                                            , "0113" , cpass            ,""       ),
    Sensor("o211"                  , "O2 Sensor: 1 - 1"				                                            , "0114" , fuel_trim_percent,"%"      ),
    Sensor("o212"                  , "O2 Sensor: 1 - 2"				                                            , "0115" , fuel_trim_percent,"%"      ),
    Sensor("o213"                  , "O2 Sensor: 1 - 3"				                                            , "0116" , fuel_trim_percent,"%"      ),
    Sensor("o214"                  , "O2 Sensor: 1 - 4"				                                            , "0117" , fuel_trim_percent,"%"      ),
    Sensor("o221"                  , "O2 Sensor: 2 - 1"				                                            , "0118" , fuel_trim_percent,"%"      ),
    Sensor("o222"                  , "O2 Sensor: 2 - 2"				                                            , "0119" , fuel_trim_percent,"%"      ),
    Sensor("o223"                  , "O2 Sensor: 2 - 3"				                                            , "011A" , fuel_trim_percent,"%"      ),
    Sensor("o224"                  , "O2 Sensor: 2 - 4"				                                            , "011B" , fuel_trim_percent,"%"      ),
    Sensor("obd_standard"          , "OBD Designation"				                                            , "011C" , cpass            ,""       ),
    Sensor("o2_sensor_position_b"  , "Loc of O2 sensor" 			                                            , "011D" , cpass            ,""       ),
    Sensor("aux_input"             , "Aux input status"				                                            , "011E" , cpass            ,""       ),
    Sensor("engine_time"           , "Engine Start MIN"				                                            , "011F" , sec_to_min       ,"min"    ),

    Sensor("pids2"                 , "Supported PIDs 21-40"		                                                , "0120" , hex_to_bitstring ,""       ),
    Sensor("mil"                   , "Distance traveled with malfunction indicator lamp (MIL) on"				, "0121" , mil              ,"km"     ),
    Sensor("rel_fuel_press"        , "Fuel Rail Pressure (relative to manifold vacuum)"				            , "0122" , rel_fuel_press   ,"kPa"    ),
    Sensor("dir_fuel_press"        , "Fuel Rail Pressure (diesel, or gasoline direct inject)"				    , "0123" , dir_fuel_press   ,"kPa"    ),

    Sensor("o2s1"                  , "O2S1_WR_lambda(1) Equivalence Ratio"				                        , "0124" , equivalence_ratio,""       ),
    Sensor("o2s2"                  , "O2S2_WR_lambda(1) Equivalence Ratio"				                        , "0125" , equivalence_ratio,""       ),
    Sensor("o2s3"                  , "O2S3_WR_lambda(1) Equivalence Ratio"				                        , "0126" , equivalence_ratio,""       ),
    Sensor("o2s4"                  , "O2S4_WR_lambda(1) Equivalence Ratio"				                        , "0127" , equivalence_ratio,""       ),
    Sensor("o2s5"                  , "O2S5_WR_lambda(1) Equivalence Ratio"				                        , "0128" , equivalence_ratio,""       ),
    Sensor("o2s6"                  , "O2S6_WR_lambda(1) Equivalence Ratio"				                        , "0129" , equivalence_ratio,""       ),
    Sensor("o2s7"                  , "O2S7_WR_lambda(1) Equivalence Ratio"				                        , "012A" , equivalence_ratio,""       ),
    Sensor("o2s8"                  , "O2S8_WR_lambda(1) Equivalence Ratio"				                        , "012B" , equivalence_ratio,""       ),

    Sensor("com_egr"               , "Commanded EGR"				                                            , "012C" , percent_scale,"%"          ),
    Sensor("error_egr"             , "EGR Error"				                                                , "012D" , fuel_trim_percent,"%"      ),
    Sensor("ce_purge"              , "Commanded evaporative purge"				                                , "012E" , percent_scale,"%"          ),
    Sensor("fuel_level_in"         , "Fuel Level Input"				                                            , "012F" , percent_scale,"%"          ),

    Sensor("warm_ups"              , "# of warm-ups since codes cleared"				                        , "0130" , cpass            ,""       ),
    Sensor("dist_code_clear"       , "Distance traveled since codes cleared"				                    , "0131" , mil            ,"km"       ),
    Sensor("vapor_press"           , "Evap. System Vapor Pressure"				                                , "0132" , vapor_press            ,"Pa"       ),
    Sensor("bar_press"             , "Barometric pressure"				                                        , "0133" , cpass            ,""       ),

    Sensor("o2s1_2"                , "O2S1_WR_lambda(1) Equivalence Ratio 2"    		                        , "0134" , equivalence_ratio,""       ),
    Sensor("o2s2_2"                , "O2S2_WR_lambda(1) Equivalence Ratio 2"			                        , "0135" , equivalence_ratio,""       ),
    Sensor("o2s3_2"                , "O2S3_WR_lambda(1) Equivalence Ratio 2"			                        , "0136" , equivalence_ratio,""       ),
    Sensor("o2s4_2"                , "O2S4_WR_lambda(1) Equivalence Ratio 2"			                        , "0137" , equivalence_ratio,""       ),
    Sensor("o2s5_2"                , "O2S5_WR_lambda(1) Equivalence Ratio 2"			                        , "0138" , equivalence_ratio,""       ),
    Sensor("o2s6_2"                , "O2S6_WR_lambda(1) Equivalence Ratio 2"			                        , "0139" , equivalence_ratio,""       ),
    Sensor("o2s7_2"                , "O2S7_WR_lambda(1) Equivalence Ratio 2"			                        , "013A" , equivalence_ratio,""       ),
    Sensor("o2s8_2"                , "O2S8_WR_lambda(1) Equivalence Ratio 2"			                        , "013B" , equivalence_ratio,""       ),

    Sensor("b1s1_temp"             , "Catalyst Temperature Bank 1, Sensor 1"			                        , "013C" , catalyst_temperature,""    ),
    Sensor("b2s1_temp"             , "Catalyst Temperature Bank 2, Sensor 1"			                        , "013D" , catalyst_temperature,""    ),
    Sensor("b1s2_temp"             , "Catalyst Temperature Bank 1, Sensor 2"			                        , "013E" , catalyst_temperature,""    ),
    Sensor("b2s2_temp"             , "Catalyst Temperature Bank 2, Sensor 2"			                        , "013F" , catalyst_temperature,""    ),

    Sensor("pids3"                 , "Supported PIDs 41-60"		                                                , "0140" , hex_to_bitstring ,""       ),

    Sensor("monitor_status"        , "Monitor status this drive cycle"		                                    , "0141" , hex_to_bitstring ,""       ),
    Sensor("ctrl_module_vol"       ,"Control module voltage"		                                            , "0142" , ctrl_module_vol  ,""       ),
    Sensor("abs_load_val"          , "Absolute load value"		                                                , "0143" , abs_load_val        ,""    ),
    Sensor("fuel_air_ratio"        , "Fuel/Air commanded equivalence ratio"		                                , "0144" , equivalence_ratio ,""      ),

    Sensor("rel_throttle"          , "Relative throttle position"				                                , "0145" , percent_scale,"%"          ),
    Sensor("amb_air_temp"          , "Ambient air temperature"				                                    , "0146" , amb_air_temp,"C"           ),
    Sensor("abs_throttle_b"        , "Absolute throttle position B"				                                , "0147" , percent_scale,"%"          ),
    Sensor("abs_throttle_c"        , "Absolute throttle position C"				                                , "0148" , percent_scale,"%"          ),
    Sensor("abs_throttle_d"        , "Absolute throttle position D"				                                , "0149" , percent_scale,"%"          ),
    Sensor("abs_throttle_e"        , "Absolute throttle position E"				                                , "014A" , percent_scale,"%"          ),
    Sensor("abs_throttle_f"        , "Absolute throttle position F"				                                , "014B" , percent_scale,"%"          ),
    Sensor("throttle_actuator"     , "Commanded throttle actuator"			    	                            , "014C" , percent_scale,"%"          ),

    Sensor("engine_mil_time"       , "Engine Run MIL"				                                            , "014D" , mil       ,"min"            ),
    Sensor("cleared_trouble_time"  , "Time since trouble codes cleared"				                            , "014E" , mil       ,"min"            ),

    Sensor("max_eq_ratio"          , "Maximum value for equivalence ratio"				                        , "014F" , cpass       ,""            ),
    Sensor("max_o2_vol"            , "Maximum value for oxygen sensor voltage"				                    , "014F" , cpass       ,""            ),
    Sensor("max_o2_curr"           , "Maximum value for oxygen sensor current"				                    , "014F" , cpass       ,""            ),
    Sensor("max_in_press"          , "Maximum value for intake manifold absolute pressure"				        , "014F" , cpass       ,""            ),

    Sensor("max_airflow_a"          , "Maximum value for air flow rate from mass air flow sensor A"				, "0150" , cpass       ,""            ),
    Sensor("max_airflow_b"          , "Maximum value for air flow rate from mass air flow sensor B"		    	, "0150" , cpass       ,""            ),
    Sensor("max_airflow_c"          , "Maximum value for air flow rate from mass air flow sensor C"		    	, "0150" , cpass       ,""            ),
    Sensor("max_airflow_d"          , "Maximum value for air flow rate from mass air flow sensor D"				, "0150" , cpass       ,""            ),

    Sensor("fuel_type"              , "Fuel Type"                                               				, "0151" , cpass       ,""            ),
    Sensor("ethanol_fuel_per"       , "Ethanol fuel %"                                               			, "0152" , percent_scale,"%"          ),
    Sensor("abs_vapor_press"        , "Absolute Evap system Vapor Pressure"                                     , "0153" , abs_vapor_press,"kPa"          ),
    Sensor("vapor_press"            , "Evap system vapor pressure"                                              , "0154" , vapor_press,"Pa"          ),

    Sensor("short_term_b1"          , "Short term secondary oxygen sensor trim bank 1"                          , "0155" , fuel_trim_percent,"%"          ),
    Sensor("short_term_b3"          , "Short term secondary oxygen sensor trim bank 3"                          , "0155" , fuel_trim_percent_2,"%"          ),
    Sensor("long_term_b1"           , "Long term secondary oxygen sensor trim bank 1"                           , "0156" , fuel_trim_percent,"%"          ),
    Sensor("long_term_b3"           , "Long term secondary oxygen sensor trim bank 3"                           , "0156" , fuel_trim_percent_2,"%"          ),
    Sensor("short_term_b2"          , "Short term secondary oxygen sensor trim bank 2"                          , "0157" , fuel_trim_percent,"%"          ),
    Sensor("short_term_b4"          , "Short term secondary oxygen sensor trim bank 4"                          , "0157" , fuel_trim_percent_2,"%"          ),
    Sensor("long_term_b2"           , "Long term secondary oxygen sensor trim bank 2"                           , "0158" , fuel_trim_percent,"%"          ),
    Sensor("long_term_b4"           , "Long term secondary oxygen sensor trim bank 4"                           , "0158" , fuel_trim_percent_2,"%"          ),

    Sensor("abs_fuel_press"         , "Fuel rail pressure (absolute)"				                            , "0159" , dir_fuel_press   ,"kPa"    ),
    Sensor("accel_pedal_pos"        , "Relative accelerator pedal position"				                        , "015A" , percent_scale   ,"%"    ),
    Sensor("hybrid_battery"         , "Hybrid battery pack remaining life"				                        , "015B" , percent_scale   ,"%"    ),
    Sensor("oil_temp"               , "Engine oil temperature"	            			                        , "015C" , amb_air_temp   ,"C"    ),
    Sensor("fuel_inj_timing"        , "Fuel injection timing"	            			                        , "015D" , fuel_inj_timing   ,"st"    ),
    Sensor("fuel_rate"              , "Engine fuel rate"	            			                            , "015E" , fuel_rate   ,"L/h"    ),
    Sensor("fuel_inj_timing"        , "Emission requirements to which vehicle is designed"	            		, "015F" , cpass   ,""    ),

    Sensor("pids4"                  , "Supported PIDs 61-80"		                                            , "0160" , hex_to_bitstring ,""       ),
    Sensor("demand_eng"             , "Driver's demand engine - percent torque"		                            , "0161" , demand_eng ,"%"       ),
    Sensor("actual_engine"          , "Actual engine - percent torque"		                                    , "0162" , demand_eng ,"%"       ),
    Sensor("reference_torque"       , "Engine reference torque"		                                            , "0163" , mil ,"Nm"       ),

    Sensor("percent_torque_a"       , "Engine percent torque data A"		                                    , "0164" , demand_eng ,"%"       ),
    Sensor("percent_torque_b"       , "Engine percent torque data B"		                                    , "0164" , demand_eng ,"%"       ),
    Sensor("percent_torque_c"       , "Engine percent torque data C"		                                    , "0164" , demand_eng ,"%"       ),
    Sensor("percent_torque_d"       , "Engine percent torque data D"		                                    , "0164" , demand_eng ,"%"       ),
    Sensor("percent_torque_e"       , "Engine percent torque data E"		                                    , "0164" , demand_eng ,"%"       ),

    Sensor("auxiliary_io"           , "Auxiliary input / output supported"		                                , "0165" , hex_string ,""       ),
    Sensor("air_flow_sensor"        , "Mass air flow sensor"		                                            , "0166" , hex_string ,""       ),
    Sensor("coolant_temp"           , "Engine coolant temperature"		                                        , "0167" , hex_string ,""       ),
    Sensor("in_air_temp"            , "Intake air temperature sensor"		                                    , "0168" , hex_string ,""       ),
    Sensor("egr"                    , "Commanded EGR and EGR Error"		                                        , "0169" , hex_string ,""       ),

    Sensor("diesel_air"             , "Commanded Diesel intake air control and relative intake air position"	, "016A" , hex_string ,""       ),
    Sensor("recirculation_temp"     , "Exhaust gas recirculation temperature"		                            , "016B" , hex_string ,""       ),
    Sensor("throttle_actuator"      , "Commanded throttle actuator control and relative throttle position"		, "016C" , hex_string ,""       ),
    Sensor("fuel_press_system"      , "Fuel pressure control system"		                                    , "016D" , hex_string ,""       ),
    Sensor("injection_pressure"     , "Injection pressure control system"		                                , "016E" , hex_string ,""       ),
    Sensor("turbocharger_press"     , "Turbocharger compressor inlet pressure"		                            , "016F" , hex_string ,""       ),

    Sensor("boost_press"            , "Boost pressure control"		                                            , "0170" , hex_string ,""       ),
    Sensor("vgt"                    , "Variable Geometry turbo (VGT) control"		                            , "0171" , hex_string ,""       ),
    Sensor("westgate_ctrl"          , "Wastegate control"		                                                , "0172" , hex_string ,""       ),
    Sensor("exhaust_press"          , "Exhaust pressure"		                                                , "0173" , hex_string ,""       ),
    Sensor("turbocharger_rpm"       , "Turbocharger RPM"		                                                , "0174" , hex_string ,""       ),
    Sensor("turbocharger_temp"      , "Turbocharger temperature"		                                        , "0175" , hex_string ,""       ),
    Sensor("turbocharger_temp2"     , "Turbocharger temperature 2"		                                        , "0176" , hex_string ,""       ),
    Sensor("charge_cooler_temp"     , "Charge air cooler temperature (CACT)"		                            , "0177" , hex_string ,""       ),
    Sensor("egt1"                   , "Exhaust Gas temperature (EGT) Bank 1"		                            , "0178" , hex_string ,""       ),
    Sensor("egt2"                   , "Exhaust Gas temperature (EGT) Bank 2"		                            , "0179" , hex_string ,""       ),

    Sensor("dpf1"                   , "Diesel particulate filter (DPF) 1"		                                , "017A" , hex_string ,""       ),
    Sensor("dpf2"                   , "Diesel particulate filter (DPF) 2"		                                , "017B" , hex_string ,""       ),
    Sensor("dpf_temperature"        , "Diesel Particulate filter (DPF) temperature"		                        , "017C" , hex_string ,""       ),
    Sensor("nox_nte"                , "NOx NTE control area status"		                                        , "017D" , hex_string ,""       ),
    Sensor("pm_nte"                 , "PM NTE control area status"		                                        , "017E" , hex_string ,""       ),
    Sensor("eng_run_time"           , "Engine run time"		                                                    , "017F" , hex_string ,""       ),

    Sensor("pids5"                  , "Supported PIDs 81-A0"		                                            , "0180" , hex_to_bitstring ,""       ),
    Sensor("aecd_1"                 , "Engine run time for Auxiliary Emissions Control Device(AECD) 1"		    , "0181" , hex_string ,""       ),
    Sensor("aecd_2"                 , "Engine run time for Auxiliary Emissions Control Device(AECD) 2"		    , "0182" , hex_string ,""       ),
    Sensor("nox_sensor"             , "NOx sensor"		                                                        , "0183" , hex_string ,""       ),
    Sensor("manifold_temp"          , "Manifold surface temperature"		                                    , "0184" , hex_string ,""       ),
    Sensor("nox_system"             , "NOx reagent system"		                                                , "0185" , hex_string ,""       ),
    Sensor("pm_sensor"              , "Particulate matter (PM) sensor"		                                    , "0186" , hex_string ,""       ),
    Sensor("manifold_press"         , "Intake manifold absolute pressure"		                                , "0187" , hex_string ,""       ),

    Sensor("pids6"                  , "Supported PIDs A1-C0"		                                            , "01A0" , hex_to_bitstring ,""       ),
    Sensor("pids7"                  , "Supported PIDs C1-E0"		                                            , "01C0" , hex_to_bitstring ,""       ),
    Sensor("c3"                     , "Returns numerous data, including Drive Condition ID and Engine Speed"	, "01C3" , hex_string ,""       ),
    Sensor("c4"                     , "B5 is Engine Idle Request B6 is Engine Stop Request*"		            , "01C4" , hex_string ,""       ),

    ]
     
    
#___________________________________________________________

def test():
    for i in SENSORS:
        print(i.name, i.value("F"))


if __name__ == "__main__":
    test()
