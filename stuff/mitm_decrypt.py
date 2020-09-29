from mitmproxy import contentviews
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import msgpack, re, json, typing

class Decrypt():
    def __init__(self):
        self.key = b'E0pBn...' # RE with IDA or Frida.

    def decrypt(self, enc: bytes):
        iv = enc[0:16]
        aes = AES.new(self.key, AES.MODE_CBC, iv)
        pad_text = aes.decrypt(enc[16:])
        text = unpad(pad_text, 16)
        data_loaded = msgpack.unpackb(text)
        return data_loaded

class ViewDecrypt(contentviews.View, Decrypt):
    name = "decrypted"
    content_types = ["raw"]

    def format_json(self, data: typing.Any) -> typing.Iterator[contentviews.base.TViewLine]:
        encoder = json.JSONEncoder(indent=4, sort_keys=True, ensure_ascii=False)
        current_line: contentviews.base.TViewLine = []
        for chunk in encoder.iterencode(data):
            if "\n" in chunk:
                rest_of_last_line, chunk = chunk.split("\n", maxsplit=1)
                # rest_of_last_line is a delimiter such as , or [
                current_line.append(('text', rest_of_last_line))
                yield current_line
                current_line = []
            if re.match(r'\s*"', chunk):
                current_line.append(('json_string', chunk))
            elif re.match(r'\s*\d', chunk):
                current_line.append(('json_number', chunk))
            elif re.match(r'\s*(true|null|false)', chunk):
                current_line.append(('json_boolean', chunk))
            else:
                current_line.append(('text', chunk))
        yield current_line

    def __call__(self, data, **metadata):
        data = self.decrypt(data)
        return "decrypted", self.format_json(data)

view = ViewDecrypt()

def load(l):
    contentviews.add(view)

def done():
    contentviews.remove(view)