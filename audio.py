import pyaudio
import pygame.mixer
import wave
import threading
import queue 
import time;

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)

samples = [
        pygame.mixer.Sound("sample1.wav"),
        pygame.mixer.Sound("sample2.wav"),
        pygame.mixer.Sound("sample3.wav"),
        pygame.mixer.Sound("sample4.wav")
]

beep_sound = pygame.mixer.Sound("beep.wav")
beep_sound.set_volume(0.3)

click_sound = pygame.mixer.Sound("click.wav")
click_sound.set_volume(0.5)

start_sound = pygame.mixer.Sound("start.wav")

audio_format = pyaudio.paInt16 # 16-bit resolution
audio_channels = 1 # 1 channel
audio_samplerate = 44100 # 44.1kHz sampling rate
audio_chunksize = 4096 # 2^12 samples for buffer
audio_device_index = 0 # device index found by p.get_device_info_by_index(ii)
audio_seconds = 1

# create pyaudio instantiation
audio = pyaudio.PyAudio()


def record_sample(n):
    global samples

    print("Start recording sample " + str(n))
    frames = []

    # Beep to show start of recording
    beep()

    # create pyaudio stream
    stream_in = audio.open(format = audio_format,rate = audio_samplerate,channels = audio_channels, \
                                input_device_index = audio_device_index,input = True, \
                                                    frames_per_buffer=audio_chunksize)

    # Wait for a bit because recording is starting and beep is playing
    time.sleep(0.4)

    # Record
    for ii in range(0,int((audio_samplerate/audio_chunksize)*audio_seconds)):
        data = stream_in.read(audio_chunksize, exception_on_overflow = False)
        frames.append(data)

    # Beep to show end of recording
    print("Stop recording sample " + str(n))
    beep()

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream_in.stop_stream()
    stream_in.close()

    # save the audio frames as .wav file
    wf = wave.open("sample" + str(n) + ".wav",'wb')
    wf.setnchannels(audio_channels)
    wf.setsampwidth(audio.get_sample_size(audio_format))
    wf.setframerate(audio_samplerate)
    wf.writeframes(b''.join(frames))
    wf.close()

    # samples[n-1] = pygame.mixer.Sound(b''.join(frames))
    samples[n-1] = pygame.mixer.Sound("sample" + str(n) + ".wav")

def play_sample(n):
    print("play sample " + str(n))
    samples[n-1].play()

def beep():
    beep_sound.play()

def click():
    click_sound.play()

def start():
    start_sound.play()
