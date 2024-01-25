from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.jpa_tuning import *
from numpy import *
import scipy.optimize as so
import time
import tables

data_dir ="C:/Users/User/Documents/IMPA/IMPA_271_4"
plotting_script = "JPA\\plot_jpa_tuning_results"

#Fcent = arange(6.5e9, 7.4e9, 0.05e9)
Fcent = arange(7.5e9, 7.65e9, 0.05e9)
#Fcent = [7.15e9,]

#Optimization goals
target_gain  = 20
target_bw = 0.6e9

#Central point weight
#The higher it is the less peaking
w_cent = 0


#Parameters ranges
bias_range = (0.25e-3, 0.75e-3)
pump_range = (1,17)
#Central frequency range. 
#Pump frequency is not optomized if 0
#It'll reduce optimization time time
target_freq_span = 0

#Bias source parameters
bias_ch = 1 #Channel
bias_source_range = 10e-3
bias_source_limit = 10

#Network analyzer paraneters
Npoints = 200
power = -35
bw = 5000

###############################################3
#vna = Agilent_PNA.NetworkAnalyzer('TCPIP0::10.1.0.75::inst0::INSTR')
vna = RS_ZVB20.NetworkAnalyzer('ZVB20')
#bias = Keithley_2400.CurrentSource('2400')
#bias = Keithley_6221.CurrentSource('GPIB0::10::INSTR')
bias = Yokogawa_GS200.CurrentSource('Yokogawa_GS200')
#bias = DAC_24.CurrentSource('DAC_24')
#bias = Keithley_2651.MagnetSupply("NNDAC", rate = 1.)
#pump = Agilent_PSG.Generator('Agilent_PSG')
pump = Agilent_PSG.Generator('Agilent_PSG')
#pump = Anapico_RFSG.Generator('RFSG20')

#Tuner settings
bias.channel(bias_ch)
tuner = IMPATuner(vna = vna, pump = pump, bias = bias)
tuner.bias_range = bias_range
tuner.pump_range = pump_range
tuner.bias_source_range = bias_source_range
tuner.bias_source_limit = bias_source_limit
tuner.target_gain = target_gain #Target gain, dB
tuner.target_bw = target_bw #Target bandwidth of the gain profile, Hz
tuner.target_freq_span = target_freq_span #If >0 then pump frequency will be optimized. It will increase an initial number of point by factor of 1.5 thus slowing down the convergence.
tuner.Ps = power    #VNA signal power
tuner.bw = bw   #VNA bandwidth
tuner.points = Npoints #VNA number of point
tuner.w_cent = w_cent  #Weight of central point. If <1 helps to get a more flat gain.

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
		op, status = tuner.find_gain(popsize = 50, minpopsize = 5, tol = 0.01, atol = 1.5, maxiter = 9, threshold = 150, disp = True)
		print(tuner.res)
		print(op)
		file.write('\n'+op.file_str())
		file.flush()

		thumbnail['group_name'] = 'group_{:d}'.format(group_n)
		thumbnail['group_number'] = group_n
		thumbnail['Fs'] = op.Fs
		thumbnail['Fp'] = op.Fp
		thumbnail['G'] = op.G
		thumbnail['Pp'] = op.Pp
		thumbnail['I'] = op.I
		thumbnail['Gsnr'] = op.Gsnr
		thumbnail.append()
		f.flush()
		
		S21on, S21off, Fpoints = tuner.vna_snapshot(op)
		group = f.create_group(f.root,'group_{:d}'.format(group_n),"S21") 
		f.create_array(group, 'pump_on', S21on, "S21")
		f.create_array(group, 'pump_off', S21off, "S21")
		f.create_array(group, 'frequency', Fpoints, "Frequency, Hz")
		f.flush()
		
		S21on, S21off, Fpoints = tuner.snr_snapshot(op, Nmeas = 100)
		f.create_array(group, 'snr_pump_on', S21on, "S21")
		f.create_array(group, 'snr_pump_off', S21off, "S21")
		f.create_array(group, 'snr_frequency', Fpoints, "Frequency, Hz")
		f.flush()
		
		group_n += 1
except KeyboardInterrupt:
	print( "Interrupted by user" )
except:
	raise

f.close()
file.close()	