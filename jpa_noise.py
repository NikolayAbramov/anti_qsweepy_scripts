from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *
import tables
from numpy import *
import time
from matplotlib.pyplot import *
import warnings
import pathlib

Noise = True

#Data mamagement
Data_dir ="E:/Abramov" 


plotting_script = "JPA/plot_jpa_noise"

#Sources

MeasDelay =1

#Spectrum analyzer
rbw = 250e3
vbw = 6.5e3 #6.5e3 for signalHound
aver  = 1
ref_lvl = -65

#Instruments
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
na = Agilent_PNA.NetworkAnalyzer('pna-x')
sa = SignalHound_SA.SpectrumAnalyzer(61660066)
pump = Agilent_PSG.Generator('Generator_E8257D')
try:
	bias = Keithley_6221.CurrentSource('GPIB0::10::INSTR')
except:
	warnings.warn("Bias source not found")
	bias = None	
##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def gain():
	pump.output(1)
	print("Gain...")
	Fna = na.freq_points()
	pump.output(0)
	na.output(1)
	P = na.power()
	na.power(P+20)
	na.soft_trig_arm()
	S21_off = na.read_data()
	pump.output(1)
	na.power(P)
	S21_on = na.read_data()
	print("Done!")
	na.soft_trig_abort()
	Pp = pump.power()
	Fp = pump.freq()
	if bias is not None:
		Ib = bias.setpoint()
	else: Ib = 0.	
	return Fna, S21_on, S21_off, Fp, Pp, Ib
	
if len(sys.argv) > 1:
	path = data_mgmt.default_save_path(Data_dir, name = "gain_noise_batch", time = False)
	parameter_str = sys.argv[1]
	path += "/"+parameter_str
	pathlib.Path(path).mkdir(parents=True, exist_ok=True)
else:
	path = data_mgmt.default_save_path(Data_dir, name = "gain_noise")
print("Saving files to: ",path)
		
try:
	#Create HDF5 data file
	f = tables.open_file(path+'\\data.h5', mode='w')
	f.close()
	f = tables.open_file(path+'\\data.h5', mode='a')
	complex_atom = tables.ComplexAtom(itemsize = 16 )
	real_atom = tables.Float64Atom()
	
	#Gain
	data_mgmt.spawn_plotting_script(path, plotting_script)
	Fna, S21_on, S21_off, Fp, Pp, Ib = gain()
	
	f.create_array(f.root, 'S21_off', S21_off, "S21 pump off")
	f.create_array(f.root, 'S21_on', S21_on, "S21 pump on")
	f.create_array(f.root, 'F_S21', Fna, "S21 frequency")
	
	txt = open(path+"\\readme.txt", 'w+')
	txt.write('''Fp = {:e}
Pp = {:e}
Ib = {:e}'''.format(Fp,Pp, Ib))
	txt.close()
	
	if Noise:
		sa.averaging(aver)
		sa.ref_level(ref_lvl)
		#Noise
		pump.output(1)
		na.output(0)
		sa.freq_center_span(na.freq_center_span())
		bw = sa.rbw(rbw)
		sa.vbw(vbw)
		Fsa = sa.freq_points()
		print("Spectra on...")
		Spec_on = sa.read_data()
		f.create_array(f.root, 'Spec_on', Spec_on, "Spectra pump on, W")
		f.create_array(f.root, 'F_Spec', Fsa, "Spectra frequency")
		print("Spectra off...")
		pump.output(0)
		Spec_off = sa.read_data()
		f.create_array(f.root, 'Spec_off', Spec_off, "Spectra pump off, W")
		print("Done!")
		na.output(1)	
except: raise	
	
finally:
	na.soft_trig_abort()
	na.output(1)
	pump.output(1)