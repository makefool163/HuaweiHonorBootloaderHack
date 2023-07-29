# HuaweiHonorBootloaderHack
Huawei cellphone Bootloader unlock code hack

As early as on https://github.com/SkywalkerFR, brute force cracking of Huawei mobile phone bootloader unlock code was available. Another repository, https://github.com/haexhub/huaweiBootloaderHack, has a breakpoint continually python version, while https://github.com/rainxh11/HuaweiBootloader_Bruteforce make multiprocesses version is used in C#.

I am considering writing a multiprocess version of Python and embedding it in the eventlet coroutine, using the asynchronous method of subprocess.Popen. This method will dramatically increase the cracking speed, such that it can guess about 100 codes every 16 seconds, allowing for approximately 300,000 attempts in 12 hours. Please note that the speed may also depend on your phone or whether you have Huawei Suite installed.

Please also note that if you run this program repeatedly, the speed will slow down. Once you restart your pc, the speed will be restored. I don't know why this happens, maybe because the fastboot.exe process is dead in memory.

Additionally, please modify the corresponding IMEI code while cracking your mobile phone, as the IMEI code in this program is directly written to the source code.

Finally, I am unsure of the amazing reduction algorithm behind the last key question of "genOEMcode += int(checksum + math.sqrt(imei) * 1024)" and whether it works.
