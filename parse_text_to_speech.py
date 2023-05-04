import os
from gtts import gTTS #AI reader
from pygame import mixer #music controller
import re #for regex --> removing weird and special characters from sentences 

'''By this method, once the story has been selected, sotry is automoatically downloaded as a mp3 file to be replayed as told by AI TTS'''

curr_directory = os.getcwd()

#Book Name
book_name = ''
chapters = []

audio_file = '' # will populate later after choosing story
story_time_length = None #time in min of story


# mixer.init() #initialize mixer to for use 
audio_controller = mixer.music 

def get_prerecordings():
    stories = [story for root, dirs, files in os.walk([folder for root, dirs, files in os.walk(curr_directory) for folder in dirs if 'Record' in folder][0]) for story in files] #get series 
    print("\nStories:", stories, end='\n')
    return stories

def audio_duration():
    global story_time_length
    
    try: 
        total_sec_length = mixer.Sound(audio_file).get_length() * 1000 #get the length of audio file in integer seconds
        story_time_length = total_sec_length / (1000 * 60)
        print("\nTOTAL LEGNTH OF AUDIO FILE: {length}\n\n".format(length= total_sec_length))
        return total_sec_length
    except Exception as e:
        print("Failed to get length of audio file: {aud_file}.".format(aud_file = audio_file), "\nError: {error}".format(error=e))

def load_audio(audio_file): 
    #intitial playing when audio_controller isn't busy
    audio_controller.load(audio_file)
    
def text_convert_play(text):
    # try to convert the text to speech
    try:
        print("\n\n File Name: ", audio_file, end='\n')
        record_dir_name = audio_file.strip('Recordings/')
        if record_dir_name in get_prerecordings(): #if the story has already been parsed, load instead of having to resave
            print("\n\tFile Found Pre-Loaded\n")
            load_audio(audio_file) #load audio to be played 
        else: 
            tts = gTTS(text=text, lang='en') #generate the ai to say the words 
            tts.save(audio_file) #save the spoken speeech to a file 
            load_audio(audio_file) #load audio to be played 
    except Exception as e:
        print("Failed to convert the text to speech.", "\nError: {error}".format(error=e))


def get_dir_list(curr_dir):
    return os.listdir(curr_dir)

def get_books():
    folders = [folder for root, dirs, files in os.walk(curr_directory) for folder in dirs]
    # print('Folders in Dir: ', folders)
    return folders
    
def get_series(chosen_series):
    book = [story for story in get_books() if chosen_series.lower() in story.lower()]
    
    if len(book) == 0:
        print("no series found")
    
    return book[0] #return the story --> directory containing book txt files 

def get_book(chosen_series, chosen_book): #from the chosen book, display all the txt files 
    series_folder = get_series(chosen_series)
    pwd_series = os.path.join(curr_directory, series_folder)
    # books = [file for root, dirs, files in os.walk(pwd_series) for file in files if '.txt' in file]
    books = [file for file in get_dir_list(pwd_series) if '.txt' in file]
    
    try: 
        found_book = [book for book in books if chosen_book.lower() in book.lower()] #if the chosen book key word is in the series
        # print('Book:', found_book)
        global book_name 
        book_name = found_book[0].split('.')[0] #get the name of the book with out file type (eg. 'txt')
    
        if len(found_book) == 0: 
            print("no book found")
    
        return os.path.join(series_folder, found_book[0])  #where to find book text file
    except Exception as e: 
        print("Exception error: {error}".format(error = e))

def parse_book(chosen_series, chosen_book):
    chapter_sections = []
    book_path = get_book(chosen_series, chosen_book) #get the book given the series and the book to be read
    
    #chapter arithmetic
    with open(book_path) as story: 
        get_chapters = [line.split() for line in story if "chapter".lower() in line.lower()]
        chapters_refs = [' '.join(chapter_pair) for chapter_pair in get_chapters if 'chapter'.lower() in chapter_pair[0].lower()] + ["THE END"]
        global chapters
        chapters = chapters_refs
        # print('Chapters:', chapters)
        
    #separate text by chapters
    with open(book_path) as full_story:
        entire_story = full_story.read()
        for i in range(len(chapters) - 1):
            j = i + 1
            findex = entire_story.find(chapters[i])
            rindex = entire_story.find(chapters[j])
            chapter_sections.append([entire_story[findex : rindex]])

        # print(chapter_sections[1])
        # print("Chapter Sections:", chapter_sections[1])
    return chapter_sections

def clean_chapter_selected(text):
    #remove special and unwanted characters from text, like escape sequnces and non alphanumeric words but keep periods and puntuation standards
    pattern = re.compile('[^A-Za-z0-9,.!\'\"\n\t]') 
    text = pattern.sub(' ', text) #separate all remove characters with ' '
    text = text.replace('\xad', '')
    text = text.strip("\n").strip("\xad")
    
    #convert text to audio to be told
    text_convert_play(text)
    
    return text
        
def chapter_select(chosen_series, chosen_book, chapter_picked):
    all_chapters = parse_book(chosen_series, chosen_book)
    
    global audio_file
    audio_file =  'Recordings/' + chosen_book + '_' + str(chapter_picked) + ".mp3" #save file with specific format in Recordings Directory
    
    if chapter_picked <= (len(all_chapters) + 1): # + 1 accounts for zero index
        return clean_chapter_selected(str(all_chapters[chapter_picked - 1])) #account for zero index & and do some replacing for speaking
    else:
        print("no chapter found")
  
        

# talk_ai(chapter_select(4, 'pot', 'gob'))

# talk_ai(chapter_select(1, 'clancy', 'patriot'))