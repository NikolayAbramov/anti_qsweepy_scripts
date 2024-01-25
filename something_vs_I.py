import os
from numpy import *
from anti_qsweepy.drivers import *

Script = "Igor\\SvsI_bias.py"

#souce_init = lambda: STS60.BiasSourceByNNDAC("NNDAC")
#souce_init = lambda: Keithley_2400.CurrentSource('2400')
#souce_init = lambda: Keithley_6221.CurrentSource('GPIB0::10::INSTR')
source_init = lambda: Keithley_2651.MagnetSupply("COM1")
src = source_init()
src.limit(5)

Ilist = [0, ]
#Ilist =  [0,3,6,9,11,13,15,16,17,18,19,20]

try:
	for I in Ilist:
		src = source_init()
		src.setpoint(I)
		src.output('on')
		src.close()
		os.system("python "+Script+" {:e}A".format(I) )
except KeyboardInterrupt: pass

src.setpoint(0)
src.output('off')
src.close()

