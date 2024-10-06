# Sketch 
# Classes : MusicLibrary, MusicStore, FileStore, Application
# MusicLibrary:
#   store, location, print, find, remove, add
# Songs:
#   title, artist, year, 
# 
# MusicStore:
#   Songs[], crunch_up, crunch_down, find, remove, add
# 
# FileStore:
#   location, readfile, writefile, 
#   
# Application:
#   start, stop, read_input, write_output, evaluate_command, 

import json
import os
import sys

class Song:
    
    def __init__(self, title=None, artist=None, year=None):
        self._title = title
        self._artist = artist
        self._year = year
    
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
    
    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, artist):
        self._artist = artist
    
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        self._year = year
    
    def to_tuple(self):
        return (self._title, self._artist, self._year)
    
    
class MusicStore:
    def __init__(self, songs=[]):
        self._songs = songs
    
    @property
    def songs(self):
        return self._songs

    def find_idx_of_song_with_name(self, title):
        low, high, title = 0, len(self._songs), title.lower()
        while low < high:
            mid = (low + high) // 2
            m_title = self._songs[mid].title.lower()
            if m_title == title:
                return True, mid
            if m_title < title:
                low = mid + 1
            else:
                high = mid
        return False, low

    def remove_song_by_title(self, title):
        status, index = self.find_idx_of_song_with_name(title)
        if status == False:
            return False, "Song doesn't exist"
        else:
            self.crunch_up_from_idx(index)
            self._songs.pop()
            return True, "Song Deleted Successfully"

    def add_song(self, new_song):
        status, index = self.find_idx_of_song_with_name(new_song.title)
        if status == True:
            return False, "Song Already Exists"
        else:
            self.crunch_down_from_idx(index)
            self._songs[index] = new_song
            return True, "Song Added Successfully"
        
    def crunch_up_from_idx(self, idx):
        songs_len = len(self._songs)
        for i in range(idx, songs_len-1):
            self._songs[i] = self._songs[i+1]              
            

    def crunch_down_from_idx(self, idx):
        songs_len = len(self._songs)
        self._songs.append("")
        for i in range(songs_len-1, idx-1, -1):
            self._songs[i+1] = self._songs[i]  
    
# MusicLibrary:
#   store, location, print, find, remove, add

class MusicLibrary:

    def __init__(self, name=None) -> None:
        if name is not None:
            self._name = name
            self._store = self.load_library()
            # self._store.add_song(Song("Zest", "Ved", "2024"))
            # print(self._store.remove_song_by_title("Last Last"))
            # print(self.print_library())
            # print(self.find_song("As It Ws"))
            # self.save_library()


    @property
    def name(self):
        return self._name
    
    @property
    def store(self):
        return self._store

    def load_library(self):
        if FileStore.does_file_exist(self._name) == True:
            store = MusicStore(FileStore.read_file(self._name))
            if store == False:
                Application.write_op("Library could not be loaded")
        else:
            FileStore.write_file([], self._name)
            store = MusicStore()
        return store
    
    def save_library(self):
        content = [f"{song.to_tuple()}" for song in self._store.songs]
        response = f"Writing library to disk.\n"
        if FileStore.write_file(content, self.name) == True:
            response += f"Library written to disk successfully.\n"         
        return response

    def add_song(self):
        title = Application.read_cmd("Enter Song Title")
        artist = Application.read_cmd("Enter Song Artist")
        year = Application.read_cmd("Enter Song Year")
        song = Song(title, artist, year)
        status, message = self._store.add_song(song)
        return f"Operation was {status} : {message}"
    
    def remove_song(self):
        title = Application.read_cmd("Enter Song Title")
        status, message = self._store.remove_song_by_title(title)
        return f"Operation was {status} : {message}"

    def print_library(self):
        response = ""
        if len(self._store.songs) > 0:
            response = self._format_songs()
        else:
            response += f"No songs in library."
        return response

    def _format_songs(self, response="", fsong=None):
        response = f"| Title: {'': <13} | Artist: {'': <12} | Year Published: | \n"
        response += f'{"-" * len(response)} \n'
        if fsong != None:
            response += f"| {fsong.title : <20} | {fsong.artist : <20} | {fsong.year : <15} | \n"
            return response
        for song in self._store.songs:
            response += f"| {song.title : <20} | {song.artist : <20} | {song.year : <15} | \n"
        return response
        
    def find_song(self):
        title = Application.read_cmd("Enter Song Title")
        status, index = self._store.find_idx_of_song_with_name(title)
        if status == False:
            return f"Song not found in library."
        return f"Song Found. \n\n" + self._format_songs(fsong=self._store.songs[index])


class FileStore:
    def __init__(self):
        pass
    
    @staticmethod
    def write_file(content, filename):
        try:
            with open(filename, 'w') as file:
                json.dump(content, file, indent=4)
                return True
        except Exception as e:
            Application.write_op(e)
            return False
    
    @staticmethod
    def read_file(filename):
        try:
            with open(filename, 'r') as file:
                data = [Song(*eval(tuple)) for tuple in json.load(file)]
                return data
        except FileNotFoundError:
            FileStore.writeFile(None, filename)
        except json.JSONDecodeError:
            Application.write_op("File Corrupted")
        return False

    @staticmethod
    def does_file_exist(filename):
        if os.path.exists(filename):
            return True
        return False

class Application:

    def __init__(self, library_name):
        self._log = None
        self._logFile = None
        self._music_library = MusicLibrary(library_name)

        self._commands = {
            'q': self.stop,
            'i': self._music_library.add_song,
            'p': self._music_library.print_library,
            'd': self._music_library.remove_song,
            'l': self._music_library.find_song,
            'h': self.show_message
        }

    def show_message(self):
        return f'''
        Usage:
        i, I    Insert a new song
        d, D    Delete a song
        l, L    Lookup a song
        p, P    Print library songs
        q, Q    Quit library
        h, H    Show this help
        '''

    def start(self):
        print("Starting Music Library")
        self.write_op(self.show_message())
        while True:
            cmd = self.read_cmd("Enter Command").lower()
            response = self.evaluate_cmd(cmd)
            self.write_op(response)
            if cmd == 'q':
                break

    def stop(self):
        response = self._music_library.save_library()
        response += f"Exiting Application."
        return response
    
    @staticmethod
    def read_cmd(text):
        return input(f"{text}: ").strip()

    def write_op(self, text):
        print(f"\n{text.strip()}\n")

    def evaluate_cmd(self, cmd):
        return self._commands.get(cmd, lambda: "Unknown command.")()


def main():
    app = Application(sys.argv[1])
    # FileStore.write_file(['(Hello, World)', '(Testing)'], sys.argv[1])
    # data = FileStore.read_file(sys.argv[1])
    # print(type(data), data)
    # check = []
    # a = Song("SOme", "Ved", 2024)
    # check.append(a)
    # print(a)
    app.start()

if __name__ == '__main__':
    main()