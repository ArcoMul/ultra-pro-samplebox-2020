import sys
import RPi.GPIO as GPIO
import time
import audio
from gpiozero import LED, Button
from threading import Timer
from signal import pause

is_pressed_twice = False
last_button = 0
last_reset = 0
should_exit = False

#happens when a button is pressed, checks for a second press within 0.3 seconds
def button_press(button, id):
        global is_pressed_twice
        print("BUTTON INTERACTION START: " + str(id))
        is_pressed_twice = False
        button.when_pressed = lambda button : pressed_twice(button, id)
        button.when_released = lambda button : when_released(button, id)
        button.when_held = lambda button : when_held(button, id)
        # Timer(0.3, evaluate_pressed_once,[button, id]).start()
        # Timer(1, evaluate_is_held,[button, id]).start()
        if should_exit:
            print("EXIIIIT1")
            sys.exit()

# when a button is pressed twice it's starting a recording
def pressed_twice(button, i):
        global is_pressed_twice
        is_pressed_twice = True
        button.when_pressed = lambda button : button_press(button, i)
        button.when_released = None
        print("pressed twice")
        on_press_twice(button, i)

def when_released(button, i):
        print("when_released")
        Timer(0.2, evaluate_pressed_once, [button, i]).start()

def when_held(button, i):
        print("when_held")
        button.when_pressed = lambda button : button_press(button, i)
        button.when_released = None
        if button.is_held == True:
                on_held_button(button, i)
        

def evaluate_pressed_once(button, i):
        print("evaluate_pressed_once")
        global is_pressed_twice
        global last_button

        if (is_pressed_twice):
            print("button is pressed twice, don't register as once")
            return

        button.when_pressed = lambda button : button_press(button, i)
        button.when_released = None
        last_button = i
        on_press_once(button, i)

def on_press_twice(button, i):
        global beats
        if mode == "edit":
                # In edit mode add a beat only to the second part of the beat section
                if beat_edit in beats[i-1+4]:
                        beats[i-1+4].remove(beat_edit)
                else:
                        beats[i-1+4].append(beat_edit)
                print("pressed twice")
                render_leds()
                print(beats)
        else:
                # In play mode record a sample on this button
                audio.record_sample(i)

def on_press_once(button, id):
        if (id == "play"):
                play(button, 0)
        else:
                if mode == "edit":
                        # In edit mode add the beat which is being edited
                        # into the beats array, both in the first 4 beats
                        # and as well in the second 4 beats
                        if beat_edit in beats[id-1] and beat_edit in beats[id-1+4]:
                                beats[id-1].remove(beat_edit)
                                beats[id-1+4].remove(beat_edit)
                        elif beat_edit in beats[id-1]:
                                beats[id-1].remove(beat_edit)
                        else:
                                beats[id-1].append(beat_edit)
                                beats[id-1+4].append(beat_edit)
                        render_leds()
                        print(beats)
                else:
                        audio.play_sample(id)

def on_held_button(button, id):
        global mode
        global beat_edit
        global last_reset
        global should_exit
        if (id == "play"):
                # When resetting twice in a row, exit the application
                print(time.time() - last_reset)
                if (last_reset != 0 and time.time() - last_reset < 5):
                        print("exit")
                        should_exit = True
                        return
                # Otherwise reset
                reset()
                last_reset = time.time()
                audio.beep()
                print("reset")
        else:
                # Go into edit mode of this button
                mode = "edit"
                beat_edit = id
                audio.click()
                for led in leds:
                    led.blink(0.5, 0.5, 1)
                render_leds()
                print("enter edit")

# Assigns a number to each sample
def assign_button(button, i):
        button.when_pressed = lambda button : button_press(button, i)

def repeat_sample(last_button):
        audio.play_sample(last_button)

def play(button, beat):
        global mode
        if mode == "edit":
                mode = "default"
                audio.click()
                render_leds()
                print("exit edit mode")
        elif mode == "play":
                mode = "default"
        else:
                mode = "play"
                run(beat)

def run(beat):
        global beats
        global last_time
        global mode
        if mode != "play":
            for led in leds:
                led.off()
            return
        # play all the samples registered to this beat
        for i in beats[beat]:
                audio.play_sample(i)
                current_time = time.time()
                print(str(current_time - last_time))
                last_time = time.time()
        # turn on the led which is on this beat
        led_count = 0
        for led in leds:
            if led_count == beat % 4:
                led.on()
            else:
                led.off()
            led_count+=1
        # prepare for next beat
        beat += 1
        if beat == 8:
                beat = 0
        Timer(0.25, run, [beat]).start()

def reset():
        global beats
        beats = [[], [], [], [], [], [], [], []]
        print("reset beats: " + str(beats))

def render_leds():
        index = 0
        if mode == "edit":
                for led in leds:
                        if (beat_edit in beats[index] and beat_edit in beats[index + 4]):
                                led.on()
                        elif beat_edit in beats[index] or beat_edit in beats[index + 4]:
                                led.blink(0.3, 0.3)
                        else:
                                led.off()
                        index += 1
                        if (index == 4):
                                break
        else:
                for led in leds:
                        led.off()

print("Let's play some music")

# set up the button definitions
sample_1 = Button(15)
sample_2 = Button(17)
sample_3 = Button(11)
sample_4 = Button(10)
play_button = Button(2)


leds = [
        LED(3),
        LED(27),
        LED(22),
        LED(9)
]

beats = [[], [], [], [], [], [], [], []]
last_time = 0
mode = "default"
beat_edit = -1

buttons = {
        1: sample_1,
        2: sample_2,
        3: sample_3,
        4: sample_4,
        "play": play_button
}
for id in buttons:
        assign_button(buttons[id], id)

# message = input("Press enter to quit\n\n") # Run until someone presses enter

audio.start()

pause()

