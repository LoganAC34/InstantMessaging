import enchant
import wx
import wx.stc as stc
from enchant.checker import SpellChecker

from Project.bin.Scripts.Global import GlobalVars


class SpellCheckTextCtrl(stc.StyledTextCtrl):
    def __init__(self, parent, _id, value, style):
        stc.StyledTextCtrl.__init__(self, parent, id=_id, style=style)
        self.value = value  # Dummy variable to appease main script
        self.ChatWindow = self.GetGrandParent().GetParent()

        # Current word
        self.currentWord = None
        self.currentWord_start = 0
        self.currentWord_end = 0

        # Set textctrl appearance
        self.SetUseHorizontalScrollBar(False)  # Enable horizontal scroll
        self.SetUseVerticalScrollBar(True)  # Enable vertical scroll
        self.SetWrapMode(1)  # Word wrap (possibly set to 3)
        self.SetMarginWidth(1, 0)
        self.SetMaxLength(GlobalVars.maxCharacterLength)
        # self.SetLexer(stc.STC_LEX_PYTHON)  # Set the lexer to use Python syntax highlighting

        # Initialize the spell checker
        self.dict = enchant.DictWithPWL("en_US", GlobalVars.pwl_path)

        # Set up the style for misspelled words
        self.StyleSetSpec(stc.STC_P_WORD2, "fore:#FF0000,underline")
        self.IndicatorSetStyle(0, stc.STC_INDIC_SQUIGGLE)
        self.IndicatorSetForeground(0, "red")
        self.IndicatorSetAlpha(0, 0x80)
        self.IndicatorSetUnder(0, True)

        # Bind the events for spell checking and context menu
        self.Bind(wx.EVT_LEFT_UP, self.OnKeyUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown, self)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(stc.EVT_STC_CLIPBOARD_PASTE, self.OnPaste)

    def OnChar(self, event):
        message = self.GetValue()
        characters = len(message) + message.count(GlobalVars.lineBreak)
        # Check if adding the new character will exceed the maximum length
        if characters >= GlobalVars.maxCharacterLength:
            print("Max characters_1")
            return  # Ignore the event
        else:
            event.Skip()  # Allow the character to be added

    def OnPaste(self, event):
        message = self.GetValue()
        characters = len(message) + message.count(GlobalVars.lineBreak) + len(wx.stc.StyledTextEvent.GetText(event))
        if characters >= GlobalVars.maxCharacterLength:
            print("Max characters_2")
            wx.stc.StyledTextEvent.SetText(event, '')
        else:
            event.Skip()  # Allow the character to be added

    def OnKeyUp(self, event):
        self.SpellCheck(event)

    def SpellCheck(self, event, replace=False):
        # print("Checking Spelling")
        if not replace:
            event.Skip()
        # Get the text from the text box
        text = self.GetValue()  # Get text
        curr = self.GetCurrentPos()  # Get the word under the cursor

        # Clear any previous style on the text
        self.IndicatorClearRange(0, len(text))

        # Reset current word parameters
        self.currentWord = None
        self.currentWord_start = 0
        self.currentWord_end = 0

        # If the word is misspelled, underline it in the text box
        checker = SpellChecker(self.dict, text)
        for word in checker:
            word_text = word.word
            word_start = word.wordpos
            word_end = word_start + len(word_text)
            if not (word_start <= curr <= word_end):
                # print(f"Misspelled word: {word.word}")
                self.SetIndicatorCurrent(0)
                self.IndicatorFillRange(word_start, len(word_text))
            else:
                self.currentWord = word_text
                self.currentWord_start = word_start
                self.currentWord_end = word_end
        if not replace:
            wx.CallAfter(event.Skip)

    def OnKeyDown(self, event):
        # print('Onkey')
        unicodeKey = event.GetUnicodeKey()
        keycode = event.KeyCode
        print(keycode)
        message = self.GetValue().replace(GlobalVars.lineBreak, '').replace('\n', '')
        characters = len(message) + message.count(GlobalVars.lineBreak)
        self.ChatWindow.UpdateStatus('characters', characters)
        self.SpellCheck(event, True)
        checkConnection = False

        if event.GetModifiers() == wx.MOD_SHIFT and unicodeKey == wx.WXK_RETURN:
            # Adding carriage return
            # print("Shift + Enter")
            event.Skip()
            checkConnection = True
        elif unicodeKey == wx.WXK_RETURN and len(message) > 0:
            # Hitting enter with message content
            # print("Just Enter with message")
            self.ChatWindow.SendMessage(event)
            checkConnection = True
        elif unicodeKey == wx.WXK_RETURN and len(message) == 0:
            # Prevents sending blank message when hitting enter twice.
            # print("Just Enter")
            checkConnection = True
        elif unicodeKey != 0:
            # Typing a message
            self.ChatWindow.SentTyping()
            checkConnection = True
            event.Skip()
        elif keycode in GlobalVars.allowed_keys:
            # Allowing various function keys (Arrow keys, Home, End, Page up/down)
            event.Skip()

        if checkConnection:
            if not self.ChatWindow.timer_connection.IsRunning():
                self.ChatWindow.timer_connection.Start(1000)
            self.ChatWindow.timer_connection_end.Start(10000)

    def OnRightUp(self, event):
        self.SpellCheck(event, True)
        if self.currentWord:
            menu = wx.Menu()

            # Get the fist 5 suggested replacement words
            suggestions = self.dict.suggest(self.currentWord)[:5]

            for x, suggestion in enumerate(suggestions):
                item = menu.Append(x, suggestion)
                self.Bind(wx.EVT_MENU, self.OnSuggestionSelected, item)

            # Add an option to add the misspelled word to the dictionary
            menu.AppendSeparator()
            item_add = menu.Append(wx.ID_ANY, f'Add \"{self.currentWord}\" to dictionary')
            self.Bind(wx.EVT_MENU, self.OnAddToDictionary, item_add)

            self.PopupMenu(menu)
        else:
            event.Skip()

    def OnAddToDictionary(self, event):
        # Add the word to the dictionary and clear any previous style on the word
        self.dict.add(self.currentWord)
        self.IndicatorClearRange(self.currentWord_start, len(self.currentWord))
        event.Skip()

    def OnSuggestionSelected(self, event):
        # Get the selected suggestion
        suggestion = event.GetEventObject().GetLabel(event.Id)

        # Replace the misspelled word with the suggestion
        self.SetTargetStart(self.currentWord_start)
        self.SetTargetEnd(self.currentWord_end)
        self.ReplaceTarget(suggestion)
