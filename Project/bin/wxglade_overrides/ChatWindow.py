#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import pickle
import queue
import random
import shutil
import subprocess
import tempfile
import threading
from os.path import exists
from tempfile import SpooledTemporaryFile

import requests
import wx.adv
import wx.lib.agw.persist
import wx.lib.newevent
import wx.richtext
from wx.lib.expando import ExpandoTextCtrl

from Project.bin.Scripts import Config
from Project.bin.Scripts.Global import GlobalVars
from Project.bin.Scripts.Server import SocketWorkerThread
from Project.bin.wxglade.ChatWindow import *
from Project.bin.wxglade_overrides import EasterEgg
from Project.bin.wxglade_overrides import FrameSettings

drop_event, EVT_DROP_EVENT = wx.lib.newevent.NewEvent()

# Server
server = SocketWorkerThread(GlobalVars.queue_from_server, GlobalVars.queue_from_server)


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, obj):
        wx.FileDropTarget.__init__(self)
        self.obj = obj

    def OnDropFiles(self, x, y, filename):
        # filename is a list of 1 or more files
        # here we are restricting it 1 file by only taking the first item of the list
        TempTxt = filename[0]
        evt = drop_event(data=TempTxt)
        wx.PostEvent(self.obj, evt)

        return True


class MyFrame(ChatWindow):
    def __init__(self, *args, **kwds):
        ChatWindow.__init__(self, *args, **kwds)
        self.SetTitle(f"Chat Window - {GlobalVars.version_number}")

        # Variables
        self.sent_to = ''
        self.ClearedChat = False
        self.previous_sender = None
        self.SettingsWindow = None
        self.EasterEggWindow = None
        self.characters = 0
        self.SetDoubleBuffered(True)
        self.SetIcon(wx.Icon(GlobalVars.icon))
        self.UserNameWidth_Default = 50
        self.UserNameWidth = self.UserNameWidth_Default
        self.UpdateStatus('characters', 0)

        # Remember window size and position
        self._persistMgr = wx.lib.agw.persist.PersistenceManager.Get()
        _configFile = GlobalVars.my_data_dir / 'persist-saved-cfg'
        self._persistMgr.SetPersistenceFile(_configFile)
        if not self._persistMgr.RegisterAndRestoreAll(self):
            print("No config file")

        # Create config file if one doesn't exist
        if not os.path.exists(GlobalVars.cfgFile_path):
            Config.create_template()

        # Server - Check for messages
        self.queue_from_server = GlobalVars.queue_from_server
        server.start_server()
        self.timer_messages = wx.Timer(self)
        self.timer_messages.Start(100)
        self.Bind(wx.EVT_TIMER, self.HandleServer, self.timer_messages)

        # Server - Check connection
        self.CheckConnection(self)  # Check connection at init
        self.timer_connection = wx.Timer(self)
        self.timer_connection_end = wx.Timer(self)
        self.timer_typing = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.CheckConnection, self.timer_connection)
        self.Bind(wx.EVT_TIMER, self.CheckConnection_Stop, self.timer_connection_end)
        self.Bind(wx.EVT_TIMER, self.ClearTyping, self.timer_typing)
        self.timer_connection.Start(1000)  # Start checking connection

        # Variables
        self.temp_file = None
        self.sha_github = None

        # Drop target
        FileDrTr = MyFileDropTarget(self)
        self.text_ctrl_message.SetDropTarget(FileDrTr)
        self.Bind(EVT_DROP_EVENT, self.LabelTextUpdate)

        # On minimize and restore
        self.Bind(wx.EVT_ACTIVATE, self.OnResize)

        # character status flashing timer
        self.flash_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer_character_status, self.flash_timer)
        self.flashing = False
        self.original_color = self.StatusCharacters.GetForegroundColour()
        self.flash_count = 0
        self.flash_count_max = 12

    def LabelTextUpdate(self, event):
        image_path = event.data
        print(f"dropped {image_path}")
        image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        self.text_ctrl_message.AddImage(image)

    def ClearTyping(self, event):
        self.TypingUser.SetLabel('')

    @staticmethod
    def SentTyping():
        server.typing(Config.get_user_info('alias', 'local'))

    # noinspection PyUnusedLocal
    def HandleServer(self, event):
        data = {}
        try:
            data = self.queue_from_server.get(False)
        except queue.Empty:
            pass

        if data:
            function = data['function']
            args = data['args']
            if function == 'message':
                username = args['user']
                message = args['message']
                self.AppendMessage(username, message)
                app = wx.TopLevelWindow()
                if not app.IsActive():
                    wx.TopLevelWindow.RequestUserAttention(self)
                    popup = wx.adv.NotificationMessage(title=username, message=message)
                    popup.SetIcon(wx.Icon(GlobalVars.icon))
                    popup.Show()
            elif function == 'status':
                self.UpdateStatus('sent to', args)
            elif function == 'update_variables':
                server.update_variables()
            elif function == 'typing':
                user = args
                self.TypingUser.SetLabel(f'{user} is typing...')
                self.timer_typing.Start(1000, oneShot=True)

    def OpenSettings(self, event):
        if not self.SettingsWindow:
            self.SettingsWindow = FrameSettings.FrameSettings(self)
            self.SettingsWindow.CentreOnParent()
            self.Disable()
            self.SettingsWindow.Show()
            event.Skip()

    def ClearChat(self, event):
        self.sizer_1.Clear(True)
        self.ClearedChat = True
        self.panel_chat_log.Scroll(0, 0)
        self.panel_chat_log.FitInside()
        self.UserNameWidth = self.UserNameWidth_Default

    def SendMessage(self, event):
        self.CheckConnection(self)
        message = self.text_ctrl_message.GetValue()
        if message and len(message) <= GlobalVars.maxCharacterLength:
            PC_Local_Name = Config.get_user_info('alias', 'local')
            self.AppendMessage(PC_Local_Name, message)
            server.send_message(PC_Local_Name, message)
            self.text_ctrl_message.ClearAll()
            self.UpdateStatus('characters', 0)
            wx.CallAfter(self.CheckConnection_Stop, event)
        elif len(message) > GlobalVars.maxCharacterLength:
            self.on_start_character_flashing(event)

    def on_start_character_flashing(self, event):
        if not self.flashing:
            self.flashing = True
            self.flash_timer.Start(300)  # Flash every 500 milliseconds

    def on_stop_character_flashing(self, event):
        if self.flashing:
            self.flash_timer.Stop()
            self.flashing = False
            self.flash_count = 0
            # Revert to original style when stopping
            self.StatusCharacters.SetForegroundColour(self.original_color)
            self.StatusCharacters.Refresh()

    def on_timer_character_status(self, event):
        current_color = self.StatusCharacters.GetForegroundColour()

        if self.flash_count == self.flash_count_max:
            self.on_stop_character_flashing(self)
        else:
            if current_color == self.original_color:
                self.StatusCharacters.SetForegroundColour(wx.Colour(255, 0, 0))
            else:
                self.StatusCharacters.SetForegroundColour(self.original_color)

            self.flash_count += 1

    @staticmethod
    def CheckConnection(self):
        server.connection_status(Config.get_user_info('alias', 'local'))

    def CheckConnection_Stop(self, event):
        # print("Stopped checking server connection.")
        # self.timer_connection.Stop()
        # self.timer_connection_end.Stop()
        pass

    def OnResize(self, event):
        if event:
            event.Skip()

        """self.Refresh()
        self.Update()
        self.Layout()  # Causing issues with message box geting resized"""

        self.panel_send.SetAutoLayout(True)
        self.panel_send.Refresh()
        self.panel_send.Update()
        self.panel_send.Layout()

        self.panel_chat_log.SetAutoLayout(True)
        self.panel_chat_log.Refresh()
        self.panel_chat_log.Update()
        self.panel_chat_log.Layout()

    def OnClose(self, event):
        # self.queue_to_server.put("Command:Shutdown")
        # print("Event handler 'OnClose' not implemented!")
        self._persistMgr.SaveAndUnregister()

        # Get Update variable
        if exists(GlobalVars.pkl_update):
            with open(GlobalVars.pkl_update, 'rb') as f:
                Update = pickle.load(f)
        else:
            Update = False
            print("No local sha value")

        if Update:
            print("Update available")
            # Copy Update script to temp folder
            py_update = 'Update.exe'
            src_script_path = os.path.join(GlobalVars.exe, 'Scripts', py_update)
            dst_script_path = os.path.join(tempfile.gettempdir(), py_update)
            print("Source: " + src_script_path)
            print("Paste: " + dst_script_path)
            shutil.copy(src_script_path, dst_script_path)

            # Copy Notification icon to temp folder
            src_icon_path = GlobalVars.icon
            dst_icon_path = os.path.join(tempfile.gettempdir(), os.path.basename(GlobalVars.icon))
            print("Source: " + src_icon_path)
            print("Paste: " + dst_icon_path)
            shutil.copy(src_icon_path, dst_icon_path)

            # Update script
            update_script = os.path.join(tempfile.gettempdir(), py_update)
            subprocess.Popen([update_script,
                              self.temp_file,
                              GlobalVars.app_path, GlobalVars.app_path,  # One is current, other is new (same place).
                              GlobalVars.pkl_sha, self.sha_github,
                              GlobalVars.pkl_update]
                             )
            print("Closing main app.")
        else:
            print("No update available")
        self.Destroy()

        event.Skip()

    def OnOpen(self, event):
        if not GlobalVars.debug:
            self.CheckForUpdate()
        event.Skip()

    def UpdateStatus(self, element, status):
        if element == 'sent to':
            if status[0] == 'Will send':
                self.StatusDevice.SetLabel(status[1])
                if status[2] == 'app':
                    self.StatusConnected.SetForegroundColour((0, 255, 0))
                    GlobalVars.maxCharacterLength = 1000
                else:
                    self.StatusConnected.SetForegroundColour((225, 0, 0))
                    GlobalVars.maxCharacterLength = 256
            self.Refresh()

        if element == 'characters':
            self.characters = str(status)
        self.StatusCharacters.SetLabel(f'{self.characters}/{GlobalVars.maxCharacterLength} characters')
        self.OnResize(None)

        # print("Event handler 'UpdateStatus' not implemented!")

    def OnMouseEvents(self, event):
        # print("Event handler 'OnMouseEvents' not implemented!")
        wheel_direction = event.GetWheelRotation()
        scroll_pos = self.panel_chat_log.GetScrollPos(wx.VERTICAL)
        scroll_rate = 15
        if wheel_direction > 0:
            if scroll_pos < scroll_rate:
                # print("Scroll top")
                scroll_pos = 0
            else:
                # print("Scroll up")
                scroll_pos -= scroll_rate
        else:
            # print("Scroll down")
            scroll_pos += scroll_rate
        self.panel_chat_log.Scroll(0, scroll_pos)

    def AppendMessage(self, username, message):
        if username == self.previous_sender and self.ClearedChat is False:
            username = ""
        else:
            self.previous_sender = username
            username = f"{username}: "
        self.ClearedChat = False

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_1.Add(sizer, flag=wx.TOP | wx.EXPAND)

        text_ctrl_username = wx.TextCtrl(self.panel_chat_log, wx.ID_ANY, username,
                                         style=wx.BORDER_NONE | wx.TE_READONLY | wx.TE_LEFT)

        # Get text height and width
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
        height = font.GetPixelSize().Height * 1.5
        text_ctrl_username.SetFont(font)
        width = text_ctrl_username.GetTextExtent(username).Width + 10
        if width > self.UserNameWidth:
            self.UserNameWidth = width

        color_background = wx.Colour(0, 0, 0)
        color_text = wx.Colour(255, 255, 255)

        text_ctrl_username.SetMinSize((self.UserNameWidth, height))
        sizer.Add(text_ctrl_username, 0, wx.LEFT, 3)
        text_ctrl_username.SetBackgroundColour(color_background)
        text_ctrl_username.SetForegroundColour(color_text)

        style = wx.BORDER_NONE | wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.TE_READONLY | wx.TE_AUTO_URL
        text_ctrl_message = ExpandoTextCtrl(self.panel_chat_log, wx.ID_ANY, message, style=style)
        sizer.Add(text_ctrl_message, 1, wx.ALL, 0)
        text_ctrl_message.SetFont(font)
        text_ctrl_message.SetBackgroundColour(color_background)
        text_ctrl_message.SetForegroundColour(color_text)

        text_ctrl_username.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseEvents)
        text_ctrl_message.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseEvents)

        self.splitter_window.Layout()
        self.panel_chat_window.Layout()
        self.panel_chat_log.Layout()
        self.panel_chat_log.FitInside()

        wx.CallAfter(self.panel_chat_log.Scroll, 0, self.panel_chat_log.GetScrollRange(wx.VERTICAL))
        wx.CallAfter(self.OnResize, None)

    def EasterEgg(self, event):
        if GlobalVars.debug and not self.EasterEggWindow:
            self.EasterEggWindow = EasterEgg.EasterEggOverride(self)
            self.EasterEggWindow.Show()
            event.Skip()
        else:
            print("No Easter egg yet")

    def Fortunes(self, event):
        menu = wx.Menu()

        for x, entry in enumerate(["Good", "Bad", "Random"]):
            item = menu.Append(x, entry)
            self.Bind(wx.EVT_MENU, self.OnFortuneSelect, item)

        self.PopupMenu(menu)

    def OnFortuneSelect(self, event):
        def read_fortune(_fortune_type):
            fortunes = []
            fortune_path = GlobalVars.exe + rf'Resources\Fortunes_{_fortune_type}'
            with open(fortune_path) as file:
                while line := file.readline():
                    fortunes.append(line.rstrip())

            PC_Local_Name = Config.get_user_info('alias', 'local')
            fortune_name = 'Fortune Teller'  # 'System'
            num = random.randint(0, len(fortunes))
            while True:
                fortune = fortunes[num]
                if fortune[0] != '#' and fortune != '':
                    break
            fortune = f"{PC_Local_Name} your fortune is: \"{fortune}\""
            print(fortune)
            self.AppendMessage(fortune_name, fortune)
            server.send_message(fortune_name, fortune)

        # Get the selected suggestion
        fortune_type = event.GetEventObject().GetLabel(event.Id)
        print(f"{fortune_type} fortune selected")

        if fortune_type != 'Good' and fortune_type != 'Bad':
            if random.randint(0, 1) == 0:
                fortune_type = 'Good'
            else:
                fortune_type = 'Bad'
        read_fortune(fortune_type)

    def CheckForUpdate(self):
        try:
            # Get GitHub sha value:
            url_sha = 'https://api.github.com/repos/LoganAC34/InstantMessaging/contents/Local_Instant_Messenger.exe'
            session = requests.Session()
            sha_github = session.get(url_sha, timeout=1).json()
            self.sha_github = sha_github['sha']

            # Get local file sha value:
            if exists(GlobalVars.pkl_sha):
                with open(GlobalVars.pkl_sha, 'rb') as f:
                    sha_local = pickle.load(f)
            else:
                sha_local = "None"
                print("No local sha value")

            print("Github sha: " + self.sha_github)
            print("Local sha: " + sha_local)

            if self.sha_github != sha_local:

                # Download GitHub file
                url_download = 'https://raw.githubusercontent.com/LoganAC34/' \
                               'InstantMessaging/master/Local_Instant_Messenger.exe'
                self.temp_file = os.path.join(tempfile.gettempdir(), os.path.basename(url_download))
                print(self.temp_file)

                # Set Update variable to True
                with open(GlobalVars.pkl_update, 'wb') as f:
                    pickle.dump(True, f)

                # Download file
                t = threading.Thread(target=self.DownloadUpdate, args=[url_download, self.temp_file])
                t.daemon = True
                t.start()

            else:
                print("Program is up to date!")

        except Exception as e:
            print(e)
            pass

    @staticmethod
    def DownloadUpdate(url_download, temp_file):
        print("Downloading updated file...")
        # Notification about update
        update_popup = wx.adv.NotificationMessage(title='Downloading update...',
                                                  message="There is an update available. Please wait for it to finish "
                                                          "downloading before closing the program")
        update_popup_icon = wx.Icon(GlobalVars.icon)
        update_popup.SetIcon(update_popup_icon)
        update_popup.Show()

        # Download current file
        while True:
            try:
                temp = SpooledTemporaryFile()
                session = requests.Session()
                resp = session.get(url_download)
                temp.write(resp.content)
                temp.seek(0)

                # Write to file
                with open(temp_file, 'wb') as local_file:
                    local_file.write(resp.content)

                # Set Update variable to True
                with open(GlobalVars.pkl_update, 'wb') as f:
                    pickle.dump(True, f)

                # Notification about update
                update_popup.Destroy()
                update_popup = wx.adv.NotificationMessage(title='Download Complete!',
                                                          message="Close the program to use updated version.")
                update_popup.SetIcon(update_popup_icon)
                update_popup.Show()
                print("Done.")
                break
            except Exception as e:
                print("Download failed. Trying again.")
                print(e)
                pass
        update_popup.Close()
        update_popup.Destroy()
        update_popup_icon.Destroy()
