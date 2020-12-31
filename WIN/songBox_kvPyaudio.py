
# -*- coding:utf-8 -*-
#kivy.require("1.19.1")
from kivy import Config
Config.set("graphics", "multisamples", "0")
from kivy.app import App
#from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.graphics import *
from kivy.graphics import Color#, Ellipse, Line, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.button import ButtonBehavior
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager#, WipeTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.scatter import Scatter
#import urllib.request
import os, sys
import time
import random
import threading
#from queue import Queue
#from multiprocessing import Process
#from multiprocessing.pool import ThreadPool
#import multiprocessing
#from queue import Queue
#import subprocess
#import signal
#from pygame import mixer
import pyaudio
import wave

import playsound as pls
from gtts import gTTS
import speech_recognition as sr

import fourth_circle as circle
import youtb_converterWAV as yc
import songBox_playerPyaudio as sbp
import songBox_userlist as sbu
import songBox_list as sbl
import songBox_singerlist as sbs
import songBox_voice as sbv

global workingDir,baseDir,mp3Dir,dataDir,userListDir,ignoreFile, winColor, boxColor,textColor,stopColor
baseDir = os.getcwd()#os.path.abspath('py_song')#workging 폴더
mp3Dir = os.path.join(baseDir, "songBox_list")#노래 폴더
fontDir = os.path.join(baseDir, "songBox_font")#글자 폴더
imgDir = os.path.join(baseDir, "songBox_img")#그림 폴더
dataDir = os.path.join(mp3Dir, "0_file_data")#데이터목록 csv 저장폴더
userListDir = os.path.join(mp3Dir, "1_dir_userlist")#userlist 폴더ttsDir = os.path.join(mp3Dir, "2_tts")#tts 폴더
singerListDir = os.path.join(mp3Dir, "2_dir_singerlist")#userlist 폴더
ttsDir = os.path.join(mp3Dir, "3_tts")#tts 폴더
ignoreFile = ['ffmpeg','youtube-dl.exe','.DS_Store','list_data','0_file_data','1_dir_userlist','2_dir_singerlist','3_tts']#dir 안에 존재해야만하는 파일 but mp3 아닌 파일 목록
print(f"baseDir:{baseDir}\nmp3Dir:{mp3Dir}\ndataDir:{dataDir}\nuserListDir:{userListDir}")
winColor =[211/255, 211/255, 211/255, 1]#[189/255,183/255,110/255,1]#[211/255,211/255,211/255,1]#
boxColor = [188/255, 143/255, 143/255, 1]#[110/255,0/255,0/255,1]#[105/255,105/255,105/255,1]#
textColor = [255/255, 255/255, 255/255, 1]
stopColor = [105/255,105/255,105/255,1]#gold[189/255,183/255,110/255,1]#red[110/255,0/255,0/255,1]

bartextColor =[189/255,183/255,110/255,1]#deepblue+green[30/255,160/255,180/255,1]#grey[105/255,105/255,105/255,1]#red[110/255,0/255,0/255,1]

soundbar_fontsize="22sp"
menu_fontsize="20sp"
text_fontsize="17sp"
todayFont = f'{fontDir}/NanumPen.otf'

FIXROW = 20
#=====사용이유:1. playing 비었을때, 오류 막기 2.img버튼클릭시, obj 대신
tempObj = Label(font_name=todayFont,text='1')
playing=[tempObj, ]
tempLabel=Label(font_name=todayFont,text='ready')
tempBtn=Button(font_name=todayFont,text='temp')
get_text=0
CALL=0
POS_CALL=0
PLAY_CALL=0
#===============volume==========================================================
def get_volumeNum(instance,value):
    VOL_TEXT = VOL_BAR.value
    VOL_LABEL.text = str(int(VOL_TEXT))
    VOL_LABEL.texture_update()
    return VOL_TEXT
def get_volumeText():
    VOL_TEXT = get_volumeNum(VOL_BAR,VOL_BAR.value)
    return VOL_TEXT
#===============song pos========================================================
def get_posNum(self,obj):
    global CALL, POS_CALL, PLAY_CALL

    CALL +=1
    #print(f"get_posNum:CALL:{CALL},POS_CALL:{POS_CALL}")

    PLAY_TEXT = PLAY_BAR.value
    #print(f"get_posNum:PLAY_TEXT:{PLAY_TEXT}")

    (RUN_DURATION, run_T) = sbp.get_playtime()
    POS = (PLAY_TEXT* RUN_DURATION) // PLAY_BAR.max

    if POS_CALL - PLAY_CALL > 2 or CALL - POS_CALL == 1 or CALL - PLAY_CALL == 1:
        sbp.get_pos(POS)
    #    print(f"move_pos_POS:{POS}")

    POS_CALL = CALL

    return PLAY_TEXT

class Root(BoxLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        winWidth = 640
        winHeight = 480
        self.spacing = 10
        self.size = (winWidth,winHeight)
        #self.orientation = "horizontal"
        #self.pos_hint: {"x": .3, "top": .9}
#===============image click시, 동기화=============================================
class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)

#===============soundbar class==================================================
class SoundBarMenu(BoxLayout):

    def __init__(self, **kwargs):
        super(SoundBarMenu, self).__init__(**kwargs)
        self.playBarLayout = GridLayout(rows=1,cols=12,size_hint=(1,1),
                                        padding=[10,10,10,10],spacing=[0,0])

        self.add_widget(self.playBarLayout)
        self.drawMylist()
        self.start_newsong()

    #==============draw widgets=================================================
    def drawMylist(self):
        global VOL_TEXT, VOL_BAR, VOL_LABEL, PLAY_BTN, PAUSE_BTN, PLAY_BAR, PLAY_TEXT

        #==============volume slider============================================
        VOL_BAR = Slider(padding=5,min= 0, max=100, value=30)#size_hint=(0.1,0.1)
        VOL_BAR.size_hint=(0.1,0.1)
        VOL_BAR.value_track=True
        VOL_BAR.value_track_width="1sp"
        VOL_BAR.value_track_color=boxColor
        VOL_BAR.cursor_size=("10sp","10sp")
        VOL_BAR.cursor_image=f'{imgDir}\\nothing.png'
        VOL_BAR.background_width = "10sp"
        VOL_BAR.sensitivity = "all"
        #volume_bar.cursor_disabled_image="True"
        #volume_bar.border_horizontal = stopColor
        VOL_LABEL = Label(font_name=todayFont,text="10",font_size =soundbar_fontsize,size_hint=(0.1,0.1),
                                halign='center',valign="bottom",bold=False,italic=False,color=boxColor)

        #==============play slider==============================================
        PLAY_BAR = Slider(padding=5,min=0, max=100)#size_hint=(0.1,0.1)
        PLAY_BAR.size_hint=(1,1)
        PLAY_BAR.value_track=True
        PLAY_BAR.value_track_width="1sp"
        PLAY_BAR.value_track_color=boxColor
        PLAY_BAR.cursor_size=("5sp","5sp")
        PLAY_BAR.cursor_image=f'{imgDir}\\nothing.png'
        PLAY_BAR.background_width = "10sp"
        PLAY_BAR.sensitivity = "all"

        #=====draw playBar =====================================================
        self.shuffle_BTN = Button(font_name=todayFont,font_size=soundbar_fontsize,text="#",size_hint=(0.1, 0.1),
                                background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)#bartextColor)

        self.replay_BTN = Button(font_name=todayFont,font_size=soundbar_fontsize,text="@",size_hint=(0.1, 0.1),
                                background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)#bartextColor)

        self.PREV_BTN = Button(font_name=todayFont,font_size=soundbar_fontsize, text="<<",size_hint=(0.1,0.1),
                                background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)#bartextColor)

        PLAY_BTN = Button(font_name=todayFont,font_size=soundbar_fontsize,text="=",size_hint=(0.1, 0.1),
                                background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)#bartextColor)

        PAUSE_BTN = Button(font_name=todayFont,font_size=soundbar_fontsize,text="|||",size_hint=(0.1,0.1),
                                background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)

        self.NEXT_BTN = Button(font_name=todayFont,font_size=soundbar_fontsize,text=">>",size_hint=(0.1,0.1),
                                background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)#bartextColor)

        self.empty1 = Button(font_name=todayFont,font_size=soundbar_fontsize,text="",size_hint=(0.1,0.1),
                                background_normal = "", background_color=[0,0,0,0],color=[0,0,0,0])

        self.playLabelLayout = GridLayout(rows=2,cols=1,size_hint=(0.5,1),
                                                padding=[10,10,10,10],spacing=[10,10])

        self.playLabel = Label(font_name=todayFont,font_size=soundbar_fontsize,text="",size_hint=(1, 0.5),
                                halign='center',valign="bottom",bold=False,italic=False, color=boxColor)#bartextColor)

        self.voice_BTN = Button(font_name=todayFont,font_size=soundbar_fontsize,text="voice",size_hint=(0.1, 0.1),
                                background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)#bartextColor)

        self.empty2 = Button(font_name=todayFont,font_size=soundbar_fontsize,text="",size_hint=(0.1,0.1),
                                background_normal = "", background_down = "",background_color=[0,0,0,0],color=[0,0,0,0])

        #=====call function regularly ==========================================
        Clock.schedule_interval(self.show_playLabel, 0.5)
        Clock.schedule_interval(self.set_volumeNum, 0.5)

        Clock.schedule_interval(self.get_playtimeNum, 0.5)

        #=====bind function ====================================================
        VOL_BAR.bind(value=get_volumeNum)
        PLAY_BAR.bind(value=get_posNum)

        PLAY_BTN.bind(on_press=self.act_PLAYBTN)
        PAUSE_BTN.bind(on_press=self.act_PAUSEBTN)

        self.PREV_BTN.bind(on_press=self.act_PREVBTN)
        self.NEXT_BTN.bind(on_press=self.act_NEXTBTN)

        self.replay_BTN.bind(on_press=self.replay_song)
        self.shuffle_BTN.bind(on_press=self.shuffle_song)

        self.voice_BTN.bind(on_press=self.recognize_voice)

        #=====add widget =======================================================
        self.playBarLayout.add_widget(self.PREV_BTN)
        self.playBarLayout.add_widget(PLAY_BTN)
        self.playBarLayout.add_widget(PAUSE_BTN)
        self.playBarLayout.add_widget(self.NEXT_BTN)
        self.playBarLayout.add_widget(self.empty1)

        self.playBarLayout.add_widget(self.playLabelLayout)
        self.playLabelLayout.add_widget(PLAY_BAR)
        self.playLabelLayout.add_widget(self.playLabel)


        self.playBarLayout.add_widget(self.empty2)
        self.playBarLayout.add_widget(self.shuffle_BTN)
        self.playBarLayout.add_widget(self.replay_BTN)
        self.playBarLayout.add_widget(VOL_BAR)
        self.playBarLayout.add_widget(VOL_LABEL)
        self.playBarLayout.add_widget(self.voice_BTN)

    #==============volume=======================================================
    def set_volumeNum(self,obj):
        VOL_TEXT = get_volumeText()
        #print(f"vol_text:{volume_text}")
        sbp.get_volume(VOL_TEXT/100)

    def get_playtimeNum(self,obj):
        global CALL, PLAY_CALL

        CALL+=1
    #    print(f"get_playtimeNum:CALL:{CALL}, PLAY_CALL:{PLAY_CALL}")

        (RUN_DURATION, run_T) = sbp.get_playtime()
        run_T = int(run_T)
        RUN_DURATION = int(RUN_DURATION)
        if run_T == 0:
            PLAY_BAR.value = 0
        elif RUN_DURATION == 0:
            PLAY_BAR.value = 0
        elif run_T == RUN_DURATION:
            PLAY_BAR.value = PLAY_BAR.max
        else:
            PLAY_BAR.value = (PLAY_BAR.max * run_T) // RUN_DURATION

        PLAY_CALL = CALL

    #=============playLabel=====================================================
    def show_playLabel(self,obj):
        playLabelText = sbp.get_playLabel()
        self.playLabel.text = f'{playLabelText}'
        self.playLabel.texture_update()

    #=============get background songlist=======================================
    def start_newsong(self):
        global playTitle,playing
        #playTitle = sbp.play_newsong()
        #playTitle = sbp.play_newsongRandom()
        #playTitle = sbp.play_songRandom()
        playTitle = sbp.play_allsong()
        #playTitle = ["firstSine_1.wav","firstSine_2.wav","firstSine_3.wav"]
        #test = SoundLoader.load(f'{mp3Dir}/test_1.mp3')
        #playTitle = ["test_1.mp3","test_1.mp3","test_1.mp3"]
        playing = [tempObj,]

        playnum=0
        thread_one = threading.Thread(target=sbp.get_playThread, args=(playTitle,playing,PLAY_BTN,PLAY_BTN,playnum), daemon=True)
        thread_one.start()

    #=============shuffle songlist > sbp.shuffle_song > start thread============
    def shuffle_song(self,obj):
        global playTitle,playing

        PAUSE_BTN.text = "|||"
        PAUSE_BTN.color = boxColor

        playTitle = sbp.shuffle_song()
        sbp.get_quit()
        time.sleep(1)

        playnum=0
        thread_one = threading.Thread(target=sbp.get_playThread, args=(playTitle,playing,PLAY_BTN,PLAY_BTN,playnum), daemon=True)
        thread_one.start()

    #=============push replay > sbp.get_replay==================================
    def replay_song(self,obj):

        if self.replay_BTN.text == "@":
            self.replay_BTN.text = "1"
            replay = 1
        elif self.replay_BTN.text == "1":
            self.replay_BTN.text = "2"
            replay = 2
        elif self.replay_BTN.text == "2":
            self.replay_BTN.text = "@"
            replay = 3

        return sbp.get_replay(replay)

    #============= PLAYBTN > Check class > start thread=========================
    def act_PLAYBTN(self,PLAY_BTN):
        global playTitle,playing

        if PLAY_BTN.text == ">":
            PLAY_BTN.text = "="
            PLAY_BTN.color = boxColor

            for i in playing:
                i.color = textColor

            if PAUSE_BTN.color == stopColor:
                PAUSE_BTN.color = boxColor
                sbp.get_restart()

            sbp.get_quit()
            print("stop song")

        #elif manager.current == "screen_setting":
        #    manager.screen_setting.playUserlist(PLAY_BTN)

        elif manager.current == "screen_song":
            manager.screen_song.play_checkedSong()

        elif manager.current == "screen_singer":
            manager.screen_singer.play_checkedSinger(PLAY_BTN)

        else:
            playnum=0
            thread_one = threading.Thread(target=sbp.get_playThread, args=(playTitle,playing,PLAY_BTN,PLAY_BTN,playnum), daemon=True)
            thread_one.start()

    #============= PAUSEBTN ====================================================
    def act_PAUSEBTN(self, PAUSE_BTN):
        if PLAY_BTN.text == ">":
            if PAUSE_BTN.color == stopColor:
                PAUSE_BTN.color = boxColor
                return sbp.get_restart()

            if PAUSE_BTN.color == boxColor:
                PAUSE_BTN.color = stopColor
                return sbp.get_pause()

    #============= PREVBTN > sbp.get_prev > playnum > start thread==============
    def act_PREVBTN(self, PREV_BTN):
        PAUSE_BTN.color = boxColor
        #self.PREV_BTN.color = stopColor
        #self.PREV_BTN.color = boxColor

        playnum = sbp.get_prev()
        sbp.get_quit()
        time.sleep(1)

        print(f"click______playnum:{playnum},playTitle:{playTitle[playnum]}")
        thread_one = threading.Thread(target=sbp.get_playThread, args=(playTitle,playing,PLAY_BTN,tempBtn,playnum), daemon=True)
        thread_one.start()

    #============= PREVBTN > sbp.get_next > playnum > start thread==============
    def act_NEXTBTN(self, NEXT_BTN):
        PAUSE_BTN.color = boxColor
        #self.NEXT_BTN.color = stopColor
        #self.NEXT_BTN.color = boxColor

        playnum = sbp.get_next()
        sbp.get_quit()
        time.sleep(1)

        print(f"click______playnum{playnum},playTitle:{playTitle[playnum]}")
        thread_one = threading.Thread(target=sbp.get_playThread, args=(playTitle,playing,PLAY_BTN,tempBtn,playnum), daemon=True)
        thread_one.start()

    """
    #============= gTTS test====================================================
    def make_gtts(self, obj):
        tts = gTTS(text="Tell me the song title or singer",lang="en",tld="com")
        tts.save(f"{mp3Dir}/searhsong.mp3")
        os.system(f"open {mp3Dir}/searhsong.mp3")
    """
    #=============voice_BTN > sbp.get_pause > sbv.searchsong_voice > start thread
    #gTTS, speech_recognition test==============================================
    def recognize_voice(self,obj):
        sbp.get_pause()
        res, resmsg = sbv.searchsong_voice()

        if res == True:
            playTitle = [resmsg]
            PAUSE_BTN.text = "|||"
            PAUSE_BTN.color = boxColor
            playing = [tempObj,]
            playnum=0

            sbp.get_restart()
            sbp.get_quit()
            time.sleep(1)

            thread_one = threading.Thread(target = sbp.get_playThread, args = (playTitle,playing,PLAY_BTN,tempBtn,playnum), daemon=True)
            thread_one.start()

        elif res == False:
            sbp.get_restart()

#===============기본 화면 구성(메뉴)=================================================
class UpperMenu(BoxLayout):
    def __init__(self, **kwargs):
        super(UpperMenu, self).__init__(**kwargs)

        self.boxLayout = BoxLayout(spacing=10,orientation='vertical')
        self.add_widget(self.boxLayout)
        self.drawMylist()

    #=============draw widgets==================================================
    def drawMylist(self):

        #=====left side menu 처리================================================
        self.boxLayoutEmptyspace = BoxLayout(size_hint=(1,1),spacing=5,orientation='vertical')
        self.songBoxDrop = DropDown()
        btnText=["Main","Song","Singer","Setting","Download","Exit"]#메뉴이름
        btnDic={}#메뉴버튼
        songBoxBtnText = ["Playlist","Color"]#Setting메뉴의 드롭다운 메뉴
        songBoxBtnDic = {}#드롭다운버튼

        #=====img_btn 처리=======================================================
        self.img_btn = ImageButton(source=f'{imgDir}\\nothing.png')
        self.img_btn.size_hint = (1, 0.2)
        self.img_btn.bind(on_release=self.callSyncSong)#image클릭시,동기화
        self.boxLayout.add_widget(self.img_btn)

        #=====메뉴버튼, 드롭다운메뉴버튼 지정===========================================
        for i in range(len(btnText)):
            btn = Button(font_name=todayFont,font_size=menu_fontsize,text=btnText[i], size_hint=(0.7, 0.07), background_normal = "", background_color=boxColor,color=textColor)
            btnDic[btnText[i]]=btn
            if btnText[i] == "Main":
                btn.bind(on_release=self.show_screen_main)
            if btnText[i] == "Song":
                btn.bind(on_release=self.show_screen_song)
            if btnText[i] == "Singer":
                btn.bind(on_release=self.show_screen_singer)
            if btnText[i] == "Download":
                btn.bind(on_release=self.songBoxPop)

            if btnText[i] == "Setting":
                for j in range(len(songBoxBtnText)):
                    songBoxDropBtn = Button(font_name=todayFont,font_size=menu_fontsize,text=songBoxBtnText[j], size_hint=(0.7,0.07),height=40, size_hint_y=None, background_normal = "", background_color=boxColor,color=textColor)
                    songBoxBtnDic[songBoxBtnText[j]] = songBoxDropBtn
                    songBoxDropBtn.bind(on_release=lambda instance: self.songBoxDrop.select(songBoxDropBtn.text))
                    self.songBoxDrop.add_widget(songBoxDropBtn)
                    if songBoxBtnText[j] == "Playlist":
                        songBoxDropBtn.bind(on_release=self.show_screen_setting)
                    if songBoxBtnText[j] == "Color":
                        songBoxDropBtn.bind(on_release=self.colorPop)
                btn.bind(on_release=self.songBoxDrop.open)
                self.songBoxDrop.bind(on_select=lambda instance, x: setattr(songBoxDropBtn, 'text', x))

            if btnText[i] == "Exit":
                btn.bind(on_release=self.closeAll)

            self.boxLayout.add_widget(btn)

        self.boxLayout.add_widget(self.boxLayoutEmptyspace)

#    def ready_widget(self,obj):
#        print("ready")

    #===============앱 정지=======================================================
    def closeAll(self,obj):
        #Fourth_mine_kv2().stop()
        #App().get_running_app().stop()
        songBox_kvPyaudio().get_running_app().stop()

    #==============동기화 함수 호출=================================================
    def callSyncSong(self,obj):
        global todayFont
        sbl.sync_song()
        sbs.make_singerDic()
        todayFont = circle.get_randomFont()
        print(todayFont)
        #ScreenSong().layout_middle.clear_widgets()#차이점-클래스를 다시 그리는 것(하지말것)
        soundbar.playBarLayout.clear_widgets()
        soundbar.drawMylist()

        upperMenu.boxLayout.clear_widgets()
        upperMenu.drawMylist()

        manager.screen_main.mainScreen.clear_widgets()
        manager.screen_main.drawMylist()

        manager.screen_setting.base1.clear_widgets()
        manager.screen_setting.drawMylist()

        manager.screen_song.base.clear_widgets()
        manager.screen_song.drawSonglist()

        manager.screen_singer.base1.clear_widgets()
        manager.screen_singer.drawMylist()

    #==============side menu btn click -> change screen ========================
    def show_screen_main(self,obj):
        manager.current = "screen_main"
    def show_screen_setting(self, obj):
        manager.current = "screen_setting"
    def show_screen_song(self,obj):
        manager.current = "screen_song"
    def show_screen_singer(self, obj):
        manager.current = "screen_singer"

    #==============setting_color click -> popup ================================
    def colorPop(self,obj):
        global COLORNUM, COLORTEXT, COLORLISTS, COLORDIC
        self.colorPopup = Popup(title='',
              size_hint=(0.7, 1), size=(800, 800),auto_dismiss=True,
              title_font='Roboto',title_size=20, title_align='center',
              title_color=textColor,
              separator_height=0.5,
              separator_color=textColor)

        COLORTEXT = ["black", "white", "gold","red","original","reverse"]
        COLORDIC = {}
        COLORNUM = len(COLORTEXT)

        self.basepop1 = BoxLayout(padding=5,spacing=5,size_hint=(1,1), orientation = 'vertical')

        self.layoutpop1_top = GridLayout(rows=1,cols=2,padding=5,spacing=5,size_hint=(1, 0.05))
        self.popText = Label(font_name=todayFont,font_size=menu_fontsize,text = 'Choose the color.',size_hint=(0.9, 0.2),color=textColor)
        self.layoutpop1_top.add_widget(self.popText)

        self.layoutpop1_middle = GridLayout(rows=COLORNUM+10,cols=1,padding=5,spacing=5,size_hint=(1, 0.9))

        for i in range(COLORNUM+10):
            if i > COLORNUM-1:
                self.colorBtn=Button(font_name=todayFont,font_size=menu_fontsize,text=f"",size_hint=(0.1, 0.2), background_normal = "", background_color=[0,0,0,0],color=[0,0,0,0])
            else:
                self.colorBtn=Button(font_name=todayFont,font_size=menu_fontsize,text=f"{COLORTEXT[i]}",size_hint=(0.1, 0.2), background_normal = "", background_color=[0,0,0,0],color=textColor)
                COLORDIC[COLORTEXT[i]] = self.colorBtn

                self.colorBtn.bind(on_press = self.color_pressed)
            self.layoutpop1_middle.add_widget(self.colorBtn)

        self.basepop1.add_widget(self.layoutpop1_top)
        self.basepop1.add_widget(self.layoutpop1_middle)
        self.colorPopup.add_widget(self.basepop1)

        self.colorPopup.open()

    #==============self.colorBtn click -> change color =========================
    def color_pressed(self,obj):
        global winColor,boxColor,textColor, stopColor

        white = [1,1,1,1]
        palegrey = [233/255, 233/255, 233/255, 1]
        lightgrey = [211/255, 211/255, 211/255, 1]
        deepgrey = [105/255,105/255,105/255,1]
        black = [0,0,0,1]

        lightyellow = [192/255,193/255,190/255,1]
        gold = [192/255,183/255,135/255,1]
        yellowgreen = [189/255,183/255,110/255,1]
        lightpink = [188/255, 143/255, 143/255, 1]
        red = [110/255,0/255,0/255,1]
        bluegreen = [30/255,160/255,180/255,1]
        #==============set color ===============================================
        if obj.text == "black":
            winColor = black
            textColor = palegrey
            boxColor = deepgrey
            stopColor = white

        elif obj.text == "white":
            winColor = white
            textColor =lightgrey
            boxColor = deepgrey
            stopColor =palegrey

        elif obj.text == "gold":
            winColor = black
            textColor =white
            boxColor = gold
            stopColor =lightyellow

        elif obj.text == "red":
            winColor = gold
            textColor =white
            boxColor = red
            stopColor =lightyellow

        elif obj.text == "original":
            winColor = lightgrey
            textColor = white
            boxColor = lightpink
            stopColor = deepgrey

        elif obj.text == "reverse":
            winColor = lightpink
            textColor = white
            boxColor = lightgrey
            stopColor = deepgrey

        Window.clearcolor = winColor
        #==============reset widget(remove -> draw) ============================
        soundbar.playBarLayout.clear_widgets()
        soundbar.drawMylist()

        upperMenu.boxLayout.clear_widgets()
        upperMenu.drawMylist()

        manager.screen_main.mainScreen.clear_widgets()
        manager.screen_main.drawMylist()

        manager.screen_setting.base1.clear_widgets()
        manager.screen_setting.drawMylist()

        manager.screen_song.base.clear_widgets()
        manager.screen_song.drawSonglist()

        manager.screen_singer.base1.clear_widgets()
        manager.screen_singer.drawMylist()

        self.colorPopup.dismiss()

    #==============Screen setting>Download메뉴 클릭시, 팝업창(다운로드, 재생, 삭제)======
    def songBoxPop(self, obj):
        self.songBoxPopup = Popup(title='',
              size_hint=(0.5, 0.4), size=(800, 800),auto_dismiss=True,
              title_font=todayFont,title_size=menu_fontsize, title_align='center',
              title_color=textColor,
              separator_height=0.5,
              separator_color=textColor)

        self.lowerContent = StackLayout(orientation="lr-tb",padding=10,spacing=10)
        self.songBoxText=Label(font_name=todayFont,font_size=menu_fontsize,text = 'Write title, name.',width=40, height=30,size_hint=(1, 0.2),color=textColor)
        self.lowerContent.add_widget(self.songBoxText)

        self.lowerContent.add_widget(Label(font_name = todayFont,font_size=menu_fontsize,text='Title?',width=40, height=30,size_hint=(0.2, 0.16),color=textColor))
        self.songText = TextInput(font_name=todayFont,multiline = False,width=40, height=30,size_hint=(0.8, 0.16))
        self.lowerContent.add_widget(self.songText)

        self.lowerContent.add_widget(Label(font_name=todayFont,font_size=menu_fontsize,text = 'Name?',width=40, height=30,size_hint=(0.2, 0.16),color=textColor))
        self.singer = TextInput(font_name=todayFont,multiline = False,width=40, height=30,size_hint=(0.8, 0.16))
        self.lowerContent.add_widget(self.singer)

        self.songBoxSubmit = Button(font_name=todayFont,font_size=menu_fontsize,text="Add",width=40, height=30,size_hint=(0.33, 0.16), background_normal = "", background_color=boxColor,color=textColor)
        self.songBoxSubmit.bind(on_press = self.press_songBox) #곡다운로드
        self.lowerContent.add_widget(self.songBoxSubmit)

        self.songBoxPlay = Button(font_name=todayFont,font_size=menu_fontsize,text="Play",width=40, height=30,size_hint=(0.33, 0.16), background_normal = "", background_color=boxColor,color=textColor)
        self.songBoxPlay.bind(on_press = self.press_play) #곡재생
        self.lowerContent.add_widget(self.songBoxPlay)

        self.songBoxDelete = Button(font_name=todayFont,font_size=menu_fontsize,text="Delete",width=40, height=30,size_hint=(0.33, 0.16), background_normal = "", background_color=boxColor,color=textColor)
        self.songBoxDelete.bind(on_press = self.press_delete) #곡삭제
        self.lowerContent.add_widget(self.songBoxDelete)

        self.songBoxPopup.add_widget(self.lowerContent)

        self.songBoxPopup.open()

    #==============곡다운로드(yc.change_Song유투브크롤링)=============================
    def press_songBox(self,instance):
        print("Song:", self.songText.text,", Singer:", self.singer.text)
        self.songBoxPopup.dismiss()
        song = self.songText.text
        singer = self.singer.text

        try:
            thread_down = threading.Thread(target = yc.change_Song, args = (song, singer), daemon=True)
            res = thread_down.start()
            print(f'Download_Threading start.')

        except Exception as msg:
                self.songBoxPopup.title = f"{msg}retry."

        self.songText.text = ""
        self.singer.text = ""

    #==============곡 삭제========================================================
    def press_delete(self,obj):
            #print("Song:", self.songText.text,"Singer:", self.singer.text)
            #self.songBoxPopup.dismiss()
            song = f'{self.songText.text}'
            singer = f'{self.singer.text}'

            try:
                res = sbl.delete_Song(song, singer)
                if res == False:
                    print("Can't delete. There is no song.")
                else:
                    print(f'{song}_{singer}.wav deleted')
            except Exception as msg:
                    self.songBoxPopup.title = f"{msg}Retry."

            self.songText.text = ""
            self.singer.text = ""

    #==============곡 검색 후,재생==================================================
    def press_play(self,obj):
        print("Song:", self.songText.text,"Singer:", self.singer.text)
        #self.songBoxPopup.dismiss()
        song = f'{self.songText.text}'
        singer = f'{self.singer.text}'
        self.songBoxPopup.title = 'Write title, name.'
        global playing
        reSong = song.lower()
        reSinger = singer.lower()
        playTitle = []
        playing = []
        tempBtn = Button(text='')

        #=====입력한 곡을 mp3 dir안에서 찾기==========================================
        try:
            for i in os.listdir(f'{mp3Dir}'):
                if i not in ignoreFile:
                    newNameDir = i[:-4]
                    newNameDir = newNameDir.lower()
                    splitNameDir=list(newNameDir.split('_'))
                    newSongDir=splitNameDir[0]
                    newSingerDir=splitNameDir[1]
                    if reSong == newSongDir and reSinger == newSingerDir:
                        thisTitle = i
                        break
            #=====찾은 thisSong의 재생시간 찾기&로드==================================
            print(thisTitle)
            playTitle.append(thisTitle)
            #=====strat thread==================================================
            sbp.get_quit()
            time.sleep(1)

            playnum = 0
            thread_one = threading.Thread(target = sbp.get_playThread, args = (playTitle,playing,tempBtn,tempBtn,playnum), daemon=True)
            thread_one.start()

        except Exception as msg:
                self.songBoxPopup.title = f"{msg}retry."

        self.songText.text = ""
        self.singer.text = ""

#==============ScreenMain=======================================================
class ScreenMain(Screen):
    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)

        self.name = "screen_main"

        self.mainScreen = GridLayout(rows=2,cols=1,size_hint = (1,1),padding=[0,0,0,0],spacing=[10,10])

        self.add_widget(self.mainScreen)
        self.drawMylist()

    #==============draw widgets=================================================
    def drawMylist(self):
        #global viList

        #==============(scroll)playlistlabel====================================
        self.scroll = ScrollView(smooth_scroll_end=10,scroll_type=['bars'],bar_width='3dp', scroll_wheel_distance=100, do_scroll_x = False, do_scroll_y = True)
        self.scroll.bar_color = boxColor
        #self.scroll.size_hint_min = (100,500)
        self.scroll.size=(Window.width, Window.height)
        self.scroll.size_hint=(1, 1)
        #self.scroll.size_hint_y = None
        #self.scroll.padding= 10, 50
        self.labelLayout = GridLayout(cols=1, spacing=10, size_hint=(1, 1))#,size_hint_y=None)
        #self.labelLayout.bind(minimum_height=self.labelLayout.setter('height'))
        self.scroll.add_widget(self.labelLayout)
        #self.visualizerLayout = GridLayout(rows=64,cols=1,#size_hint=(1,1),
        #                                padding=[0,0,0,0],spacing=[0,0])

        self.timeLabel = Label(text_language='ko_KR',font_name=todayFont,font_size =menu_fontsize,text='',
                                halign='center',valign="bottom",bold=False,italic=False,
                                size_hint=(1, 1),color=textColor)

        #self.mainScreen.add_widget(self.visualizerLayout)

        self.mainScreen.add_widget(self.scroll)
        self.mainScreen.add_widget(self.timeLabel)

        Clock.schedule_interval(self.timeAdd, 0.5)
        Clock.schedule_interval(self.show_playList, 0.5)

        #==============visualizer test==========================================
        """
        viList = [""]*32

        for i in range(len(viList)):
            btn = Button(font_name=todayFont,font_size=soundbar_fontsize, text="",# pos_hint =  {"x": .1, "top": .1, "y":.0,"bottom":.0},size_hint=(0,1),#,size_hint=(0.01,0.01),
                                background_normal = "", background_down = "",background_color=[0,0,0,0],color=[0,0,0,0])#bartextColor)
            #btn2 = Button(font_name=todayFont,font_size=soundbar_fontsize, text="",size_hint=(0.1,1),# pos_hint =  {"x": .1, "top": .1, "y":.0,"bottom":.0},size_hint=(0,1),#,size_hint=(0.01,0.01),
            #                    background_normal = "", background_down = "",background_color=winColor,color=winColor)#bartextColor)
            viList[i] = btn

            self.visualizerLayout.add_widget(btn)
            #self.visualizerLayout.add_widget(btn2)
        """

    #==============draw time > circle.current_time()============================
    def timeAdd(self,obj):
        timeText=circle.current_time()
        self.timeLabel.text = timeText
        self.timeLabel.texture_update()

    #==============(scroll)draw playlist > sbp.get_playTitle()==================
    def show_playList(self,obj):
        global playTitle
        playTitle = sbp.get_playTitle()
        self.labelLayout.clear_widgets()

        self.emptyLabel = Label(font_name=todayFont,font_size =text_fontsize
                            ,size_hint_y=None, height=40,color=[0,0,0,0])

        self.titleLabel = Label(text="================Playlist===============",
                            font_name=todayFont,font_size =text_fontsize
                            ,size_hint_y=None, height=40,color=textColor)
        self.labelLayout.add_widget(self.emptyLabel)
        self.labelLayout.add_widget(self.titleLabel)
        for i in playTitle:
            title = i.split('.wav')
            self.playLabel = Label(font_name=todayFont,font_size =text_fontsize
                                ,size_hint_y=None, height=40,color=textColor)
            self.playLabel.text=f'{title[0]}\n'
            self.labelLayout.add_widget(self.playLabel)


#==============ScreenSetting(다운로드팝업, userlist관리, 색상)========================
class ScreenSetting(Screen):
    def __init__(self, **kwargs):
        super(ScreenSetting, self).__init__(**kwargs)
        self.name = "screen_setting"

        global ROWNUM, NOWLISTS, NOWLISTSTEXT, NOWLISTSDIC, SETTINGBTNLIST, POPDELBTNLIST

        ROWNUM = FIXROW#보여줄 곡 수
        NOWLISTSTEXT = [['']*2 for x in range(ROWNUM)]#저장한위젯저장
        NOWLISTSDIC = {}#저장한위젯호출위해저장

        SETTINGBTNLIST = ['']*12#페이지버튼(지정한 목록 15개 초과시)
        POPDELBTNLIST = ['']*12#userlist popup페이지버튼(지정한 목록 15개 초과시)

        NOWLISTS = sbu.show_userlist()#userlist 목록 불러오기
        NOWLISTS.sort()

        self.base1 = BoxLayout(padding=5,spacing=5,size_hint=(1,1), orientation = 'vertical')
        self.add_widget(self.base1)

        self.drawMylist()

    #==============draw widgets=================================================
    def drawMylist(self):
        #global playList, playing
        NOWLISTS = sbu.show_userlist()#userlist 목록 불러오기
        NOWLISTS.sort()
        listNum = len(NOWLISTS)#userlist 개수

        self.layout1_top = GridLayout(rows=1,cols=9,padding=5,spacing=5,size_hint=(1, 0.05))
        self.layout1_middle = GridLayout(rows=ROWNUM,cols=9,padding=5,spacing=5,size_hint=(1, 0.9))
        self.layout1_page = GridLayout(rows=1,cols=12,padding=5,spacing=5,size_hint=(0.9, 0.05))

        self.base1.add_widget(self.layout1_top)
        self.base1.add_widget(self.layout1_middle)
        self.base1.add_widget(self.layout1_page)

        self.titleEmptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint=(1, 0.2))
        self.titleEmptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint=(1, 0.2))
        self.titleEmptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint=(1, 0.2))
        self.topLabel=Label(font_name=todayFont,font_size =menu_fontsize,text ='Playlist',halign="left",valign="top", size_hint=(2, 0.2))#,color=boxColor)
        self.titleEmptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint=(1, 0.2))
        self.titleEmptyLabel5=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint=(1, 0.2))
        self.editBtn = Button(font_name=todayFont,font_size =menu_fontsize,text="+/-", size_hint=(0.9, 0.03), background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)
        self.titleEmptyLabel6=Label(font_name=todayFont,text ='',font_size=30,halign="left",valign="top", size_hint=(1, 0.2))

        self.editBtn.bind(on_press = self.makeListPop) #userlist 생성&삭제하기위한 팝업창 호출

        self.layout1_top.add_widget(self.titleEmptyLabel1)
        self.layout1_top.add_widget(self.titleEmptyLabel2)
        self.layout1_top.add_widget(self.topLabel)
        self.layout1_top.add_widget(self.titleEmptyLabel3)
        self.layout1_top.add_widget(self.titleEmptyLabel4)
        self.layout1_top.add_widget(self.titleEmptyLabel5)
        self.layout1_top.add_widget(self.editBtn)
        self.layout1_top.add_widget(self.titleEmptyLabel6)

        for i in range(ROWNUM):#보여줄 목록의 개수만큼 위젯추가

            if i <= listNum-1:#초과되지 않는 부분은 보이도록 처리
                self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top", width=40, height=30,size_hint=(1, 0.2))
                self.userListBtn=Button(font_name=todayFont,font_size =text_fontsize,text=f'{NOWLISTS[i]}', width=10, height=10, size_hint=(0.9, 0.03), background_normal = "", background_down = "",background_color=[0,0,0,0],color=textColor)
                self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel5=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.editBtn = Button(font_name=todayFont,font_size =text_fontsize,text="edit", width=10, height=10, size_hint=(0.9, 0.03), background_normal = "",background_color=boxColor,color=textColor)
                self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))

                NOWLISTSTEXT[i][0] = f'{NOWLISTS[i]}'
                NOWLISTSTEXT[i][1] = f'{NOWLISTS[i]}+add/sub'
                self.userListBtn.bind(on_press=self.playUserlist)#userlist의 곡 재생을 위한 함수 호출
                self.editBtn.bind(on_press=self.del_userlistSong)#userlist의 곡 삭제를 위한 함수 호출
                NOWLISTSDIC[NOWLISTSTEXT[i][0]]=self.userListBtn
                NOWLISTSDIC[NOWLISTSTEXT[i][1]]=self.editBtn

            if i > listNum-1:#userlist 개수가 보여줄목록수(15)보다 작은 경우, 초과되는 부분은 안보이도록 처리
                self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.userListBtn=Button(font_name=todayFont,font_size =text_fontsize,text=f'{i}',size_hint=(0.9, 0.03), background_normal = "", background_down = "",background_color=[0,0,0,0],color=[0,0,0,0])
                self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel5=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.editBtn = Button(font_name=todayFont,font_size =text_fontsize,text="edit",size_hint=(0.9, 0.03), background_color=[0,0,0,0],color=[0,0,0,0])
                self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))

                NOWLISTSTEXT[i][0] = f'{i}'
                NOWLISTSTEXT[i][1] = f'{i}+add/sub'
                NOWLISTSDIC[NOWLISTSTEXT[i][0]]=self.userListBtn
                NOWLISTSDIC[NOWLISTSTEXT[i][1]]=self.editBtn

            self.layout1_middle.add_widget(self.emptyLabel1)
            self.layout1_middle.add_widget(self.userListBtn)
            self.layout1_middle.add_widget(self.emptyLabel2)
            self.layout1_middle.add_widget(self.emptyLabel3)
            self.layout1_middle.add_widget(self.emptyLabel4)
            self.layout1_middle.add_widget(self.emptyLabel5)
            self.layout1_middle.add_widget(self.emptyLabel6)
            self.layout1_middle.add_widget(self.editBtn)
            self.layout1_middle.add_widget(self.emptyLabel7)

        #=====페이지버튼 추가하기 전에 계산============================================
        pageLISTNO = listNum//(ROWNUM) #총userlist수(ex.236) // 한페지화면의userlist수(15) == 총페이지개수(15, 나머지있으면 16)
        lastLISTNO = listNum%(ROWNUM) #총userlist수 % 한페지화면의userlist수(15) == 마지막페이지에보여질userlist수(ex.11) => 총페이지개수(15+나머지=16)
        if lastLISTNO > 0:
            pageLISTNO+=1
        pageSetLISTNO = pageLISTNO // 10 # 총페이지개수 //한레이아웃페이지수(1~10페이지) ==  다음 >> 넘기는 횟수와 동일
        lastPageLISTNO = pageLISTNO % 10 #총페이지개수 % 한레이아웃페이지수(1~10페이지) == 마지막에 남은 보여줄 버튼 개수(6)

        #=====페이지버튼 추가=======================================================

        if listNum > ROWNUM:

            for i in range(len(SETTINGBTNLIST)):
                self.PAGEBTN = Button(font_name=todayFont,font_size =text_fontsize,text=f"{i}",size_hint=(0.1, 0.2),background_color=winColor,color=textColor)
                if pageSetLISTNO  == 0 and i > lastPageLISTNO:
                        self.PAGEBTN.background_color=[0,0,0,0]
                        self.PAGEBTN.color=[0,0,0,0]
                else:
                    if i == 0:#첫번째인덱스
                        self.PAGEBTN.text = "<<"
                    if i == 11:#마지막인덱스
                        self.PAGEBTN.text = ">>"
                    self.PAGEBTN.bind(on_press=self.press_settingpageBTN)#페이지번호 클릭시, 화면리셋 함수 호출

                SETTINGBTNLIST[i] = self.PAGEBTN
                self.layout1_page.add_widget(self.PAGEBTN)
        else:
            self.PAGEBTN = Button(font_name=todayFont,font_size=text_fontsize,text="1",size_hint=(0.1, 0.2), background_color=winColor,color=textColor)
            SETTINGBTNLIST[1] = self.PAGEBTN

    #==============페이지 번호 클릭시, 해당 화면으로 리셋================================
    def press_settingpageBTN(self, obj):

        #=====<<,>>버튼이 클릭되었을 경우에, 보여줄 화면 파악하기 위하여
        BTNnum = obj.text#클릭된 버튼의 text
        nowpageQ = int(SETTINGBTNLIST[1].text)#두번째 버튼의 text(현재페이지세트 파악)
        if nowpageQ > 10:
            nowpageA = ((nowpageQ-1)//10)
        else:
            nowpageA = 0

        listNum = len(NOWLISTS)
        pageLISTNO = listNum//(ROWNUM) #총userlist수(ex.236) // 한페지화면의userlist수(15) == 총페이지개수(15, 나머지있으면 16)
        lastLISTNO = listNum%(ROWNUM) #총userlist수 % 한페지화면의userlist수(15) == 마지막페이지에보여질userlist수(ex.11) => 총페이지개수(15+나머지=16)
        if lastLISTNO > 0:
            pageLISTNO+=1
        pageSetLISTNO = pageLISTNO // 10 # 총페이지개수 //한레이아웃페이지수(1~10페이지) ==  다음 >> 넘기는 횟수와 동일
        lastPageLISTNO = pageLISTNO % 10 #총페이지개수 % 한레이아웃페이지수(1~10페이지) == 마지막에 남은 보여줄 버튼 개수(6)
        print(f"ScreenSetting:: BTNnum:{BTNnum}, pageLISTNO:{pageLISTNO}")

        #=====페이지버튼의 숫자 바꾸기================================================
        if BTNnum == "<<":
            if nowpageA != 0:
                for i in range(1,len(SETTINGBTNLIST)):
                    if nowpageA != "1": #1-10은 "<<"버튼은 작동 안하기에
                        SETTINGBTNLIST[i].text = str((nowpageA-1)*10+i)
                        SETTINGBTNLIST[i].background_color=winColor
                        SETTINGBTNLIST[i].color=textColor
                    if i == 11:
                        SETTINGBTNLIST[i].text = ">>"
                        SETTINGBTNLIST[i].background_color=winColor
                        SETTINGBTNLIST[i].color=textColor
            endIndex = int(SETTINGBTNLIST[1].text)*FIXROW
        elif BTNnum == ">>":
            if pageSetLISTNO == nowpageA+1:#마지막페이지세트일경우,userlist개수의 페이지번호까지만 보여주기
                #print(f"BTN set: pageSetNO{pageSetLISTNO},click nowpageA{nowpageA}")
                for i in range(1,len(SETTINGBTNLIST)):
                    SETTINGBTNLIST[i].text = str((nowpageA+1)*10+i)#페이지버튼의 번호바꾸기
                    if i > lastPageLISTNO:#마지막페이지세트일 경우, 남은 페이지번호까지만 화면에 보여주기
                        SETTINGBTNLIST[i].background_color=[0,0,0,0]
                        SETTINGBTNLIST[i].color=[0,0,0,0]
            else:#페이지버튼의 번호바꾸기
                for i in range(1,len(SETTINGBTNLIST)):
                    SETTINGBTNLIST[i].text = str((nowpageA+1)*10+i)
                    SETTINGBTNLIST[i].background_color=winColor
                    SETTINGBTNLIST[i].color=textColor
                    if i == 11:#">>" 바뀌지 않도로
                        SETTINGBTNLIST[i].text = ">>"
                        SETTINGBTNLIST[i].background_color=winColor
                        SETTINGBTNLIST[i].color=textColor
            endIndex = int(SETTINGBTNLIST[1].text)*FIXROW
        else:
            endIndex = int(BTNnum)*FIXROW
        startIndex = endIndex - (FIXROW-1)

        #=====화면 리셋===========================================================
        count = 0
        self.layout1_middle.clear_widgets()
        for i in range(startIndex,endIndex+1):#그때그때 인덱스를 지정, 보여줄 화면
            if str(BTNnum) == str(pageLISTNO) and lastLISTNO != 0:
                sub = (FIXROW-lastLISTNO)
                overIndex = endIndex-sub
                if i > overIndex:#마지막페이지의 userlist dir 수보다 i 가 크면, 위젯을 안보이도록 처리
                    self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.userListBtn=Button(font_name=todayFont,font_size =text_fontsize,text=f'',size_hint=(0.9, 0.03), background_normal = "", background_down = "",background_color=[0,0,0,0],color=[0,0,0,0])
                    self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel5=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.editBtn = Button(font_name=todayFont,font_size =text_fontsize,text="edit",size_hint=(0.9, 0.03), background_normal = "", background_color=[0,0,0,0],color=[0,0,0,0])
                    self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))

                else:#NOWLISTS의 인덱스가 i-1임을 유의
                    self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.userListBtn=Button(font_name=todayFont,font_size =text_fontsize,text=f'{NOWLISTS[i-1]}',size_hint=(0.9, 0.03), background_normal = "", background_down = "",background_color=[0,0,0,0],color=textColor)
                    self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel5=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.editBtn = Button(font_name=todayFont,font_size =text_fontsize,text="edit",size_hint=(0.9, 0.03), background_normal = "", background_color=boxColor,color=textColor)
                    self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))

                    self.userListBtn.bind(on_press=self.playUserlist)#userlist의 곡 재생을 위한 함수 호출
                    self.editBtn.bind(on_press=self.del_userlistSong)#userlist의 곡 삭제를 위한 함수 호출
                    NOWLISTSTEXT[count][0] = f'{NOWLISTS[i-1]}'#userlist 이름, obj 인덱스는 count 임을 유의
                    NOWLISTSTEXT[count][1] = f'{NOWLISTS[i-1]}+add/sub'
                    NOWLISTSDIC[NOWLISTSTEXT[count][0]]=self.userListBtn
                    NOWLISTSDIC[NOWLISTSTEXT[count][1]]=self.editBtn

            else:
                self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.userListBtn=Button(font_name=todayFont,font_size =text_fontsize,text=f'{NOWLISTS[i-1]}',size_hint=(0.9, 0.03), background_normal = "", background_down = "",background_color=[0,0,0,0],color=textColor)
                self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel5=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.editBtn = Button(font_name=todayFont,font_size =text_fontsize,text="edit",size_hint=(0.9, 0.03), background_normal = "", background_color=boxColor,color=textColor)
                self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))

                self.userListBtn.bind(on_press=self.playUserlist)#userlist의 곡 재생을 위한 함수 호출
                self.editBtn.bind(on_press=self.del_userlistSong)#userlist의 곡 삭제를 위한 함수 호출
                NOWLISTSTEXT[count][0] = f'{NOWLISTS[i-1]}'
                NOWLISTSTEXT[count][1] = f'{NOWLISTS[i-1]}+add/sub'
                NOWLISTSDIC[NOWLISTSTEXT[count][0]]=self.userListBtn
                NOWLISTSDIC[NOWLISTSTEXT[count][1]]=self.editBtn

            self.layout1_middle.add_widget(self.emptyLabel1)
            self.layout1_middle.add_widget(self.userListBtn)
            self.layout1_middle.add_widget(self.emptyLabel2)
            self.layout1_middle.add_widget(self.emptyLabel3)
            self.layout1_middle.add_widget(self.emptyLabel4)
            self.layout1_middle.add_widget(self.emptyLabel5)
            self.layout1_middle.add_widget(self.emptyLabel6)
            self.layout1_middle.add_widget(self.editBtn)
            self.layout1_middle.add_widget(self.emptyLabel7)
            count+=1
        #=====페이지 번호 바꾸고 난 후, 재생 중인 곡 표시위해서, playing 중인 obj의 곡명 저장==
        playing = sbp.get_playResult()#play 재생목록이 끝까지 완료된 경우, playing 안의 obj 비우기위해(버튼을 원래색으로 바꾸기)
        names = {}
        for i in playing:
            name = i.text
            names[name] = i
        print(f"userlist_playing-listname & obj: {names}")
        #=====페이지 번호 바뀌어도, 재생 중인 곡 표시 & stop하면 작동하도록, 바뀐 obj를 playing에 저장
        for i in range(len(NOWLISTSTEXT)):
            if NOWLISTSTEXT[i][0] in names.keys():
                NOWLISTSDIC[NOWLISTSTEXT[i][0]].color = stopColor
                playing.append(NOWLISTSDIC[NOWLISTSTEXT[i][0]])

    #==============userlist dir에 들어있는 곡 선택 삭제 ==============================
    def del_userlistSong(self, obj):
        global DELROWNUM, DELLISTSTEXT, DELLISTSDIC, DELLISTS, CHECKEDONEUSERLIST, CHECKEDONEUSERSONG

        DELROWNUM = FIXROW
        DELLISTSTEXT=[['']*2 for x in range(DELROWNUM)]
        DELLISTSDIC={}
        CHECKEDONEUSERLIST = ""
        CHECKEDONEUSERSONG = []

        for i in range(len(NOWLISTSTEXT)):
            if NOWLISTSDIC[NOWLISTSTEXT[i][1]] == obj:#클릭한 edit obj의 userlist파악위해
                CHECKEDONEUSERLIST = NOWLISTSTEXT[i][0]#userlist이름저장
                #print(CHECKEDONEUSERLIST)

        DELLISTS = sbu.show_oneUserlist(CHECKEDONEUSERLIST)
        DELLISTS.sort()
        delListNum = len(DELLISTS)
        #print(f'DELLISTS:{DELLISTS}')
        self.delUserlistSongPopup = Popup(title='',
              size_hint=(0.7, 1), size=(800, 800),auto_dismiss=True,
              title_font=todayFont,title_size=menu_fontsize, title_align='center',
              title_color=textColor,
              separator_height=0.5,
              separator_color=textColor)

        self.basepop = BoxLayout(padding=5,spacing=5,size_hint=(1,1), orientation = 'vertical')

        self.layoutpop_top = GridLayout(rows=1,cols=3,padding=5,spacing=5,size_hint=(1, 0.05))
        self.layoutpop_middle = GridLayout(rows=DELROWNUM,cols=2,padding=5,spacing=5,size_hint=(1, 0.9))
        self.layoutpop_page = GridLayout(rows=1,cols=12,padding=5,spacing=5,size_hint=(0.9, 0.05))

        self.basepop.add_widget(self.layoutpop_top)
        self.basepop.add_widget(self.layoutpop_middle)
        self.basepop.add_widget(self.layoutpop_page)

        self.popText=Label(font_name=todayFont,font_size=menu_fontsize,text = 'Choose the song.',size_hint=(0.9, 0.2),color=textColor)
        self.delBtn = Button(font_name=todayFont,font_size=menu_fontsize,text="-",size_hint=(0.05, 0.2), background_normal = "", background_down = "",background_color=boxColor,color=textColor)

        self.editBtn = Button(font_name=todayFont,font_size=menu_fontsize,text="edit",size_hint=(0.05, 0.2), background_normal = "", background_down = "",background_color=boxColor,color=textColor)

        self.delBtn.bind(on_press = self.del_pressed) #"-"버튼 클릭시, userlist의 곡삭제 함수호출
        self.editBtn.bind(on_press=lambda instance : self.open_userTitlePopup(obj))
        #self.editBtn.bind(on_press=self.open_userTitlePopup)
        self.layoutpop_top.add_widget(self.popText)
        self.layoutpop_top.add_widget(self.delBtn)
        self.layoutpop_top.add_widget(self.editBtn)


        for i in range(DELROWNUM):
            if i <= delListNum-1:
                title = DELLISTS[i].split(".wav")
                self.userListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'{title[0]}',halign="left",valign="top",size_hint=(0.9, 0.2), color=[1,1,1,1])
                self.checkboxBtn=CheckBox(size_hint=(0.1, 0.2),color=winColor)

                self.checkboxBtn.bind(active=self.checked_userlistSong)#check된 list 파악 함수 호출
                DELLISTSTEXT[i][0] = f'{DELLISTS[i]}'
                DELLISTSDIC[DELLISTSTEXT[i][0]]=self.checkboxBtn
            if i > delListNum-1:
                self.userListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'{i}',halign="left",valign="top",size_hint=(0.9, 0.2), color=[0,0,0,0])
                self.checkboxBtn=CheckBox(size_hint=(0.1, 0.2),color=[0,0,0,0])

                #self.checkboxBtn.bind(active=self.checked_userlistSong)
                DELLISTSTEXT[i][0] = f'{i}'
                DELLISTSDIC[DELLISTSTEXT[i][0]]=self.checkboxBtn

            self.layoutpop_middle.add_widget(self.userListLabel)
            self.layoutpop_middle.add_widget(self.checkboxBtn)

        #=====페이지버튼 추가하기 전에 계산============================================
        pageLISTNOpop = delListNum//(DELROWNUM) #총userlist수(ex.236) // 한페지화면의userlist수(15) == 총페이지개수(15, 나머지있으면 16)
        lastLISTNOpop = delListNum%(DELROWNUM) #총userlist수 % 한페지화면의userlist수(15) == 마지막페이지에보여질userlist수(ex.11) => 총페이지개수(15+나머지=16)
        if lastLISTNOpop > 0:
            pageLISTNOpop+=1
        pageSetLISTNOpop = pageLISTNOpop // 10 # 총페이지개수 //한레이아웃페이지수(1~10페이지) ==  다음 >> 넘기는 횟수와 동일
        lastPageLISTNOpop = pageLISTNOpop % 10 #총페이지개수 % 한레이아웃페이지수(1~10페이지) == 마지막에 남은 보여줄 버튼 개수(6)

        #=====페이지버튼 추가=======================================================

        if delListNum > DELROWNUM:

            for i in range(len(POPDELBTNLIST)):
                self.popdelBTN = Button(font_name=todayFont,font_size=text_fontsize,text=f"{i}",size_hint=(0.1, 0.2), background_color=winColor,color=textColor)
                if pageSetLISTNOpop  == 0 and i > lastPageLISTNOpop:
                        self.popdelBTN.background_color=[0,0,0,0]
                        self.popdelBTN.color=[0,0,0,0]
                else:
                    if i == 0:#첫번째인덱스
                        self.popdelBTN.text = "<<"
                    if i == 11:#마지막인덱스
                        self.popdelBTN.text = ">>"
                    self.popdelBTN.bind(on_press=self.press_popdelBTN)#페이지번호 클릭시, 화면리셋 함수 호출

                POPDELBTNLIST[i] = self.popdelBTN
                self.layoutpop_page.add_widget(self.popdelBTN)

            #print(DELLISTSTEXT,"\n",DELLISTSDIC,"\n")

        self.delUserlistSongPopup.add_widget(self.basepop)
        self.delUserlistSongPopup.open()

    #==============팝업창(userlist dir 생성&삭제)===================================
    def makeListPop(self, obj):
        self.makeListPopup = Popup(title='',
              size_hint=(0.5, 0.4), size=(800, 800),auto_dismiss=True,
              title_font=todayFont,title_size=menu_fontsize, title_align='center',
              title_color=textColor,
              separator_height=0.5,
              separator_color=textColor)

        self.lowerContent = StackLayout(orientation="lr-tb",padding=10,spacing=10)
        self.makeListText=Label(font_name=todayFont,font_size =menu_fontsize,text = 'Write list name.',width=40, height=30,size_hint=(1, 0.2),color=textColor)
        self.lowerContent.add_widget(self.makeListText)

        self.listNameText = TextInput(font_name=todayFont,multiline = False,width=40, height=30,size_hint=(1, 0.2))
        self.lowerContent.add_widget(self.listNameText)

        self.listMakeBtn = Button(font_name=todayFont,font_size =menu_fontsize,text="Create",width=40, height=30,size_hint=(0.5, 0.16), background_normal = "", background_color=boxColor,color=textColor)
        self.listMakeBtn.bind(on_press = self.press_listMake) #userlist dir 생성
        self.lowerContent.add_widget(self.listMakeBtn)

        self.listDeleteBtn = Button(font_name=todayFont,font_size =menu_fontsize,text="Delete",width=40, height=30,size_hint=(0.5, 0.16), background_normal = "", background_color=boxColor,color=textColor)
        self.listDeleteBtn.bind(on_press = self.press_listDelete) #userlist dir 삭제
        self.lowerContent.add_widget(self.listDeleteBtn)

        self.makeListPopup.add_widget(self.lowerContent)

        self.makeListPopup.open()

    #==============userlist dir 생성 & 반영된 화면 리셋==============================
    def press_listMake(self, obj):
        print("List Name:", self.listNameText.text)
        listName = f'{self.listNameText.text}'
        try:
            res = sbu.make_userlist(listName)

            if res == False:
                print("Can't created. there is same list.")
            else:
                print(f'{listName} was created.')

                self.base1.clear_widgets()
                self.drawMylist()
        except Exception as msg:
                self.makeListPopup.title = f"{msg}Retry."

        self.listNameText.text = ""

    #==============userlist dir 삭제 & 반영된 화면 리셋==============================
    def press_listDelete(self, obj):
        print("List Name:", self.listNameText.text)
        listName = f'{self.listNameText.text}'
        try:
            res = sbu.delete_userlist(listName)
            if res == False:
                print("Can't delete. there is no such listname.")
            else:
                print(f'{listName} was deleted.')

                self.base1.clear_widgets()
                self.drawMylist()
        except Exception as msg:
                self.makeListPopup.title = f"{msg}Retry."

        self.listNameText.text = ""

    #=====userlist title 변경 popup> self.res_touchTitle> sbu.touch_userTitle=====
    def open_userTitlePopup(self,listobj):
        self.titlePopup = Popup(title='',
              size_hint=(0.5, 0.4), size=(800, 800),auto_dismiss=True,
              title_font=todayFont,title_size=menu_fontsize, title_align='center',
              title_color=textColor,
              separator_height=0.5,
              separator_color=textColor)

        for i in range(ROWNUM):
            if NOWLISTSDIC[NOWLISTSTEXT[i][1]] == listobj:
                beforeTitle = NOWLISTSTEXT[i][0]

        self.lowerContent = StackLayout(orientation="lr-tb",padding=10,spacing=10)
        self.titlePopupText=Label(font_name=todayFont,font_size=menu_fontsize,text = 'Write new title',width=40, height=30,size_hint=(1, 0.2),color=textColor)
        self.lowerContent.add_widget(self.titlePopupText)

        self.lowerContent.add_widget(Label(font_name = todayFont,font_size=menu_fontsize,text='New Title?',width=40, height=30,size_hint=(0.2, 0.16),color=textColor))
        self.newTitle = TextInput(font_name=todayFont,multiline = False,width=40, height=30,size_hint=(0.8, 0.16))
        self.lowerContent.add_widget(self.newTitle)

        self.submit = Button(font_name=todayFont,font_size=menu_fontsize,text="Edit",width=40, height=30,size_hint=(0.33, 0.16), background_normal = "", background_color=boxColor,color=textColor)

        self.submit.bind(on_press=lambda instance : self.res_touchtitle(self.titlePopup,beforeTitle,self.newTitle))

        self.lowerContent.add_widget(self.submit)
        self.titlePopup.add_widget(self.lowerContent)

        self.titlePopup.open()

    #=============sbu.touch_userTitle 결과 받아서 화면 리셋==========================
    def res_touchtitle(self,titlePopup,beforeTitle,newTitle):
        self.titlePopup.dismiss()
        try:
            res = sbu.touch_userTitle(titlePopup,beforeTitle,newTitle)

            if res == False:
                print("Can't rename.")
            else:
                print(f'changed.')
                self.base1.clear_widgets()
                self.drawMylist()
        except Exception as msg:
                print(f"{msg}Retry.")

    #==============del popup창의 페이지번호 화면에 그리기==============================
    def press_popdelBTN(self, obj):
        BTNnum = obj.text#클릭된 버튼의 text
        nowpageQ = int(POPDELBTNLIST[1].text)#두번째 버튼의 text
        #===<<,>>버튼이 클릭되었을 경우에, 보여줄 화면 파악하기 위하여
        if nowpageQ > 10:
            nowpageA = ((nowpageQ-1)//10)
        else:
            nowpageA = 0
        #print(f"final nowpageQ{nowpageQ},nowpageA{nowpageA}")

        #=====페이지버튼 추가하기 전에 계산============================================
        DELLISTS = sbu.show_oneUserlist(CHECKEDONEUSERLIST)
        DELLISTS.sort()
        delListNum = len(DELLISTS)
        pageLISTNOpop = delListNum//(DELROWNUM) #총userlist수(ex.236) // 한페지화면의userlist수(15) == 총페이지개수(15, 나머지있으면 16)
        lastLISTNOpop = delListNum%(DELROWNUM) #총userlist수 % 한페지화면의userlist수(15) == 마지막페이지에보여질userlist수(ex.11) => 총페이지개수(15+나머지=16)
        if lastLISTNOpop > 0:
            pageLISTNOpop+=1
        pageSetLISTNOpop = pageLISTNOpop // 10 # 총페이지개수 //한레이아웃페이지수(1~10페이지) ==  다음 >> 넘기는 횟수와 동일
        lastPageLISTNOpop = pageLISTNOpop % 10 #총페이지개수 % 한레이아웃페이지수(1~10페이지) == 마지막에 남은 보여줄 버튼 개수(6)
        print(f"ScreenSetting_POPUP:: BTNnum:{BTNnum}, pageLISTNOpop:{pageLISTNOpop}")

        #=====페이지버튼의 숫자 바꾸기================================================
        if BTNnum == "<<":
            if nowpageA != 0:
                for i in range(1,len(POPDELBTNLIST)):
                    if nowpageA != "1": #1-10은 "<<"버튼은 작동 안하기에
                        POPDELBTNLIST[i].text = str((nowpageA-1)*10+i)
                        POPDELBTNLIST[i].background_color=winColor
                        POPDELBTNLIST[i].color=textColor
                    if i == 11:#
                        POPDELBTNLIST[i].text = ">>"
                        POPDELBTNLIST[i].background_color=winColor
                        POPDELBTNLIST[i].color=textColor
            endIndex = int(POPDELBTNLIST[1].text)*FIXROW
        elif BTNnum == ">>":
            if pageSetLISTNOpop == nowpageA+1:#userlist의 곡개수의 페이지번호까지만 보여주기
                #print(f"BTN set: pageSetNO{pageSetLISTNOpop},nowpageA{nowpageA}")
                for i in range(1,len(POPDELBTNLIST)):
                    POPDELBTNLIST[i].text = str((nowpageA+1)*10+i)#페이지버튼의 번호바꾸기
                    if i > lastPageLISTNOpop:#마지막페이지일 경우, 남은 userlist의 곡개수만큼만 화면에 보여주기
                        POPDELBTNLIST[i].background_color=[0,0,0,0]
                        POPDELBTNLIST[i].color=[0,0,0,0]
            else:#페이지버튼의 번호바꾸기
                for i in range(1,len(POPDELBTNLIST)):
                    POPDELBTNLIST[i].text = str((nowpageA+1)*10+i)
                    POPDELBTNLIST[i].background_color=winColor
                    POPDELBTNLIST[i].color=textColor
                    if i == 11:#">>" 바뀌지 않도로
                        POPDELBTNLIST[i].text = ">>"
                        POPDELBTNLIST[i].background_color=winColor
                        POPDELBTNLIST[i].color=textColor
            endIndex = int(POPDELBTNLIST[1].text)*FIXROW
        else:
            endIndex = int(BTNnum)*FIXROW
        startIndex = endIndex - (FIXROW-1)

        #=====화면 리셋===========================================================
        count = 0
        self.layoutpop_middle.clear_widgets()
        for i in range(startIndex,endIndex+1):#그때그때 인덱스를 지정, 보여줄 화면
            if str(BTNnum) == str(pageLISTNOpop) and lastLISTNOpop != 0:
                sub = (FIXROW-lastLISTNOpop)
                overIndex = endIndex-sub
                title = DELLISTS[i-1].split(".wav")
                if i > overIndex:#마지막페이지의 userlist 곡 수보다 i 가 크면, 위젯을 안보이도록 처리
                    self.userListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'',halign="left",valign="top",size_hint=(0.9, 0.2), color=[0,0,0,0])
                    self.checkboxBtn=CheckBox(size_hint=(0.1, 0.2),color=winColor)
                else:
                    self.userListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'{title[0]}',halign="left",valign="top",size_hint=(0.9, 0.2), color=[1,1,1,1])
                    self.checkboxBtn=CheckBox(size_hint=(0.1, 0.2),color=winColor)

                    self.checkboxBtn.bind(active=self.checked_userlistSong)
                    DELLISTSTEXT[count][0] = f'{DELLISTS[i-1]}'
                    DELLISTSDIC[DELLISTSTEXT[count][0]]=self.checkboxBtn
            else:
                self.userListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'{title[0]}',halign="left",valign="top",size_hint=(0.9, 0.2), color=[1,1,1,1])
                self.checkboxBtn=CheckBox(size_hint=(0.1, 0.2),color=winColor)

                self.checkboxBtn.bind(active=self.checked_userlistSong)
                DELLISTSTEXT[count][0] = f'{DELLISTS[i-1]}'
                DELLISTSDIC[DELLISTSTEXT[count][0]]=self.checkboxBtn

            self.layoutpop_middle.add_widget(self.userListLabel)
            self.layoutpop_middle.add_widget(self.checkboxBtn)
            count+=1

    #==============userlist 팝업창에서 저장된 곡 중에, 체크한 곡 알기위한 함수==============
    def checked_userlistSong(self, checkbox, yes_check):
        #thisTitle = ''
        if yes_check:
            for i in range(len(DELLISTSTEXT)):
                if DELLISTSDIC[DELLISTSTEXT[i][0]] == checkbox:
                    thisTitle = DELLISTSTEXT[i][0]
                    #print(f"checked one song{DELLISTSTEXT[i][0]}")
                    if DELLISTSDIC[DELLISTSTEXT[i][0]] not in CHECKEDONEUSERSONG:
                        CHECKEDONEUSERSONG.append(thisTitle)
                        #print(f"add one song{DELLISTSTEXT[i][0]}")
                elif DELLISTSDIC[DELLISTSTEXT[i][0]] != checkbox:
                    thisTitle = DELLISTSTEXT[i][0]
                    #print(f"no checked one song{DELLISTSTEXT[i][0]}")
                    if DELLISTSDIC[DELLISTSTEXT[i][0]] in CHECKEDONEUSERSONG:
                        CHECKEDONEUSERSONG.remove(DELLISTSDIC[DELLISTSTEXT[i][0]])
                        #print(f"delete no checked one song{DELLISTSTEXT[i][0]}")

    #==============userlist팝업창의 '-'버튼 클릭하면, 체크된 곡 삭제=====================
    def del_pressed(self, obj):
        #print(f"CHECKEDONEUSERLIST:{CHECKEDONEUSERLIST}\nCHECKEDONEUSERSONG:{CHECKEDONEUSERSONG}")
        for i in os.listdir(f"{userListDir}\\{CHECKEDONEUSERLIST}"):
            if i in CHECKEDONEUSERSONG:
                os.remove(f"{userListDir}\\{CHECKEDONEUSERLIST}\\{i}")
                #print(f"removed this song: {userListDir}/{CHECKEDONEUSERLIST}/{i}")

    #==============userlist버튼 클릭시, play thread 시작===================
    def playUserlist(self, playBtn):
        global playTitle,playing #playing은 재생곡의 위젯
        #print(f"userlist_playing:{playing}")
        PAUSE_BTN.text = "|||"
        PAUSE_BTN.color = boxColor
        PAUSE_BTN.texture_update()

        playTitle = []
        playList = []
        playing = []

        for i in range(len(NOWLISTSTEXT)):
            if NOWLISTSDIC[NOWLISTSTEXT[i][0]] == playBtn:
                thisTitle = NOWLISTSTEXT[i][0]
                playTitle = os.listdir(f"{userListDir}\\{thisTitle}")
                playing.append(playBtn)
                break
        print(f"playTitle{playTitle}")
        playTitle.sort()
        for i in playTitle:
            if i in ignoreFile:
                playTitle.remove(i)
        print(f"playTitle:{playTitle}")

        sbp.get_restart()
        playnum = 0
        thread_one = threading.Thread(target = sbp.get_playThread, args = (playTitle,playing,PLAY_BTN,playBtn,playnum), daemon=True)
        thread_one.start()

#==============class ScreenSong=================================================
class ScreenSong(Screen):
    def __init__(self, **kwargs):
        super(ScreenSong, self).__init__(**kwargs)
        global SONGROWNUM, SONGNOWLISTS, SONGNOWLISTSTEXT, SONGNOWLISTSDIC, CHECKBOXLISTS, CHECKEDSONG, CHECKEDUSERLIST, SONGBTNLIST, POPADDBTNLIST
        self.name = "screen_song"

        SONGNOWLISTS = sbl.show_Song()#총 곡
        SONGNOWLISTS.sort()

        SONGROWNUM = FIXROW#한 페이지번호에 보여줄 곡 수

        SONGNOWLISTSTEXT = [['']*3 for x in range(SONGROWNUM)]#한 화면의 곡 수 만큼만 저장
        SONGNOWLISTSDIC = {}
        CHECKBOXLISTS = [''] * (SONGROWNUM)#체크박스

        CHECKEDSONG = []
        CHECKEDUSERLIST = []

        SONGBTNLIST = ['']*12#한 화면에 보여줄 페이지번호 개수(<<, 1~10, >>)
        POPADDBTNLIST = ['']*12#userlist popup페이지버튼(지정한 목록 15개 초과시)

        self.base = BoxLayout(padding=5,spacing=5,size_hint=(1,1), orientation = 'vertical')
        self.add_widget(self.base)
        self.drawSonglist()

    #==============SongScreen 위젯 추가===========================================
    def drawSonglist(self):
        SONGNOWLISTS = sbl.show_Song()#총 곡
        SONGNOWLISTS.sort()
        songListNum = len(SONGNOWLISTS)
        #print(f"songListNum:{songListNum}")

        pageNO = songListNum//(SONGROWNUM) #총곡수(ex.236) // 한페지화면의곡수(15) == 총페이지개수(15, 나머지있으면 16)
        lastsongNum = songListNum%(SONGROWNUM) #총곡수 % 한페지화면의곡수(15) == 마지막페이지에보여질곡수(ex.11) => 총페이지개수(15+나머지=16)
        if lastsongNum > 0:
            pageNO+=1
        pageSetNO = pageNO // 10 # 총페이지개수 //한레이아웃페이지수(1~10페이지) ==  다음 >> 넘기는 횟수와 동일
        lastPageNO = pageNO % 10 #총페이지개수 % 한레이아웃페이지수(1~10페이지) == 마지막에 남은 보여줄 버튼 개수(6)
        #print(f"pageNO:{pageNO}, lastsongNum:{lastsongNum}")

        self.layout_top = GridLayout(rows=1,cols=9,padding=5,spacing=5,size_hint=(1, 0.05))
        self.layout_middle = GridLayout(rows=SONGROWNUM,cols=9,padding=5,spacing=5,size_hint=(1, 0.9))
        self.layout_page = GridLayout(rows=1,cols=12,padding=5,spacing=5,size_hint=(0.9, 0.05))

        self.base.add_widget(self.layout_top)
        self.base.add_widget(self.layout_middle)
        self.base.add_widget(self.layout_page)

        self.titleEmptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
        self.titleEmptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
        self.topLabel=Label(font_name=todayFont,font_size=menu_fontsize,text ='Song List',halign="left",valign="top",size_hint=(1, 0.2))
        self.titleEmptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
        self.titleEmptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
        self.titleEmptyLabel5=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
        self.addUserlistBtn = Button(font_name=todayFont,font_size=menu_fontsize,text="+ MyList",size_hint=(0.9, 0.03), background_normal = "",background_down = "",background_color=[0,0,0,0],color=boxColor)
        self.titleEmptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))

        self.addUserlistBtn.bind(on_press = self.add_checkedsong)

        self.layout_top.add_widget(self.titleEmptyLabel1)
        self.layout_top.add_widget(self.titleEmptyLabel2)
        self.layout_top.add_widget(self.topLabel)
        self.layout_top.add_widget(self.titleEmptyLabel3)
        self.layout_top.add_widget(self.titleEmptyLabel4)
        self.layout_top.add_widget(self.titleEmptyLabel5)
        self.layout_top.add_widget(self.addUserlistBtn)
        self.layout_top.add_widget(self.titleEmptyLabel6)

        for i in range(SONGROWNUM):


            if i > songListNum-1:
                title = i
                self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.songLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'',halign="left",valign="middle",size_hint=(1, 0.2), color=[0,0,0,0])
                self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.checkBox=CheckBox(size_hint=(1, 0.2),color=[0,0,0,0])
                self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.editBtn = Button(font_name=todayFont,font_size=text_fontsize,text="edit", size_hint=(0.9, 0.03), background_normal = "", background_color=[0,0,0,0],color=[0,0,0,0])
                self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))

            elif i <= songListNum-1:
                title = SONGNOWLISTS[i][:-4]
                tempTitle = title.split('* ')

                self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.songLabel=Button(font_name=todayFont,font_size=text_fontsize,text = f'{title}',halign="left",valign="middle",size_hint=(2, 0.2), background_normal = "", background_down = "",background_color=[0,0,0,0], color=textColor)
                self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.checkBox=CheckBox(size_hint=(1, 0.2),color=textColor)
                self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.editBtn = Button(font_name=todayFont,font_size=text_fontsize,text="edit",size_hint=(0.9, 0.03), background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)
                self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))


                self.checkBox.bind(active=self.checked_song)
                self.songLabel.bind(on_press=self.play_oneSong)
                self.editBtn.bind(on_press=self.open_titlePopup)

                if len(tempTitle) > 1:
                    print(f'draw start tempTitle{tempTitle}')
                    SONGNOWLISTSTEXT[i][0] = f'{tempTitle[1]}.wav'
                else:
                    SONGNOWLISTSTEXT[i][0] = f'{title}.wav'

                SONGNOWLISTSTEXT[i][1] = f'{title}+edit'
                SONGNOWLISTSTEXT[i][2] = f'{title}+checkbox'
                SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][0]]=self.songLabel
                SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][1]]=self.editBtn
                SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][2]]=self.checkBox

            self.layout_middle.add_widget(self.emptyLabel1)
            self.layout_middle.add_widget(self.emptyLabel2)
            self.layout_middle.add_widget(self.songLabel)
            self.layout_middle.add_widget(self.emptyLabel3)
            self.layout_middle.add_widget(self.emptyLabel4)
            self.layout_middle.add_widget(self.emptyLabel6)
            self.layout_middle.add_widget(self.checkBox)
            self.layout_middle.add_widget(self.editBtn)
            self.layout_middle.add_widget(self.emptyLabel7)
        #=====페이지번호위젯추가=====================================================
        if songListNum > SONGROWNUM:

            for i in range(len(SONGBTNLIST)):
                self.SONGBTN = Button(font_name=todayFont,font_size=text_fontsize,text=f"{i}",size_hint=(0.1, 0.2), background_color=winColor,color=textColor)
                if pageSetNO == 0 and i > lastPageNO :#(ex.<< 1 2 3 4 5 6 7 8 9 10 >>의 버튼 12개 중에 총곡수가 첫번째 페이지세트에 국한될 경우.
                        self.SONGBTN.background_color=[0,0,0,0]
                        self.SONGBTN.color=[0,0,0,0]
                else:
                    if i == 0:
                        self.SONGBTN.text = "<<"
                    if i == 11:
                        self.SONGBTN.text = ">>"

                    self.SONGBTN.bind(on_press=self.press_songBTN)#페이지번호클릭시,화면리셋함수호출

                SONGBTNLIST[i] = self.SONGBTN
                self.layout_page.add_widget(self.SONGBTN)
        else:
            self.SONGBTN = Button(font_name=todayFont,font_size=text_fontsize,text="1",size_hint=(0.1, 0.2), background_color=winColor,color=textColor)
            SONGBTNLIST[1] = self.SONGBTN

    #==============곡명 수정 popup창 -> sbl.touch_title 호출========================
    def open_titlePopup(self, obj):
        self.titlePopup = Popup(title='',
              size_hint=(0.5, 0.4), size=(800, 800),auto_dismiss=True,
              title_font=todayFont,title_size=menu_fontsize, title_align='center',
              title_color=textColor,
              separator_height=0.5,
              separator_color=textColor)

        for i in range(SONGROWNUM):
            if SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][1]]==obj:
                beforeTitle = SONGNOWLISTSTEXT[i][1]
                print(beforeTitle)
                break

        self.lowerContent = StackLayout(orientation="lr-tb",padding=10,spacing=10)
        self.titlePopupText=Label(font_name=todayFont,font_size=menu_fontsize,text = 'Write title & singer.',width=40, height=30,size_hint=(1, 0.2),color=textColor)
        self.lowerContent.add_widget(self.titlePopupText)

        self.lowerContent.add_widget(Label(font_name = todayFont,font_size=menu_fontsize,text='Title?',width=40, height=30,size_hint=(0.2, 0.16),color=textColor))
        self.song = TextInput(font_name=todayFont,multiline = False,width=40, height=30,size_hint=(0.8, 0.16))
        self.lowerContent.add_widget(self.song)

        self.lowerContent.add_widget(Label(font_name=todayFont,font_size=menu_fontsize,text = 'Singer?',width=40, height=30,size_hint=(0.2, 0.16),color=textColor))
        self.singer = TextInput(font_name=todayFont,multiline = False,width=40, height=30,size_hint=(0.8, 0.16))
        self.lowerContent.add_widget(self.singer)

        self.songBoxSubmit = Button(font_name=todayFont,font_size=menu_fontsize,text="Edit",width=40, height=30,size_hint=(0.33, 0.16), background_normal = "", background_color=boxColor,color=textColor)

        self.songBoxSubmit.bind(on_press=lambda instance : self.call_touchtitle(beforeTitle))

        self.lowerContent.add_widget(self.songBoxSubmit)
        self.titlePopup.add_widget(self.lowerContent)

        self.titlePopup.open()

    #==============song edit->change title(1.song 2.singer)=====================
    def call_touchtitle(self,beforeTitle):

        res = sbl.touch_title(beforeTitle,self.song,self.singer)

        if res == True:
            manager.screen_song.layout_middle.clear_widgets()#songlist 레이아웃 지우기
            manager.screen_song.press_songBTN(tempObj)#songlist 다시그리기

            manager.screen_singer.base1.clear_widgets()
            manager.screen_singer.drawMylist()

        self.titlePopup.dismiss()

    #==============페이지번호 눌렀을 때, 화면 리셋 함수==================================
    def press_songBTN(self, obj):
        BTNnum = obj.text

        nowpageQ = int(SONGBTNLIST[1].text)#클릭했을 때의 몇번째의 페이지셋이었는지 알기위함
        if nowpageQ > 10: #클릭했을 때의 페이지세트가 첫번째세트가 아니었다면,
            nowpageA = ((nowpageQ-1)//10)
        else:
            nowpageA = 0
            #print(f"nowpageQ{nowpageQ},nowpageA{nowpageA}")
        #print(f"final nowpageQ{nowpageQ},nowpageA{nowpageA}")

        SONGNOWLISTS = sbl.show_Song()
        SONGNOWLISTS.sort()
        songListNum = len(SONGNOWLISTS)
        #ex.236= 150*1+86(15*5+11)(마지막페이지는 나머지곡수만큼리셋)
        pageNO = songListNum//(SONGROWNUM) #총곡수(ex.236) // 한페지화면의곡수(15) == 총페이지개수(15, 나머지있으면 16)
        lastsongNum = songListNum%(SONGROWNUM) #총곡수 % 한페지화면의곡수(15) == 마지막페이지에보여질곡수(ex.11) => 총페이지개수(15+나머지=16)
        if lastsongNum > 0:
            pageNO+=1
        pageSetNO = pageNO // 10 # 총페이지개수 //한레이아웃페이지수(1~10페이지) ==  다음 >> 넘기는 횟수와 동일
        lastPageNO = pageNO % 10 #총페이지개수 % 한레이아웃페이지수(1~10페이지) == 마지막에 남은 보여줄 버튼 개수(6)

        if len(SONGNOWLISTS) < FIXROW:
            lastsongNum = len(SONGNOWLISTS)

        print(f"ScreenSong:: BTNnum:{BTNnum}, pageNO:{pageNO}")
        if BTNnum == "<<":#<<버튼 클릭시,
            if nowpageA != 0:#첫번째페이지셋이 아니었다면,
                for i in range(1,len(SONGBTNLIST)):
                    if nowpageA != "1":#첫번째페이지세트에서는 <<버튼은 작동할필요가없으므로,
                        SONGBTNLIST[i].text = str((nowpageA-1)*10+i)
                        SONGBTNLIST[i].background_color=winColor
                        SONGBTNLIST[i].color=textColor
                    if i == 11:#>>라면,
                        SONGBTNLIST[i].text = ">>"
                        SONGBTNLIST[i].background_color=winColor
                        SONGBTNLIST[i].color=textColor
            endIndex = int(SONGBTNLIST[1].text)*FIXROW
        elif BTNnum == ">>":#>>버튼 클릭시,
            if pageSetNO == nowpageA+1:#마지막페이지세트일경우,
                #print(f"BTN set: pageSetNO{pageSetNO},nowpageA{nowpageA}")
                for i in range(1,len(SONGBTNLIST)):
                    SONGBTNLIST[i].text = str((nowpageA+1)*10+i)
                    if i > lastPageNO:#마지막페이지일경우,
                        SONGBTNLIST[i].background_color=[0,0,0,0]
                        SONGBTNLIST[i].color=[0,0,0,0]

            else:#마지막페이지세트 외의 경우에,
                for i in range(1,len(SONGBTNLIST)):
                    SONGBTNLIST[i].text = str((nowpageA+1)*10+i)
                    SONGBTNLIST[i].background_color=winColor
                    SONGBTNLIST[i].color=textColor
                    if i == 11:
                        SONGBTNLIST[i].text = ">>"
                        SONGBTNLIST[i].background_color=winColor
                        SONGBTNLIST[i].color=textColor
            endIndex = int(SONGBTNLIST[1].text)*FIXROW
        else:
            endIndex = int(BTNnum)*FIXROW#루프돌릴때, 끝인덱스번호
        startIndex = endIndex - (FIXROW-1)#루프돌릴때, 시작인덱스번호

        count = 0
        self.layout_middle.clear_widgets()#전화면지우기
        for i in range(startIndex,endIndex+1):#화면위젯다시추가
            if (str(BTNnum) == str(pageNO) and lastsongNum != 0): #마지막 페이지세트를 클릭했을경우,

                sub = (FIXROW-lastsongNum)
                overIndex = endIndex-sub

                #print(startIndex,endIndex,overIndex)
                #마지막페이지에 보여줄 곡까지만 그리기위함
                if i > overIndex:
                    self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.songLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'',halign="left",valign="middle",size_hint=(1, 0.2), color=[0,0,0,0])
                    self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.checkBox=CheckBox(size_hint=(1, 0.2),color=[0,0,0,0])
                    self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.editBtn = Button(font_name=todayFont,font_size=text_fontsize,text="edit", size_hint=(0.9, 0.03), background_normal = "", background_color=[0,0,0,0],color=[0,0,0,0])
                    self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                else:#SONGNOWLISTS 인덱스가 i-1 임을 유의, SONGNOWLISTSTEXT, SONGNOWLISTSDIC의 인덱스는 count임을 유의
                    self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint=(1, 0.2))
                    self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint=(1, 0.2))
                    self.songLabel=Button(font_name=todayFont,font_size=text_fontsize,text = f'{SONGNOWLISTS[i-1][:-4]}',halign="left",valign="middle",size_hint=(1, 0.2), background_normal = "", background_down = "",background_color=[0,0,0,0], color=textColor)
                    self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.checkBox=CheckBox(size_hint=(1, 0.2),color=textColor)
                    self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                    self.editBtn = Button(font_name=todayFont,font_size=text_fontsize,text="edit", size_hint=(0.9, 0.03), background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)
                    self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))

                    self.checkBox.bind(active=self.checked_song)
                    self.songLabel.bind(on_press = self.play_oneSong)
                    self.editBtn.bind(on_press=self.open_titlePopup)

                    tempTitle = SONGNOWLISTS[i-1].split('* ')
                    if len(tempTitle) > 1:
                        SONGNOWLISTSTEXT[count][0] = f'{tempTitle[1]}'
                        print(f'last pageBTN{tempTitle},{tempTitle[1]}')
                    else:
                        SONGNOWLISTSTEXT[count][0] = f'{SONGNOWLISTS[i-1]}'
                    SONGNOWLISTSTEXT[count][1] = f'{SONGNOWLISTS[i-1]}+edit'
                    SONGNOWLISTSTEXT[count][2] = f'{SONGNOWLISTS[i-1]}+checkbox'
                    SONGNOWLISTSDIC[SONGNOWLISTSTEXT[count][0]]=self.songLabel
                    SONGNOWLISTSDIC[SONGNOWLISTSTEXT[count][1]]=self.editBtn
                    SONGNOWLISTSDIC[SONGNOWLISTSTEXT[count][2]]=self.checkBox
            #마지막 페이지세트를 클릭하지않은경우,
            else:
                self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.songLabel=Button(font_name=todayFont,font_size=text_fontsize,text = f'{SONGNOWLISTS[i-1][:-4]}',halign="left",valign="middle",size_hint=(2, 0.2), background_normal = "", background_down = "",background_color=[0,0,0,0], color=textColor)
                self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.checkBox=CheckBox(size_hint=(1, 0.2),color=textColor)
                self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))
                self.editBtn = Button(font_name=todayFont,font_size=text_fontsize,text="edit",size_hint=(0.9, 0.03), background_normal = "", background_down = "",background_color=[0,0,0,0],color=boxColor)
                self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint=(1, 0.2))

                self.checkBox.bind(active=self.checked_song)
                self.songLabel.bind(on_press = self.play_oneSong)
                self.editBtn.bind(on_press=self.open_titlePopup)

                tempTitle = SONGNOWLISTS[i-1].split('* ')
                if len(tempTitle) > 1:
                    SONGNOWLISTSTEXT[count][0] = f'{tempTitle[1]}'
                    print(f'pageBTN{tempTitle},{tempTitle[1]}')
                else:
                    SONGNOWLISTSTEXT[count][0] = f'{SONGNOWLISTS[i-1]}'

                SONGNOWLISTSTEXT[count][1] = f'{SONGNOWLISTS[i-1]}+edit'
                SONGNOWLISTSTEXT[count][2] = f'{SONGNOWLISTS[i-1]}+checkbox'
                SONGNOWLISTSDIC[SONGNOWLISTSTEXT[count][0]]=self.songLabel
                SONGNOWLISTSDIC[SONGNOWLISTSTEXT[count][1]]=self.editBtn
                SONGNOWLISTSDIC[SONGNOWLISTSTEXT[count][2]]=self.checkBox

            self.layout_middle.add_widget(self.emptyLabel1)
            self.layout_middle.add_widget(self.emptyLabel2)
            self.layout_middle.add_widget(self.songLabel)
            self.layout_middle.add_widget(self.emptyLabel3)
            self.layout_middle.add_widget(self.emptyLabel4)
            self.layout_middle.add_widget(self.emptyLabel6)
            self.layout_middle.add_widget(self.checkBox)
            self.layout_middle.add_widget(self.editBtn)
            self.layout_middle.add_widget(self.emptyLabel7)
            count+=1

        #=====페이지 번호 바꾸고 난 후, 재생 중인 곡 표시위해서, playing 중인 obj의 곡명 저장
        playing = sbp.get_playResult()
        songs = {}
        for i in playing:
            tempTitle = i.text.split('* ')
            if len(tempTitle) > 1:
                song = f'{tempTitle[1]}.wav'
            else:
                song = f'{i.text}.wav'
            songs[song] = i
        print(f"playing-song name & obj: {songs}")
        #=====페이지 번호 바뀌어도, 재생 중인 곡 표시 & stop하면 작동하도록, 바뀐 obj playing에 저장
        for i in range(len(SONGNOWLISTSTEXT)):
            if SONGNOWLISTSTEXT[i][0] in songs.keys():
                SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][0]].color = stopColor
                playing.append(SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][0]])

    #==============체크된 곡을 userlist에 추가하는 팝업창 띄우는 함수=====================
    def add_checkedsong(self, obj):
        self.addUserlistPopup = Popup(title='',
              size_hint=(0.7, 1), size=(800, 800),auto_dismiss=True,
              title_font='Roboto',title_size=20, title_align='center',
              title_color=textColor,
              separator_height=0.5,
              separator_color=textColor)
        global POPROWNUM, POPLISTS, POPLISTSTEXT, POPLISTSDIC
        POPROWNUM = FIXROW
        POPLISTS = sbu.show_userlist()
        POPLISTS.sort()
        poplistNum = len(POPLISTS)
        POPLISTSTEXT = [['']*2 for x in range(POPROWNUM)]
        POPLISTSDIC = {}

        self.basepop1 = BoxLayout(padding=5,spacing=5,size_hint=(1,1), orientation = 'vertical')

        self.layoutpop1_top = GridLayout(rows=1,cols=2,padding=5,spacing=5,size_hint=(1, 0.05))
        self.layoutpop1_middle = GridLayout(rows=POPROWNUM,cols=2,padding=5,spacing=5,size_hint=(1, 0.9))
        self.layoutpop1_page = GridLayout(rows=1,cols=12,padding=5,spacing=5,size_hint=(0.9, 0.05))

        self.basepop1.add_widget(self.layoutpop1_top)
        self.basepop1.add_widget(self.layoutpop1_middle)
        self.basepop1.add_widget(self.layoutpop1_page)

        self.popText = Label(font_name=todayFont,font_size=menu_fontsize,text = 'Choose the userlist.',size_hint=(0.9, 0.2),color=textColor)
        self.addBtn = Button(font_name=todayFont,font_size=menu_fontsize,text="+",size_hint=(0.05, 0.2), background_normal = "", background_color=boxColor,color=textColor)

        self.addBtn.bind(on_press = self.add_pressed) #bind 콜벡함수연결함수

        self.layoutpop1_top.add_widget(self.popText)
        self.layoutpop1_top.add_widget(self.addBtn)

        for i in range(POPROWNUM):
            if i <= poplistNum-1:
                self.userListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'{POPLISTS[i]}',halign="left",valign="top",size_hint=(0.9, 0.2), color=[1,1,1,1])
                self.checkboxBtn=CheckBox(size_hint=(0.1, 0.2),color=winColor)

                self.checkboxBtn.bind(active=self.checked_userlist)
                POPLISTSTEXT[i][0] = f'{POPLISTS[i]}'
                POPLISTSDIC[POPLISTSTEXT[i][0]]=self.checkboxBtn
            if i > poplistNum-1:
                self.userListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'{i}',halign="left",valign="top",size_hint=(0.9, 0.2), color=[0,0,0,0])
                self.checkboxBtn=CheckBox(size_hint=(0.1, 0.2),color=[0,0,0,0])

                self.checkboxBtn.bind(active=self.checked_userlist)
                POPLISTSTEXT[i][0] = f'{i}'
                POPLISTSDIC[POPLISTSTEXT[i][0]]=self.checkboxBtn

            self.layoutpop1_middle.add_widget(self.userListLabel)
            self.layoutpop1_middle.add_widget(self.checkboxBtn)

        #=====페이지버튼 추가하기 전에 계산============================================
        pageLISTNOpopadd = poplistNum//(POPROWNUM) #총userlist dir수(ex.236) // 한페지화면의userlist dir수(15) == 총페이지개수(15, 나머지있으면 16)
        lastLISTNOpopadd = poplistNum%(POPROWNUM) #총userlist dir수 % 한페지화면의userlist수(15) == 마지막페이지에보여질userlist dir수(ex.11) => 총페이지개수(15+나머지=16)
        if lastLISTNOpopadd > 0:
            pageLISTNOpopadd+=1
        pageSetLISTNOpopadd = pageLISTNOpopadd // 10 # 총페이지개수 //한레이아웃페이지수(1~10페이지) ==  다음 >> 넘기는 횟수와 동일
        lastPageLISTNOpopadd = pageLISTNOpopadd % 10 #총페이지개수 % 한레이아웃페이지수(1~10페이지) == 마지막에 남은 보여줄 버튼 개수(6)

        #=====페이지버튼 추가=======================================================

        if poplistNum > POPROWNUM:

            for i in range(len(POPADDBTNLIST)):
                self.popaddBTN = Button(font_name=todayFont,font_size=text_fontsize,text=f"{i}",background_color=winColor,color=textColor)
                if pageSetLISTNOpopadd  == 0 and i > lastPageLISTNOpopadd:
                        self.popaddBTN.background_color=[0,0,0,0]
                        self.popaddBTN.color=[0,0,0,0]
                else:
                    if i == 0:#첫번째인덱스
                        self.popaddBTN.text = "<<"
                    if i == 11:#마지막인덱스
                        self.popaddBTN.text = ">>"
                    self.popaddBTN.bind(on_press=self.press_popaddBTN)#페이지번호 클릭시, 화면리셋 함수 호출

                POPADDBTNLIST[i] = self.popaddBTN
                self.layoutpop1_page.add_widget(self.popaddBTN)

        self.addUserlistPopup.add_widget(self.basepop1)
        self.addUserlistPopup.open()

    #==============add popup창의 페이지번호 화면에 그리기==============================
    def press_popaddBTN(self, obj):
        BTNnum = obj.text#클릭된 버튼의 text
        nowpageQ = int(POPADDBTNLIST[1].text)#두번째 버튼의 text
        #<<,>>버튼이 클릭되었을 경우에, 보여줄 화면 파악하기 위하여
        if nowpageQ > 10:
            nowpageA = ((nowpageQ-1)//10)
        else:
            nowpageA = 0
        #print(f"final nowpageQ{nowpageQ},nowpageA{nowpageA}")

        #=====페이지버튼 추가하기 전에 계산============================================
        poplistNum = len(POPLISTS)
        pageLISTNOpopadd = poplistNum//(POPROWNUM) #총userlist dir수(ex.236) // 한페지화면의userlist dir수(15) == 총페이지개수(15, 나머지있으면 16)
        lastLISTNOpopadd = poplistNum%(POPROWNUM) #총userlist dir수 % 한페지화면의userlist수(15) == 마지막페이지에보여질userlist dir수(ex.11) => 총페이지개수(15+나머지=16)
        if lastLISTNOpopadd > 0:
            pageLISTNOpopadd+=1
        pageSetLISTNOpopadd = pageLISTNOpopadd // 10 # 총페이지개수 //한레이아웃페이지수(1~10페이지) ==  다음 >> 넘기는 횟수와 동일
        lastPageLISTNOpopadd = pageLISTNOpopadd % 10 #총페이지개수 % 한레이아웃페이지수(1~10페이지) == 마지막에 남은 보여줄 버튼 개수(6)

        #=====페이지버튼의 숫자 바꾸기================================================
        if BTNnum == "<<":
            if nowpageA != 0:
                for i in range(1,len(POPADDBTNLIST)):
                    if nowpageA != "1": #1-10은 "<<"버튼은 작동 안하기에
                        POPADDBTNLIST[i].text = str((nowpageA-1)*10+i)
                        POPADDBTNLIST[i].background_color=winColor
                        POPADDBTNLIST[i].color=textColor
                    if i == 11:#
                        POPADDBTNLIST[i].text = ">>"
                        POPADDBTNLIST[i].background_color=winColor
                        POPADDBTNLIST[i].color=textColor
            endIndex = int(POPADDBTNLIST[1].text)*FIXROW
        elif BTNnum == ">>":
            if pageSetLISTNOpopadd == nowpageA+1:#userlist의 dir수의 페이지번호까지만 보여주기
                #print(f"BTN set: pageSetNO{pageSetLISTNOpopadd},nowpageA{nowpageA}")
                for i in range(1,len(POPADDBTNLIST)):
                    POPADDBTNLIST[i].text = str((nowpageA+1)*10+i)#페이지버튼의 번호바꾸기
                    if i > lastPageLISTNOpopadd:#마지막페이지일 경우, 남은 userlist의 dir수만큼만 화면에 보여주기
                        POPADDBTNLIST[i].background_color=[0,0,0,0]
                        POPADDBTNLIST[i].color=[0,0,0,0]
            else:#페이지버튼의 번호바꾸기
                for i in range(1,len(POPADDBTNLIST)):
                    POPADDBTNLIST[i].text = str((nowpageA+1)*10+i)
                    POPADDBTNLIST[i].background_color=winColor
                    POPADDBTNLIST[i].color=textColor
                    if i == 11:#">>" 바뀌지 않도로
                        POPADDBTNLIST[i].text = ">>"
                        POPADDBTNLIST[i].background_color=winColor
                        POPADDBTNLIST[i].color=textColor
            endIndex = int(POPADDBTNLIST[1].text)*FIXROW
        else:
            endIndex = int(BTNnum)*FIXROW
        startIndex = endIndex - (FIXROW-1)

        #=====화면 리셋===========================================================
        count = 0
        self.layoutpop1_middle.clear_widgets()
        for i in range(startIndex,endIndex+1):#그때그때 인덱스를 지정, 보여줄 화면
            if str(BTNnum) == str(pageLISTNOpopadd) and lastLISTNOpopadd != 0:
                sub = (FIXROW-lastLISTNOpopadd)
                overIndex = endIndex-sub
                if i > overIndex:#마지막페이지의 userlist dir수보다 i 가 크면, 위젯을 안보이도록 처리
                    self.userListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'',halign="left",valign="top",size_hint=(0.9, 0.2), color=[0,0,0,0])
                    self.checkboxBtn=CheckBox(size_hint=(0.1, 0.2),color=[0,0,0,0])
                else:#POPLISTS 의 인덱스가 i-1임을 유의, POPLISTSTEXT,POPLISTSDIC의 인덱스는 count임을 유의
                    self.userListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'{POPLISTS[i-1]}',halign="left",valign="top",size_hint=(0.9, 0.2), color=[1,1,1,1])
                    self.checkboxBtn=CheckBox(size_hint=(0.1, 0.2),color=[0,0,0,0])

                    self.checkboxBtn.bind(active=self.checked_userlist)
                    POPLISTSTEXT[count][0] = f'{POPLISTS[i-1]}'
                    POPLISTSDIC[POPLISTSTEXT[count][0]]=self.checkboxBtn
            else:
                self.userListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'{POPLISTS[i-1]}',halign="left",valign="top",size_hint=(0.9, 0.2), color=[1,1,1,1])
                self.checkboxBtn=CheckBox(size_hint=(0.1, 0.2),color=[0,0,0,0])

                self.checkboxBtn.bind(active=self.checked_userlist)
                POPLISTSTEXT[count][0] = f'{POPLISTS[i-1]}'
                POPLISTSDIC[POPLISTSTEXT[count][0]]=self.checkboxBtn

            self.layoutpop1_middle.add_widget(self.userListLabel)
            self.layoutpop1_middle.add_widget(self.checkboxBtn)
            count+=1

    #==============체크박스에 체크된 곡 알기위한 함수====================================
    def checked_userlist(self, checkbox, yes_check):
        #thisTitle = ''
        if yes_check:
            for i in range(len(POPLISTSTEXT)):
                if POPLISTSDIC[POPLISTSTEXT[i][0]] == checkbox:
                    thisTitle = POPLISTSTEXT[i][0]
                    if POPLISTSDIC[POPLISTSTEXT[i][0]] not in CHECKEDUSERLIST:
                        CHECKEDUSERLIST.append(thisTitle)
                elif POPLISTSDIC[POPLISTSTEXT[i][0]] != checkbox:
                    thisTitle = POPLISTSTEXT[i][0]
                    if POPLISTSDIC[POPLISTSTEXT[i][0]] in CHECKEDUSERLIST:
                        CHECKEDUSERLIST.remove(POPLISTSDIC[POPLISTSTEXT[i][0]])
        #print(CHECKEDSONG)
        #print(yes_check, checkbox, CHECKEDUSERLIST)

    #=============="+"버튼 클릭시, userlist에 곡추가위한 함수==========================
    def add_pressed(self,obj):
        titleList = []
        #thisTitle=''
        try:
            for i in range(len(SONGNOWLISTSTEXT)):
                if SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][2]] in CHECKEDSONG:
                    thisTitle = SONGNOWLISTSTEXT[i][0]
                    #print(f'yescheck {thisTitle}\n')
                    if thisTitle not in titleList:
                        titleList.append(thisTitle)
                    #    print(f'yestitle add {thisTitle}\n')
                elif SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][2]] not in CHECKEDSONG:
                    thisTitle = SONGNOWLISTSTEXT[i][0]
                    #print(f'nocheck {thisTitle}\n')
                    if thisTitle in titleList:
                        titleList.remove(thisTitle)
                        #print(f'notitle removed {thisTitle}\n')
            #print(f'titleList:{titleList}')
            sbu.copy_checkedsongTOuserlist(CHECKEDUSERLIST,titleList)
        except Exception as msg:
            print(f"{msg}retry.")

    #==============체크되었었던 곡 알기위한 함수========================================
    def checked_song(self, checkbox, yes_check):
        if yes_check:
            #print(f"yes:{checkbox}")
            if checkbox not in CHECKEDSONG:
                CHECKEDSONG.append(checkbox)
                #print(f"yes,append:{checkbox}")
        else:
            if checkbox in CHECKEDSONG:
                CHECKEDSONG.remove(checkbox)
                #print(f"remove:{checkbox}")
        #print(f"checked song:{CHECKEDSONG}")

    #==============체크된곡 재생===================================================
    def play_checkedSong(self):
        global playTitle,playing #playing은 재생곡의 위젯

        playTitle = []
        playing = []
        SONGNOWLISTSDIC[''] ='' #화면리셋오류때문에 범위 FIXROW로 고정->list 고정길이('')주느라-> dic에도('') 임의값 줌

        try:
            for i in range(SONGROWNUM):
                if SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][2]] in CHECKEDSONG:
                    thisTitle = SONGNOWLISTSTEXT[i][0]
                    #print(f'yescheck {thisTitle}\n')
                    if thisTitle not in playTitle:
                        playTitle.append(thisTitle)
                        playing.append(SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][0]])

                        #print(f'yestitle add {thisTitle}\n')
                elif SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][2]] not in CHECKEDSONG:
                    thisTitle = SONGNOWLISTSTEXT[i][0]
                    #print(f'nocheck {thisTitle}\n')
                    if thisTitle in playTitle:
                        playTitle.remove(thisTitle)
                        playing.remove(SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][0]])

            print(f"playTitle:{playTitle}")
            sbp.get_restart()
            playnum=0
            thread_one = threading.Thread(target=sbp.get_playThread, args=(playTitle,playing,PLAY_BTN,PLAY_BTN,playnum), daemon=True)
            thread_one.start()

        except Exception as msg:
            print(f"{msg}retry.")

    #==============한곡만 재생하는 thread 시작(무한루프로 재생)==========================
    def play_oneSong(self, playBtn):
        global playTitle,playing,TITLE_BTN
        TITLE_BTN = playBtn

        PAUSE_BTN.text = "|||"
        PAUSE_BTN.color = boxColor
        PAUSE_BTN.texture_update()

        playTitle=[]
        playing = []

        for i in range(len(SONGNOWLISTSTEXT)):
            if SONGNOWLISTSDIC[SONGNOWLISTSTEXT[i][0]] == TITLE_BTN:
                thisTitle = SONGNOWLISTSTEXT[i][0]
                playing.append(TITLE_BTN)
                print(thisTitle)
                break
        try:
            playTitle.append(thisTitle)
            print(f"playTitle:{playTitle}")

            sbp.get_quit()
            time.sleep(1)

            playnum=0
            thread_one = threading.Thread(target=sbp.get_playThread, args=(playTitle,playing,PLAY_BTN,TITLE_BTN,playnum), daemon=True)
            thread_one.start()

        except Exception as msg:
            print(f"{msg}retry.")
            #print(playTitle)


#==============(Scroll)class ScreenSinger=======================================
class ScreenSinger(Screen):
    def __init__(self, **kwargs):
        super(ScreenSinger, self).__init__(**kwargs)
        self.name = "screen_singer"
        global SINGER_NOWLISTS, SINGER_NOWLISTSTEXT, SINGER_NOWLISTSDIC, SINGER_CHECKBOXLISTS, CHECKEDSINGER, CHECKEDSINGERLIST
        SINGER_NOWLISTS = sbs.show_singer()#singerlist 목록 불러오기
        SINGER_NOWLISTS.sort()
        listNum = len(SINGER_NOWLISTS)

        SINGER_NOWLISTSTEXT = [['']*3 for x in range(listNum)]#저장한위젯저장
        SINGER_NOWLISTSDIC = {}#저장한위젯호출위해저장

        SINGER_CHECKBOXLISTS = [''] * listNum#체크박스

        CHECKEDSINGER = []
        CHECKEDSINGERLIST = []

        self.base1 = BoxLayout(padding=5,spacing=5,size_hint=(1,1), orientation = 'vertical')
        self.add_widget(self.base1)

        self.drawMylist()

    #==============draw widgets=================================================
    def drawMylist(self):
        global SINGER_NOWLISTSTEXT, SINGER_CHECKBOXLISTS
        SINGER_NOWLISTS = sbs.show_singer()#singerlist 목록 불러오기
        SINGER_NOWLISTS.sort()
        listNum = len(SINGER_NOWLISTS)

        #==============새 가수 추가된 경우, widget reset 시 오류 방지(scroll view라서)===
        if listNum > len(SINGER_NOWLISTSTEXT):
            SINGER_NOWLISTSTEXT = [['']*3 for x in range(listNum)]#저장한위젯저장
            SINGER_CHECKBOXLISTS = [''] * listNum#체크박스

        self.layout1_top = GridLayout(rows=1,cols=9,padding=5,spacing=5,size_hint=(1, 0.05))

        self.layout1_middle = GridLayout(rows=listNum,cols=9,padding=5,spacing=5,size_hint_y=None)
        self.layout1_middle.bind(minimum_height=self.layout1_middle.setter('height'),minimum_width=self.layout1_middle.setter('width'))

#####playBtn은 아직 기능 안줌
        self.titleEmptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint_y=None, height=55)
        self.titleEmptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint_y=None, height=55)
        self.titleEmptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint_y=None, height=55)
        self.topLabel=Label(font_name=todayFont,font_size =menu_fontsize,text ='Singer List',halign="left",valign="top", size_hint_y=None, height=55)#,color=boxColor)
        self.titleEmptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint_y=None, height=55)
        self.titleEmptyLabel5=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint_y=None, height=55)
        self.playBtn = Button(font_name=todayFont,font_size =menu_fontsize,text="???", size_hint_y=None, height=55, background_normal = "", background_down = "",background_color=[0,0,0,0],color=[0,0,0,0])
        self.titleEmptyLabel6=Label(font_name=todayFont,text ='',font_size=30,halign="left",valign="top", size_hint_y=None, height=55)

        #####self.playBtn.bind(on_press = self.)

        self.layout1_top.add_widget(self.titleEmptyLabel1)
        self.layout1_top.add_widget(self.titleEmptyLabel2)
        self.layout1_top.add_widget(self.topLabel)
        self.layout1_top.add_widget(self.titleEmptyLabel3)
        self.layout1_top.add_widget(self.titleEmptyLabel4)
        self.layout1_top.add_widget(self.titleEmptyLabel5)
        self.layout1_top.add_widget(self.playBtn)
        self.layout1_top.add_widget(self.titleEmptyLabel6)

        for i in range(listNum):
            self.emptyLabel1=Label(font_name=todayFont,text ='',halign="left",valign="top", size_hint_y=None, height=55)
            self.singerListBtn=Button(font_name=todayFont,font_size =text_fontsize,text=f'{SINGER_NOWLISTS[i]}', size_hint_y=None, height=55, background_normal = "", background_down = "",background_color=[0,0,0,0],color=textColor)
            self.emptyLabel2=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint_y=None, height=55)
            self.emptyLabel3=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint_y=None, height=55)
            self.emptyLabel4=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint_y=None, height=55)
            self.checkBox=CheckBox(size_hint=(1, 0.2),color=textColor,size_hint_y=None, height=55)
            self.emptyLabel6=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint_y=None, height=55)
            self.showBtn = Button(font_name=todayFont,font_size =text_fontsize,text="show", size_hint_y=None, height=55, background_normal = "",background_color=boxColor,color=textColor)
            self.emptyLabel7=Label(font_name=todayFont,text ='',halign="left",valign="top",size_hint_y=None, height=55)


            self.checkBox.bind(active=self.checked_song)
            self.singerListBtn.bind(on_press=self.play_singerlist)#singerlist의 곡 재생을 위한 함수 호출
            self.showBtn.bind(on_press=self.open_singerSongPopup)#singerlist의 곡 보기

            SINGER_NOWLISTSTEXT[i][0] = f'{SINGER_NOWLISTS[i]}'
            SINGER_NOWLISTSTEXT[i][1] = f'{SINGER_NOWLISTS[i]}+add/sub'
            SINGER_NOWLISTSTEXT[i][2] = f'{SINGER_NOWLISTS[i]}+checkbox'

            SINGER_NOWLISTSDIC[SINGER_NOWLISTSTEXT[i][0]]=self.singerListBtn
            SINGER_NOWLISTSDIC[SINGER_NOWLISTSTEXT[i][1]]=self.showBtn
            SINGER_NOWLISTSDIC[SINGER_NOWLISTSTEXT[i][2]]=self.checkBox

            self.layout1_middle.add_widget(self.emptyLabel1)
            self.layout1_middle.add_widget(self.singerListBtn)
            self.layout1_middle.add_widget(self.emptyLabel2)
            self.layout1_middle.add_widget(self.emptyLabel3)
            self.layout1_middle.add_widget(self.emptyLabel4)
            self.layout1_middle.add_widget(self.checkBox)
            self.layout1_middle.add_widget(self.emptyLabel6)
            self.layout1_middle.add_widget(self.showBtn)
            self.layout1_middle.add_widget(self.emptyLabel7)

        #==============singerlist scroll========================================
        self.scroll = ScrollView(smooth_scroll_end=10,scroll_type=['bars'],bar_width='3dp', scroll_wheel_distance=100, do_scroll_x = False, do_scroll_y = True)
        self.scroll.bar_color = boxColor
        #self.scroll.size_hint_min = (100,500)
        #self.scroll.size=(Window.width, Window.height)
        self.scroll.size_hint=(1, 1)
        #self.scroll.size_hint_y = None
        #self.scroll.padding= 10, 10

        self.scroll.add_widget(self.layout1_middle)

        self.base1.add_widget(self.layout1_top)
        self.base1.add_widget(self.scroll)

    #==============가수의 곡 목록 보기==============================================
    def open_singerSongPopup(self, obj):

        for i in range(len(SINGER_NOWLISTSTEXT)):
            if SINGER_NOWLISTSDIC[SINGER_NOWLISTSTEXT[i][1]] == obj:#클릭한 edit obj의 singerlist파악위해
                singer = SINGER_NOWLISTSTEXT[i][0]#singerlist이름저장

        singerlist = sbs.show_onerSinger(singer)
        singerlist.sort()
        songNum = len(singerlist)

        self.singerSongPopup = Popup(title='',
              size_hint=(0.5, 0.4), size=(800, 800),auto_dismiss=True,
              title_font=todayFont,title_size=menu_fontsize, title_align='center',
              title_color=textColor,
              separator_height=0.5,
              separator_color=textColor)

        self.basepop = BoxLayout(padding=5,spacing=5,size_hint=(1,None), orientation = 'vertical')
        self.basepop.bind(minimum_height=self.basepop.setter('height'),minimum_width=self.basepop.setter('width'))

        self.layoutpop_top = GridLayout(rows=1,cols=1,padding=5,spacing=5,size_hint_y=None)
        self.popText=Label(font_name=todayFont,font_size=menu_fontsize,text = f'{singer} Song List.',size_hint_y=None, height=40,color=textColor)
        self.layoutpop_top.add_widget(self.popText)


        self.layoutpop_middle = GridLayout(rows=songNum,cols=1,padding=5,spacing=5,size_hint_y=None)

        for i in range(songNum):
            title = singerlist[i].split(".wav")
            self.singerListLabel=Label(font_name=todayFont,font_size=text_fontsize,text = f'{title[0]}',halign="left",valign="top",size_hint_y=None, height=40,color=[1,1,1,1])
            self.layoutpop_middle.add_widget(self.singerListLabel)

        self.basepop.add_widget(self.layoutpop_top)
        self.basepop.add_widget(self.layoutpop_middle)

        #==============singerlist scroll========================================
        self.scroll = ScrollView(smooth_scroll_end=10,scroll_type=['bars'],bar_width='3dp', scroll_wheel_distance=100, do_scroll_x = False, do_scroll_y = True)
        self.scroll.bar_color = boxColor
        #self.scroll.size_hint_min = (100,500)
        #self.scroll.size=(Window.width, Window.height)
        self.scroll.size_hint=(1,1)
        #self.scroll.size_hint_y = None
        #self.scroll.padding= 10, 10
        self.scroll.add_widget(self.basepop)

        self.singerSongPopup.add_widget(self.scroll)
        self.singerSongPopup.open()

    #==============체크된 가수 알기위한 함수==========================================
    def checked_song(self, checkbox, yes_check):
        if yes_check:
            print(f"yes:{checkbox}")
            if checkbox not in CHECKEDSINGER:
                CHECKEDSINGER.append(checkbox)
                print(f"yes,append:{checkbox}")
        else:
            if checkbox in CHECKEDSINGER:
                CHECKEDSINGER.remove(checkbox)
                print(f"remove:{checkbox}")
        print(f"checked song:{CHECKEDSINGER}")

    #==============체크된 가수 재생=================================================
    def play_checkedSinger(self, obj):
        global playTitle,playing #playing은 재생곡의 위젯

        SINGER_NOWLISTS = sbs.show_singer()#singerlist 목록 불러오기
        SINGER_NOWLISTS.sort()
        listNum = len(SINGER_NOWLISTS)#singerlist 개수

        singerList = []
        playTitle = []
        playing = []

        try:
            for i in range(listNum):
                if SINGER_NOWLISTSDIC[SINGER_NOWLISTSTEXT[i][2]] in CHECKEDSINGER:
                    thisSinger = SINGER_NOWLISTSTEXT[i][0]
                    print(f'yescheck {thisSinger}\n')

                    if thisSinger not in singerList:
                        singerList.append(thisSinger)
                        for j in os.listdir(f'{singerListDir}\\{thisSinger}'):
                            if j not in ignoreFile:
                                playTitle.append(j)
                                playing.append(SINGER_NOWLISTSDIC[SINGER_NOWLISTSTEXT[i][0]])

                                print(f'yestitle add {j}\n')
                elif SINGER_NOWLISTSDIC[SINGER_NOWLISTSTEXT[i][2]] not in CHECKEDSINGER:
                    thisSinger = SINGER_NOWLISTSTEXT[i][0]
                    print(f'nocheck {thisSinger}\n')
                    if thisSinger in singerList:
                        singerList.remove(thisSinger)
                        for j in os.listdir(f'{singerListDir}\\{thisSinger}'):
                            if j not in ignoreFile:
                                playTitle.remove(j)
                                playing.remove(SINGER_NOWLISTSDIC[SINGER_NOWLISTSTEXT[i][0]])
                                print(f'del {j}\n')

            print(f"playTitle:{playTitle},playing:{playing}")
            sbp.get_restart()
            playnum=0
            thread_one = threading.Thread(target=sbp.get_playThread, args=(playTitle,playing,PLAY_BTN,PLAY_BTN,playnum), daemon=True)
            thread_one.start()

        except Exception as msg:
            print(f"{msg}retry.")

    #==============클릭된 가수 재생=================================================
    def play_singerlist(self, playBtn):
        global playTitle,playing #playing은 재생곡의 위젯
        #print(f"userlist_playing:{playing}")
        PAUSE_BTN.text = "|||"
        PAUSE_BTN.color = boxColor
        PAUSE_BTN.texture_update()

        playTitle = []
        playList = []
        playing = []

        for i in range(len(SINGER_NOWLISTSTEXT)):
            if SINGER_NOWLISTSDIC[SINGER_NOWLISTSTEXT[i][0]] == playBtn:
                thisSinger = SINGER_NOWLISTSTEXT[i][0]
                playTitle = os.listdir(f"{singerListDir}\\{thisSinger}")
                playing.append(playBtn)
                break
        print(f"playTitle:{playTitle}")
        playTitle.sort()

        for i in playTitle:
            if i in ignoreFile:
                playTitle.remove(i)
        print(f"playTitle:{playTitle}")

        sbp.get_quit()
        time.sleep(1)

        playnum = 0
        thread_one = threading.Thread(target = sbp.get_playThread, args = (playTitle,playing,PLAY_BTN,playBtn,playnum), daemon=True)
        thread_one.start()


#==============화면관리메니저클래스===================================================
class Manager(ScreenManager):
    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)
        self.screen_main = ScreenMain(name="screen_main", size_hint = (0.9, 1))
        self.screen_setting = ScreenSetting(name="screen_setting", size_hint = (0.9, 1))
        self.screen_song = ScreenSong(name="screen_song", size_hint = (0.9, 1))
        self.screen_singer = ScreenSinger(name="screen_singer", size_hint = (0.9, 1))
        self.add_widget(self.screen_main)
        self.add_widget(self.screen_setting)
        self.add_widget(self.screen_song)
        self.add_widget(self.screen_singer)

#################################################################################
class songBox_kvPyaudio(App):
    global manager, soundbar,upperMenu
    proc = os.getpid()
    #print("songBox_kv: ",proc)
    Window.clearcolor = winColor
    manager = Manager()
    soundbar = SoundBarMenu(size_hint = (1,1))
    upperMenu = UpperMenu(size_hint = (0.1,1))

    def build(self):
        proc = os.getpid()
        #print("Appbuild: ", proc)
        self.root = Root(orientation = "vertical")
        self.root1 = Root(orientation = "horizontal",size_hint = (1,0.1), spacing = 10)#spacing = 10
        self.root2 = Root(orientation = "horizontal",size_hint = (1,0.9))

        self.root1.add_widget(soundbar)

        #upperMenu = UpperMenu(size_hint = (0.1,1))

        self.root2.add_widget(upperMenu)
        self.root2.add_widget(manager)

        self.root.add_widget(self.root1)
        self.root.add_widget(self.root2)

        return self.root
#def show_screen_main(self,obj):
#        manager.current = "screen_main"
#    def show_screen_setting(self, obj):
        #print(self,obj)
#        manager.current = "screen_setting"
#    def show_screen_song(self,obj):
#        manager.current = "screen_song"
#    def show_screen_three(self,obj):
#        manager.current = "Class3"
#    def show_clear(self):
#        manager.clear_widgets()
#        manager.screen_main.clear_widgets()
#        manager.screen_setting.clear_widgets()
#        manager.screen_song.clear_widgets()
#        manager.screen_singer.clear_widgets()
#    def show_remove(self,obj):
#        manager.remove_widget(manager.screen_main)
#        manager.remove_widget(manager.screen_setting)
#        manager.remove_widget(manager.screen_song)
#        manager.remove_widget(manager.screen_singer)
################################################################################
if __name__ == '__main__':
    proc = os.getpid()
    print("AppSTart: ", proc)

    syncList=sbl.sync_song()
    sbs.make_singerDic()

    songBox_kvPyaudio().run()
