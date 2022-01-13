from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *
import tables
import time
from numpy import *

Data_dir ="E:\Abramov" 
plotting_script = "plot_2d_S"
row_descr = "Time, s"
delay = 10e-3
preset = False
Fstart = 4e9
Fstop = 10.5e9
Npoints = 1500
power = -20
bw = 20

SegmentedSweep = False

Segments =[ {'start':Fstart, 'bandwidth': 500, 'power':power },
{'start':7e9, 'bandwidth': 100, 'power':power },
{'start':15e9,'bandwidth': 20, 'power':power }]

na = Agilent_PNA.NetworkAnalyzer('PNA-X')
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
###########################################################################
print("VNA sweeps in time")
path = data_mgmt.default_save_path(Data_dir, name = "SvsTime")
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
	
Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path, Fna, row_descr = row_descr)
data_mgmt.spawn_plotting_script(path, plotting_script)

na.output('on')
#Sweep
na.soft_trig_arm()
t_start=time.time()
n = 0
while True:
	try: 
		t = time.time()-t_start
		n+=1
		print("Time = {:.2f}, doing sweep {:d}".format(t,n), end = '\r')
		S = na.read_data()
		d_array.append(S.reshape(1,len(S) ))
		r_array.append( array([t]) )
		f.flush()
	except KeyboardInterrupt:
		print( "Interrupted by user" )
		break
na.soft_trig_abort()	
f.close()	