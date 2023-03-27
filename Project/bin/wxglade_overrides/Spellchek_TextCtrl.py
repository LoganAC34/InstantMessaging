import re

import enchant
import wx
import wx.stc as stc

from Project.bin.Scripts.Global import GlobalVars


class SpellCheckTextCtrl(stc.StyledTextCtrl):
    def __init__(self, parent, _id, value, style):
        stc.StyledTextCtrl.__init__(self, parent, id=_id, style=style)

        # Set textctrl appearance
        self.SetUseHorizontalScrollBar(False)  # Enable horizontal scroll
        self.SetUseVerticalScrollBar(True)  # Enable vertical scroll
        self.SetWrapMode(1)  # Word wrap (possibly set to 3)
        self.SetMarginWidth(1, 0)
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
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_LEFT_UP, self.OnKeyUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

    def OnKeyUp(self, event):
        # Get the text from the text box
        text = self.GetValue()

        # Get the current position of the cursor
        curr = self.GetCurrentPos()

        # Get the word under the cursor
        current_word_start = self.WordStartPosition(curr, True)
        current_word_end = self.WordEndPosition(curr, True)
        current_word = self.GetTextRange(current_word_start, current_word_end)

        # Split the text into words and check their spelling
        words = re.split(r'(\W+)', text)[:-1]
        for i, word in enumerate(words):
            if word != '' and word is not None and word.isalpha():
                pos = len(''.join(words[:i])) + 1  # calculate position of misspelled word
                word_start = self.WordStartPosition(pos, True)

                if word != current_word and not self.dict.check(word):
                    # If the word is misspelled, underline it in the text box
                    self.SetIndicatorCurrent(0)
                    self.IndicatorFillRange(word_start, len(word))
                else:
                    # Clear any previous style on the word
                    self.IndicatorClearRange(word_start, len(word))

        event.Skip()

    def OnRightUp(self, event):
        # Get the current position of the cursor
        pos = self.GetCurrentPos()

        # Get the word under the cursor
        word_start = self.WordStartPosition(pos, True)
        word_end = self.WordEndPosition(pos, True)
        word = self.GetTextRange(word_start, word_end)

        # Show the context menu only if the word is misspelled
        if word != '' and word is not None and word.isalpha():
            if not self.dict.check(word):
                menu = wx.Menu()

                # Get the suggested replacement words
                suggestions = self.dict.suggest(word)[:5]

                for x, suggestion in enumerate(suggestions):
                    item = menu.Append(x, suggestion)
                    self.Bind(wx.EVT_MENU, self.OnSuggestionSelected, item)

                # Add an option to add the misspelled word to the dictionary
                menu.AppendSeparator()
                item_add = menu.Append(wx.ID_ANY, f'Add \"{word}\" to dictionary')
                self.Bind(wx.EVT_MENU, self.OnAddToDictionary, item_add)

                self.PopupMenu(menu)
            else:
                event.Skip()
        else:
            event.Skip()

    def OnAddToDictionary(self, event):
        # Get the current position of the cursor
        pos = self.GetCurrentPos()

        # Get the word under the cursor
        word_start = self.WordStartPosition(pos, True)
        word_end = self.WordEndPosition(pos, True)
        word = self.GetTextRange(word_start, word_end)

        # Add the word to the dictionary
        self.dict.add(word)

        # Clear any previous style on the word
        self.IndicatorClearRange(word_start, len(word))

        event.Skip()

    def OnSuggestionSelected(self, event):
        # Get the selected suggestion
        suggestion = event.GetEventObject().GetLabel(event.Id)

        # Replace the misspelled word with the suggestion
        pos = self.GetCurrentPos()
        word_start = self.WordStartPosition(pos, True)
        word_end = self.WordEndPosition(pos, True)
        self.SetTargetStart(word_start)
        self.SetTargetEnd(word_end)
        self.ReplaceTarget(suggestion)
