#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import wx.adv
import wx.lib.agw.persist
import wx.lib.newevent
import wx.richtext

from Project.bin.Scripts import Config
from Project.bin.Scripts.Global import GlobalVars
from Project.bin.wxglade.SettingsWindow import *
from Project.bin.wxglade_overrides import ChatWindow


class FrameSettings(SettingsWindow):
    def __init__(self, *args, **kwds):
        SettingsWindow.__init__(self, *args, **kwds)
        self.server = ChatWindow.server
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

        GlobalVars.queue_from_server.put({'function': 'update_variables', 'args': ''})
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
