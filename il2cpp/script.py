import subprocess, time
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename

Tk().withdraw()
filename = askopenfilename(filetypes=[("Native Library files", ".so .so.*")])
if len(filename) < 3:
    exit()

# Not the classiest, but works :)
class Adb:

    def cmd(self, args):
        cmd = ['adb'] + args
        subprocess.call(cmd)

    def check_adb(self):
        cmd = ['adb', 'get-state']
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        state = process.communicate()[0].decode()
        if state.find('device') == -1:
            self.kill_server()
            active = self.start_server()
            while not active:
                self.kill_server()
                active = self.start_server()

    def start_server(self):
        self.cmd(['start-server'])
        cmd = ['adb', 'get-state']
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        state = process.communicate()[0].decode()
        if state.find('device') == -1:
            return False
        return True

    def kill_server(self):
        self.cmd(['kill-server'])
        time.sleep(1)

    def pull(self, dir: str, file: str):
        self.cmd(['pull', dir, file])

    def push(self, file: str, dir: str):
        self.cmd(['push', file, dir])

    def su_shell(self, cmd: str):
        self.cmd(['shell', f"su -c '{cmd}'"])

    def kill_app(self, app: str):
        self.cmd(['shell', f"am force-stop {app}"])

adb = Adb()
app = 'com.nexon.sinoalice'
backup = False

def backup_lib():
    timestamp = int(datetime.timestamp(datetime.now()))

    adb.su_shell(f'cp /data/data/{app}/lib/libil2cpp.so /sdcard/')
    adb.pull('/sdcard/libil2cpp.so', f'libil2cpp.so.{timestamp}.bak')
    adb.su_shell('rm /sdcard/libil2cpp.so')

def push_and_mv():
    adb.push(filename, '/sdcard/libil2cpp.so')
    adb.su_shell(f'mv /sdcard/libil2cpp.so /data/data/{app}/lib/libil2cpp.so')

def update_perms():
    adb.su_shell(f'chmod 755 /data/data/{app}/lib/libil2cpp.so')
    adb.su_shell(f'chown system:system /data/data/{app}/lib/libil2cpp.so')

adb.check_adb()
adb.kill_app(app)

if backup:
    backup_lib()
push_and_mv()
update_perms()

input('Finished.')