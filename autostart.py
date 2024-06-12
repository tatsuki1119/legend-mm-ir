import os
import subprocess
import time

print("getcwd:      ", os.getcwd())
print("__file__:    ", __file__)


subprocess.Popen("lxterminal -e python /home/momo/piz/flask/app.py", shell=True)


print("finish...")
time.sleep(10)
