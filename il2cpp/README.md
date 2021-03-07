# Stuff to do with the il2cpp library
* `script.py` - Script to automatically replace game's il2cpp with the selected one, **requires root**. Tested with rooted BlueStacks 4.230.10 (use BSTweaker to root it).  
  
**Mods for armeabi_v7a [8.3.0]:**  
Replace SPFX's KickTrigger R1 to #0 (removes most particles/effects).  
`0x02A8AE80`: `01 40 A0 E1` ➔ `00 40 A0 E3`.