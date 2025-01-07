import os
import pathlib
import threading

import emojis
from PIL import Image, ImageDraw, ImageFont
from wx.lib.agw.scrolledthumbnail import EVT_THUMBNAILS_SEL_CHANGED

from scripts import GlobalVars
from wxglade.EmojiSelectorWindow import *

EMOJI_FILE_NAME_NUMBER_SEPARATOR = '__'

def generate_emoji_bitmap(index, emoji_char, emoji_name, emoji_size):
    """
    Render the given emoji with the specified font and return a PIL Image.
    https://stackoverflow.com/questions/77259325/how-to-download-noto-color-emoji-into-png
    """

    emoji_path = os.path.join(GlobalVars.emoji_directory,
                              f"{index:04d}{EMOJI_FILE_NAME_NUMBER_SEPARATOR}{emoji_name}.png".replace(":", ""))

    emoji_class = Emoji()
    emoji_class.Name = emoji_name
    emoji_class.ImagePath = emoji_path

    if pathlib.Path(emoji_path).exists():
        im = Image.open(emoji_path)
        emoji_class.Bitmap = im
        return emoji_class

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
        im.save(emoji_path)

        emoji_class.Bitmap = im

        return emoji_class
    return None

class Emoji(object):
    def __init__(self, *args, **kwds):
        self.Name = None
        self.Bitmap = None
        self.ImagePath = None

class EmojiSelectorWindowEx(EmojiSelectorWindow):
    def __init__(self, *args, **kwds):
        EmojiSelectorWindow.__init__(self, *args, **kwds)
        self.SetTitle("EmojiSelector")

        self.emoji_size = 27
        self.emoji_list = {}
        self.emoji_generation_thread = threading.Thread(target=self.generate_emojis)
        self.emoji_generation_thread.start()

        self.emoji_size_with_margin = self.emoji_size + 3
        self.scrolledThumbNail.SetScrollRate(self.emoji_size_with_margin, self.emoji_size_with_margin)

        self.on_resize(self)
        self.SetMinSize(self.GetSize())
        self.emoji_selector.Bind(EVT_THUMBNAILS_SEL_CHANGED, self.on_emoji_click)
        self.scrolledThumbNail.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)

    def generate_emojis(self):
        all_emoji_list = emojis.emojis.db.get_emoji_aliases()
        for i, (emoji_name, emoji_char) in enumerate(all_emoji_list.items()):
            # Generate a bitmap for the emoji with the font applied
            emoji = generate_emoji_bitmap(i, emoji_char, emoji_name, self.emoji_size)
            if emoji:
                self.emoji_list[emoji_name] = emoji

        emoji = generate_emoji_bitmap(9999, '', ':NONE:', self.emoji_size)
        self.emoji_list[':NONE:'] = emoji

        self.emoji_selector.ShowFileNames(False)
        self.emoji_selector.ShowDir(str(GlobalVars.emoji_directory))
        self.on_show(self)
        self.Layout()

    def on_emoji_click(self, event):
        emoji_index = self.scrolledThumbNail.GetSelection()
        list_item = self.scrolledThumbNail.GetItem(emoji_index)
        emoji_name = list_item.GetFileName().split(EMOJI_FILE_NAME_NUMBER_SEPARATOR)[-1]
        emoji_name = os.path.splitext(emoji_name)[0]
        emoji = self.emoji_list[f':{emoji_name}:']

        if emoji.Name == ':NONE:':
            event.Skip()
            return
        else:
            wx.CallAfter(self.scrolledThumbNail.SetSelection, len(self.emoji_list) - 1)

        print(f"Emoji selected: {emoji.Name}")

        GlobalVars.queue_server_and_app.put({'function': 'emoji_selected', 'args': emoji.Name})
        self.on_close(None)

    def on_window_activate(self, event):
        if self.IsActive():
            print("Not Focused")
            self.on_close(None)

    def on_show(self, event):
        wx.CallAfter(lambda: (
            self.emoji_selector.Layout(),
            self.SetSize(300, 200),  # Approximate size. Auto sizes to multiples of emoji size
            self.on_resize(event),
            self.scrolledThumbNail.Scroll(0, 0)
        ))

    @staticmethod
    def on_mouse_wheel(event):
        """Disables zooming"""
        if event.ControlDown():
            pass
        else:
            event.Skip()

    def on_resize(self, event):
        print("Resize")
        window_width = ((round(self.GetClientSize().Width / self.emoji_size_with_margin) * self.emoji_size_with_margin)
                        - 10)  # 10px for some reason make this work
        window_height = (round(self.GetClientSize().Height / self.emoji_size_with_margin) * self.emoji_size_with_margin)
        window_size = (window_width, window_height)
        self.SetClientSize(window_size)
        self.emoji_selector.SetMinSize(window_size)
        self.emoji_selector.SetMaxSize(window_size)
        self.Layout()

    def on_close(self, event):
        self.Hide()
