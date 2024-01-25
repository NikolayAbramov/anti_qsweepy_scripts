from anti_qsweepy.drivers import *
from anti_qsweepy.routines.helper_functions import *

chan = "JT_CERNOX"

tc = Mercury_iTc.TemperatureController( "iTc" )
tc.shutdown(chan)
tc.close()