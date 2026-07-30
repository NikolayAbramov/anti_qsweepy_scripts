from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
import scipy.interpolate as si
from numpy import *

Data_dir =r"D:\Abramov"
plotting_script = "plot_2d_S_upd"
#powers = hstack (( arange(-50,-40,2), arange(-40,10, 1) ))
#14 powers = hstack (( arange(-60,-40,10), arange(-45,15,5) ))
powers = hstack ( arange(-50, -15,0.5) )

abaptive_aperture = True
#[[power, bandwidth],...]
bw_profile  = [[-70,10],[-60,100],[-50,500],[10,500]]
averaging_profile = [[-70,1],[-50,1],[10,1]]

# Regular sweep
preset = False
points = 200
f_cent = 7e9
span = 50e6
bw = 100

SegmentedSweep = False
# Segmented sweep
fc_list = [6.92756e9, 7.0333e9, 7.13325e9]

def mk_seg_tab(fc_list, span, points, power, bw):
	segment_table = []
	for fc in fc_list:
		segment_table += [{'start':fc-span/2, 'stop':fc+span/2, 'points':points, 'power':power,'bandwidth':bw}]
	return segment_table

###########################################################################
print("VNA power scan")
#na = Agilent_PNA.NetworkAnalyzer('pna-x')
na = RS_ZVB20.NetworkAnalyzer('TCPIP0::10.1.0.55::INSTR')
#na = Agilent_PNA.NetworkAnalyzer('TCPIP0::10.1.0.24::hislip0::INSTR')
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
path = data_mgmt.default_save_path(Data_dir, name = "SvsP")
print("Saving files to: ",path)

na.sweep_type("LIN")
if SegmentedSweep:
	na.seg_tab(mk_seg_tab(fc_list, span, points, -60, bw))
	na.sweep_type("SEGM")
else:
	na.sweep_type("LIN")
	if preset:
		na.num_of_points(points)
		na.freq_center_span((f_cent, span))
		na.bandwidth(bw)

Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path,Fna )
data_mgmt.spawn_plotting_script(path, plotting_script)

bw_func = si.interp1d([x[0] for x in bw_profile], [x[1] for x in bw_profile])
averaging_func = si.interp1d([x[0] for x in averaging_profile], [x[1] for x in averaging_profile])

na.output('on')

#Sweep
print( "Parameter range: from {:.3f} to {:.3f}".format( min(powers), max(powers) ))
na.soft_trig_arm()
try:
	for P in powers:
		if SegmentedSweep:
			if abaptive_aperture:
				na.averaging(int(round(averaging_func([P])[0])))
				bw = bw_func(P)
			na.seg_tab(mk_seg_tab(fc_list, span, points, P, bw))
			na.sweep_type("SEGM")
		else:
			if abaptive_aperture:
				na.averaging(int(round(averaging_func([P])[0])))
				na.bandwidth(bw_func(P))
			na.power(P)

		print("P={:.3f}".format(P), end = '\r')
		S = na.read_data()
		d_array.append(S.reshape(1,len(S) ))
		r_array.append( array([P]) )
		f.flush()
except KeyboardInterrupt:
	print( "Interrupted by user" )
na.soft_trig_abort()	
f.close()	