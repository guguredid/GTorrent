import wx

class MyFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MyFrame, self).__init__(parent, title="Example for SDI", size=(500,500))
        # create status bar
        self.CreateStatusBar(1)
        self.SetStatusText("Developed by Merry Geva 1/1/2000")
        # create main panel - to put on the others panels
        main_panel = MainPanel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(main_panel, 1, wx.EXPAND)
        # arrange the frame
        self.SetSizer(box)
        self.Layout()
        self.Show()

app = wx.App()
frame = MyFrame()
frame.Show()
app.MainLoop()