# Stuff to do with the il2cpp library
* `script.py` - Script to automatically replace game's il2cpp with a modified one, **requires root**. Tested with rooted BlueStacks `4.230.10` (use BSTweaker to root it).  
  
**Mods for armeabi_v7a [8.3.0]:**  
Replace SPFX's KickTrigger R1 to #0 (removes most animations).  
`2A8AE80`: `01 40 A0 E1` ➔ `00 40 A0 E3`.