import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename

signatures = {
    'example': ('04 00 A0 E1 70 4C BD E8 11 ?? ?? EA', 0, '00 00 A0 E3'), # (signature, offset to patch within signature, patch)
}

# open file dialog
Tk().withdraw()
filename = askopenfilename(filetypes=[("Native Library files", ".so .so.*")])
if len(filename) < 3:
    exit()

with open(filename, 'rb') as f:
    file = f.read()

for signature in signatures:
    s_data = signatures[signature]
    pattern = b''

    for x in s_data[0].replace('??', '.').split(' '):
        if x != '.':
            pattern += bytes.fromhex(x)
        else:
            pattern += b'.'

    matches = re.search(pattern, file)
    offset = matches.start() + s_data[1]
    print('Patched' + ' %12s' % signature + ' offset: 0x%x' % offset)

    patched = bytes.fromhex(s_data[2])
    file = file[:offset] + patched + file[offset+len(patched):]

with open('libil2cpp.so', 'wb') as f:
    f.write(file)

input('\nSuccessfully patched, press any key to exit...')