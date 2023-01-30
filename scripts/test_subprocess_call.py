#!/usr/bin/env python3


import subprocess
import os
import time
os.chdir(r"C:\Program Files\Plaxis\PLAXIS 2D")
subprocess.Popen("Plaxis2DXInput.exe --AppserverPassword=mypassword --AppServerPort=10000", shell=True)

time.sleep(1)

print('Next line!!!!!!!!!')

