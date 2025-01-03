#!/usr/src/env python3
# -*- coding: UTF-8 -*-
import string

import wx.adv
import wx.lib.agw.persist
import wx.lib.newevent
import wx.richtext
from scripts import GlobalVars, config
from wxglade.SettingsWindow import *
import wxglade_ex


class SettingsWindowEx(SettingsWindow):
    def __init__(self, *args, **kwds):
        SettingsWindow.__init__(self, *args, **kwds)
        self.AboutWindow = None
        self.EditColors = None
        self.WarningMessage = None
        self.server = wxglade_ex.MainWindowEx.server
        self.SetIcon(wx.Icon(GlobalVars.program_icon))

        # Local name
        local_name = config.get_user_info('alias', 'local')
        self.text_ctrl_Local_Name.SetValue(local_name)

        # Character limits
        # space, select punctuation, alphanumeric, backspace, del, left-right
        allowableChars = ' .-_&' + string.ascii_letters + string.digits
        allowableActions = [1, 3, 22, 24, 26, 393, 25, 313, 312, 314, 315, 317, 8, 127, 314, 316, ord('\t')]
        self.allowableChars = [ord(x) for x in allowableChars] + allowableActions
        self.maxNameLength = 20
        self.tooltip = "Allowable characters: letter, numbers, spaces, .-_&"
        self.text_ctrl_Local_Name.SetMaxLength(self.maxNameLength)
        self.text_ctrl_Local_Name.SetToolTip(self.tooltip)

        # Add users to UI
        users = config.get_user_count()
        num = list(range(1, users + 1))
        for x in num:
            self.AddUser_UI(x)

    def on_click_edit_colors(self, event):  # wxGlade: SettingsWindow.<event_handler>
        print("Event handler 'on_click_edit_colors' not implemented!")
        pass  # TODO: implement this
        """
        if not self.EditColors:
            self.EditColors = EditColors.EditColorsWindowEx(self)
            self.EditColors.CentreOnParent()
            self.Disable()
            self.EditColors.Show()
            event.Skip()
        """

    def on_click_about(self, event):  # wxGlade: SettingsWindow.<event_handler>
        if not self.AboutWindow:
            self.AboutWindow = wxglade_ex.AboutWindowEx(self)
            self.AboutWindow.CentreOnParent()
            self.Disable()
            self.AboutWindow.Show()
            event.Skip()

    def OnChar(self, event):
        key_code = event.GetKeyCode()
        character = chr(key_code)
        # print(f"Unicode character: {key_code}")

        # Allow characters and tab navigation between TextCtrls
        if key_code in self.allowableChars:  # Test if pasting
            if key_code == wx.WXK_CONTROL_V:  # If so, test clipboard data
                not_empty = wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_UNICODETEXT))
                text_data = wx.TextDataObject()
                if not_empty:
                    wx.TheClipboard.Open()
                    wx.TheClipboard.GetData(text_data)
                    wx.TheClipboard.Close()
                    clipboard = text_data.GetText()
                    for x in clipboard:
                        if ord(x) not in self.allowableChars:
                            print(f'blocked clipboard: "{clipboard}" for character "{x}" unicode: {ord(x)}')
                            return  # Block paste and end loop
                    event.Skip()  # Allow paste

            else:  # If not pasting, check character
                # print(f'allowed character: "{character}"')
                event.Skip()  # Allow character
        else:
            print(f'blocked character "{character}" unicode: {key_code}')

    def AddUser_UI(self, user_num):
        # If existing, get values:
        try:
            device_name = config.get_user_info('device_name', 'remote', user_num)
            alias = config.get_user_info('alias', 'remote', user_num)
            alias_override = config.get_user_info('override', 'remote', user_num)
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
        text_ctrl_User_DeviceName.SetMinSize((120, 20))
        text_ctrl_User_DeviceName.SetValue(device_name)
        sizer_User_DeviceName.Add(text_ctrl_User_DeviceName, 0, wx.ALL, 2)

        sizer_User_Alias = wx.BoxSizer(wx.HORIZONTAL)
        sizer_User_Sub.Add(sizer_User_Alias, 1, wx.EXPAND, 0)

        label_User_Alias = wx.StaticText(self.panel_Main, wx.ID_ANY, "Alias:")
        label_User_Alias.SetMinSize((80, 20))
        sizer_User_Alias.Add(label_User_Alias, 0, wx.ALL, 2)

        text_ctrl_User_Alias = wx.TextCtrl(self.panel_Main, wx.ID_ANY, "")
        text_ctrl_User_Alias.SetMinSize((120, 20))
        text_ctrl_User_Alias.SetValue(alias)
        text_ctrl_User_Alias.SetMaxLength(self.maxNameLength)
        text_ctrl_User_Alias.SetToolTip(self.tooltip)
        text_ctrl_User_Alias.Bind(wx.EVT_CHAR, self.OnChar, text_ctrl_User_Alias)
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
            config.delete_user('remote', user_num)

            for x, user in enumerate(users):
                x += 1
                sizer = user.Sizer.StaticBox
                sizer.SetLabel(f'User {x}')
            print(f"Removed user {user_num}")
        else:
            print("Not removing user last user")

    def CheckFields(self):
        all_good = True
        value = self.text_ctrl_Local_Name.GetValue().lower()

        # ('<Blocked word>', [('<find>', '<replace>'),...]) <- Blocked word template
        blocked_words = [('Fortune Teller', [('0', 'o'), ('i', 'l'), ('_', ' '), ('-', ' ')])]
        value_replacement_check = value
        for word in blocked_words:
            blocked_word = word[0].lower()
            for replacing in word[1]:
                find = replacing[0].lower()
                replace = replacing[1].lower()
                value_replacement_check = value_replacement_check.replace(find, replace)
            if blocked_word in value_replacement_check:
                all_good = False

        if value.strip() == 'system':
            all_good = False

        return all_good

    def Apply_OnClick(self, event):
        all_good = self.CheckFields()
        if all_good:
            local_name = self.text_ctrl_Local_Name.GetValue()
            config.set_user_info('alias', local_name, 'local')

            # Get settings attributes
            users = self.sizer_RemoteUsers.GetChildren()
            for x, user in enumerate(users):
                sizer = user.Sizer.GetChildren()[1]
                user_DeviceName = sizer.Sizer.GetChildren()[0].Sizer.GetChildren()[1].GetWindow().GetValue()
                user_Alias = sizer.Sizer.GetChildren()[1].Sizer.GetChildren()[1].GetWindow().GetValue()
                user_Override = sizer.Sizer.GetChildren()[2].GetWindow().GetValue()
                x += 1
                config.set_user_info('device_name', user_DeviceName, 'remote', x)
                config.set_user_info('alias', user_Alias, 'remote', x)
                config.set_user_info('override', user_Override, 'remote', x)
                print(f'REMOTE_USER_{x} | {user_DeviceName} | {user_Alias} | {str(user_Override)}')

            GlobalVars.queue_server_and_app.put({'function': 'update_variables', 'args': ''})
            self.OnClose()
        else:
            print("Not good")
            if not self.WarningMessage:
                self.WarningMessage = wxglade_ex.ErrorDialogWindowEx(self)
                self.WarningMessage.CentreOnParent()
            self.Disable()
            self.WarningMessage.Show()
            event.Skip()
        # event.Skip()

    def Cancel_OnClick(self, event):  # wxGlade: SettingsWindow.<event_handler>
        self.OnClose()

    def OnClose(self, event=None):
        self.Parent.Enable()
        self.Destroy()
        print("Closing settings")
