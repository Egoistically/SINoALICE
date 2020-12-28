import mitmproxy.websocket, time, json, zlib, msgpack, base64

class WSS:

    def decompress(self, string: str):
        while '\/' in string:
            string = string.replace('\/', '/')

        decoded = base64.b64decode(string)
        decompressed = zlib.decompress(decoded)
        payload = msgpack.unpackb(decompressed)
        return payload

    def handle_message(self, message: mitmproxy.websocket.WebSocketMessage):
        msg = time.strftime('[%Y-%m-%d %H-%M-%S]')
        clean = message.content
        if any(x in clean for x in ['scheduler_uuid', 'user_act']):
            prefix = clean[:9]
            r = json.loads(clean[9:])
            m = json.loads(r[1])

            payload = self.decompress(m['payload'].replace('"', ''))

            m['payload'] = payload
            r[1] = json.dumps(m)
            clean = prefix + json.dumps(r)

        msg += (' [OUT] >> ' if message.from_client else ' [IN]  << ') + clean
        print(msg)

    def websocket_message(self, flow: mitmproxy.websocket.WebSocketFlow):
        # get the latest message
        message = flow.messages[-1]

        # was the message sent from the client or server?
        self.handle_message(message)

addons = [
    WSS()
]