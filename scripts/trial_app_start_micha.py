import os
import subprocess
import time


def start_plaxis(app_path, portnr=10000, password='mypassword', no_controllers=False):
    args = [app_path]
    args.append('--AppServerPort={}'.format(portnr))
    if password:
        args.append('--AppServerPassword={}'.format(password))

    if no_controllers is True:
        args.append('--NO_CONTROLLERS')    
    p = subprocess.Popen(args)
    # wait a second for the application to launch
    print("Launched: {}".format(os.path.basename(app_path)))
    delay = 1 # second
    time.sleep(delay)
    return p
    

#plaxisfolder = r'C:\Plaxis\Released\PLAXIS 2D\2018.00'
plaxisfolder = r'C:\Program Files\Plaxis\PLAXIS 2D'

plx_input = os.path.join(plaxisfolder, 'Plaxis2DXInput.exe')
plx_output = os.path.join(plaxisfolder, 'Plaxis2DOutput.exe')

app_port_input = 10000
app_port_output = 9997
app_pw = 'BauerPlaxisPower'

start_plaxis(plx_input, app_port_input, app_pw, no_controllers=True)
start_plaxis(plx_output, app_port_output, app_pw)



