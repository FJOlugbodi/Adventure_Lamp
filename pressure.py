import board
import busio
import adafruit_lps2x
import time

i2c = busio.I2C(board.SCL, board.SDA)
sensor = lps = adafruit_lps2x.LPS22(i2c)

DELTA = 2.0

def hpa_to_pascal(hpa):
    pascal = hpa * 100
    return pascal

def celsius_to_fahrenheit(celsius):
    fahrenheit = (celsius * 9/5) + 32
    return fahrenheit

def check_delta_temp():
    temp = celsius_to_fahrenheit(lps.temperature)
    while True:
        new_temp = celsius_to_fahrenheit(lps.temperature)
        if new_temp >= temp + DELTA: #true if user blows above threshold
            return True
        temp = celsius_to_fahrenheit(lps.temperature)
        time.sleep(2)


if __name__ == '__main__':

    temp = lps.temperature
    while True:
        # print(f"Pressure: {hpa_to_pascal(lps.pressure):.2f} Pa ")
        print(f"Temperature: {celsius_to_fahrenheit(temp):.2f} F")

        new_temp = lps.temperature
        if new_temp >= temp + DELTA: 
            print("Nice blow")
        temp = lps.temperature
        time.sleep(2)