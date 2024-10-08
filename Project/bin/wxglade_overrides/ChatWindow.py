#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import html
import json
import os
import pickle
import queue
import random
import shutil
import subprocess
import tempfile
import threading
from tempfile import SpooledTemporaryFile

import requests
import wx.adv
import wx.html2
import wx.lib.agw.persist
import wx.lib.newevent
import wx.richtext

from Project.bin.Scripts import Config
from Project.bin.Scripts.Server import SocketWorkerThread
from Project.bin.wxglade.ChatWindow import *
from Project.bin.wxglade_overrides import EasterEgg
from Project.bin.wxglade_overrides import FrameSettings

drop_event, EVT_DROP_EVENT = wx.lib.newevent.NewEvent()

# Server
server = SocketWorkerThread(GlobalVars.queue_server_and_app)

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
        self.SetTitle(f"Chat Window - {GlobalVars.VERSION}")
        self.update = None

        # Variables
        self.sent_to = ''
        self.previous_sender = None
        self.SettingsWindow = None
        self.EasterEggWindow = None
        self.characters = 0
        # self.SetDoubleBuffered(True)
        self.SetIcon(wx.Icon(GlobalVars.icon))
        self.UpdateStatus('characters', 0)

        # Remember window size and position
        self._persistMgr = wx.lib.agw.persist.PersistenceManager.Get()
        _configFile = GlobalVars.my_data_dir / 'persist-saved-cfg'
        self._persistMgr.SetPersistenceFile(_configFile)
        if not self._persistMgr.RegisterAndRestoreAll(self):
            print("No config file")

        # Create a config file if one doesn't exist
        if not os.path.exists(GlobalVars.cfgFile_path):
            Config.create_template()

        # Server - Check for messages
        self.queue_server_and_app = GlobalVars.queue_server_and_app
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
            data = self.queue_server_and_app.get_nowait()
            # print(data)
        except queue.Empty:
            pass

        if data:
            function = data['function']
            args = data['args']
            if function == 'message':
                print(data)
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
                typing_status = f'{user} is typing...'
                self.timer_typing.Start(2000, oneShot=True)
                if self.TypingUser.Label != typing_status:
                    self.TypingUser.SetLabel(typing_status)

    def OpenSettings(self, event):
        if not self.SettingsWindow:
            self.SettingsWindow = FrameSettings.FrameSettings(self)
            self.SettingsWindow.CentreOnParent()
            self.Disable()
            self.SettingsWindow.Show()
            event.Skip()

    def ClearChat(self, event):
        self.previous_sender = None
        self.html_chat_log.SetPage(GlobalVars.html_template_code, "")

    def SendMessage(self, event):
        self.CheckConnection(self)
        message = self.text_ctrl_message.GetValue()
        if message and len(message) <= GlobalVars.maxCharacterLength:
            PC_Local_Name = Config.get_user_info('alias', 'local')
            server.send_message(PC_Local_Name, message)
            self.AppendMessage(PC_Local_Name, message)
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

    # noinspection PyUnusedLocal
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
        self._persistMgr.SaveAndUnregister()

        if self.update:
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
                              GlobalVars.pkl_update]
                             )
            print("Closing main app.")
        else:
            print("No update available")
        self.Destroy()

        event.Skip()

    def OnOpen(self, event):
        self.CheckForAndDownloadUpdate()
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

    def on_script_message(self, event):
        data = json.loads(event.String)
        print(data)

        if 'keyPress' in data:
            print(data['keyPress'])
        elif 'mouseDown' in data:
            print(data['mouseDown'])
        elif 'wheel' in data:
            print(data['wheel'])

    def AppendMessage(self, username, message):
        if username != self.previous_sender:
            self.previous_sender = username
            user_type = 'local-user'
            username = html.escape(username)
            self.html_chat_log.RunScript(f'window.insertUsername({json.dumps(username)}, {json.dumps(user_type)})')

        message = html.escape(message)
        self.html_chat_log.RunScript(f'window.insertMessage({json.dumps(message)})')

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

    def CheckForAndDownloadUpdate(self):
        url_repo = 'https://api.github.com/repos/LoganAC34/InstantMessaging/releases/latest'
        response_data = requests.get(url_repo).json()
        version_name = response_data['name']
        online_version_number_string = response_data['tag_name']
        online_version_number = online_version_number_string.split(".")
        online_version_major = int(online_version_number[0].lower().replace("v", ""))
        online_version_minor = int(online_version_number[1])
        online_version_patch = int(online_version_number[2])
        url_download = response_data['assets'][0]['browser_download_url']

        current_version = GlobalVars.VERSION.split(".")
        current_version_major = int(current_version[0].lower().replace("v", ""))
        current_version_minor = int(current_version[1])
        current_version_patch = int(current_version[2])

        print("Current version: " + GlobalVars.VERSION)
        print("Repo version: " + version_name)

        is_new_version = (
                (online_version_major, online_version_minor, online_version_patch) >
                (current_version_major, current_version_minor, current_version_patch)
        )
        if is_new_version and 'Stable' in version_name and not GlobalVars.debug:
            self.temp_file = os.path.join(tempfile.gettempdir(), os.path.basename(url_download))

            # Set Update variable to True
            with open(GlobalVars.pkl_update, 'wb') as f:
                # noinspection PyTypeChecker
                pickle.dump(True, f)
            self.update = True

            # Download file
            t = threading.Thread(target=self.DownloadUpdate, args=[url_download, self.temp_file])
            t.daemon = True
            t.start()

        else:
            print("Program is up to date!")

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

        # Download the current file
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
                    # noinspection PyTypeChecker
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
