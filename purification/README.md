# Purification API
Requirements:
* AES key for packet encryption and decryption, find it with Frida or IDA.
* User ID, private RSA key and payment UUID, all can be found in `gl-payment_gamelib.xml`, inside the game folder.
* Session ID, you can find it by intercepting game traffic.

Replace `config.py`'s parameters with these.  
  
Values of the packets can be modified, there are no server-side checks in place.  
**Proof of concept, [don't be an asshole](https://cafe.naver.com/sinoalice/27224)**.  
  
Credits to [see-aestas](https://github.com/see-aestas), most of the code is theirs.  
Based on: https://github.com/see-aestas/SINoALICE-API.