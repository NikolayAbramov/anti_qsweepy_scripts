from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt

from numpy import *

Data_dir =r"C:\Users\User\Documents\meas_data"
plotting_script = "2d_S_dly_upd"
row_descr = "Voltage, V"

bias_vals = linspace(-0,5,200)
bias_range = 10
bias_limit = 2e-2
bias_ch = 8

preset = True
Fstart = 4e9
Fstop = 10e9
Npoints = 200
power = -40
bw = 500

SegmentedSweep = True

# Continuous sweep with variable bandwidth and power
Segments =[ {'start':Fstart, 'bandwidth': 500, 'power':power },
{'start':7e9, 'bandwidth': 100, 'power':power },
{'start':15e9,'bandwidth': 20, 'power':power }]

# Segmented sweep
fc_list = [6.92756e9, 7.0333e9, 7.13325e9]
span = 50e6
segment_table = []
for fc in fc_list:
	segment_table += [{'start':fc-span/2, 'stop':fc+span/2, 'points':Npoints, 'power':power,'bandwidth':bw}]

#na = Dummy_VNA.NetworkAnalyzer()
na = Agilent_PNA.NetworkAnalyzer('TCPIP0::10.1.0.24::hislip0::INSTR')
#na = Agilent_PNA.NetworkAnalyzer('TCPIP0::10.1.0.75::inst0::INSTR')
# na = Agilent_PNA.NetworkAnalyzer('pna-x')
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
#bias_source = STS60.BiasSourceByNNDAC("NNDAC")
#bias_source = Keithley_2400.CurrentSource('2400')
#bias_source = Keithley_6221.CurrentSource('GPIB0::12::INSTR')
#bias_source = Keithley_2651.MagnetSupply("NNDAC", rate = 1.)
bias_source = Yokogawa_GS200.VoltageSource('GPIB0::2::INSTR')
#bias_source = DAC_24.VoltageSource('TCPIP0::192.168.0.3::1000::SOCKET')
#bias_source = Dummy_CurrentSource.CurrentSource()
###########################################################################
print("VNA bias scan")
path = data_mgmt.default_save_path(Data_dir, name = "SvsBias")
print("Saving files to: ",path)

if preset:
	na.num_of_points(Npoints)
	na.freq_start_stop((Fstart,Fstop))
	na.bandwidth(bw)
	na.power(power)
	
na.sweep_type("LIN")	
if SegmentedSweep:
	#segment_table = uniform_segment_table(Fstop,Npoints,Segments)
	na.seg_tab(segment_table)
	na.sweep_type("SEGM")
else:
	na.sweep_type("LIN")

bias_source.channel(bias_ch)
bias_source.range(bias_range)
bias_source.limit(bias_limit)
	
Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path, Fna, row_name = row_descr)
data_mgmt.spawn_plotting_script(path, plotting_script)

na.output('on')
bias_source.output('on')
#Sweep
print( f"Parameter range: from {min(bias_vals)} to {max(bias_vals)}" )
na.soft_trig_arm()
for bias_val in bias_vals:
	try:
		bias_source.setpoint(bias_val) 
		print(f"Bias = {bias_val}               ", end = '\r')
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