#!/usr/local/bin/python

import RPi.GPIO as GPIO
from time import sleep, time

# Set GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set GPIO pins for ultrasonic sensor
PIN_TRIGGER = 15
PIN_ECHO = 24
#Photoresistor Pin
PIN_PHT_RES = 23


# Set GPIO direction Ultrasonic Sensor
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)


def find_distance():
    sleep(1) #seconds between sensing

    GPIO.output(PIN_TRIGGER, GPIO.HIGH) #trigger to send out us wave
    sleep(0.00001) #wait time 10us
    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    pulse_start = time()
    while GPIO.input(PIN_ECHO)==0: #object detected?
        pulse_start = time()

    pulse_end = time()
    while GPIO.input(PIN_ECHO)==1: #object not detected?
        pulse_end = time()

    pulse_duration = pulse_end - pulse_start 
    distance = round(pulse_duration * 17150, 2)

    # print(f"Ditance sensed: {distance} cm")
    
    return distance

def resistor_sense(PIN_PHT_RES):
    '''
    function measures the time it takes for the capacitor to charge through the photoresistor
    which is proportional to the resistance of the photoresistor
    '''
    count = 0
  
    #Output on the pin for 
    GPIO.setup(PIN_PHT_RES, GPIO.OUT)
    GPIO.output(PIN_PHT_RES, GPIO.LOW)
    sleep(0.1) #wait 100 milliseconds to allow capacitor to discharge

    #Change the pin back to input
    GPIO.setup(PIN_PHT_RES, GPIO.IN)
  
    #Count time until the pin goes high - when the capacitor is charged enough to trigger the pin
    while (GPIO.input(PIN_PHT_RES) == GPIO.LOW):
        count += 1

    print(f"Photo Resistance: {count}")

    return count


# def idle_mode_sensing():
#    #Catch when script is interrupted, cleanup correctly
#     try:
#         GPIO.setup(PIN_LED, GPIO.OUT, initial=GPIO.LOW) #for LED

#         while True:
#             photo_res_val = resistor_sense(PIN_PHT_RES)
#             ultra_sense_distance = find_distance()
            
#             # find_distance()
#             sleep(0.01)
#             if photo_res_val > 5000 or ultra_sense_distance < 30:
#                 GPIO.output(PIN_LED, GPIO.HIGH)

#                 sleep(2) #buffer for LED to signal human detection

#                 print("Human Detected, Exit Idle Mode")
#                 break
#             else:
#                 GPIO.output(PIN_LED, GPIO.LOW) 
        
#     except Exception as e:
#         print(f"Error: {e}")
#         pass
#     except KeyboardInterrupt as keyE:
#         pass
#     finally:
#         GPIO.cleanup() #clean up GPIO 

def idle_mode_sensing():
    #Catch when script is interrupted, cleanup correctly
    try:

        while True:

            photo_res_val = resistor_sense(PIN_PHT_RES)
            ultra_sense_distance = find_distance()
            
            # find_distance()
            sleep(0.01)
            if photo_res_val > 30000 or ultra_sense_distance < 30:

                sleep(2) #buffer for LED to signal human detection

                print("Human Detected, Exit Idle Mode")
                break
        
    except Exception as e:
        print(f"Error: {e}")
        pass
    except KeyboardInterrupt as keyE:
        pass
    finally:
        GPIO.cleanup() #clean up GPIO 
    
    return True


if __name__ == '__main__':
    # idle_mode_sensing()
    while True:
        # find_distance()
        resistor_sense(PIN_PHT_RES)