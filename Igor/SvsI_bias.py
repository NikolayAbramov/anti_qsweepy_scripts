#For DC biasing via the resonator
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

DCbias_vals = hstack([arange(0, 2.2e-3, 1.e-4)])
DCbias_range = 2.1e-3
DCbias_limit = 1

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
segment_table=[	{'start':Fstart, 'stop':Fstop, 'points':Npoints, 'power':power,'bandwidth':bw}]

na = Agilent_PNA.NetworkAnalyzer('pna')
DCbias_source = Keithley_6221.CurrentSource('GPIB0::10::INSTR')

###########################################################################
print("VNA DCbias scan")
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

DCbias_source.range(DCbias_range)
DCbias_source.limit(DCbias_limit)
	
Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path, Fna, row_descr = row_descr)
data_mgmt.spawn_plotting_script(path, plotting_script)

if len(sys.argv) > 1:
	data_mgmt.add_vna_description(f, segment_table, float(re.findall(r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', sys.argv[1])[0][0]))
else:
	data_mgmt.add_vna_description(f, segment_table)

na.output('on')
DCbias_source.setpoint(0.)
DCbias_source.output('on')
#Sweep
print( "Parameter range: from {:.3f} to {:.3f}".format( min(DCbias_vals), max(DCbias_vals) ))
na.soft_trig_arm()
for DCbias_val in DCbias_vals:
	try:
		DCbias_source.setpoint(DCbias_val) 
		print("DCbias = {:f}".format(DCbias_val), end = '\r')
		S = na.read_data()
		d_array.append(S.reshape(1,len(S) ))
		r_array.append( array([DCbias_val]) )
		f.flush()
	except KeyboardInterrupt:
		print( "Interrupted by user" )
		break
DCbias_source.setpoint(0.) 
DCbias_source.output('off')
na.soft_trig_abort()
f.close()