from io import BytesIO #IO capabilities --> buffer wirtes, etc.
from PIL import Image #picture
from threading import Thread, Event
from time import sleep
import PySimpleGUI as sg #GUI
import base64 #picture encode/decode

import parse_text_to_speech as ptts
import light_menu as lux
import pressure as pr
import menu_selection as menu


#pause and play images
def base64_image_import(path):
    image = Image.open(path) #get image
    image = image.resize((40, 40)) #resize image then remove background
    buffer = BytesIO() #get buffer to retranslate image to PNG
    image.save(buffer, format='PNG') #write image as PNG to ram
    b64 = base64.b64encode(buffer.getvalue())
    return b64


def player_window():
    
    book_name = ptts.audio_file.strip('Recordings/').strip('.mp3').replace('_', ': ')

    #play tab
    play_layout = [
        [sg.VPush()],
        [sg.Push(), sg.Text(book_name, text_color = 'white', key='-TITLE-'), sg.Push()],
        [sg.VPush()],
        [
            sg.VPush(),
            sg.Button(image_data=base64_image_import('Audio_Button_Pictures/play.png'), border_width=0, key='-PLAY-'),
            sg.Push(),
            sg.Button(image_data=base64_image_import('Audio_Button_Pictures/pause.png'), border_width=0, key='-PAUSE-'), 
            sg.Push(),
            sg.Button(image_data=base64_image_import('Audio_Button_Pictures/stop.png'), border_width=0, key='-STOP-'),
            sg.Push(),
        ],
        [sg.VPush()],
        [sg.Push(), sg.Text('- AUDIO PLAYER -', key='-STATUS-'), sg.Push()],
                ]

    #volume tab
    volume_layout = [
        [sg.VPush()],
        [sg.Push(), sg.Slider(range=(0, 100), orientation = 'horizontal', default_value=50, resolution = 0.5, key='-VOLUME-'), sg.Push()],
        [sg.VPush()]
                ]

    layout = [
        [sg.TabGroup(
            [[sg.Tab('Play', play_layout), 
            sg.Tab('Volume', volume_layout)]]
        )]
        ]

    return sg.Window('The Adventure Lamp Story Genie', layout)
    
def player(window, color, action_func, pixel_remote):
    isPaused = False

    # Define a function to run the action function in a separate thread
    def run_action_func():
        while not action_thread_stop.is_set():
            action_func(color, pixel_remote)

    def run_temp_read_func():
        while not temp_read_stop.is_set():
            if pr.check_delta_temp():
                temp_event.set()

    # Start the thread to run the action function
    action_thread_stop = Event()
    temp_read_stop = Event()
    temp_event = Event()

    action_thread = Thread(target=run_action_func)
    temp_read_thread = Thread(target=run_temp_read_func)

    action_thread.start()
    temp_read_thread.start()




    while True: 
        event, values = window.read(timeout = 1)
                    
        if event == sg.WIN_CLOSED:
            break

        # Handle events using a switch statement
        switcher = {
            '-PLAY-': lambda: ptts.audio_controller.unpause() if isPaused else ptts.audio_controller.play(),
            '-PAUSE-': ptts.audio_controller.pause, #pause_and_set_paused,
            '-STOP-': ptts.audio_controller.stop,
        }
        func = switcher.get(event, lambda: None)
        if func:
            func()
            
            # Update isPaused flag based on audio controller state
            isPaused = ptts.audio_controller.get_pos() > 0 and not ptts.audio_controller.get_busy()

        # Set volume if it has changed
        set_volume = round(float(values['-VOLUME-'] / 100), 2)
        if set_volume != ptts.audio_controller.get_volume():
            ptts.audio_controller.set_volume(set_volume)

        # Wait for temperature threshold to be reached
        if temp_event.wait(timeout=0.1):
            # Do something when temperature threshold is reached
            print("Temperature threshold reached!")
            temp_event.clear()
            menu.restart_program()
            
        
    # Stop the action thread and wait for it to finish
    sleep(5)
    action_thread_stop.set()
    temp_read_stop.set()

    action_thread.join()
    temp_read_thread.join()

    # Close resources before exiting
    ptts.mixer.quit()
    window.close()

def audio_player(color, action, pixel_remote):
    action_func = lux.get_action(action.capitalize())

    player(player_window(), color, action_func, pixel_remote)

    lux.fill_all('black', pixel_remote)

    
    # if __name__ == '__main__':
    #     audio_player()