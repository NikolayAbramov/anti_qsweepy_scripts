from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *

import tables
from numpy import *

Data_dir ="E:\Abramov" 
plotting_script = "plot_2d_scalar"
row_descr = "Current, A"

target_gain  = 22

bias_vals = arange(2.8e-3, 4.4e-3, 0.005e-3)
bias_range = 10e-3
bias_limit = 10

preset = True
Fcent = 6.6e9
Fspan = 600e6
Npoints = 350
power = -30
bw = 5000

pump_amps = arange(-7,1.8,0.1)

na = Agilent_PNA.NetworkAnalyzer('PNA-X')
#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
#bias_source = STS60.BiasSourceByNNDAC("NNDAC")
#bias_source = Keithley_2400.CurrentSource('2400')
bias_source = Keithley_6221.CurrentSource('GPIB0::10::INSTR')
#bias_source = Keithley_2651.MagnetSupply("NNDAC", rate = 1.)
pump = Agilent_PSG.Generator('Generator_E8257D')
###########################################################################
print("Gain search")
path = data_mgmt.default_save_path(Data_dir, name = "experimental")
print("Saving files to: ",path)

if preset:
	na.num_of_points(Npoints)
	na.freq_center_span((Fcent,Fspan))
	na.bandwidth(bw)
	na.power(power)

na.sweep_type("LIN")

bias_source.range(bias_range)
bias_source.limit(bias_limit)

pump.freq(Fcent*2.)
	
Fna = na.freq_points()
f, d_array, r_array = data_mgmt.extendable_2d(path, bias_vals, row_descr = row_descr)
data_mgmt.spawn_plotting_script(path, plotting_script)

na.output('on')
bias_source.output('on')
#Sweep

#Reference
pump.output('off')
na.soft_trig_arm()
db_ref = mean(20*log10(abs(na.read_data())))
print("Reference level: {:f}db".format(db_ref))
pump.output('on')
bias_scan = zeros(len(bias_vals))
try:
	for pump_amp in pump_amps:
		pump.power(pump_amp)
		for i, bias_val in enumerate(bias_vals):
			bias_source.setpoint(bias_val) 
			print("Pump = {:.2f} Bias = {:e}      ".format(pump_amp, bias_val), end = '\r')
			gain = 20*log10(abs(na.read_data()))-db_ref
			bias_scan[i] = mean((gain-target_gain)**2)
		d_array.append(bias_scan.reshape(1,len(bias_scan) ))
		r_array.append( array([pump_amp]) )
		f.flush()	
except KeyboardInterrupt:
	print( "Interrupted by user" )
			
bias_source.output('off')
pump.output('off')		
na.soft_trig_abort()	
f.close()