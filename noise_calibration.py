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
path = data_mgmt.default_save_path(Data_dir, name = "noise_calibration", time = False)
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

#Temperature controller
sensor_low = 'T5'
sensor_high = 'T6'
Tthr = 1.45

#Instruments
tc = Triton_DR200.TemperatureController("DR200")
sa = SignalHound_SA.SpectrumAnalyzer(61660066)
##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Create HDF5 data file
title = 'Noise calibration'
class Thumbnail(tables.IsDescription):
	group_name = tables.StringCol(16)   # 16-character String
	group_number = tables.Int32Col()
	temperature = tables.Float64Col()
	bandwidth = tables.Float64Col()

f = tables.open_file(path+'\\data.h5', mode='a')

if f.title == title:
	thumbnail = f.root.thumbnail.row
	n_start = f.root.thumbnail[-1]['group_number']
	print("Appending data to an existing data file")
else:
	f.close()
	f = tables.open_file(path+'\\data.h5', mode='w', title = 'Noise calibration')
	f.close()
	f = tables.open_file(path+'\\data.h5', mode='a')
	thumbnail = f.create_table(f.root, 'thumbnail', Thumbnail, "thumbnail").row
	n_start = 0
	print("New data file created")

#Plotting script
data_mgmt.spawn_plotting_script(path, plotting_script)

#Add thumbnail record
thumbnail['group_name'] = 'group_{:d}'.format(n_start+1)
thumbnail['group_number'] = n_start+1
T = tc.temperature(sensor_low)
if T>=Tthr:
	T = tc.temperature(sensor_high)
thumbnail['temperature'] = T
thumbnail['bandwidth'] = rbw
thumbnail.append()

sa.averaging(aver)
sa.ref_level(ref_lvl)
sa.freq_start_stop((f_start,f_stop))
bw = sa.rbw(rbw)
sa.vbw(vbw)
Fsa = sa.freq_points()
print("Measuring...")
Spec = sa.read_data()
group = f.create_group(f.root,'group_{:d}'.format(n_start+1),"Spectra") 
f.create_array(group, 'P', Spec, "Power, W")
f.create_array(group, 'F', Fsa, "Frequency, Hz")
print("Done!")
f.flush()
f.close()