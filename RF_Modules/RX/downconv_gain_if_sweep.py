from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *

import tables
from numpy import *
import time
    
Data_dir =r"C:\Users\Nikolay\OneDrive - НИТУ МИСиС\Документы\RF_modules" 
plotting_script = "plot_xy_multi"

# Generator channels
gen_rf_ch = 4
gen_lo_ch = 3
set_gen_params = True

# Intermediate frequency
f_lo = 6e9

# Amplitudes, dBm
p_lo = 3
p_rf = -19

sa_rbw = 3e6
sa_vbw = 1e3

# Frequency range
Fstart = 0e9
Fstop = 1e9
Npoints = 500

sa = Keysight_MXA.ListSpectrumAnalyzer('TCPIP0::10.1.0.121::inst0::INSTR')
gen =  Anapico_SG.Generator('USB0::0x03EB::0xAFFF::3B5-0B4M4001C-0781::INSTR')

###########################################################################
print("Downconversion gain measurement")
path = data_mgmt.default_save_path(Data_dir, name = "DownconvGainIf")
print("Saving files to: ",path)

file = data_mgmt.data_file(path)

amp_array = data_mgmt.add_extandable_1d(file, "Amp", x_label = "Frequency, GHz", y_label = "Power, dBm", 
    metadata = {
    "Flo":f_lo,
    "Prf":p_rf,
    "Plo":p_lo,
    "sa_rbw":sa_rbw, 
    "sa_vbw":sa_vbw,
    "Fstart":Fstart,
    "Fstop":Fstop,
    "Npoints":Npoints  
    })

data_mgmt.spawn_plotting_script(path, plotting_script)

sa.rbw(sa_rbw)
sa.vbw(sa_vbw)

if set_gen_params:

    gen.channel(gen_rf_ch)
    gen.power(p_rf)
    gen.output(True)

    gen.channel(gen_lo_ch)
    gen.power(p_lo)
    gen.output(True)
    
#Sweep
print( "Frequency range: from {0} to {1}".format( Fstart, Fstop ))

gen.channel(gen_rf_ch)
gen.freq(f_lo)

for freq in linspace(Fstart,Fstop,Npoints):
    try:
        sa.freq_points( [abs(freq)] )
        gen.channel(gen_rf_ch)
        gen.freq(f_lo+freq)
        gen.channel(gen_lo_ch)
        gen.freq(f_lo)
            
        print("Frequency = {:f}".format(freq), end = '\r')
        time.sleep(0.02)
        data = sa.read_data()
        
        amp_array[0].append( array([freq]) )
        amp_array[1].append( array([data[0]]) )

        file.flush()
    except KeyboardInterrupt:
        print( "Interrupted by user" )
        break

file.close()
sa.close()
sa = Keysight_MXA.SpectrumAnalyzer( 'TCPIP0::10.1.0.121::inst0::INSTR')
sa.close()   