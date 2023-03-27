#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import pickle
import queue
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
        self.sent_to = ''
        self.ClearedChat = False
        self.previous_sender = None
        self.SettingsWindow = None
        self.characters = 0
        self.SetDoubleBuffered(True)
        self.SetIcon(wx.Icon(GlobalVars.icon))
        self.UserNameWidth = 50

        # Remember window size and position
        self._persistMgr = wx.lib.agw.persist.PersistenceManager.Get()
        _configFile = GlobalVars.my_data_dir / 'persist-saved-cfg'
        self._persistMgr.SetPersistenceFile(_configFile)
        if not self._persistMgr.RegisterAndRestoreAll(self):
            print("No config file")

        # Create config file if one doesn't exist
        if not os.path.exists(GlobalVars.cfgFile_path):
            Config.create_template()

        # Server
        self.queue_from_server = GlobalVars.queue_from_server
        server.start_server()
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        self.Bind(wx.EVT_TIMER, self.HandleServer, self.timer)

        # Variables
        self.temp_file = None
        self.sha_github = None

        # Drop target
        FileDrTr = MyFileDropTarget(self)
        self.text_ctrl_message.SetDropTarget(FileDrTr)
        self.Bind(EVT_DROP_EVENT, self.LabelTextUpdate)

    def LabelTextUpdate(self, event):
        image_path = event.data
        print(f"dropped {image_path}")
        image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        self.text_ctrl_message.AddImage(image)

    # noinspection PyUnusedLocal
    def HandleServer(self, event):
        result = {}
        try:
            result = self.queue_from_server.get(False)
        except queue.Empty:
            pass

        if result:
            function = result['function']
            args = result['args']
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
                status = args
                self.UpdateStatus('sent to', status)
            elif function == 'update_variables':
                server.update_variables()

    def OpenSettings(self, event):  # wxGlade: FrameMain.<event_handler>
        self.SettingsWindow = FrameSettings.FrameSettings(self)
        self.SettingsWindow.CentreOnParent()
        self.SettingsWindow.Show()
        self.SettingsWindow.MakeModal(True)
        event.Skip()

    def ClearChat(self, event):
        self.sizer_1.Clear(True)
        self.ClearedChat = True

    def SendMessage(self, event):
        message = self.text_ctrl_message.GetValue()
        self.UpdateStatus('characters', 0)
        if message:
            PC_Local_Name = Config.get_user_info('alias', 'local')
            self.AppendMessage(PC_Local_Name, message)
            server.send_message(PC_Local_Name, message)
            self.text_ctrl_message.ClearAll()

    @staticmethod
    def CheckConnection():
        server.test_connection()

    def OnKey_Press(self, event):  # wxGlade: FrameMain.<event_handler>
        # print('Onkey')
        unicodeKey = event.GetUnicodeKey()
        message = self.text_ctrl_message.GetValue()
        if event.GetModifiers() == wx.MOD_SHIFT and unicodeKey == wx.WXK_RETURN:
            # print("Shift + Enter")
            self.text_ctrl_message.WriteText('\n')
        elif unicodeKey == wx.WXK_RETURN and message:
            # print("Just Enter with message")
            self.SendMessage(self)
        elif unicodeKey == wx.WXK_RETURN:
            # print("Just Enter") # Prevents sending blank message when hitting enter twice.
            pass
        else:
            self.CheckConnection()
            event.Skip()

    def OnKey_Release(self, event):
        message = self.text_ctrl_message.GetValue()
        characters = len(message) + message.count('\n')
        self.UpdateStatus('characters', characters)
        event.Skip()

    def OnResize(self, event):
        self.panel_chat_log.Scroll(0, self.panel_chat_log.GetScrollRange(wx.VERTICAL))
        event.Skip()

    def OnClose(self, event):  # wxGlade: FrameMain.<event_handler>
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

    def OnOpen(self, event):  # wxGlade: FrameMain.<event_handler>
        self.CheckForUpdate()
        event.Skip()

    def UpdateStatus(self, element, status):
        if element == 'sent to':
            self.sent_to = status
        if element == 'characters':
            self.characters = str(status)
        status = f'{self.sent_to} | {self.characters}/256 characters'
        self.MainFrame_statusbar.SetStatusText(status, 0)
        # print("Event handler 'UpdateStatus' not implemented!")

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

        text_ctrl_username.SetMinSize((self.UserNameWidth, height))
        sizer.Add(text_ctrl_username, 0, wx.LEFT, 3)
        text_ctrl_username.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND))
        text_ctrl_username.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))

        style = wx.BORDER_NONE | wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.TE_READONLY | wx.TE_AUTO_URL
        text_ctrl_message = ExpandoTextCtrl(self.panel_chat_log, wx.ID_ANY, message, style=style)
        sizer.Add(text_ctrl_message, 1, wx.ALL, 0)
        text_ctrl_message.SetFont(font)
        text_ctrl_message.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND))
        text_ctrl_message.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))

        self.panel_chat_log.FitInside()
        self.panel_chat_log.Scroll(0, self.panel_chat_log.GetScrollRange(wx.VERTICAL))

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
