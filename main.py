import tkinter
import os
import urllib.request
import re
import pygame
import requests
from PIL import ImageTk, Image
from io import BytesIO
import re
import unicodedata
import yt_dlp
from tkinter import DoubleVar, Label, messagebox, Toplevel
from mttkinter import mtTkinter
from tkinter import font as tkFont 
from tkmacosx import Button
from RangeSlider.RangeSlider import RangeSliderH
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
from dataclasses import dataclass
import ast
from pathlib import Path
import shutil
import random


@dataclass
class Song:
    name: str
    artists: list
    duration: int

def maxOccurrenceCounter(stringList, targetString=None, dict=None, artistName=None):
    maxOccurences = 0
    occurences = 0

    print(stringList)

    if dict != None:
        for item in dict:
            for artist in item["artists"]:
                if onlyLetters(artist["name"], False) == onlyLetters(artistName, False):
                    occurences = occurrenceCounter(stringList, item["name"])
            if  occurences >  maxOccurences:
                maxOccurences = occurences
    else:
        for s in stringList:
            print("t - " + targetString)
            occurences = occurrenceCounter(s.lower().split(" "), targetString)
            if  occurences >  maxOccurences:
                maxOccurences = occurences

    print("max = " + str(maxOccurences))
    return maxOccurences

def occurrenceCounter(stringList, targetString):
    nameString = onlyLetters(targetString, False)
    s = re.sub(r'[^A-Za-z0-9 ]+', '', targetString)
    print(s)
    if "" in stringList:
        stringList.remove('')
    print(nameString)
    count = 0

    for index in range(len(stringList)):
        there = True
        tempCount = 1
        word = stringList[index]
        if word in nameString:
            if word in s.lower():
                while there and (index + tempCount) < len(stringList):
                    words = word + stringList[index + tempCount]
                    if words in nameString:
                        print(words)
                        count += tempCount * 3
                        print("count is " + str(count))
                        tempCount += 1
                    else:
                        there = False
                        count += 2

            else:
                count += 1
    
    print("count=" + str(count))
    return count

def removeBrackets(s):
    s = re.sub("[\(\[].*?[\)\]]", "", s)
    if s.endswith(" "):
        s = s[:-1]
    return s

def createImage(filepath, width, height):
    i = Image.open(filepath)
    i = i.resize((width, height), Image.ANTIALIAS)
    i = ImageTk.PhotoImage(image=i)

    return i

def isascii(s):
    return len(s) == len(s.encode())

def onlyLetters(s, removeAccents):
    if not removeAccents:
        s = ''.join(filter(str.isalnum, s))
        s = s.lower()
    
    s = ''.join(c for c in unicodedata.normalize('NFD', s)if unicodedata.category(c) != 'Mn')

    return s

def createScale(i):
    hVar1 = DoubleVar() 
    hVar2 = DoubleVar() 

    image = Image.new("RGB", (13, 13), "#2C2831")
    scale = RangeSliderH(canvas, [hVar1, hVar2], show_value=False, Height=59, padX=-1, bgColor="#2C2831", imageR=ImageTk.PhotoImage(image=image), imageL=i, auto=False, line_color="#8D0BC4", line_s_color="#E0F1F1") 

    return scale

def getArtistString(artistArray):
    print(type(artistArray))
    if isinstance(artistArray, str):
        artistArray = ast.literal_eval(artistArray)
        print(artistArray)

    artistString = ", ".join(artistArray)
    print(artistString)
    return artistString

def getSongOffline(name, artist):
    print("n=" + name)
    print("A=" + artist)
    with open("playlists/" + playlist + "/songInfo.csv", "r") as f:
        reader = csv.reader(f)
        song = Song("", [], 0)
        for row in reader:
            if name == row[0] and artist in row[1]:
                song = Song(row[0], row[1], int(row[2]))
                return song.name, song.artists, song.duration
        
        return "", [], 0

def getInfo(nameOfSong, nameOfArtist):
    artists = [nameOfArtist]
    clientID = 'a0204459710a44eab9eab570df2c8ff7'
    clientSecret = '43e264f0c7d24a989031f1646ff11b84'
    try:
        client_credentials_manager = SpotifyClientCredentials(client_id=clientID, client_secret=clientSecret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        responseJson = sp.search(q=nameOfSong + " " + artists[0], limit=15)

    except:
        print("NO Internet")
        return "", "Song Not Found", [""], [], False
    else:

        items = responseJson["tracks"]["items"]
        found = False
        list = nameOfSong.lower().split(' ')
        maxOccurences = maxOccurrenceCounter(stringList=list, dict=items, artistName=nameOfArtist)
        occurrences = 0
        print(str(maxOccurences))

        for item in items:  
            occurrences = occurrenceCounter(nameOfSong.lower().split(' '), item["name"])
            if found:
                artists.pop(0)
                return thumbnail, name, artists, genres, True
            else:
                artists = [nameOfArtist]
                for artist in item["album"]["artists"]:
                    if onlyLetters(artist["name"], False) == onlyLetters(artists[0], False) and isascii(onlyLetters(item["name"], False)):
                        print("occ " + str(occurrences))
                        if occurrences == maxOccurences:
                            valid = True
                        else: 
                            valid = False
                        
                        if valid:
                            print("YAY- album")
                            found = True
                            thumbnail = item["album"]["images"][0]["url"]
                            name = item["name"]
                            artistGenres = sp.artist(item["album"]["artists"][0]["external_urls"]["spotify"])
                            print(artistGenres["name"])
                            genres = artistGenres["genres"]
                            print(genres)
                            for songArtist in item["artists"]:
                                print(songArtist["name"])
                                artists.append(songArtist["name"])

        for item in items:
            print(item["name"])
            occurrences = occurrenceCounter(nameOfSong.lower().split(' '), item["name"])
            if found:
                artists.pop(0)
                return thumbnail, name, artists, genres, True
            else:
                artists = [nameOfArtist]
                for songArtist in item["artists"]:
                    print(songArtist["name"])
                    artists.append(songArtist["name"])
                    if onlyLetters(songArtist["name"], False) == onlyLetters(artists[0], False) and isascii(onlyLetters(item["name"], False)):
                        if occurrences == maxOccurences:
                            valid = True
                        else: 
                            valid = False
                        
                        if valid:
                            found = True
                            print("YAY - artist")
                            found = True
                            artistGenres = sp.artist(item["artists"][0]["external_urls"]["spotify"])
                            print(artistGenres)
                            print(artistGenres["name"])
                            genres = artistGenres["genres"]
                            print(genres)
                            thumbnail = item["album"]["images"][0]["url"]
                            name = item["name"]
        
        print("YARRRR")
        return "", "Song Not Found", ["Artist Not Found - Please Double Check Spelling"], [], True

def getSong(name, artists, genres):
    global pos
    global playlist

    print("POS IS - " + str(pos))

    with open("playlists/" + playlist + "/songInfo.csv", "r") as inp, open("playlists/" + playlist + '/tempSongInfo.csv', 'a') as out:
        writer = csv.writer(out)
        for row in csv.reader(inp):
            if pos == 0 and row != [] and name == row[0] and artists[0] in row[1]:
                    duration = int(row[2])
                    mins = duration // 60
                    secs = duration % 60
                    os.remove("playlists/" + playlist + "/tempSongInfo.csv")
                    return mins, secs
            elif pos > 0:
                if row[0] != name:
                    writer.writerow(row)
                
    if pos > 0:
        os.remove("playlists/" + playlist + "/songs/" + removeBrackets(name) + ".mp3")
        os.remove("playlists/" + playlist + "/songInfo.csv")
        os.rename("playlists/" + playlist + "/tempSongInfo.csv", "/songInfo.csv")
    else:
        os.remove("playlists/" + playlist + "/tempSongInfo.csv")


    newName = onlyLetters(name, True)
    dashName = newName.replace(" ", "-")
    newArtist = onlyLetters(artists[0], True)
    dashArtist = newArtist.replace(" ", "-")

    print(genres)
    if "classical" in genres:
        appendix = ""
    else:
        appendix = "-lyrics"
    searchTerm = dashName + "-" + dashArtist+ "-" + appendix
        
    print(searchTerm)
    searchUrl = "https://www.youtube.com/results?search_query=" + searchTerm
    searchUrl = searchUrl.replace("&", "and")
    html = urllib.request.urlopen(searchUrl)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    songUrl = "https://www.youtube.com/watch?v="

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': "playlists/" + playlist + '/songs/' + removeBrackets(name),

    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        
        print(songUrl + str(video_ids[pos]))
        info = ydl.extract_info(songUrl + video_ids[pos], download=True)
        duration = info["duration"]
        minutes = duration // 60
        seconds = duration % 60

    f = open("playlists/" + playlist + '/songInfo.csv', "r")
    i = sum(1 for _ in csv.reader(f))

    with open("playlists/" + playlist + '/songInfo.csv', 'a') as f:
        writer = csv.writer(f)
        artistArray = []
        if i == 0:
            headers = ["SONG NAME", "ARTISTS", "DURATION"]
            writer.writerow(headers)

        for artist in artists:
            artistArray.append(artist)
        data =  [name, artistArray, str(duration)]
        writer.writerow(data)
   
    return minutes, seconds

def playSong(title, tempMins, tempSecs, tempDuration, image, songArray):
    global paused
    global scale
    global fastforward
    global reverse
    global reverse
    global mouseY
    global mouseX
    global timeAfterFinish
    global changePos
    global songIndex
    global shuffle
    global repeat

    print("HEY")

    alreadyPaused = False
    alreadyUnpaused = True
    mins = tempMins
    secs = tempSecs
    duration = tempDuration
    songIndex = 0
    pastSongs = [0]
    startTime = time.time()
    print("TIME - " + str(startTime))
    inc = 1

    for song in songArray:
        print(title)
        print(song.name)
        if song.name == title:
            songIndex = songArray.index(song)

    print("DURATION -" + str(duration))
    
    pygame.mixer.init()

    while title != "":
        pos = -1

        pygame.mixer.music.load("playlists/" + playlist + "/songs/" + removeBrackets(songArray[songIndex].name) + ".mp3")
        pygame.mixer.music.play()
        duration = mins*60+secs
        while (pygame.mixer.music.get_busy() or scale.winfo_x() < 320 or paused) and not fastforward and not reverse:
            if paused:
                if not alreadyPaused:
                    pygame.mixer.music.pause()
                    alreadyPaused = True
                    alreadyUnpaused = False
                else:
                    root.update()                
            elif not paused:
                pos += 1
                xCoord = (pos/duration) * 293 + 30
                print(pos)

                if not alreadyUnpaused:
                    pygame.mixer.music.unpause()
                    alreadyPaused = False
                    alreadyUnpaused = True
                elif changePos:
                    print("YOOOOOO")
                    print("mouseX is + " + str(mouseX))
                    pos = mouseX/293 * duration 
                    print("POS IS - " + str(pos + (1/13 * duration)))
                    pygame.mixer.music.rewind()
                    pygame.mixer.music.set_pos(pos + (1/13 * duration))
                    pygame.mixer.music.unpause()
                    updateScale(image, xCoord, pos, duration)
                    changePos = False
                else:
                    updateScale(image, xCoord, pos, duration)
                    if secs > 0:
                        secs -= 1
                    elif mins > 0:
                        mins -= 1
                        secs = 59
            # time.sleep(0.75)  
            currentTime = time.time()
            while currentTime < startTime + (inc + 5/duration):
                currentTime = round(time.time())
                time.sleep(0.1)
            inc += 1
    
            # print("TIME IS " + str(currentTime))

            pygame.time.Clock().tick(10)
        
        

        if shuffle:
            print("SHUFFFFlLLLLEEEEE")
            songIndex = random.randint(0, len(songArray) - 1)
            while songIndex in pastSongs:
                songIndex = random.randint(0, len(songArray) - 1)
            pastSongs.append(songIndex)
        elif not repeat:
            if reverse and songIndex != 0:
                songIndex -= 1
                reverse = False
            else:
                songIndex += 1
            if songIndex == len(songArray):
              songIndex = 0
        if reverse:
            reverse = False


        print("SONG INDEX IS " + str(songIndex))
        
        scale.destroy()
        artists = ast.literal_eval(songArray[songIndex].artists)
        _, mins, secs = setupUI(songArray[songIndex].name, artists[0])
        fastforward = False

    
    root.mainloop()

def updateScale(img, x, pos, duration):
    global scale 
    global timeAfterFinish
    global newPlaylist

    if not newPlaylist:
        var1 = DoubleVar()
        var2 = DoubleVar()
        image = Image.new("RGB", (13, 13), "#2C2831")
        mins = int(pos // 60)
        secs = int(pos % 60)
        if mins * 60 + secs <= duration:
            if secs < 10:
                secsString = "0" + str(secs)
            else:
                secsString = str(secs)

            timeString = str(mins) + ":" + secsString
            timeLabel.config(text=timeString)
            timeLeft = duration - (mins*60+secs)
            minsLeft = timeLeft // 60
            secsLeft = timeLeft % 60
            if secsLeft < 10:
                secsString = "0" + str(secsLeft)
            else:
                secsString = str(secsLeft)
            timeString2 = str(minsLeft) + ":" + secsString

            if len(timeString2) >= 5:
                timeLabel2.place(x=258, y=5)
            timeLabel2.config(text=timeString2)

        if x <= 335:
            scale.destroy()
            scale = RangeSliderH(canvas, [var1, var2], show_value=False, Height=59, bgColor="#2C2831", padX=-1, imageR=ImageTk.PhotoImage(image=image), imageL=img, auto=False, line_s_color="#E0F1F1") 
            scale.place(x=x, y=460)

        print("X=" + str(x))
        timeToFinish = duration - ((x - 30)/293 * duration)
        print(timeToFinish)
    
    else:
        scale.place(x=30, y=460)
        timeLabel.config(text="0:00")
        timeLabel2.config(text="0:00")



    root.update()

def textEnter(event):
    text = event.widget.get()
    if text == 'Name of Playlist' or text == "Song Name" or text == "Artist Name":
        event.widget.delete(0, "end")

    return None

def getFiles():
    songArray = []
    global playlist

    f = open("playlists/" + playlist + "/songInfo.csv", "r")
    reader = csv.reader(f)
    for row in reader:
        if row != [] and "SONG NAME" not in row:
            songArray.append(Song(row[0], row[1], int(row[2])))
    return songArray

def add(entry, window, label, button):
    text = entry.get()
    if len(text) > 20 or len(text) < 1:
        label.configure(text="Name must be between 1 and 20 characters")
    elif os.path.exists("playlists/"+text):
        label.configure(text="Playlist with this name already exists")
    else:
        button["state"] = "disabled"
        os.mkdir("playlists/"+text)
        with open("playlists/"+text+"/songInfo.csv", "w") as f:
            writer = csv.writer(f)
            headers = ["SONG NAME", "ARTISTS", "DURATION"]
            writer.writerow(headers)    
        os.mkdir("playlists/"+text+"/songs")
        window.destroy()
        playlistChooser()

def pause(self):
    global paused
    print("OK")
    if paused:
        print("unpausing")
        canvas4.itemconfig(playButton, image=images[0])
        paused = False
    else:
        print("pausing")
        canvas4.itemconfig(playButton, image=images[1])
        paused = True

def fastForward(self):
    global fastforward
    fastforward = True
    print("fast forwarding")

def rewind(self):
    global reverse
    reverse = True
    print("reversing")

def shuffling(self):
    global shuffle
    global repeat

    if shuffle:
        canvas4.itemconfig(shuffleButton, image=images[12])
        print("not shuffling")
        shuffle = False
    else:
        canvas4.itemconfig(shuffleButton, image=images[9])
        print("shuffling")
        shuffle = True
        repeat = False
        canvas4.itemconfig(repeatButton, image=images[11])


def repeating(self):
    global repeat
    global shuffle

    if repeat:
        canvas4.itemconfig(repeatButton, image=images[11])
        print("Not repeating")
        repeat = False
    else:
        canvas4.itemconfig(repeatButton, image=images[10])
        print("Repeating")
        repeat = True
        shuffle = False
        canvas4.itemconfig(shuffleButton, image=images[12])


def menu(event, addID, deleteID):    
    global hidden

    if hidden:
        menuCanvas.itemconfigure(addID, state='normal')
        menuCanvas.itemconfigure(deleteID, state='normal')
        hidden = False
    else:
        menuCanvas.itemconfigure(addID, state='hidden')
        menuCanvas.itemconfigure(deleteID, state='hidden')
        hidden = True


def addSong(e1, e2, win, label):
    global songArray
    global newPlaylist

    songName = e1.get()
    artistName = e2.get()
    mins, secs = 0, 0

    _, realSongName, artistNames, genres, internet = getInfo(songName, artistName)

    if artistNames[0] != "Artist Not Found - Please Double Check Spelling" and internet:
        label.config(text="Success")
        newPlaylist = False
        mins, secs = getSong(realSongName, artistNames, genres)
        duration = mins*60+secs
        songArray = getFiles()
        win.destroy()
        songPlayer.lift()
        setupUI(songName, artistName)
        playSong(realSongName, mins, secs, duration, image2, songArray)
    elif not internet:
        label.config(text="Error-No Internet")
    else:
        label.config(text="Song Not Found - Please check spelling")
    
    win.destroy()
    songPlayer.lift()




def addSongClicked(event, a, d):
    global hidden
    
    b, entry, entry2, label, top = getInputs("Add New Song")
    entry2.place(x=30, y=130)
    b.config(command=lambda e=entry, e2=entry2, win=top, l=label: addSong(e, e2, win, l))

    entry.insert(0, "Song Name")
    entry.bind("<Button-1>", textEnter)

    entry2.insert(0, "Artist Name")
    entry2.bind("<Button-1>", textEnter)

    menuCanvas.itemconfigure(a, state='hidden')
    menuCanvas.itemconfigure(d, state='hidden')
    hidden = True


def deletePlaylist(event, playlistArray, buttonsArray):
    itemId = event.widget.find_withtag('current')[0]
    i = buttonsArray.index(itemId)
    # playlistArray[i].destroy()
    for button in playlistArray:
        button.destroy()
    shutil.rmtree("playlists/" + playlistArray[i].cget("text"))
    playlistChooser()

def deleteSong(event, a, d):
    global songArray
    global hidden

    songName = songArray[songIndex].name
    duration = songArray[songIndex].duration

    os.remove("playlists/" + playlist + "/songs/" + removeBrackets(songName) + ".mp3")
    with open("playlists/" + playlist + "/songInfo.csv", "r") as inp, open("playlists/" + playlist + '/tempSongInfo.csv', 'w') as out:
        writer = csv.writer(out)
        for row in csv.reader(inp):
            if songName != row[0] and str(duration) != row[2]:
                writer.writerow(row)
    
    os.remove("playlists/" + playlist + "/songInfo.csv")
    os.rename("playlists/" + playlist + "/tempSongInfo.csv", "playlists/" + playlist + "/songInfo.csv")

    songArray = getFiles()
    menuCanvas.itemconfigure(a, state='hidden')
    menuCanvas.itemconfigure(d, state='hidden')
    hidden = True


def getInputs(text,):
    top = Toplevel(songPlayer)
    top.title(text)
    c = tkinter.Canvas(top, highlightthickness=0, width=373, height=300, bg="black")
    c.pack()

    c.create_image(186, 150, image=background3)

    label = tkinter.Label(c, text="", font="Ubuntu 13 normal", bg="#2C2831", fg="#E0F1F1")
    label.place(x=30, y=150)

    entry = tkinter.Entry(c, width=17, bg="#2C2831", bd=1, font="Ubuntu 25 bold", highlightbackground="#E0F1F1", fg="#E0F1F1")
    entry.place(x=30, y=70)

    entry2 = tkinter.Entry(c, width=17, bg="#2C2831", bd=1, font="Ubuntu 25 bold", highlightbackground="#E0F1F1", fg="#E0F1F1")

    font = tkFont.Font(family='Ubuntu', size=25, weight='bold')

    b = Button(c, text="Add", bg="#8D0BC4", width=150, height=40, fg="#E0F1F1", highlightbackground="#2C2831")
    b.config(command=lambda e=entry, win=top, l=label, button=b: add(e, win, l, button))
    b['font'] = font
    b.place(x=122, y=190)

    return b, entry, entry2, label, top


def addPlaylist(self):
    _, entry, _, _, _ = getInputs("Add New Playlist")
    entry.insert(0, "Name of Playlist")
    entry.bind("<Button-1>", textEnter)

def onClick(event):
    global mouseY
    global mouseX
    global changePos

    print("x=" + str(event.x))
    print("y=" + str(event.y))

    if event.y > 487 and event.y < 497 and event.x > 30 and event.x < 335:
        print("Clicked")
        mouseX = ((event.x - 30) / 305) * 293
        changePos = True

def setupScale():
    image2 = createImage("images/slidercircle.png", 13, 13)
    scale = createScale(image2)
    canvas2 = tkinter.Canvas(songPlayer, highlightthickness=0, width=50, height=56, bg="#2C2831")
    canvas2.place(x=335, y=460)

    return scale, image2

def setupUI(songName, artistName):
    global thumbnailImage
    global background
    global songLabel
    global artistLabel
    global pos 

    realSongName = ""
    mins = 0
    secs = 0
    pos = 0
    internet = True
    genres = []
    url = ""

    #GET SONG INFO
    if (songName and artistName) == "":
        realSongName = "Add a song..."
        artistNames = ["...To start jamming to some tunes"]
        timeLabel.config(text="0:00")
        timeLabel2.config(text="0:00")
        scale.place(x=30, y=460)
    else:
        url, realSongName, artistNames, genres, internet = getInfo(songName, artistName)


    #PERFORM RELEVANT FUNCTION DEPENDING ON PRESENCE OF INTERNET CONNECTION
    if artistNames[0] != "Artist Not Found - Please Double Check Spelling" and internet and artistName != "":
        mins, secs = getSong(realSongName, artistNames, genres)
    elif not internet:
        print("nice")
        realSongName, artistNames, duration = getSongOffline(songName, artistName)
        print(realSongName)
        mins = duration // 60
        secs = duration % 60
    elif realSongName != "Add a song...":
        print("RISHI MB")
        realSongName = "Song Not Found"


    #CREATE THUMBNAIL IMAGE
    if url == "":
        thumbnailImage = createImage("images/musicNote.png", 256, 256)
    else:
        response = requests.get(url)
        thumbnailImage = createImage(BytesIO(response.content), 256, 256)
    canvas.create_image(185.5, 181, image=thumbnailImage)


    #CREATE BACKGROUND IMAGE
    print("BACKGROUND")
    canvas.create_image(185, 337, image=background)


    #DETERMINE CORRECT FORMATTING FOR SONG AND ARTIST LABELS
    if len(realSongName) >= 29 and len(realSongName) < 36:
        font = "Ubuntu 23 bold"
        yPos = 394
        increment = 36
    elif len(realSongName) >= 22 and len(realSongName) < 29:
        font = "Ubuntu 23 bold"
        yPos = 377
        increment = 32
    elif len(realSongName) >= 36 and len(realSongName) < 70:
        font = "Ubuntu 20 bold"
        yPos = 390
        increment = 42
    elif len(realSongName) >= 70:
        font = "Ubuntu 18 bold"
        yPos = 396
        increment = 54
    else:
        font = "Ubuntu 27 bold"
        yPos = 380
        increment = 30
    artistString = getArtistString(artistNames)


    #CREATE SONG NAME LABEL
    songLabel.config(text=realSongName, font=font)
    songLabel.place(x=186.5, y=yPos, anchor="center")


    #CREATE ARTIST NAME LABEL
    if len(artistString) > 50:
        increment += 10
    artistLabel.config(text=artistString)
    artistLabel.place(x=186.5, y=yPos + increment, anchor="center")


    #CREATE PROGRESS LINE
    canvas.create_line(30, 490, 350, 490, fill="#8D0BC4", width=5)


    return realSongName, mins, secs

def setupButtonsAndTimeLabel():
    global playButton
    global timeLabel
    global timeLabel2

    playButton = canvas4.create_image(132, 35, image=images[0])
    forwardButton = canvas4.create_image(197, 35, image=images[2])
    backwardButton = canvas4.create_image(67, 35, image=images[3])
    menuButton = menuCanvas.create_image(30,10, image=images[8])
    addButton = menuCanvas.create_image(105, 10, image=images[6])
    deleteButton = menuCanvas.create_image(180, 10, image=images[7])
    shuffleButton = canvas4.create_image(15, 35, image=images[12])
    repeatButton = canvas4.create_image(249, 35, image=images[11])


    menuCanvas.itemconfigure(addButton, state='hidden')
    menuCanvas.itemconfigure(deleteButton, state='hidden')
    # refreshButton = menuCanvas.create_image(30,7, image=images[8])
    
    canvas4.tag_bind(playButton, "<Button-1>", pause)
    canvas4.tag_bind(forwardButton, "<Button-1>", fastForward)
    canvas4.tag_bind(backwardButton, "<Button-1>", rewind)
    canvas4.tag_bind(shuffleButton, "<Button-1>", shuffling)
    canvas4.tag_bind(repeatButton, "<Button-1>", repeating)
    menuCanvas.tag_bind(menuButton, "<Button-1>", lambda event, a=addButton, d=deleteButton: menu(event, a, d))
    menuCanvas.tag_bind(addButton, "<Button-1>", lambda event, a=addButton, d=deleteButton: addSongClicked(event, a, d))
    menuCanvas.tag_bind(deleteButton, "<Button-1>", lambda event, a=addButton, d=deleteButton: deleteSong(event, a, d))

    canvas3 = tkinter.Canvas(songPlayer, highlightthickness=0, width=305, height=40, bg="#2C2831")
    canvas3.place(x=30, y=500)
    timeLabel = tkinter.Label(canvas3, text="0:00", bg="#2C2831", fg="#E0F1F1")
    timeLabel.place(x=0, y=5)
    timeLabel2 = tkinter.Label(canvas3, text="0:00", bg="#2C2831", fg="#E0F1F1")
    timeLabel2.place(x=270, y=5)

    return playButton, shuffleButton, repeatButton, timeLabel, timeLabel2

def playlistChooser():

    buttons = []
    deleteButtons = []
    # for i in buttons:
    #     playlistCanvas.delete(i)

    playlistNames = []

    playlistCanvas.create_image(186, 337, image=background2)
    label = Label(playlistCanvas, text="Playlists", font = "Ubuntu 35 bold", bg="#2C2831", fg="#E0F1F1")
    label.place(x=120, y=60)

    addCanvas = tkinter.Canvas(root, width=40, height=40, highlightthickness=0, bg="#2C2831")
    addCanvas.place(x=320, y=10)

    addButton = addCanvas.create_image(20, 20, image=images[6])
    addCanvas.tag_bind(addButton, "<Button-1>", addPlaylist)

    yPos=160
    i = 0
    paths = sorted(Path("playlists").iterdir())
    print(paths)
    for path in paths:
        print("p - " + str(path).replace("playlists/", ""))
        playlistNames.append(str(path).replace("playlists/", ""))

    font = tkFont.Font(family='Ubuntu', size=17, weight='bold')

    for name in playlistNames:
        # numSongs = len(os.listdir("playlists/" + name + "/songs"))
        button = Button(playlistCanvas, font=font, highlightcolor="white",bg="#E0F1F1", highlightbackground="#2C2831", activebackground="#8D0BC4", text=name, width=333, height=40, fg="#2C2831")
        buttons.append(button)
        button.config(command=lambda index = i, array=playlistNames, buttonArray=buttons:  getPlaylist(index, array, buttonArray))
        button.place(x=0.5,y=yPos)
        btn = playlistCanvas.create_image(355, yPos + 20, image=images[7])
        playlistCanvas.tag_bind(btn, "<Button-1>", lambda event, array=buttons, buttonArray=deleteButtons: deletePlaylist(event, array, buttonArray))
        deleteButtons.append(btn)
        yPos += 50
        i += 1

    for widget in root.winfo_children():
        if '!toplevel' in str(widget): 
            return 
       
    songPlayer = Toplevel(root)
    songPlayer.title("Song Player")
    songPlayer.overrideredirect(True) 
    return songPlayer

def getPlaylist(index, array, buttonArray):
    global root 
    global songPlayer
    global playlist
    global songArray
    global newPlaylist

    playlist = array[index]
    songPlayer.geometry("373x672")
    songPlayer.resizable(False, False)
    songPlayer.lift()

    for i in range(len(buttonArray)):
        if i == index:
            buttonArray[index].config(bg="#B751C6", fg="white")
        elif buttonArray[i].cget('bg') != "#E0F1F1":
            buttonArray[i].config(bg="#E0F1F1", fg="black")
    
    if os.listdir("playlists/" + playlist + "/songs") != []:
        newPlaylist = False
        for filename in os.listdir("playlists/" + playlist):
            if filename == "songInfo.csv":
                with open("playlists/" + playlist + "/songInfo.csv", "r") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if "SONG" not in row[0]:
                            name = row[0]
                            artists = row[1]
                            artists = ast.literal_eval(artists)
                            print(name)
                            print(artists)
                            title, mins, secs = setupUI(name, artists[0])
                            duration = mins*60+secs
                            songArray = getFiles()
                            playSong(title, mins, secs, duration, image2, songArray)
    else:
       artist = ""
       song = ""
       setupUI(song, artist)
       if pygame.mixer.music.get_busy(): 
            pygame.mixer.music.stop()
            newPlaylist = True
        

# Main Program
root=tkinter.Tk(mt_debug=1)

hidden = True
paused = False
fastforward = False
shuffle = False
repeat = False
changePos = False
reverse = False
thumbnailImage = ""
images = [createImage("images/pause.png", 50, 50), createImage("images/play.png", 50, 50), createImage("images/forward.png", 40, 30), createImage("images/backward.png", 40, 30), createImage("images/refresh.png", 20, 20), createImage("images/musicNote.png", 256, 256), createImage("images/add.png", 20, 20), createImage("images/delete.png", 20, 20), createImage("images/menu.png", 20, 20), createImage("images/shuffle.png", 30, 26), createImage("images/repeat.png", 30, 26), createImage("images/repeatClicked.png", 30, 26), createImage("images/shuffleClicked.png", 30, 26)]
background = createImage("images/backgroundTransparent.png", 373, 670)
background2 = createImage("images/background2.png", 373, 673)
background3 = createImage("images/background3.png", 373, 300)
songIndex = 0
newPlaylist = False

root.title("Playlists")
root.resizable(False, False)
playlistCanvas = tkinter.Canvas(root, width=373, height=672, highlightthickness=0)
playlistCanvas.pack()


playlist = ""
songArray = []

mouseY = 0
mouseX = 0
pos = 0
timeAfterFinish = 0

songPlayer = playlistChooser()

songPlayer.bind("<Button-1>", onClick)

canvas = tkinter.Canvas(songPlayer, bg="black", width=373, height=672, highlightthickness=0)
canvas.pack()

canvas4 = tkinter.Canvas(songPlayer, highlightthickness=0, width=300, height=65, bg="#2C2831")
canvas4.place(x=53, y=530)

menuCanvas = tkinter.Canvas(songPlayer, highlightthickness=0, width=193, height=20, bg="#2C2831")
menuCanvas.place(x=83, y=5)

songLabel = tkinter.Message(songPlayer, text="Song", background="#2C2831", fg="#E0F1F1", font="Ubuntu 35 bold", justify="left", width=335)
songLabel.place(x=186.5, y=395, anchor="center")

artistLabel = tkinter.Message(songPlayer, text="Artist", background="#2C2831", fg="#8F8297", width=350, justify="left")
artistLabel.place(x=186.5, y=435, anchor="center")

timeLabel = tkinter.Label()
timeLabel2 = tkinter.Label()
playButton = tkinter.Button()


scale, image2 = setupScale()
scale.place(x=30, y=460)
scale.lower()

canvas.create_image(185.5, 181, image=images[5])
canvas.create_image(186, 337, image=background)

playButton, shuffleButton, repeatButton, timeLabel, timeLabel2 = setupButtonsAndTimeLabel()

root.mainloop()


# def test():
#     with open("testData.csv") as f:
#         reader = csv.reader(f)
#         for row in reader:
#             print(row[0])
#             songname, artistname = row[0], row[1]
#             _, song, artists, genres, _ = getInfo(songname, artistname)
#             getSong(song, artists[0], genres)
# test()


#TODO
