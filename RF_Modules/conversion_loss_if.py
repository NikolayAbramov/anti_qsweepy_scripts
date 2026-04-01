from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *

import tables
from numpy import *
import time
    
Data_dir =r"C:\Users\Nikolay\OneDrive - НИТУ МИСиС\Документы\RF_modules" 
plotting_script = "plot_xy_multi"

#rf_module_id = 1
#set_offsets = False
#rf_mixer_offsets = (1440,2910)

# Generator channels
gen_i_ch = 1
gen_q_ch = 2
gen_lo_ch = 3
set_gen_params = False

f_lo = 5.75e9

# Amplitudes, dBm
p_lo = 3
p_i = -3
p_q = -3.35

# Phases, deg
ph_i = 0
ph_q = 99.6

sa_rbw = 100e3
sa_vbw = 1e3

# Frequency range
Fstart = 1e6
Fstop = 1000e6
Npoints = 1000

sa = Keysight_MXA.ListSpectrumAnalyzer('TCPIP0::10.1.0.121::inst0::INSTR')
gen =  Anapico_SG.Generator('USB0::0x03EB::0xAFFF::3B5-0B4M4001C-0781::INSTR')
#rf = RF_Modules.TX('')
###########################################################################
print("Conversion loss measurement")
path = data_mgmt.default_save_path(Data_dir, name = "ConversionLoss_if")
print("Saving files to: ",path)

file = data_mgmt.data_file(path)

low_array = data_mgmt.add_extandable_1d(file, "Low", x_label = "Frequency, GHz", y_label = "Power, dBm")
center_array = data_mgmt.add_extandable_1d(file, "Center", x_label = "Frequency, GHz", y_label = "Power, dBm")
high_array = data_mgmt.add_extandable_1d(file, "High", x_label = "Frequency, GHz", y_label = "Power, dBm")

data_mgmt.spawn_plotting_script(path, plotting_script)

sa.rbw(sa_rbw)
sa.vbw(sa_vbw)

if set_gen_params:
    gen.channel(gen_i_ch)
    gen.power(p_i)
    gen.freq(f_iq)
    gen.phase(ph_i)
    gen.output(True)

    gen.channel(gen_q_ch)
    gen.power(p_q)
    gen.freq(f_iq)
    gen.phase(ph_q)
    gen.output(True)

    gen.channel(gen_lo_ch)
    gen.power(p_lo)
    gen.output(True)
"""
else:
    gen.channel(gen_i_ch)
    f_i = gen.freq()
    gen.channel(gen_q_ch)
    f_q = gen.freq()
    if f_i != f_q:
        raise Exception('I and Q frequencies must be equal fI ={0} fQ ={1}'.format(f_i, f_q))
    f_iq = f_i
"""    
"""
rf.rf_output(rf_module_id, True)
rf.lo_amp_pwr(rf_module_id, True)
rf.lo_attenuation(rf_module_id, 0)
rf.mixer_bypass(rf_module_id, False)
if set_offsets:
    rf.mixer_offsets(rf_module_id, rf_mixer_offsets)
"""    
gen.channel(gen_lo_ch)
gen.freq(f_lo)
#Sweep
print( "Frequency range: from {0} to {1}".format( Fstart, Fstop ))
time.sleep(1)
for freq in linspace(Fstart,Fstop,Npoints):
    try:
        gen.channel(gen_i_ch)
        gen.freq(freq)
        gen.channel(gen_q_ch)
        gen.freq(freq)
        
        f_low = f_lo - freq
        f_high = f_lo + freq
        
        sa.freq_points( [f_low, freq, f_high] )    
        print("Frequency = {:f}".format(freq), end = '\r')
        time.sleep(0.01)
        data = sa.read_data()
        
        low_array[0].append( array([f_low]) )
        low_array[1].append( array([data[0]]) )
        
        center_array[0].append( array([freq]) )
        center_array[1].append( array([data[1]]) )
        
        high_array[0].append( array([f_high]) )
        high_array[1].append( array([data[2]]) )

        file.flush()
    except KeyboardInterrupt:
        print( "Interrupted by user" )
        break
            
file.close()    