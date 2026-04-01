from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *

import tables
from numpy import *

Data_dir =r"C:\Users\Nikolay\OneDrive - НИТУ МИСиС\Документы\RF_modules" 
plotting_script = "plot_2d_S"
row_descr = "Attenuation value"

att_vals = arange(0,64)
module_id = 1

preset = False
Fstart = 4e9
Fstop = 10e9
Npoints = 1000
power = -5
bw = 100

SegmentedSweep = False

Segments =[ {'start':Fstart, 'bandwidth': 500, 'power':power },
{'start':7e9, 'bandwidth': 100, 'power':power },
{'start':15e9,'bandwidth': 20, 'power':power }]

#na = Agilent_PNA.NetworkAnalyzer('TCPIP0::10.1.0.75::inst0::INSTR')
#na = Agilent_PNA.NetworkAnalyzer('pna-x')
na = RS_ZVB20.NetworkAnalyzer('ZVB20')
#bias_source = STS60.BiasSourceByNNDAC("NNDAC")
#bias_source = Keithley_2400.CurrentSource('2400')
#bias_source = Keithley_6221.CurrentSource('GPIB0::10::INSTR')
#bias_source = Keithley_2651.MagnetSupply("NNDAC", rate = 1.)
#bias_source = Yokogawa_GS200.CurrentSource('GPIB0::2::INSTR')
# bias_source = DAC_24.CurrentSource('DAC_24')
rf = RF_Modules.TX()
###########################################################################
print("VNA LO att. scan")
path = data_mgmt.default_save_path(Data_dir, name = "SvsBias")
print("Saving files to: ",path)

if preset:
	na.num_of_points(Npoints)
	na.freq_start_stop((Fstart,Fstop))
	na.bandwidth(bw)
	na.power(power)
	
na.sweep_type("LIN")	
if SegmentedSweep:
	segment_table = uniform_segment_table(Fstop,Npoints,Segments)
	na.seg_tab(segment_table)
	na.sweep_type("SEGM")
else:
	na.sweep_type("LIN")
	
Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path, Fna, row_descr = row_descr)
data_mgmt.spawn_plotting_script(path, plotting_script)

na.output('on')

rf.lo_amp_pwr( module_id, True)
#Sweep
print( "Parameter range: from {0} to {1}".format( min(att_vals), max(att_vals) ))
na.soft_trig_arm()
for att_val in att_vals:
	try:
		rf.lo_attenuation(module_id, att_val) 
		print("Parameter = {:f}".format(att_val), end = '\r')
		S = na.read_data()
		d_array.append(S.reshape(1,len(S) ))
		r_array.append( array([att_val]) )
		f.flush()
	except KeyboardInterrupt:
		print( "Interrupted by user" )
		break
		
na.soft_trig_abort()	
f.close()	