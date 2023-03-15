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
from wx.lib.expando import ExpandoTextCtrl

from Files.Global import GlobalVars
from Files.Server import Config
from Files.Server import SocketWorkerThread
from wxglade.ChatWindow import *
from wxglade.SettingsWindow import *


class MyFrame(ChatWindow):
    def __init__(self, *args, **kwds):
        ChatWindow.__init__(self, *args, **kwds)
        self.SettingsWindow = None
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
        self.queue_to_server = queue.Queue()
        self.queue_from_server = queue.Queue()
        # noinspection PyGlobalUndefined
        global server
        server = SocketWorkerThread(self.queue_to_server, self.queue_from_server)
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        self.Bind(wx.EVT_TIMER, self.HandleServer, self.timer)

        # Variables
        self.temp_file = None
        self.sha_github = None

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
                if not app.IsActive():
                    popup = wx.adv.NotificationMessage(title=username, message=message)
                    popup.SetIcon(wx.Icon(GlobalVars.icon))
                    popup.Show()
            elif function == 'status':
                status = args
                self.UpdateStatus(status)

    def OpenSettings(self, event):  # wxGlade: FrameMain.<event_handler>
        self.SettingsWindow = FrameSettings(self)
        self.SettingsWindow.CentreOnParent()
        self.SettingsWindow.Show()
        self.SettingsWindow.MakeModal(True)
        event.Skip()

    def SendMessage(self, event):
        message = self.text_ctrl_message.GetValue()
        if message:
            PC_Local_Name = Config.get_user_info('alias', 'local')
            self.AppendMessage(PC_Local_Name, message)
            server.send_message(PC_Local_Name, message)
            self.text_ctrl_message.Clear()

    def OnKey(self, event):  # wxGlade: FrameMain.<event_handler>
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
            src_script_path = GlobalVars.exe + py_update
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

    def UpdateStatus(self, status):
        self.MainFrame_statusbar.SetStatusText(status, 0)
        # print("Event handler 'UpdateStatus' not implemented!")

    def AppendMessage(self, username, message):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_1.Add(sizer, flag=wx.TOP | wx.EXPAND)

        text_ctrl_username = wx.TextCtrl(self.panel_chat_log, wx.ID_ANY, f"{username}: ",
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


class FrameSettings(SettingsWindow):
    def __init__(self, *args, **kwds):
        SettingsWindow.__init__(self, *args, **kwds)
        self._disabler = None
        self.SetIcon(wx.Icon(GlobalVars.icon))

        local_name = Config.get_user_info('alias', 'local')
        self.text_ctrl_Local_Name.SetValue(local_name)

        # Add users to UI
        users = Config.get_user_count()
        num = list(range(1, users + 1))
        for x in num:
            self.AddUser_UI(x)

    def AddUser_UI(self, user_num):
        # If existing, get values:
        try:
            device_name = Config.get_user_info('device_name', 'remote', user_num)
            alias = Config.get_user_info('alias', 'remote', user_num)
            alias_override = Config.get_user_info('override', 'remote', user_num)
        except Exception as e:
            print(e)
            device_name = ''
            alias = ''
            alias_override = False

        # User UI template
        sizer_User_Main = wx.StaticBoxSizer(wx.StaticBox(self.panel_Main, wx.ID_ANY, f"User {user_num}"), wx.HORIZONTAL)
        self.sizer_RemoteUsers.Add(sizer_User_Main, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)

        button_User_Subtract = wx.Button(self.panel_Main, wx.ID_ANY, "-")
        button_User_Subtract.SetMinSize((30, 30))
        button_User_Subtract.SetForegroundColour(wx.Colour(216, 0, 0))
        button_User_Subtract.SetFont(
            wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        button_User_Subtract.Bind(wx.EVT_BUTTON, self.Subtract_OnClick, button_User_Subtract)
        sizer_User_Main.Add(button_User_Subtract, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer_User_Sub = wx.BoxSizer(wx.VERTICAL)
        sizer_User_Main.Add(sizer_User_Sub, 1, wx.EXPAND, 0)

        sizer_User_DeviceName = wx.BoxSizer(wx.HORIZONTAL)
        sizer_User_Sub.Add(sizer_User_DeviceName, 1, wx.EXPAND, 0)

        label_User_DeviceName = wx.StaticText(self.panel_Main, wx.ID_ANY, "Device Name:")
        label_User_DeviceName.SetMinSize((80, 20))
        sizer_User_DeviceName.Add(label_User_DeviceName, 0, wx.ALL, 2)

        text_ctrl_User_DeviceName = wx.TextCtrl(self.panel_Main, wx.ID_ANY, "")
        text_ctrl_User_DeviceName.SetMinSize((100, 20))
        text_ctrl_User_DeviceName.SetValue(device_name)
        sizer_User_DeviceName.Add(text_ctrl_User_DeviceName, 0, wx.ALL, 2)

        sizer_User_Alias = wx.BoxSizer(wx.HORIZONTAL)
        sizer_User_Sub.Add(sizer_User_Alias, 1, wx.EXPAND, 0)

        label_User_Alias = wx.StaticText(self.panel_Main, wx.ID_ANY, "Alias:")
        label_User_Alias.SetMinSize((80, 20))
        sizer_User_Alias.Add(label_User_Alias, 0, wx.ALL, 2)

        text_ctrl_User_Alias = wx.TextCtrl(self.panel_Main, wx.ID_ANY, "")
        text_ctrl_User_Alias.SetMinSize((100, 20))
        text_ctrl_User_Alias.SetValue(alias)
        sizer_User_Alias.Add(text_ctrl_User_Alias, 0, wx.ALL, 2)

        checkbox_User_AliasOverride = wx.CheckBox(self.panel_Main, wx.ID_ANY, "Override Alias?")
        checkbox_User_AliasOverride.SetValue(alias_override)
        sizer_User_Sub.Add(checkbox_User_AliasOverride, 0, wx.ALL, 3)

        print(f"Added user {user_num}")
        self.sizer_Main.Fit(self)

    def Add_OnClick(self, event):
        print("On click")
        users = len(self.sizer_RemoteUsers.GetChildren())
        self.AddUser_UI(users + 1)

    def Subtract_OnClick(self, event):
        # print("Subtract_OnClick not implemented")
        # Get settings attributes
        users = self.sizer_RemoteUsers.GetChildren()
        if len(users) != 1:
            sizer = event.EventObject.GetContainingSizer()
            user_num = sizer.StaticBox.Label.replace('User ', '')
            sizer.Clear(True)
            self.sizer_RemoteUsers.Remove(sizer)
            self.sizer_RemoteUsers.Fit(self)
            self.sizer_Main.Fit(self)
            Config.delete_user('remote', user_num)

            for x, user in enumerate(users):
                x += 1
                sizer = user.Sizer.StaticBox
                sizer.SetLabel(f'User {x}')
            print(f"Removed user {user_num}")
        else:
            print("Not removing user last user")

    def Apply_OnClick(self, event):
        local_name = self.text_ctrl_Local_Name.GetValue()
        Config.set_user_info('alias', local_name, 'local')

        # Get settings attributes
        users = self.sizer_RemoteUsers.GetChildren()
        for x, user in enumerate(users):
            sizer = user.Sizer.GetChildren()[1]
            user_DeviceName = sizer.Sizer.GetChildren()[0].Sizer.GetChildren()[1].GetWindow().GetValue()
            user_Alias = sizer.Sizer.GetChildren()[1].Sizer.GetChildren()[1].GetWindow().GetValue()
            user_Override = sizer.Sizer.GetChildren()[2].GetWindow().GetValue()
            x += 1
            Config.set_user_info('device_name', user_DeviceName, 'remote', x)
            Config.set_user_info('alias', user_Alias, 'remote', x)
            Config.set_user_info('override', user_Override, 'remote', x)
            print(f'REMOTE_USER_{x} | {user_DeviceName} | {user_Alias} | {str(user_Override)}')

        server.update_variables()
        self.OnClose()
        # event.Skip()

    def Cancel_OnClick(self, event):  # wxGlade: SettingsWindow.<event_handler>
        self.OnClose()

    def OnClose(self, event=None):
        self.MakeModal(False)
        self.Destroy()
        print("Closing settings")

    def MakeModal(self, modal=True):
        if modal and not hasattr(self, '_disabler'):
            self._disabler = wx.WindowDisabler(self)
        if not modal and hasattr(self, '_disabler'):
            del self._disabler


class MyApp(wx.App):
    def __init__(self):
        super().__init__(False, None, False, True)
        self.ChatWindow = None

    def OnInit(self):
        self.ChatWindow = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.ChatWindow)
        self.ChatWindow.Show()
        return True


# end of class MyApp

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
