import base64
from io import BytesIO

import wx
from wxglade import ImageViewerWindow
from wx.lib.floatcanvas import FloatCanvas


class ImageViewerWindowEx(ImageViewerWindow):
    def __init__(self, *args, **kwds):
        ImageViewerWindow.__init__(self, *args, **kwds)
        self.SetMinSize((300, 300))

        self.image = None
        self.bitmap = None

        self.dragging = False
        self.last_pos = None
        self.image_scale = 1
        self.image_scale_scroll_factor = 1.5

        self.Layout()

    def change_image(self, image_data:str):
        # https://stackoverflow.com/questions/58145240/is-there-any-possible-way-how-to-show-image-from-base64-data-in-wxpython-app
        decodedImgData = base64.b64decode(image_data)
        bio = BytesIO(decodedImgData)
        img = wx.Image(bio)
        if not img.IsOk():
            raise ValueError("this is a bad/corrupt image")

        self.image = wx.Bitmap(img)
        # self.image = wx.Bitmap(r"C:\Users\lcarrozza\Documents\My files\Stuff\Screenshot 2022-08-25 084715.png")

        w, h = self.GetSize()
        self.bitmap = FloatCanvas.ScaledBitmap(self.image, (0, 0), h)  # , 'cc')
        self.Canvas.AddObject(self.bitmap)
        self.Canvas.Draw(True)
        self.ZoomToFit(self)

    def on_left_down(self, event):
        self.dragging = True
        self.last_pos = wx.GetMousePosition()

    def on_motion(self, event):
        #TODO: Add limits
        if self.dragging:
            self.Canvas.ScreenPosition
            self.Canvas.ScreenRect.Width
            self.Canvas.ScreenRect.Height
            self.bitmap.BoundingBox.X
            self.bitmap.ScaledBitmap.ScaledWidth
            self.bitmap.ScaledBitmap.ScaledHeight
            new_pos = wx.GetMousePosition()
            dx = self.last_pos.x - new_pos.x
            dy = self.last_pos.y - new_pos.y
            self.Canvas.MoveImage((dx, dy), "Pixel")
            self.last_pos = new_pos

    def on_left_up(self, event):
        self.dragging = False

    def on_mousewheel(self, event):
        # TODO: Improve zoom limits
        max_scale = 25 # factor
        min_size = 10 # px

        image = self.bitmap.ScaledBitmap
        scale_factor = self.image_scale_scroll_factor
        if event.GetWheelRotation() < 0:
            scale_factor = 1 / self.image_scale_scroll_factor

        if ((image.ScaledWidth >= min_size and image.ScaledHeight >= min_size and scale_factor <= 1)
                or (self.Canvas.Scale <= max_scale and scale_factor >= 1)):
            self.Canvas.Zoom(scale_factor, event.Position, "Pixel", keepPointInPlace=True)

    def ZoomToFit(self, event):
        self.Canvas.ZoomToBB()

    def on_resize(self, event):
        wx.CallAfter(lambda: (
            print("Resizing")
        ))

    def on_close(self, event):
        self.Destroy()
