from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
from anti_qsweepy.routines.helper_functions import *

import tables
from numpy import *

Data_dir =r"C:\Users\Nikolay\OneDrive - НИТУ МИСиС\Документы\RF_modules" 
plotting_script = "plot_xy"


preset = False

Fstart = 4e9
Fstop = 10e9
vbw = 100e3
rbw = 1e6

sa = Keysight_MXA.SpectrumAnalyzer('Keysight_MXA')
###########################################################################
print("Spectrum analyzer snapshot")
path = data_mgmt.default_save_path(Data_dir, name = "sa_snapshot")
print("Saving files to: ",path)

if preset:
    sa.rbw(rbw)
    sa.vbw(vbw)
    sa.freq_start_stop((Fstart,Fstop))

F = sa.freq_points()
file  = data_mgmt.data_file(path)
y_atom = tables.ComplexAtom(itemsize = 16 )
x_atom = tables.Float64Atom() #coordinates dtype
file.create_array(file.root, 'x', F, "Frequency, Hz")

data_mgmt.spawn_plotting_script(path, plotting_script)

#Sweep
sa.soft_trig_arm()
try: 
    print("Measuring...", end = '\r')
    S = log10(sa.read_data()/1e-3)*10
    file.create_array(file.root, 'y', S, "Power, dBm")
    file.flush()
except KeyboardInterrupt:
    print( "Interrupted by user" )
sa.soft_trig_abort()    
file.close()    