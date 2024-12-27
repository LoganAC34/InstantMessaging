from wxglade import EditColorsWindow

class EditColorsWindowEx(EditColorsWindow):
    def __init__(self, *args, **kwds):
        EditColorsWindow.__init__(self, *args, **kwds)
        self.preset_color_themes = {
            "Light Theme": {
                "Chat Log Text Color": (0, 0, 0),
                "Chat Log Background Color": (255, 255, 255),
                "Message Box Text Color": (0, 0, 0),
                "Message Box Color": (255, 255, 255),
                "App Text Color": (0, 0, 0),
                "App Background Color": (240, 240, 240),
                "Button Text Color": (0, 0, 0),
                "Button Color": (229, 241, 251)

            },
            "Dark Theme": {
                "Chat Log Text Color": (255, 255, 255),
                "Chat Log Background Color": (81, 81, 81),
                "Message Box Text Color": (0, 0, 0),
                "Message Box Color": (255, 255, 255),
                "App Text Color": (0, 0, 0),
                "App Background Color": (81, 81, 81),
                "Button Text Color": (0, 0, 0),
                "Button Color": (229, 241, 251)
            }
        }

    def On_Preset(self, event):  # wxGlade: EditColors.<event_handler>
        print("Event handler 'On_Preset' not implemented!")
        button = event.EventObject
        button_text = button.Label

        # Toggle off other preset buttons
        for preset in self.sizer_Presets.Children:
            preset = preset.Window
            if preset.Label != button_text:
                preset.Value = False

        # Get theme colors
        if button_text in ["Light Theme", "Dark Theme"]:
            print(f"Pre-made Preset: {button_text}")
        else:
            print(button_text)

        # Set colors
        for color in self.sizer_Colors.Children:
            color_element = color.Sizer.Children[0].Window
            color_name = color.Sizer.Children[1].Window.Label
            print(color_name)

        event.Skip()

    def Edit_Color(self, event):  # wxGlade: EditColors.<event_handler>
        print("Event handler 'Edit_Color' not implemented!")
        event.Skip()

    def On_Save(self, event):  # wxGlade: EditColors.<event_handler>
        print("Event handler 'On_Save' not implemented!")
        event.Skip()

    def On_Cancel(self, event):  # wxGlade: EditColors.<event_handler>
        self.Destroy()
        event.Skip()

    def On_Close(self, event=None):
        self.Parent.Enable()
        self.Destroy()
        print("Closing settings")

# end of class EditColors
