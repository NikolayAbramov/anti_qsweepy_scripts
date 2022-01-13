from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *

import tables
from numpy import *

Data_dir ="E:\Abramov" 
plotting_script = "plot_S"


preset = False
Fstart = 4.7e9
Fstop = 8e9
Npoints = 32000
power = -20
bw = 1000

SegmentedSweep = False

Segments =[ {'start':Fstart, 'bandwidth': 500, 'power':power },
{'start':7e9, 'bandwidth': 100, 'power':power },
{'start':15e9,'bandwidth': 20, 'power':power }]

na = Agilent_PNA.NetworkAnalyzer('pna-x')
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
###########################################################################
print("VNA snapshot")
path = data_mgmt.default_save_path(Data_dir, name = "vna_snapshot")
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
f  = data_mgmt.data_file(path)
y_atom = tables.ComplexAtom(itemsize = 16 )
x_atom = tables.Float64Atom() #coordinates dtype
f.create_array(f.root, 'x', Fna, "Frequency, Hz")

data_mgmt.spawn_plotting_script(path, plotting_script)

na.output('on')
#Sweep
na.soft_trig_arm()
try: 
	print("Measuring...", end = '\r')
	S = na.read_data()
	f.create_array(f.root, 'y', S, "Complex S-parameter")
	f.flush()
except KeyboardInterrupt:
	print( "Interrupted by user" )
na.soft_trig_abort()	
f.close()	