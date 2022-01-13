from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *
import tables
from numpy import *
import time
from matplotlib.pyplot import *

Noise = True

#Data mamagement
Data_dir ="E:/Abramov" 
path = data_mgmt.default_save_path(Data_dir, name = "noise_calibration")
print("Saving files to: ",path)

plotting_script = "plot_noise_calibration"

MeasDelay =1

#Spectrum analyzer
rbw = 250e3
vbw = 6.5e3 
aver  = 3
ref_lvl = -64
f_start = 4e9
f_stop = 8.5e9

#Cryostat
Th = 3.
Pmc = 20e-3

#Instruments
dr = Triton_DR200.Cryostat("DR200")
sa = SignalHound_SA.SpectrumAnalyzer(61660066)

##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Create HDF5 data file
title = 'Noise calibration'
class Thumbnail(tables.IsDescription):
	group_name = tables.StringCol(16)   # 16-character String
	group_number = tables.Int32Col()
	temperature = tables.Float64Col()
	bandwidth = tables.Float64Col()

f = tables.open_file(path+'\\data.h5', mode='w', title = 'Noise calibration')
f.close()
f = tables.open_file(path+'\\data.h5', mode='a')
thumbnail = f.create_table(f.root, 'thumbnail', Thumbnail, "thumbnail").row
group_number = 1
#Plotting script
data_mgmt.spawn_plotting_script(path, plotting_script)
#Add thumbnail record
thumbnail['group_name'] = 'group_{:d}'.format(group_number)
thumbnail['group_number'] = group_number
T = dr.Tmc()
thumbnail['temperature'] = T
thumbnail['bandwidth'] = rbw
thumbnail.append()

sa.averaging(aver)
sa.ref_level(ref_lvl)
sa.freq_start_stop((f_start,f_stop))
bw = sa.rbw(rbw)
sa.vbw(vbw)
Fsa = sa.freq_points()
#Tl measurement
print("Measuring at Tl={:f}...".format(T))
Spec = sa.read_data()
group = f.create_group(f.root,'group_{:d}'.format(group_number),"Spectra") 
f.create_array(group, 'P', Spec, "Power, W")
f.create_array(group, 'F', Fsa, "Frequency, Hz")
f.flush()
print("Done!")

#Warmup cryostat up to Th
print("Warming up cryostat to Th={:.2f}K".format(Th))

dr.turbo(0)
dr.forepump(0)
dr.compressor(0)
for i in range(1,10):
	dr.valve(i,0)
try:
	turbo_speed = dr.turbo_status()['speed']	
	while turbo_speed>100:
		turbo_speed = dr.turbo_status()['speed']
		print("Waiting for turbo to spin down {:.0f}Hz    ".format(turbo_speed), end = '\r')
except KeyboardInterrupt: 
	print('Interrupted by user')
print("\nChamber heater ON at {:e}W".format(Pmc))	
dr.still_heater(0.)	
dr.chamber_heater(Pmc*1e6)

try:
	T = dr.Tmc()	
	while T < Th:
		T = dr.Tmc()
		print("Waiting for Tmc >= Th, Tmc = {:.3f}K".format(T), end = '\r')
except KeyboardInterrupt:
	dr.chamber_heater(0.)
	print('Interrupted by user')
print("\nChamber heater OFF")	
dr.chamber_heater(0.)
stupid_waiting(120)
print("Measuring at Th...")
T = dr.Tmc()
Spec = sa.read_data()
group = f.create_group(f.root,'group_{:d}'.format(group_number+1),"Spectra") 
f.create_array(group, 'P', Spec, "Power, W")
f.create_array(group, 'F', Fsa, "Frequency, Hz")

thumbnail['group_name'] = 'group_{:d}'.format(group_number+1)
thumbnail['group_number'] = group_number+1
thumbnail['temperature'] = T
thumbnail['bandwidth'] = rbw
thumbnail.append()
f.flush()

print("Done!")
print("Starting mixture collection")
dr.valve(9,1)
try:
	p3 = dr.pressure(3)	
	p1 = dr.pressure(1)
	while p1 >= p3*0.7:
		p3 = dr.pressure(3)	
		p1 = dr.pressure(1)
		print("Waiting for P1 and P3 to equalize, P1 = {:e}mbar P3 = {:e}mbar".format(p1,p3), end = '\r')
except KeyboardInterrupt:
	print('\nInterrupted by user')
print("\nPumping mixture back into the tank...")	
dr.valve(9,0)
stupid_waiting(3, prnt=False)
dr.valve(4,1)
dr.valve(5,1)
dr.compressor(1)
print("Compressor started")
try:
	p5 = dr.pressure(5)
	while p5 > 50.:
		p5 = dr.pressure(5)	
		print("Waiting for P5 to drop, P5 = {:e}mbar".format(p5), end = '\r')
except KeyboardInterrupt:
	print('\nInterrupted by user')
dr.forepump(1)
print("Foreoump started")
try:
	p3 = dr.pressure(3)
	while p3 < 20.:
		p3 = dr.pressure(3)	
		print("Waiting for P3 to drop, P3 = {:e}mbar".format(p3), end = '\r')
except KeyboardInterrupt:
	print('\nInterrupted by user')
dr.compressor(0)
dr.valve(4,0)
dr.valve(5,0)
dr.forepump(0)
stupid_waiting(5, prnt=False)
print('Starting condensation')
dr.start_condensing()
f.close()
dr.close()