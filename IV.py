from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from numpy import *
import time
from collections import *

data_dir = "D:/Belanovsky"
plotting_script = "plot_all_iv.gp"

#Sample switching sequence
sw_seq = OrderedDict((('Tolya_w11_RF3_small_capa', [1,11]), ))
#sw_seq = OrderedDict((('1', [1,2]),('2', [1,3]),('3', [1,4]),('4', [1,5]),('5', [1,6]),('6', [1,7]),('7', [1,8]),('8', [1,9]),('9', [1,10]),('10', [1,11]) ))
#sw_seq = OrderedDict((('4', [7,8]),('5', [7,9]),('6', [7,10]),('7', [7,11]),('8', [7,12]) ))
#sw_seq = OrderedDict((('10-1', [1,11]), ))
#sw_seq = OrderedDict((('2_full_2', [3,5]), ))

#Current sweep range
start = 0.
stop = 2e-6
step = 0.001e-6
delay = 100e-6

I_list = arange(start, stop + step, step)
#I_list = append( I_list, arange(stop, step, -step))
#I_list = append( I_list, arange(stop, -stop-step, -step))
#I_list = append( I_list, arange(-stop, step, step))

#Surce-measure unit 
#smu = Keithley_2400.SMU("GPIB2::11::INSTR")
smu = Artificial_SMU.Artificial_SMU( Keithley_6221.CurrentSource("Keithley_6221"), Keithley_2182A.Voltmeter("Keithley_2182A") )
#smu = Artificial_SMU.Artificial_SMU( Keithley_2400.CurrentSource("GPIB0::11::INSTR"), Keithley_2182A.Voltmeter("GPIB0::7::INSTR") )
smu.four_wire("on")
smu.source('CURR')
smu.source_range(10e-6)
smu.source_autorange("ON")
smu.limit(30.0)
smu.aperture(2)
smu.meter_range(0.01)
smu.meter_autorange('OFF')
smu.averaging_count(1)

#Optional sample switch
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