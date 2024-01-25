#For splitrings
import sys
import pathlib
from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *
import re
import tables
from numpy import *

Data_dir ="D:\Igor" 
plotting_script = "plot_resonators"
row_descr = "Current, A"

#bias_vals = hstack([arange(0,2)])
bias_vals = hstack([arange(-20, 20.2, 1.0)])
#bias_vals = hstack([arange(-2.5, 2.51, 0.01)])
#bias_vals = hstack([arange(-10, -1.55, 0.05),arange(-1.5, 1.5, 0.005),arange(1.55, 10, 0.05)])
#bias_vals = hstack([arange(10, 1.55, -0.05),arange(1.5, -1.5, -0.005),arange(-1.55, -10, -0.05)]) 
bias_range = 20
bias_limit = 5

preset = True
Fstart = 1.7e9
Fstop = 2.6e9
Npoints = 32001
power = -20
bw = 5000

SegmentedSweep = True

Segments =[ {'start':Fstart, 'bandwidth': 500, 'power':power },
{'start':1e9, 'bandwidth': 500, 'power':power },
{'start':2e9,'bandwidth': 500, 'power':-40 }]

raw_seg_table = True
#1
#segment_table=[	{'start':3.5e9, 'stop':4.5e9, 'points':600, 'power':power,'bandwidth':bw},
#				{'start':5.8e9, 'stop':6.8e9, 'points':600, 'power':power,'bandwidth':bw}]
#1 2.5K				
#segment_table=[	{'start':3.6e9, 'stop':4.1e9, 'points':600, 'power':power,'bandwidth':bw},
#				{'start':5.9e9, 'stop':6.3e9, 'points':600, 'power':power,'bandwidth':bw}]
#1 3.5K				
#segment_table=[	{'start':2.9e9, 'stop':3.5e9, 'points':600, 'power':power,'bandwidth':bw},
#				{'start':5.1e9, 'stop':6.2e9, 'points':600, 'power':power,'bandwidth':bw}]
#2
#segment_table=[	{'start':3.9e9, 'stop':4.9e9, 'points':1000, 'power':power,'bandwidth':bw},
#				{'start':5.8e9, 'stop':6.8e9, 'points':1000, 'power':power,'bandwidth':bw}]
#2 3.5K
#segment_table=[	{'start':3.5e9, 'stop':4.5e9, 'points':1000, 'power':power,'bandwidth':bw},
#				{'start':5.e9, 'stop':5.75e9, 'points':1000, 'power':power,'bandwidth':bw}]
#2 2.5K
#segment_table=[	{'start':3.9e9, 'stop':4.75e9, 'points':10001, 'power':power,'bandwidth':bw},
#				{'start':5.8e9, 'stop':6.6e9, 'points':10001, 'power':power,'bandwidth':bw}]
segment_table=[	{'start':Fstart, 'stop':Fstop, 'points':Npoints, 'power':power,'bandwidth':bw}]

na = Agilent_PNA.NetworkAnalyzer('pna')
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
#bias_source = STS60.BiasSourceByNNDAC("NNDAC")
#bias_source = Keithley_2400.CurrentSource('2400')
#bias_source = Keithley_6221.CurrentSource('GPIB0::10::INSTR')
bias_source = Keithley_2651.MagnetSupply("COM1")
###########################################################################
print("VNA bias scan")
if len(sys.argv) > 1:
	path = data_mgmt.default_save_path(Data_dir, name = "SvsIvsPar", time = False)
	parameter_str = sys.argv[1]
	path += "/"+parameter_str
	pathlib.Path(path).mkdir(parents=True, exist_ok=True)
else:	
	path = data_mgmt.default_save_path(Data_dir, name = "SvsI")
print("Saving files to: ",path)

if preset:
	na.num_of_points(Npoints)
	na.freq_start_stop((Fstart,Fstop))
	na.bandwidth(bw)

na.sweep_type("LIN")
if SegmentedSweep:
	if not raw_seg_table:
		segment_table = uniform_segment_table(Fstop,Npoints,Segments)
	na.seg_tab(segment_table)
	na.sweep_type("SEGM")
else:
	segment_table = [{'start':Fstart, 'stop':Fstop, 'points':Npoints, 'power':power,'bandwidth':bw},]
	na.sweep_type("LIN")

bias_source.range(bias_range)
bias_source.limit(bias_limit)
	
Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path, Fna, row_descr = row_descr)
data_mgmt.spawn_plotting_script(path, plotting_script)

if len(sys.argv) > 1:
	data_mgmt.add_vna_description(f, segment_table, float(re.findall(r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', sys.argv[1])[0][0]))
else:
	data_mgmt.add_vna_description(f, segment_table)

na.output('on')
bias_source.setpoint(0.)
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
bias_source.setpoint(0.) 
bias_source.output('off')
na.soft_trig_abort()
f.close()