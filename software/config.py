# there are definitely many much better solutions. I'm no coder.
# though it seems that "from config import *" does what I expect it to.

import platform

if platform.node() == 'riiul-nuc':
	serialport = "/dev/ttyACM0" 
	cameranum = 0
else:
	serialport = "COM3"
	cameranum = 1