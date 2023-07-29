"""
Sky' 💜 https://github.com/SkywalkerFR
https://fr.wikipedia.org/wiki/Formule_de_Luhn

💜 https://github.com/haexhub/huaweiBootloaderHack
💜 https://github.com/rainxh11/HuaweiBootloader_Bruteforce
"""

import time
import math
import eventlet

import ctypes
import os
import subprocess
import joblib

const_PCount = 8

def luhn_checksum(imei):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits      = digits_of(imei)
    oddDigits   = digits[-1::-2]
    evenDigits  = digits[-2::-2]
    checksum    = 0
    checksum    += sum(oddDigits)
    for i in evenDigits:
        checksum += sum(digits_of(i * 2))
    return checksum % 10

def algoIncrementChecksum(imei, checksum, genOEMcode):
    """
    I don't know what's with this algorithm, 
    anyway, you are such a copy, can reduce 
    the amount of data of 9 x10e15 below 300000. 
    I don't know if it work.
    """
    genOEMcode  += int(checksum + math.sqrt(imei) * 1024)
    return genOEMcode

"""
hcu-client / hde-tool / sigkill windows app 
all support reading bootloader's unlock code on Ares Snapdragon devices (ARE- and ARS-).

That shall cost like 4usd to do it yourself.
"""
def sub_Proc(pMain, pSub):
    while True:
        try:
            algoOEMcode = pMain.get(block=True, timeout=1)
        except eventlet.queue.Empty:
            break

        if algoOEMcode < 0:
            # recv the EXIT sign
            break

        #print (algoOEMcode, end=" ", flush=True) 
        p = subprocess.Popen(["fastboot","oem","unlock",str(algoOEMcode)], \
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while p.poll() is None:
            eventlet.sleep(0.5)
        _, error = p.communicate()

        #print (error)
        if b"FAILED" in error:
            print (".", end ="", flush=True)
            pSub.put (algoOEMcode)
        else:
            pSub.put (-algoOEMcode)


def sub_Data_init (pMain, run_OEMCode, fail_Codes, imei, checksum):
    i = 0
    j = 0
    while run_OEMCode < 10000 * 10000 * 10000 * 10000:
        i += 1
        run_OEMCode  += int(checksum + math.sqrt(imei) * 1024)
        if run_OEMCode not in fail_Codes:
            pMain.put (run_OEMCode)
            #pMain.send (str(run_OEMCode))
            j += 1
        eventlet.sleep (0)
    for _ in range(1000):
        pMain.put (-1)
        #pMain.send ("")
        eventlet.sleep (0)
    print ("OEMCode Count:", i, "/", j, end="", flush=True)
    return i
    
if __name__ == "__main__":
    run_OEMCode = 1000 * 10000 * 10000 * 10000
    imei = 867502024085067

    fail_dump_file = "./munlock." + str(imei) + ".fail"

    if os.path.exists(fail_dump_file):
        fail_Codes = joblib.load(fail_dump_file)
    else:
        fail_Codes = []
    recv_Count = len(fail_Codes)

    checksum = luhn_checksum(imei)

    pMain = eventlet.queue.Queue()
    pSub  = eventlet.queue.Queue()

    init_p = eventlet.spawn (sub_Data_init, pMain, run_OEMCode, fail_Codes, imei, checksum)
    eventlet.sleep(3)

    subprocess.run(['adb', 'devices'])

    subprocess.run(
        ['adb', 'reboot', 'bootloader']
    , stdout = subprocess.DEVNULL
    , stderr = subprocess.DEVNULL
    )

    eventlet.sleep(3)
    input('Press any key when your device is in fastboot mode\n')

    pList = []
    for i in range(const_PCount):
        p = eventlet.spawn_n (sub_Proc, pMain, pSub)
        pList.append(p)
        
    t0 = time.time()
    exit_Count = 64
    working_Count = -1
    print ("Enter circle ")
    while True:        
        if working_Count < 0 and init_p.dead:
            working_Count = init_p.wait()
            print ("working_Count ", working_Count)

        try:
            r = pSub.get(block=True, timeout=5)
            if r > 0:
                recv_Count += 1
                fail_Codes.append(r)
            else:
                with open("./munlock_OK." + str(imei) + ".log", "w") as fp:
                    fp.write(r)
                print ("Find unlock code:", r)
                break
            exit_Count = 64
        except eventlet.queue.Empty:
            exit_Count -= 0
            print ("#", end="", flush=True)
            if exit_Count < 0:
                break

        if recv_Count >0 and recv_Count % 200 == 0:
            joblib.dump(fail_Codes, fail_dump_file)
            print (recv_Count, time.time() - t0, end="", flush=True)
            ctypes.windll.kernel32.SetConsoleTitleW(str(recv_Count)+" : " + str(working_Count))
            t0 = time.time()
