from anti_qsweepy.drivers import *
from anti_qsweepy.routines import data_mgmt
import scipy.interpolate as si
import numpy as np
import matplotlib.pyplot as plt
db = lambda x: 20*np.log10(np.abs(x))
import time

Nmeas = 200
data_dir =r"D:\Abramov"

na = RS_ZVB20.NetworkAnalyzer('TCPIP0::10.1.0.55::INSTR')
pump = Anapico_SG.Generator('USB0::0x03EB::0xAFFF::121-33A6D0600-1884::INSTR')
bias = Yokogawa_GS200.CurrentSource('USB0::0x0B21::0x0039::90ZA44433::INSTR')

N = na.num_of_points()
S21off = np.zeros((Nmeas, N), dtype=complex)
S21on = np.zeros((Nmeas, N), dtype=complex)

# Measure
na.soft_trig_arm()
pump.output(False)
time.sleep(1)
for i in range(Nmeas):
    S21off[i] = na.read_data()

pump.output(True)
time.sleep(10)
for i in range(Nmeas):
    S21on[i] = na.read_data()
na.soft_trig_abort()

f_points = na.freq_points()
f_nop = len(f_points)

# Calculate snr gain
S21on_mean = np.mean(S21on, axis=0)
S21off_mean = np.mean(S21off, axis=0)

snr_off = np.abs(S21off_mean) / np.std(np.abs(S21off), axis=0)
snr_on = np.abs(S21on_mean) / np.std(np.abs(S21on), axis=0)
snr_gain = snr_on / snr_off

# Save
save_path = data_mgmt.default_save_path(data_dir, name = "SNR_gain")
result = data_mgmt.IMPA_Tuning_Result(save_path, f_nop)
data_mgmt.spawn_plotting_script(save_path, r'JPA\plot_jpa_tuning_results')

f_center, f_span = na.freq_center_span()
result.thumbnail['Fs'] = f_center
result.thumbnail['Fp'] = pump.freq()
result.thumbnail['G'] = 20
result.thumbnail['Pp'] = pump.power()
result.thumbnail['I'] = bias.setpoint()
result.thumbnail['Gsnr'] = 0
result.thumbnail.append()

print(np.shape(S21on))
print(f_nop)
result.s21_on.append(S21on)
result.s21_off.append(S21off)
result.s21_freq.append(f_points.reshape(1, f_nop))
result.s21_on_snr.append(S21on_mean.reshape(1, len(S21on_mean)))
result.s21_off_snr.append(S21off_mean.reshape(1, len(S21off_mean)))
result.snr_gain.append((snr_on / snr_off).reshape(1, f_nop))
result.snr_freq.append(f_points.reshape(1, f_nop))

result.file.flush()
result.file.close()

# f_target = 6.5e9
# idx = np.abs(f_points - f_target).argmin()
#
# plt.figure('SNR Gain')
# plt.plot(f_points, db(S21on_mean/S21off_mean))
# plt.plot(f_points, db(snr_gain))
#
#
# plt.show()
