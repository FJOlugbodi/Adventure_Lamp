import PySimpleGUI as sg #GUI
from math import sqrt
import random 
from time import sleep, monotonic
import board
import neopixel 
import pandas as pd



#global variables 
colors_list = [
    'red', 'green', 'blue', 'yellow', 'orange', 'purple',
    'pink', 'turquoise', 'lime', 'cyan', 'magenta', 'lavender',
    'brown', 'tan', 'olive', 'navy', 'teal', 'Dark Sea Green',
    'gold', 'silver', 'black', 'white', 'gray', 'beige',
    'dark red', 'dark green', 'dark blue', 'Misty Rose', 'dark orange', 'thistle',
    'light Pink', 'aquamarine', 'blue violet', 'light cyan', 'Lime Green', 'Medium Violet Red',
]#36 usable colors as buttoncolors 

colors_dict = {
    'red': (255, 0, 0),
    'green': (0, 128, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'turquoise': (64, 224, 208),
    'lime': (0, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'lavender': (230, 230, 250),
    'brown': (165, 42, 42),
    'tan': (210, 180, 140),
    'olive': (128, 128, 0),
    'navy': (0, 0, 128),
    'teal': (0, 128, 128),
    'dark sea green': (143, 188, 143),
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gray': (128, 128, 128),
    'beige': (245, 245, 220),
    'dark red': (139, 0, 0),
    'dark green': (0, 100, 0),
    'dark blue': (0, 0, 139),
    'misty rose': (255, 228, 225),
    'dark orange': (255, 140, 0),
    'thistle': (216, 191, 216),
    'light pink': (255, 182, 193),
    'aquamarine': (127, 255, 212),
    'blue violet': (138, 43, 226),
    'light cyan': (224, 255, 255),
    'lime green': (50, 205, 50),
    'medium violet red': (199, 21, 133)
}


N_matrix_length = int(sqrt(len(colors_list))) #matrix size n in nxn
#color DataFrame
color_list_df = pd.DataFrame([colors_list[i:i+6] for i in range(0, len(colors_list), N_matrix_length)], columns=[i for i in range(N_matrix_length)])

light_actions_list = ['Blink', 'Shimmer', 'Comet']

button_size = (15, 2) #size of each button in the df

button_color = None
button_action = None

# NeoPixel Setup
PIXEL_PIN = board.D18
PIXEL_NUM = 60
PIXEL_COLOR_ORDER = neopixel.GRB

def Pixel_Construct():
    return neopixel.NeoPixel(PIXEL_PIN, PIXEL_NUM, brightness=0.8, auto_write=False, pixel_order=PIXEL_COLOR_ORDER)

def solid_blink_action(RGB_color, pixel_remote, num_blinks=3, blink_delay=0.5):
    """Blink effect on NeoPixel LED strip."""

    for i in range(num_blinks):
        pixel_remote.fill(RGB_color)
        pixel_remote.show()
        sleep(blink_delay)
        pixel_remote.fill(get_RGB('black'))
        pixel_remote.show()
        sleep(blink_delay)

def fill_all(RGB_color, pixel_remote):
    pixel_remote.fill(get_RGB(RGB_color))
    pixel_remote.show()

def multicolor_blink_action(RGB_colors, pixel_remote):
    for color in RGB_colors:
        pixel_remote.fill(color)
        pixel_remote.show()
        sleep(0.1) #100ms

'''Func. Adpted from ChatGPT'''
comet_length = 10 #length of commet
comet_speed = 2 #position on strip
comet_position = 0
def comet_action(comet_color, pixel_remote): 
    global comet_position # Use the global comet_position variable
    global comet_speed # Use the global comet_speed variable
    global comet_length # Use the global comet_length variable

    # Update the position of the comet
    comet_position += comet_speed
    if comet_position >= PIXEL_NUM + comet_length: #reset position
        comet_position = 0
    
    # Update the colors and brightness of the LED strip
    for i in range(PIXEL_NUM):
        pixel_position = (i - comet_position) % PIXEL_NUM #pixel psoition relative to comet position
        brightness = max(0, (comet_length - pixel_position) / float(comet_length))
        color = tuple(int(brightness * c) for c in comet_color)
        pixel_remote[i] = color
    
    # Display the updated LED strip
    pixel_remote.show()
    sleep(0.05)

'''Func. Adpted from ChatGPT'''
def shimmer_action(shimmer_color, pixel_remote, speed=0.1, density=0.5):
    """Shimmer effect on NeoPixel LED strip."""
    for i in range(PIXEL_NUM):
        if random.random() <= density:
            pixel_remote[i] = tuple(int(c * (random.random() * 0.5 + 0.5)) for c in shimmer_color)
        else:
            pixel_remote[i] = get_RGB('black')
    pixel_remote.show()
    sleep(speed)

def get_action(button_action):
   # use a switch statement to return the corresponding action function
    switcher = {
        'Blink': solid_blink_action,
        'Shimmer': shimmer_action,
        'Comet': comet_action
    }
    
    # get the corresponding function based on the button action
    action_function = switcher.get(button_action)
    
    return action_function


def light_color_selection():
    
    color_layout = [
        
        [sg.Button(color_list_df.iloc[i, j].capitalize(), button_color=color_list_df.iloc[i, j], key=f"-{color_list_df.iloc[i, j].upper()}-", pad=(0,0), size=button_size) for i in range(color_list_df.shape[0])] for j in range(color_list_df.shape[1])
        
    ]
    
    return sg.Window("Light Color Selection", color_layout, modal = True)

def light_color_window(window):
    global button_color

    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED:
            break
        if event in [f"-{color.upper()}-" for color in colors_list]:
            color = str(event).split('-')[1] # Get the color of the button and exit 
            button_color = get_RGB(color)
            break

    # Close the window
    window.close()
    
    return button_color

def get_RGB(color_choice):
    return colors_dict[color_choice.lower()]

def get_random_light_color_with_action():
    random_light_color = random.choice(colors_list)
    rgb_color = get_RGB(random_light_color)
    random_light_action = random.choice(light_actions_list)

    # action_func = get_action(random_light_action)
    
    return rgb_color, random_light_action

def light_action_selection():
    
    action_layout = [
        
        [sg.VPush()],
        [sg.Button(action.capitalize(), key=f"-{action.upper()}-", size=button_size, pad=(4, 2)) for action in light_actions_list],
        [sg.VPush()]
    
    ]
    
    return sg.Window("Light Action Selection", action_layout, modal = True)

def light_action_window(window):
    global button_action
    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED:
            break
        if event in [f"-{action.upper()}-" for action in light_actions_list]:
            button_action = str(event).split('-')[1] # Get the color of the button and exit 
            break
        
    window.close() #close window

    # action_func = get_action(button_action)

    return button_action
    

if __name__ == '__main__':
    pixel_remote = Pixel_Construct()

    # comet_action(get_RGB('purple'), pixel_remote)
    # while True:
        # comet_action(get_RGB('purple'), pixel_remote)
        # solid_blink_action(get_RGB('red'), pixel_remote)
    while True:
        pixel_remote.fill(get_RGB('black')) 
        pixel_remote.show()

    # start_time = monotonic()
    # while monotonic() - start_time < 20):
    #     fill_all('orange', pixel_remote)
   
        
    
    
    

