from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
import scipy.interpolate as si

import tables
from numpy import *

Data_dir ="E:/Abramov" 
plotting_script = "plot_2d_S"
#powers = hstack (( arange(-50,-40,2), arange(-40,10, 1) ))
#14 powers = hstack (( arange(-60,-40,10), arange(-45,15,5) ))
powers = hstack ( arange(-50, 6,1) )

abaptive_aperture = True
#[[power, bandwidth],...]
#bw_profile  = [[-60,1],[-50,1],[-40,5],[-20,10],[10,10e3]]
bw_profile  = [[-50,10],[-30,100],[-20,500],[10,10e3]]
#14 averaging_profile = [[-60,10],[-50,5],[-40,1],[10,1]]
#averaging_profile = [[-60,3],[-50,1],[10,1]]
averaging_profile = [[-60,1],[-50,1],[10,1]]

preset = False
points = 600
f_cent = 7e9
span = 1e9
bw = 100
###########################################################################
print("VNA power scan")
na = Agilent_PNA.NetworkAnalyzer('pna-x')
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
path = data_mgmt.default_save_path(Data_dir, name = "SvsP")
print("Saving files to: ",path)

if preset:
	na.num_of_points(points)
	na.freq_center(f_cent)
	na.freq_span(span)
	na.bandwidth(bw)

Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path,Fna )
data_mgmt.spawn_plotting_script(path, plotting_script)

if abaptive_aperture:
	bw_func = si.interp1d([x[0] for x in bw_profile], [x[1] for x in bw_profile])
	averaging_func = si.interp1d([x[0] for x in averaging_profile], [x[1] for x in averaging_profile])

na.output('on')

#Sweep
print( "Parameter range: from {:.3f} to {:.3f}".format( min(powers), max(powers) ))
na.soft_trig_arm()
try:
	for P in powers:
		na.power(P)
		if abaptive_aperture:
			na.averaging( int(round( averaging_func([P])[0] )) )
			na.bandwidth( bw_func(P) ) 
		print("P={:.3f}".format(P), end = '\r')
		S = na.read_data()
		d_array.append(S.reshape(1,len(S) ))
		r_array.append( array([P]) )
		f.flush()
except KeyboardInterrupt:
	print( "Interrupted by user" )
na.soft_trig_abort()	
f.close()	