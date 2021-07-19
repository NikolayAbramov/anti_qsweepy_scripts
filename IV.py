from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from numpy import *
import time

data_dir = "D:/Abramov"
file_name = '1'

start = 0.
stop = 3e-3
step = 5e-6
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

print("IV measurement")
path = data_mgmt.default_save_path(data_dir, time = False, name = "IV")
print("Saving files to: ",path)

file=open(path+'/'+file_name+'.dat','a+')
file.write( "#I, A\t\t\tU, V\n" )

smu.output('ON')
try:	
	for I in I_list:
		smu.setpoint( I )
		print("I = {:e} A".format(I), end = "\r")
		time.sleep(delay)
		V = smu.read_data()
		file.write( "{:e}\t{:e}\n".format(I, V) )
		file.flush()
except KeyboardInterrupt:
	print("Interrupted by user")
smu.setpoint(0)
smu.output("OFF")
smu.close()
file.close()