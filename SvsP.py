from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt

import tables
from numpy import *

Data_dir ="D:/Igor" 
plotting_script = "plot_2d_S"
powers = arange(-20,12, 0.02)

abaptive_bw = True
ref_bw  = 100
min_bw= 10
ref_p = -20

preset = False
points = 600
f_cent = 7e9
span = 1e9
bw = 1e3
###########################################################################
print("VNA power scan")
na = Agilent_PNA.NetworkAnalyzer('pna')
path = data_mgmt.default_save_path(Data_dir, name = "SvsP")
print("Saving files to: ",path)

if preset:
	na.num_of_points(points)
	na.freq_center(f_cent)
	na.freq_span(span)
	na.bandwidth(bw)

Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path)
data_mgmt.spawn_plotting_script(path, plotting_script)

na.output('on')
#Sweep
print( "Parameter range: from {:.3f} to {:.3f}".format( min(powers), max(powers) ))
na.soft_trig_arm()
for P in powers:
	try:
		na.power(P)
		if abaptive_bw:
			bw = 10**((P - ref_p)/10)*ref_bw 
			if bw<min_bw:
				bw = min_bw
			na.bandwidth( bw ) 
		print("P={:.3f}".format(P), end = '\r')
		S = na.read_data()
		d_array.append(S.reshape(1,len(S) ))
		r_array.append( array([P]) )
		f.flush()
	except KeyboardInterrupt:
		print( "Interrupted by user" )
		break
na.soft_trig_abort()	
f.close()	