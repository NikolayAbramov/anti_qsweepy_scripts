from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from numpy import *
import time
from collections import *

data_dir = "E:/Abramov"
plotting_script = "plot_all_iv.gp"
sw_seq = OrderedDict((('3', [5,6]), ))
#sw_seq = OrderedDict((('1', [1,2]),('2', [1,3]),('3', [1,4]),('4', [1,5]),('5', [1,6]),('6', [1,7]),('7', [1,8]),('8', [1,9]),('9', [1,10]),('10', [1,11]) ))
#sw_seq = OrderedDict((('1', [3,4]),('2', [3,5]),('3', [3,6]),('4', [3,7]),('5', [3,8]),('6', [3,9]),('7', [3,10]),('8', [3,11]),('9', [3,12]) ))
#sw_seq = OrderedDict((('10-1', [1,11]), ))
#sw_seq = OrderedDict((('2_full_2', [3,5]), ))

start = 0.
stop = 200e-3
step = 1e-3
delay = 10e-3	

I_list = arange(start, stop + step, step)
I_list = append( I_list, arange(stop, -stop-step, -step))
#I_list = append( I_list, arange(-stop, step, step))

smu = Keithley_2400.SMU("GPIB0::11::INSTR")
vmeter = Keithley_2182A.Voltmeter("GPIB0::7::INSTR")
#smu = Artificial_SMU.Artificial_SMU( Keithley_6221.CurrentSource("GPIB2::10::INSTR"), Keithley_2182A.Voltmeter("GPIB2::7::INSTR") )
#smu = Artificial_SMU.Artificial_SMU( Keithley_2400.CurrentSource("GPIB2::11::INSTR"), Keithley_2182A.Voltmeter("GPIB2::7::INSTR") )
smu.four_wire("off")
smu.source('VOLT')
smu.source_autorange("OFF")
smu.source_range(200e-3)
smu.limit(100e-6)
smu.aperture(2)
smu.meter_range(0.1)
smu.meter_autorange('ON')
smu.averaging_count(1)

vmeter.range(10e-3)
vmeter.autorange("on")
vmeter.aperture(2)

switch_present = False
try:
	switch = DC_Switch.DC_Switch('dc_switch')
except:
	switch_present = False
	print('DC Switch not found')	

print("IV measurement")
path = data_mgmt.default_save_path(data_dir, time = False, name = "IV")
print("Saving files to: ",path)
data_mgmt.spawn_plotting_script(path, plotting_script, py = False)

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
			I = smu.read_data()
			V = vmeter.read_data()
			file.write( "{:e}\t{:e}\n".format(I, V) )
			file.flush()
		if not switch_present:
			break
except KeyboardInterrupt:
	print("Interrupted by user")
smu.setpoint(0)
#smu.output("OFF")
smu.close()
file.close()