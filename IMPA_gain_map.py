from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.jpa_tuning import *
from numpy import *
import scipy.optimize as so
import time
import tables

data_dir ="E:/Abramov"
plotting_script = "JPA\\plot_jpa_tuning_results"

#Fcent = arange(5.8e9, 7.65e9, 0.05e9)
#Fcent = arange(6e9, 8e9, 0.05e9)
Fcent = [7.1e9,]

target_gain  = 22
target_bw = 0.1e9

bias_range = (2.5e-3, 4e-3)
pump_range = (-5,15)

bias_source_range = 10e-3
bias_source_limit = 10

Npoints = 200
power = -30
bw = 5000

###############################################3
vna = Agilent_PNA.NetworkAnalyzer('PNA-X')
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
#bias = Keithley_2400.CurrentSource('2400')
bias = Keithley_6221.CurrentSource('GPIB0::10::INSTR')
#bias = Keithley_2651.MagnetSupply("NNDAC", rate = 1.)
pump = Agilent_PSG.Generator('Generator_E8257D')

tuner = IMPATuner(vna = vna, pump = pump, bias = bias)
tuner.bias_range = bias_range
tuner.pump_range = pump_range
tuner.bias_source_range = bias_source_range
tuner.bias_source_limit = bias_source_limit
tuner.target_gain = target_gain #dB
tuner.target_bw = target_bw
tuner.target_freq_span = 100e6
tuner.Ps = power
tuner.bw = bw
tuner.points = Npoints
tuner.w_cent = 0.5

path = data_mgmt.default_save_path(data_dir, name = "jpa_tuning")
print("Saving files to: ",path)
data_mgmt.spawn_plotting_script(path, plotting_script)
file = open(path+'/tuning_table.txt', 'w+')
file.write(OperationPoint().file_str_header())

hdf5_title = 'JPA tuning table'
class Thumbnail(tables.IsDescription):
	group_name = tables.StringCol(16)   # 16-character String
	group_number = tables.Int32Col()
	Fp = tables.Float64Col()
	Fs = tables.Float64Col()
	G = tables.Float64Col()
	Pp = tables.Float64Col()
	I = tables.Float64Col()
	Gsnr = tables.Float64Col()

f = tables.open_file(path+'\\data.h5', mode='w', title = hdf5_title)
thumbnail = f.create_table(f.root, 'thumbnail', Thumbnail, "thumbnail").row
group_n = 0

try:
	for f_cent in Fcent:
		print("Fs = {:e} Hz".format(f_cent))
		tuner.target_freq = f_cent 
		op, status = tuner.find_gain(popsize = 50, minpopsize = 5, tol = 0.01, maxiter = 40, disp = True)
		print(tuner.res)
		print(op)
		file.write('\n'+op.file_str())
		file.flush()

		thumbnail['group_name'] = 'group_{:d}'.format(group_n)
		thumbnail['group_number'] = group_n
		thumbnail['Fs'] = f_cent
		thumbnail['Fp'] = f_cent*2.
		thumbnail['G'] = op.G
		thumbnail['Pp'] = op.Pp
		thumbnail['I'] = op.I
		thumbnail['Gsnr'] = op.Gsnr
		thumbnail.append()
		
		S21on, S21off, Fpoints = tuner.vna_snapshot(op)
		group = f.create_group(f.root,'group_{:d}'.format(group_n),"S21") 
		f.create_array(group, 'pump_on', S21on, "S21")
		f.create_array(group, 'pump_off', S21off, "S21")
		f.create_array(group, 'frequency', Fpoints, "Frequency, Hz")
		f.flush()
		group_n += 1
except KeyboardInterrupt:
	print( "Interrupted by user" )

f.close()
file.close()	