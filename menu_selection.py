import PySimpleGUI as sg
import os
import sys
from time import time, sleep, monotonic


import parse_text_to_speech as ptts #book parser
import audio_player as ap #audio player
import speech_selection as genie #AI genie
import light_menu as lux #Light menu
import idle_mode as id #idle mode

########################## IMPORTS ########################## 

#initial variables
menu_options = ["Choose Your Own Adventure", "The Tailored Route"] #choices to select in menu
mm_speech_command = [options.title() for options in menu_options] +  ['Exit'.title()]
adventure_lamp_title = 'The Adventure Lamp'

curr_dir = os.getcwd() #get working curr directory

'''Complete Selection Dictionary: Series, Book, Chapter'''
comp_user_select = {}
user_selec_keys = ['series', 'book', 'chapter']
user_selec_vals = []
next_selec_vals = []

is_chosen_cyoa = True #boolean in for chosen path to issue light menu 
is_nxt_chapter = False #boolean for user chosen next chapter in book, book series 

screen_size = sg.Window.get_screen_size() #get screen size
window_width = int(screen_size[0] * 0.8) # Set the desired window size as a fraction of the screen size
window_height = int(screen_size[1] * 0.8)
window_size = (window_width, window_height) 
column_width = int(screen_size[0] * 0.7)
column_height = int(screen_size[1] * 0.7)
column_size = (window_width, window_height) 

theme = 'LightPurple' #set theme
sg.theme(theme)
font_type = 'Comic'

user_name = None

########################## FIELD VARIABLES ########################## 

def restart_program():
    '''Restarts the current program'''
    python = sys.executable
    os.execl(python, python, *sys.argv)
    
def strip_event(event):
    '''Event-Key String Format Stripper'''
    return str(event).split('-')[1] #strip key to return value from selection meu

# def check_idx_within_bounds(idx, checked_list):
#     if idx < (len(checked_list) - 2):  # Check if index is within bounds of list and not the last element 
#         return True
    
#     return False 

def play_chapter(series, book, chapter, color, action, pixel_remote):
    '''Play the Chosen Selection via Audio Player'''
    ptts.mixer.init() #initialize audio player
    ptts.chapter_select(series, book, chapter) #load the complete selection into the tts algorith program
    # ptts.audio_initialize() #initialize audio controller
    ap.audio_player(color, action, pixel_remote) #go to audio player program with separate window pane

def get_series():
    '''Get the series (i.e. dir names in curr dir'''
    series = [s_names for root, dir, files in os.walk(curr_dir) for s_names in dir if 'series' in s_names.lower()] #get series 
    return series

def get_books(selected_series):
    '''Get the books given the series'''
    books_dir = os.path.join(curr_dir, selected_series) #path: curr_dir/series_dir
    books = [name.replace('.txt', '') for name in [b_names for b_names in os.listdir(books_dir) if 'txt'.lower() in b_names.lower()]]  #[[#get the txt files in sereies] remove '.txt' for display]
    return books
    
def get_book_chapters(user_selec_vals):
    '''Get the Chapters in the Book'''
    series, book = user_selec_vals[0], user_selec_vals[1]
    ptts.parse_book(series, book) 
    return ptts.chapters

########################## HELPER FUNCTIONS ########################## 
pixel_remote = lux.Pixel_Construct()

def get_light_color():
    '''Collect Light Color From User'''
    selected_light_color = lux.light_color_window(lux.light_color_selection()) 
    
    return selected_light_color #corresponding RGB colour value

def get_light_action():
    '''Collect Light Action From User'''
    selected_light_action = lux.light_action_window(lux.light_action_selection())
    return selected_light_action
########################## LIGHT FUNCTIONS ########################## 

def continue_to_next_chapter(nxt_chap):
    
    next_chap_layout = [
        [sg.VPush()], 
        [sg.Text(f"Continue to the next chapter: {nxt_chap}?", justification='center', font=(font_type,  40, 'bold'), expand_x = True, key='-series_selec_title')],
        [sg.VPush()],
        [sg.Button('Yes', key='-yes-', expand_x = True, size=(20, 10), font=(font_type, 20, 'bold'))],
        [sg.Button('Sleep', key='-sleep-', expand_x = True, size=(20, 10), font=(font_type, 20, 'bold'))],
        [sg.VPush()],
    ]
    
    return sg.Window("Continue or Sleep", next_chap_layout, size=screen_size)

def continue_to_next_chapter_window(window, timeout=(30 * 1000)): #30 second reset timer (in miliseconds)
    start_time = time()
    while True: 
        event, values = window.read(timeout=timeout)
        
        if event  == '-yes-':
            global is_nxt_chapter 
            is_nxt_chapter = True
            break
        
        if event in (sg.WIN_CLOSED, '-sleep-', '__TIMEOUT__'):
            break
        
        elapsed_time = time() - start_time
        if elapsed_time >= timeout / 1000:
            break
        
    window.close()
    
    return is_nxt_chapter
########################## CONTINUE? FUNCTIONS ########################## 


'''Choose a book series to read from'''
def series_selection(series):
    
    #make buttons for each series 
    series_buttons = [sg.Button(sery, size=(20, 10), key=f"-{sery}-", font=(font_type, 20, 'bold')) for sery in series]
    
    series_layout = [
        [sg.VPush()], 
        [sg.Text("Please select a Book Series", justification='center', font=(font_type,  40, 'bold'), expand_x = True, key='-series_selec_title')],
        [sg.VPush()],
        [sg.Column([series_buttons], scrollable = True, key='-SERIES_COLUMN-', size=column_size)], #column is 70% of screen
        [sg.VPush()],
        [sg.Button('Exit', button_color='white', key='-exit-')],
        [sg.VPush()],
    ]
    
    return sg.Window("Series Selection", series_layout, size=window_size)

def series_selec_window(series, window):
    while True: 
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, '-exit-'):
            restart_program()
        
        if event in [f"-{sery}-" for sery in series]: #if a series is selected
            selected_series = strip_event(event)
            user_selec_vals.append(selected_series)  
            
            books = get_books(user_selec_vals[0])
            
            window.close() #close out of the series window
            book_selec_window(books, book_selection(books)) #go to book selection window-pane
            
########################## SERIES SELECTION BREAK ########################## 

'''Choose a book to read from'''
def book_selection(books):
    
    #make buttons for each book
    books_buttons = [sg.Button(book, size=(20, 10), key=f"-{book}-", font=(font_type, 20, 'bold')) for book in books]
    
    book_layout = [
        [sg.VPush()],
        [sg.Text("Please select a Book", justification='center', font=(font_type,  40, 'bold'), expand_x = True, key='-book_selec_title')],
        [sg.VPush()],
        [sg.Column([books_buttons], scrollable = True, key='-BOOK_COLUMN-', size=column_size)], #column is 70% of screen
        [sg.VPush()],
        [sg.Button('Exit', button_color='white', key='-exit-')],
    ]
    
    return sg.Window("Book Selection", book_layout, size=window_size)

def book_selec_window(books, window):
    while True: 
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, '-exit-'):
            restart_program()
        
        if event in [f"-{book}-" for book in books]: #if a book is selected
            selected_book = strip_event(event) #get the selected chapter
            user_selec_vals.append(selected_book)
            
            chapters = get_book_chapters(user_selec_vals) #get book chapters
            
            window.close() #close out of the books window
            chapter_selec_window(chapters, chapter_selection(chapters)) #go to chapter selection window-pane

########################## BOOK SELECTION BREAK ########################## 

'''Choose a chapter from the chosen book to read from'''
def chapter_selection(chapters):
    
    #make buttons for each chapter
    chapter_buttons = [sg.Button(chapter, size=(20, 10), key=f"-{chapter}-", font=(font_type, 20, 'bold')) for chapter in chapters]
    
    chapter_layout = [
        [sg.VPush()],
        [sg.Text("Please select a Chapter", justification='center', font=(font_type,  40, 'bold'), expand_x = True, key='-chapter_selec_title-')],
        [sg.VPush()],
        [sg.Column([chapter_buttons], scrollable = True, key='-CHPATER_COLUMN-', size=column_size)],
        [sg.VPush()],
        [sg.Button('Exit', button_color='white', key='-exit-')],
    ]
    
    return sg.Window("Chapter Selection", chapter_layout, size=window_size)

def chapter_selec_window(chapters, window):

    while True: 
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, '-exit-'):
            restart_program()
        
        if event in [f"-{chapter}-" for chapter in chapters]: #if a book is selected, print it
            selected_chapter = strip_event(event) #get the selected chapter
            
            user_selec_vals.append(''.join(selected_chapter))  #add the chapter to the complete select dictionary's value list
           
            #create the formatted complete select dictionary of series, book, chapter
            comp_user_select = dict(zip(user_selec_keys, user_selec_vals))
            #chapter dictionary to map chapter number to chapter title
            chapter_dict = {chap_title : number+1  for number, chap_title in enumerate(chapters)}
            series, book, chapter = comp_user_select['series'], comp_user_select['book'], comp_user_select['chapter']
            
            window.close() #close out of the chapter window
            
            '''Users Continue the Option to Move to the Next Chapter or Restart the Program through Sleep Mode'''   
            for chap in chapters[chapters.index(selected_chapter): -1]: #loop through all chapters, stop before 'The End'
                
                if is_chosen_cyoa: #if on the choose your own adventure track
                    selected_light_color = get_light_color()
                    selected_light_aciton = get_light_action()
                else: 
                    selected_light_color, selected_light_aciton = lux.get_random_light_color_with_action()
                
                play_chapter(series, book, chapter_dict[chap], selected_light_color, selected_light_aciton, pixel_remote) #call audio player
                
                if chap == chapters[-2]: #if chapter is the last one in the list of chapters 
                    restart_program() #restart program
                
                global is_nxt_chapter
                is_nxt_chapter = False
                if not continue_to_next_chapter_window(continue_to_next_chapter(chapters[chapters.index(chap) + 1])): #if user stops contuing 
                    restart_program() #restart program

########################## CHAPTER SELECTION BREAK ########################## 

'''choose your own adventure window path'''
def choose_own_adv():
    
    cyoa_layout = [
        [sg.VPush()],
        [sg.Text('Welcome to Choose Your Own Adventure', justification='center', font=(font_type, 40, 'bold'), expand_x = True, key='WCYOA')],
        [sg.VPush()],
        [sg.Button('Continue on this Path', size=(40, 3), font=(font_type, 35, 'bold'), expand_x=True, key='-continue-')],
        [sg.Button('Return to Main Menu', size=(40, 3), font=(font_type, 35, 'bold'), expand_x=True, key='-Return_to_Menu-')],
        [sg.VPush()],
        [sg.Button('Exit', button_color = 'white', key='-exit-')],
    ]
    
    return sg.Window(adventure_lamp_title, cyoa_layout, size=screen_size) #modal: you can't move to another window without answering

'''choose your own adventure reading in window values '''
def cyoa_window(window):
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, '-exit-'):
            restart_program()
    
        if event == '-continue-':
            window.close()
            series = get_series()
            series_selec_window(series, series_selection(series)) #get book series
        elif event == '-Return_to_Menu-': #return to previous screen by just exiting
            window.close()
            restart_program()

########################## CREATE YOUR OWN ADVENTURE PATH ########################## 

'''choose your own adventure window path'''
def the_tailored_route():

    ttr_layout = [
        [sg.VPush()],
        [sg.Text('Welcome to The Tailored Route', justification='center', font=(font_type,  40, 'bold'), expand_x = True, key='-WTTR-')],
        [sg.VPush()],
        [sg.Button('Continue on this Path', size=(40, 3), font=(font_type, 35, 'bold'), expand_x=True, key='-continue-')],
        [sg.Button('Return to Main Menu', size=(40, 3), font=(font_type, 35, 'bold'), expand_x=True, key='-Return_to_Menu-')],
        [sg.VPush()],
        [sg.Button('Exit', button_color = 'white', key='-exit-')],
    ]
    
    return sg.Window(adventure_lamp_title, ttr_layout, size=screen_size) #modal: you can't move to another window without answering

'''tailoured route reading in window values '''
def ttr_window(window):
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, '-exit-'):
            restart_program()
        
        if event == '-continue-':
            window.close()
            series = get_series()
            series_selec_window(series, series_selection(series)) #get book series
        elif event == '-Return_to_Menu-':
            window.close()
            restart_program()
    
########################## THE TAILORED ROUTE PATH ########################## 

'''main menu shown upon program start'''
def main_menu_window():
    
    main_layout = [
        [sg.VPush()],
        [sg.Text('What Path Will You Venture?', justification='center', font=(font_type,  40, 'bold'), expand_x = True, key='-TITLE_QUESTION-')],
        [sg.VPush()],
        [sg.Button(menu_options[0], size=(40, 3), font=(font_type, 35, 'bold'), expand_x=True, key='-CYOA-')],
        [sg.VPush()],
        [sg.Button(menu_options[1], size=(40, 3), font=(font_type, 35, 'bold'), expand_x=True, key='-TTR-')],
        [sg.VPush()],
        [sg.Button('Exit', button_color = 'white', key='-EXIT_MAIN-')],
    ]
    
    return sg.Window(adventure_lamp_title, main_layout, element_justification='center', size=screen_size)

def main_menu(window):
    
    while True:  
        
        event, values = window.read()
            
        #exit main_menu
        if event in (sg.WIN_CLOSED, '-EXIT_MAIN-'):
            restart_program()
        
        if event == '-CYOA-': #if window chosen, read events and values of that window (cyoa_window) in fucntion: cyoa_window_chosen
            window.close() #close main menu
            
            cyoa_window(choose_own_adv())
        
        if event == '-TTR-': #if window chosen, read events and values of that window (ttr_window) in fucntion: ttr_window_chosen
            window.close()
            
            global is_chosen_cyoa #turn 'off' the light menu functionality if on tailored route 
            is_chosen_cyoa = False
            
            ttr_window(the_tailored_route())

########################## MAIN MENU ########################## 

def welcome_procedure_window():
    
    welcome_layout = [
        [sg.VPush()],
        [sg.Text('What is your name?', justification='center', font=(font_type,  40, 'bold'), expand_x = True, key='-name_question-')],
        [sg.InputText('', size=(30, 15), key='-name_input-')],
        [sg.VPush()],
        [sg.Button('Speak', key='-speak_name-', size=(40, 3), font=(font_type, 35, 'bold'), expand_x=True)],
        [sg.Button('Confirm', key='-confirm_name-', size=(40, 3), font=(font_type, 35, 'bold'), expand_x=True)],
        [sg.VPush()],

    ]

    return sg.Window(adventure_lamp_title, welcome_layout, element_justification='center', size=screen_size)

def welcome_procedure(window):
    global user_name
    
    while True: 
        event, values = window.read()
        
        if event == '-speak_name-':
            name = genie.get_speech_input()# get user name 
            print(f"Name is: {name}")
            window['-name_input-'].update(name)
            
        elif event == '-confirm_name-':
            user_name = values['-name_input-']
            window['-name_input-'].update('')
            print(f"Name is: {user_name}")
            
            break
            
        elif event == sg.WIN_CLOSED:
            restart_program()
            
        window.refresh()

    
def begin_story_sequence_window():
    
    blank_window_layout = [
        [sg.VPush()],
        [sg.Button('Press Start to Begin!', size=(40, 3), font=(font_type, 35, 'bold'), expand_x=True, key='-begin-')],
        [sg.VPush()],
    ]
    
    return sg.Window(adventure_lamp_title, blank_window_layout, size=screen_size)

def begin_story_sequence(window):
    
    while True: 
        event, values = window.read()
        
        if event == sg.WIN_CLOSED:
            restart_program()
        if event == '-begin-':
            window['-begin-'].Update(visible=False)
            main_menu(main_menu_window())
        else:
            sg.PopupNonBlocking('What is your name dear friend?', no_titlebar=True, auto_close=True, auto_close_duration=5)
    


# def idle_sense_window():
#     orange_yellow_color = 'orange'
    
#     idle_blank_window_layout = [
#         [sg.VPush()],
#         [sg.Button('', size=(2, 3), button_color=orange_yellow_color, key='-none-'),],
#         [sg.VPush()],
#     ]
    
#     return sg.Window("Sensing Activated", idle_blank_window_layout, size=screen_size, background_color=orange_yellow_color, no_titlebar=False)


# def idle_sense(window):
#     # Create an event to signal when idle_mode_sensing has finished
#     sensing_finished = Event()

#     while True:
#         event, values = window.read()
        
#         if event == sg.WIN_CLOSED:
#             # restart_program()
#             break
        
#         if not sensing_finished.is_set():
#             t = Thread(target=id.idle_mode_sensing, args=(sensing_finished,))
#             t.start()
#         else:
#             # idle_mode_sensing has finished, begin story telling sequence 
#             begin_story_sequence(begin_story_sequence_window())

########################## BEGIN SEQUENCE ########################## 

if __name__ == '__main__':
    
    
    #first window created 
    while True:

        start_sequence = id.idle_mode_sensing()
        if(start_sequence == True):
            start_time = monotonic()

            while True:
                lux.fill_all('orange', pixel_remote)

                if (monotonic() - start_time > 7):
                    lux.fill_all('black', pixel_remote)
                    break
            
            # welcome_procedure(welcome_procedure_window())
            begin_story_sequence(begin_story_sequence_window())