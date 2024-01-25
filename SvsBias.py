from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *

import tables
from numpy import *

Data_dir ="D:\Igor" 
plotting_script = "plot_2d_S"
row_descr = "Current, A"

bias_vals = arange(-6e-3,6e-3, 0.1e-3)
bias_range = 10e-3
bias_limit = 10

preset = False
Fstart = 4e9
Fstop = 10.5e9
Npoints = 1500
power = -10
bw = 100

SegmentedSweep = False

Segments =[ {'start':Fstart, 'bandwidth': 500, 'power':power },
{'start':7e9, 'bandwidth': 100, 'power':power },
{'start':15e9,'bandwidth': 20, 'power':power }]

na = Agilent_PNA.NetworkAnalyzer('PNA-X')
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
#bias_source = STS60.BiasSourceByNNDAC("NNDAC")
#bias_source = Keithley_2400.CurrentSource('2400')
bias_source = Keithley_6221.CurrentSource('GPIB0::10::INSTR')
#bias_source = Keithley_2651.MagnetSupply("NNDAC", rate = 1.)
###########################################################################
print("VNA bias scan")
path = data_mgmt.default_save_path(Data_dir, name = "SvsBias")
print("Saving files to: ",path)

if preset:
	na.num_of_points(Npoints)
	na.freq_start_stop((Fstart,Fstop))
	na.bandwidth(bw)

na.sweep_type("LIN")	
if SegmentedSweep:
	segment_table = uniform_segment_table(Fstop,Npoints,Segments)
	na.seg_tab(segment_table)
	na.sweep_type("SEGM")
else:
	na.sweep_type("LIN")

bias_source.range(bias_range)
bias_source.limit(bias_limit)
	
Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path, Fna, row_descr = row_descr)
data_mgmt.spawn_plotting_script(path, plotting_script)

na.output('on')
bias_source.output('on')
#Sweep
print( "Parameter range: from {:.3f} to {:.3f}".format( min(bias_vals), max(bias_vals) ))
na.soft_trig_arm()
for bias_val in bias_vals:
	try:
		bias_source.setpoint(bias_val) 
		print("Bias = {:f}".format(bias_val), end = '\r')
		S = na.read_data()
		d_array.append(S.reshape(1,len(S) ))
		r_array.append( array([bias_val]) )
		f.flush()
	except KeyboardInterrupt:
		print( "Interrupted by user" )
		break
bias_source.output('off')		
na.soft_trig_abort()	
f.close()	