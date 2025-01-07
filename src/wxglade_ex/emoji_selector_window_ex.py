import threading

import emojis
import wx
from PIL import Image, ImageDraw, ImageFont

from scripts import GlobalVars
from wxglade.EmojiSelectorWindow import *


def generate_emoji_bitmap(emoji_char, emoji_size):
    """
    Render the given emoji with the specified font and return a PIL Image.
    https://stackoverflow.com/questions/77259325/how-to-download-noto-color-emoji-into-png
    """

    # Load the emoji font
    emoji_font = ImageFont.truetype(GlobalVars.emoji_font, size=109)

    bbox = emoji_font.getbbox(emoji_char)

    width = int(bbox[2])
    height = int(bbox[3])

    """Emoji sizes i noticed:
    (136, 128), (272, 128), | (408, 128), (543, 128), (544, 128), (680, 128)"""
    if width <= 136:  # Size cutoff to remove multi-emoji emojis.
        im = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), emoji_char, font=emoji_font, embedded_color=True)
        im.thumbnail((emoji_size, emoji_size))
        im = im.crop((0, 0, emoji_size, emoji_size))

        return im
    return None


def initialize_emoji_data():
    GlobalVars.queue_server_and_app.put({'function': 'emoji_selector_updated', 'args': None})
    print("Done initializing emoji selector")


class EmojiSelectorWindowEx(EmojiSelectorWindow):
    def __init__(self, *args, **kwds):
        EmojiSelectorWindow.__init__(self, *args, **kwds)
        self.SetSize((400, 300))
        self.SetTitle("EmojiSelector")
        self.SetMinSize(self.GetSize())

        self.emoji_size = 27
        self.emoji_bitmap_list = None
        self.emoji_list = []
        self.emoji_bitmap_list = wx.ImageList(self.emoji_size, self.emoji_size, mask=True)

        self.emoji_generation_thread = threading.Thread(target=self.generate_emojis)
        self.emoji_generation_thread.start()

        self.sizer_1.Fit(self)
        self.panel_1.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.SetBackgroundColour("WHITE")

    def generate_emojis(self):
        all_emoji_list = emojis.emojis.db.get_emoji_aliases()
        i = 0
        for emoji_name, emoji_char in all_emoji_list.items():
            # Generate a bitmap for the emoji with the font applied
            emoji_bitmap = generate_emoji_bitmap(emoji_char, self.emoji_size)
            if emoji_bitmap:
                bitmap = wx.Bitmap.FromBufferRGBA(emoji_bitmap.width, emoji_bitmap.height, emoji_bitmap.tobytes())
                self.emoji_bitmap_list.Add(bitmap)
                self.emoji_list.append([emoji_name, bitmap])
                self.emoji_sizer.InsertItem(i, i)
                i += 1

        self.emoji_sizer.AssignImageList(self.emoji_bitmap_list, wx.IMAGE_LIST_SMALL)
        self.emoji_sizer.SetColumnWidth(-1, 27) #TODO: Figure out column width issue
        self.emoji_sizer.SetScrollPos(0, 0) #TODO: Set to scroll to top

        initialize_emoji_data()

    def on_emoji_click(self, event):
        button = event.GetEventObject()
        print(f"Emoji selected: {button.GetName()}")

    def on_window_activate(self, event):
        if self.IsActive():
            print("Not Focused")
            self.on_close(self)

    def on_close(self, event):
        print('close')
        self.Hide()
