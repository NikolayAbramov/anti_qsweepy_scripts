from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from numpy import *

data_dir = "D:/Abramov"
file_name = '1'

start = 0.
stop = 30e-3
step = 500e-6
delay = 10e-3

I_list = arange(start, stop + step, step)
I_list = append( I_list, arange(stop, -step, -step))

smu = Keithley_2400.SMU('2400')
smu.four_wire("ON")
smu.source('CURR')
smu.source_autorange("OFF")
smu.source_range(10e-3)
smu.limit(20.)
smu.aperture(2)
smu.measurement_range(0.1)
smu.measurement_autorange('ON')
smu.averaging_count(1)

print("IV measurement")
path = data_mgmt.default_save_path(data_dir, time = False name = "IV")
print("Saving files to: ",path)

file=open(path+'/'+FileName+'.dat','a+')
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