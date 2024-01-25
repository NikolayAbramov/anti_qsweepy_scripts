from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *
from numpy import *
import time
from collections import *

data_dir = "E:/data/Abramov"

tc_chan_high = "T6"
tc_chan_low = "T5"
T_high_low = 1.6 #between Low and High

Ttol = 1

#Sample name: switch state
sw_seq = OrderedDict(( ('1',[3,4]),('2',[7,8]) ))

meas_delay = 1.
Rthr = 1e3 #Do not swap polarity above

Imeas = 1e-6

tc = Triton_DR200.TemperatureController('Triton_DR200')

#smu = Artificial_SMU.Artificial_SMU( Keithley_6221.CurrentSource('GPIB1::10::INSTR'), Keithley_2182A.Voltmeter('GPIB1::7::INSTR') )
smu = Keithley_2400.SMU("Keithley_2400")

smu.four_wire("off")
smu.source('CURR')
smu.source_autorange("OFF")
smu.source_range(10e-6)
smu.limit(2)
smu.aperture(2)
smu.meter_range(0.1)
smu.meter_autorange('ON')
smu.averaging_count(1)


switch_present = True
try:
	switch = DC_Switch.DC_Switch('DC_switch')
except:
	switch_present = False
	print('Warning!: DC Switch not found')

##################################################################################
def GetT():
	Tlow = tc.temperature(tc_chan_low)
	Thigh = tc.temperature(tc_chan_high)
	if Thigh < T_high_low: return Tlow
	else: return Thigh

print("R vs temperature free run")
path = data_mgmt.default_save_path(data_dir, time = False, name = "RvsT")
print("Saving files to: ",path)

Files = []
for Sample in sw_seq.keys():
		Files.append(open(path+'/'+Sample+'.dat','a+'))
		Files[-1].write( "#I = {:e} A\n".format(Imeas) )
		Files[-1].write("#T, K\t\tU,V\t\t\tR, Ohm\t\tV+\t\tV-\n")
		Files[-1].flush()

smu.setpoint(0.)
smu.output("ON")
try:
	#Measure
	LastT=0.0
	while 1:
		T = GetT()
		print ("T = {:.4f} K                                                    ".format( T ), end = "\r")
		if abs(T - LastT)>Ttol:
			LastT = T
			#Scan samples
			i=0
			for sample in sw_seq.keys():
				if switch_present:
					sw_list = [0]*12
					switch.state(sw_list)
					for chan in sw_seq[sample]:
						sw_list[chan-1] = 1  
					switch.state( sw_list )	
					T = GetT()
					print("Sample: "+sample+ " Measuring at T = {:.4f} K                    ".format( T ), end = "\r")
				smu.setpoint(Imeas)
				stupid_waiting(meas_delay)
				NV_V1 = smu.read_data()
				if NV_V1 > 200.:
					smu.setpoint(0.)
					dV = 0.
					R = 100e9
				elif (NV_V1/Imeas) > Rthr:
					R = NV_V1/Imeas
					NV_V2 = NV_V1
					dV=0.
				else:	
					smu.setpoint(-Imeas)
					stupid_waiting(meas_delay)
					NV_V2 = smu.read_data()
					smu.setpoint(0.)
					dV = NV_V1 - NV_V2
					R = dV/(2.*Imeas)
				
				Files[i].write( "{:.4f}\t{:e}\t{:e}\t{:e}\t{:e}\n".format( T, dV, R, NV_V1, NV_V2 ) )
				Files[i].flush()
				i+=1
		else:
			time.sleep(0.1)

except KeyboardInterrupt:
	print ("\nInterrupted by user")
	
tc.close()
for File in Files:
	File.close()

try: 
	switch.close()
except: pass		
smu.setpoint(0.)
smu.close()