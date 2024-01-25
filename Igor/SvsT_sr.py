from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *

import tables
from numpy import *
import sys
import pathlib
import re

Data_dir ="D:\Igor" 
plotting_script = "plot_2d_S"
row_descr = "Temperature, K"

#Tvals = hstack([ [0,],arange(2.5,9.5, 0.5),arange(7.,8., 0.1), arange(8.,9.3, 0.05)])
#Tvals = hstack([ [0,],arange(2.2,3, 0.1), arange(3,4.5, 0.05)])
Tvals = hstack([ [0,],arange(1.8,7.0, 0.1)])
Tsensor = "SAMP_DB6"
PIDtable = "D:\\anti_qsweepy_scripts\\iTC PID tables\\FMR.txt"
Ttol = 1e-2
T_hold_time = 30. 
T_timeout = 1200.

preset = True
Fstart = 1.7e9
Fstop = 2.6e9
Npoints = 32001
power = -20
bw = 5000

SegmentedSweep = True
Segments =[ {'start':Fstart, 'bandwidth': 500, 'power':power },
{'start':7e9, 'bandwidth': 100, 'power':power },
{'start':15e9,'bandwidth': 20, 'power':power }]

raw_seg_table = True

#segment_table=[	{'start':3.9e9, 'stop':4.75e9, 'points':10001, 'power':power,'bandwidth':bw},
#				{'start':5.8e9, 'stop':6.6e9, 'points':10001, 'power':power,'bandwidth':bw}]

#segment_table=[	{'start':2.e9, 'stop':6.2e9, 'points':5000, 'power':power,'bandwidth':bw},] #sr2
#segment_table=[	{'start':2.e9, 'stop':8e9, 'points':5000, 'power':power,'bandwidth':bw},]
segment_table=[	{'start':Fstart, 'stop':Fstop, 'points':Npoints, 'power':power,'bandwidth':bw}]

na = Agilent_PNA.NetworkAnalyzer('pna')
tc = Mercury_iTc.TemperatureController('iTC')
###########################################################################
print("VNA temperature scan")
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
	na.sweep_type("LIN")
	
tc.SetLoopParam( Tsensor,"ENAB", "ON" )
tc.SetPIDtable( Tsensor, PIDtable)
tc.SetAutoPID( Tsensor, True )
	
Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path, Fna, row_descr = row_descr)
data_mgmt.spawn_plotting_script(path, plotting_script)

if len(sys.argv) > 1:
	data_mgmt.add_vna_description(f, segment_table, float(re.findall(r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', sys.argv[1])[0][0]))
else:
	data_mgmt.add_vna_description(f, segment_table)

na.output('on')
#Sweep
na.soft_trig_arm()
for Tval in Tvals:
	try:
		tc.setpoint(Tsensor,Tval) 
		WaitForStableT( Tval, tc.temperature, Tsensor, Ttol, T_hold_time, tc.heater_value, T_timeout)
		Tmeas = tc.temperature(Tsensor)
		print("Measuring at {:.5f}K...                                       ".format(Tmeas), end = '\r')
		S = na.read_data()
		d_array.append(S.reshape(1,len(S) ))
		r_array.append( array([Tmeas]) )
		f.flush()
	except KeyboardInterrupt:
		print( "Interrupted by user" )
		break
na.soft_trig_abort()	
tc.shutdown(Tsensor)
f.close()	