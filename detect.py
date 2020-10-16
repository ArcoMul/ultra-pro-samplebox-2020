import pyaudio
po = pyaudio.PyAudio()
for index in range(po.get_device_count()): 
    desc = po.get_device_info_by_index(index)
    print("DEVICE: " + str(desc["name"]) + " INDEX:  "+str(index)+ " RATE:  " + str(desc["defaultSampleRate"]))
