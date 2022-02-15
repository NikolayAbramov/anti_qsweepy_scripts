import os
from numpy import *
from anti_qsweepy.drivers import *
from anti_qsweepy.routines.helper_functions import *
from anti_qsweepy.routines.jpa_tuning import *

noise_script = "jpa_noise.py"

tuning_table = "E:\\Abramov\\2022-02-10\\20-31-02-jpa_tuning\\tuning_table.txt"

span = 1.6e9
bw = 100
power = -35
points = 600

def open_devices():
	vna = Agilent_PNA.NetworkAnalyzer('PNA-X')
	#na = RS_ZNB20.NetworkAnalyzer('ZNB20')
	#bias = Keithley_2400.CurrentSource('2400')
	bias = Keithley_6221.CurrentSource('GPIB0::10::INSTR')
	#bias = Keithley_2651.MagnetSupply("NNDAC", rate = 1.)
	pump = Agilent_PSG.Generator('Generator_E8257D')
	return vna,bias,pump
	
def close_devices():
	vna.close()
	bias.close()
	pump.close()

tt = TuningTable()
tt.load(tuning_table)
vna,bias,pump = open_devices()
bias.setpoint(0)
bias.output(1)
pump.output(1)
vna.output(1)
vna.power(power)
vna.bandwidth(bw)
vna.num_of_points(points)
close_devices()
try:
	for op in tt:
		vna,bias,pump = open_devices()
		bias.setpoint(op.I)
		pump.freq(op.Fp)
		pump.power(op.Pp)
		vna.freq_center_span((op.Fp/2,span))
		close_devices()
		os.system("python "+noise_script+" {:.6f}GHz".format(1e-9*op.Fp/2) )
except KeyboardInterrupt: pass