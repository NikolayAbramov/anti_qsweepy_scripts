from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from numpy import *
import time
from collections import *

data_dir = "D:/Abramov"

sw_seq = OrderedDict((('2', [1,2]),('2', [3,4]),('3', [5,6]),('4', [7,8]),('5', [9,10]),('6', [11,12])))

start = 0.
stop = 3e-3
step = 50e-6
delay = 10e-3

I_list = arange(start, stop + step, step)
I_list = append( I_list, arange(stop, -step, -step))

#smu = Keithley_2400.SMU('2400')
smu = Artificial_SMU.Artificial_SMU( Keithley_2400.CurrentSource('2400'), Keithley_2182A.Voltmeter('2182A') )
smu.four_wire("off")
smu.source('CURR')
smu.source_autorange("OFF")
smu.source_range(10e-3)
smu.limit(20.)
smu.aperture(2)
smu.meter_range(0.1)
smu.meter_autorange('ON')
smu.averaging_count(1)

switch_present = True
try:
	switch = DC_Switch.DC_Switch('Switch')
except:
	switch_present = False
	print('DC Switch not found')	

print("IV measurement")
path = data_mgmt.default_save_path(data_dir, time = False, name = "IV")
print("Saving files to: ",path)

smu.setpoint(0)
smu.output('ON')
try:
	for sample in sw_seq.keys():
		smu.setpoint(0)
		if switch_present:
			switch.state([0]*12)	
			for chan in sw_seq[sample]:
				switch.set( chan, 'ON' )
		print("Sample: "+sample )
		file=open(path+'/'+sample+'.dat','a+')
		file.write( "#I, A\t\t\tU, V\n" )	
		
		for I in I_list:
			smu.setpoint( I )
			print("I = {:e} A".format(I), end = "\r")
			time.sleep(delay)
			V = smu.read_data()
			file.write( "{:e}\t{:e}\n".format(I, V) )
			file.flush()
		if not switch_present:
			break
except KeyboardInterrupt:
	print("Interrupted by user")
smu.setpoint(0)
smu.output("OFF")
smu.close()
file.close()