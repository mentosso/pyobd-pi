#!/usr/bin/env python

import obd_io
import serial
import platform
import obd_sensors
from datetime import datetime
import time
import getpass
import AccGyro
import operator


from obd_utils import scanSerial

class OBD_Recorder():
    def __init__(self, path, log_items):
        self.port = None
        self.sensorlist = []
        localtime = time.localtime(time.time())
        filename = path+"car-"+str(localtime[0])+"-"+str(localtime[1])+"-"+str(localtime[2])+"-"+str(localtime[3])+"-"+str(localtime[4])+"-"+str(localtime[5])+".log"
        self.log_file = open(filename, "w", 128)

	# str_shortnames = ""
	# str_name = ""
	# str_cmd = ""
	# for i in obd_sensors.SENSORS:
	#     str_shortnames += i.shortname + ";"
	#     str_name += i.name + ";"
	#     str_cmd += i.cmd + ";"

 #        self.log_file.write(str_shortnames + "\n" + str_name + "\n" + str_cmd + "\n");

        for item in log_items:
            self.add_log_item(item)

        self.gear_ratios = [34/13, 39/21, 36/23, 27/20, 26/21, 25/22]
        #log_formatter = logging.Formatter('%(asctime)s.%(msecs).03d,%(message)s', "%H:%M:%S")

    def connect(self):
        portnames = scanSerial()
        #portnames = ['COM10']
        print portnames
        for port in portnames:
            self.port = obd_io.OBDPort(port, None, 2, 2)
            if(self.port.State == 0):
                self.port.close()
                self.port = None
            else:
                break

        if(self.port):
            print "Connected to "+self.port.port.name

    def is_connected(self):
        return self.port

    def add_log_item(self, item):
        for index, e in enumerate(obd_sensors.SENSORS):
            if(item == e.shortname):
                self.sensorlist.append(index)
                print "Logging item: "+e.name
                break


    def record_data(self):
        if(self.port is None):
            return None

        print "Logging started"

        str_shortnames = "time;"
        str_name = "time;"
        str_cmd = "time;"
        #print len(self.sensorlist), " ", len(obd_sensors.SENSORS)
    	#print("Sensor list: {}".format(obd_sensors.SENSORS))
    	#print("Sensors: {}".format(self.sensorlist))

    	only_once = ['01001', '01011', '01201', '09001', '09011', '09031' '09041', '09051', '09061', '09071', '09081']

    	lista = list(self.sensorlist)
        for index in self.sensorlist:
	    # print self.sensorlist
            (name, value, unit) = self.port.sensor(index)
            if str(value).strip() == 'NODATA':
		# print "if: ", index, " ", value
                lista.remove(index)
            else:
		if obd_sensors.SENSORS[index].cmd not in only_once:
        	# print "else", index, " ", value
        	str_shortnames += obd_sensors.SENSORS[index].shortname + ";"
        	str_name += obd_sensors.SENSORS[index].name + ";"
        	str_cmd += obd_sensors.SENSORS[index].cmd + ";"
		else:
			lista.remove(index)

    	self.sensorlist = lista
            self.log_file.write(str_shortnames + "gyro_x; gyro_y; gyro_z" + "\n" + str_name + "\n" + str_cmd + "\n");

    	print len(self.sensorlist), " ", len(obd_sensors.SENSORS)
        gyro = AccGyro()
        gyro_last_greater_value = gyro.get_all_values()

     	while 1:
            localtime = datetime.now()
            current_time = str(localtime.hour)+":"+str(localtime.minute)+":"+str(localtime.second)+"."+str(localtime.microsecond)
            log_string = current_time
            results = {}
            gyro_value = 0
            for index in self.sensorlist:
                gyro_value = gyro.get_all_values()
                gyro_last_greater_value = get_greater_gyro_read(gyro_value, gyro_last_greater_value)
                (name, value, unit) = self.port.sensor(index)
                log_string = log_string + ";"+str(value)
                results[obd_sensors.SENSORS[index].shortname] = value;

            log_string = log_string + ";"+str(gyro_last_greater_value.x) + ";"+str(gyro_last_greater_value.y) + ";"+str(gyro_last_greater_value.z)
            self.log_file.write(log_string+"\n")
	    print(localtime)

    def get_greater_gyro_read(first, second):
        first_max = max(first.iteritems(), key=operator.itemgetter(1))[1]
        second_max = max(first.iteritems(), key=operator.itemgetter(1))[1]

        if first_max >= second_max
            return first_max
        else
            return second_max

    def calculate_gear(self, rpm, speed):
        if speed == "" or speed == 0:
            return 0
        if rpm == "" or rpm == 0:
            return 0

        rps = rpm/60
        mps = (speed*1.609*1000)/3600

        primary_gear = 85/46 #street triple
        final_drive  = 47/16

        tyre_circumference = 1.978 #meters

        current_gear_ratio = (rps*tyre_circumference)/(mps*primary_gear*final_drive)

        #print current_gear_ratio
        gear = min((abs(current_gear_ratio - i), i) for i in self.gear_ratios)[1]
        return gear

username = getpass.getuser()

logitems = []
for index, e in enumerate(obd_sensors.SENSORS):
    logitems.append(e.shortname)

o = OBD_Recorder('/home/'+username+'/pyobd-pi/log/', logitems)
o.connect()

if not o.is_connected():
    print "Not connected"
o.record_data()
