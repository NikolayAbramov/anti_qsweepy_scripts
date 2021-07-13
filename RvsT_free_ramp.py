import visa
import string
import time
from anti_qsweepy.drivers import *
import os
from numpy import *
from collections import *

Data_dir ="D:\Abramov"

#Switching seqvence
SwSeq = OrderedDict((('Nb_cpw', [1,2]),('Nb_film', [3,4]) ))

Delay = 1.0
Ttol = 5e-3
MeasDelay = 0.2
Rthr = 1e3 #Do not do polarity switch above

#Mesurement current
I = 100e-6	
#CS_I = {'aper':5e-3,'per':5e-3,'violet':0.5e-6,'yellow':2e-6}

cs_range = 200e-6 	#Current range
cs_autorange = "OFF"
cs_lim = 10. 		#Voltage limit

nv_aperture = 50e-3
nv_range = 1.
nv_autorange = "ON"
nv_count = 1
nv_window = 10.
nv_analog_fiter = 'ON'
nv_timeout = 30

#Temperature controller settings
tc_sensor = "SAMP_DB6"

#Instruments
tc = Mercury_iTc('iTc', term_chars="\n")
cs = Keithley_6221.CurrentSource("GPIB0::10::INSTR")
nv = Keitley_2182a.Voltmeter("GPIB::6::INSTR")
try:
	sw = DC_Switch('Switch',term_chars = "\n")
except:
	print("Warning: DC switch not found!")
	pass	
######################################################################
cs.range(cs_range)
cs.autorange(cs_autorange)
cs.limit(cs_lim)

nv.range(nv_range)
nv.autorange(nv_autorange)
nv.aperture(nv_aperture)
nv.averaging_count(nv_count)
nv.averaging_window(nv_window)
nv.analog_filter(nv_analog_filter)
nv.instr.timeout(nv_timeout * 1000)
print("Resistance vs Temperature free run measurement")
path = data_mgmt.default_save_path(Data_dir, name = "RvsT")
print("Saving files to: ",path)

Files = []
for Sample in SwSeq.keys():
		if type(CS_I)==dict: I = CS_I[Sample]
		else: I=CS_I
		Files.append( open( path+'\\'+Sample+'.dat','a+') )
		Files[-1].write( "#I = {:e} A\n".format(I) )
		Files[-1].write("#T, K\t\tU,V\t\t\tR, Ohm\t\tV+\t\tV-\n")
		Files[-1].flush()

cs.setpoint(0)
cs.output("ON")
LastT = 0.
try:
	while(1):
		T = tc.temperature(tc_sensor)
		print("Measuring at T = {:.4f} K".format( T )+' '*40,end = '\r')
		if abs(T - LastT)>Ttol:
			LastT = T
			#Scan samples
			i=0
			for Sample in SwSeq.keys():
				sw_list = [0]*12
				sw.state(sw_list)
				for chan in SwSeq[Sample]:
					sw_list[chan-1] = 1  
				sw.state( sw_list )
				time.sleep(0.01)
				
				T = tc.temperature(TcSensor)
				if type(CS_I)==dict: I = CS_I[Sample]
				else: I=CS_I	
				cs.setpoint(I)
				time.sleep(MeasDelay)
				NV_V1 = nv.read_data()
				
				if NV_V1 > 200.:
					cs.setpoint(0.)
					dV = 0.
					R = 100e9
				elif (NV_V1/I) > Rthr:
					R = NV_V1/I
					NV_V2 = NV_V1
					dV=0.
				else:	
					cs.setpoint( -I )
					time.sleep(MeasDelay)
					NV_V2 = nv.read_data()
					cs.setpoint(0.)
					dV = NV_V1 - NV_V2
					R = dV/(2.*I)
				
				Files[i].write( "{:.4f}\t{:e}\t{:e}\t{:e}\t{:e}\n".format( T, dV, R, NV_V1, NV_V2 ) )
				Files[i].flush()
				i+=1
		time.sleep(Delay)
except KeyboardInterrupt:
	print "Interrupted by user	"
for File in Files:
		File.close()
cs.output("OFF")
#tc.shutdown(TcSensor)