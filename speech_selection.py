import speech_recognition as sr
import pyttsx3
import difflib
import time 
from threading import Thread, Timer
# import pygame
# from pygame.locals import MOUSEBUTTONDOWN, FINGERDOWN

# Initialize the recognizer
r = sr.Recognizer()
#initialize mic
# mic = sr.Microphone() #will need to seet microphone on RPi
mic_index = 0
mic = sr.Microphone(device_index=mic_index)
#initialize test-to-speech engine
engine = pyttsx3.init()
#initialize pygame module
# pygame.init ()

max_time = 7 #seconds to listen from microphone
    
#initialization of speaking rate
engine.setProperty('rate', 110) 

def genie_speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 110) 
    engine.say(text)
    engine.startLoop(False)
    engine.iterate()
    engine.endLoop()
    
    # Stop audio after #.0 seconds
    t = Timer(6.0, engine.stop)
    t.start()
    

# Define a function to get user input using speech
def get_speech_input():


    with mic as source:
        # print("Say your selection:")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    assert audio is not None
    try:
        text = r.recognize_google(audio)
        return text.upper() #turn into title formatted string
    except sr.WaitTimeoutError:
        print("Timeout! No speech detected after 10 seconds.")
        return ""
    except sr.UnknownValueError:
        genie_speak("Sorry, I didn't understand that.")
        return ""
    except sr.RequestError as e:
        genie_speak("Could not request results from Google Speech Recognition service; {0}".format(e))
        return ""

def match_speech(menu): 
    start_time = time.time()
    best_match = None 
    best_score = 0 #best score so far

    # Get user input using speech or touch-screen
    while True:
        if (time.time() - start_time) > max_time:
            return "NO CHOICE" #break while loop
        
        user_input = get_speech_input()
            
        
        #find best match of user's speech input to menu choice
        for choice in menu:
            score =  difflib.SequenceMatcher(None, user_input, choice).ratio() #find score
            
            if score > best_score: 
                best_match = choice  #update best matched item
                best_score = score #update best score 

        if best_match is None:
            genie_speak(f"Sorry, {user_input} is not a valid selection. Please try again.")
            # counter += 1 #increment chances'.
            start_time = time.time() #reset start time 
            
        else:
            genie_speak(f"You have selected: {best_match}.")
            print("Word Heard: {word}\n".format(word = user_input.title()))
            return best_match #best_matched menu choice and break while loop

# def test_input(timeout=4):
#     '''
#     Listens for touchscreen input by checking for a MOUSEBUTTONDOWN event in pygame.
#     If no touchscreen input is detected within the specified timeout period (in seconds),
#     then returns 'voice'.
#     '''
    
#     start_time = time.time()
#     while (time.time() - start_time) < timeout:
#         for gotten_event in pygame.event.get():
#             if gotten_event.type == FINGERDOWN:# or pygame.MOUSEBUTTONDOWN:
#                 return 'touchscreen'
#     return 'voice'

if __name__ == '__main__':
    get_speech_input()