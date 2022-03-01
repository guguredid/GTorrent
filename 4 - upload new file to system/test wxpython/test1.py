import wx
import wx.lib.scrolledpanel as scrolled
import string


class MyFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MyFrame, self).__init__(parent, title="GTorrent", size=wx.DisplaySize())
        # create status bar
        # self.CreateStatusBar(1)
        # self.SetStatusText("Developed by Merry Geva 1/1/2000")
        # create main panel - to put on the others panels
        main_panel = MainPanel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(main_panel, 1, wx.EXPAND)

        # GTorrent icon
        icon = wx.Icon("logo.png")
        self.SetIcon(icon)

        # arrange the frame
        self.SetSizer(box)
        self.Layout()
        self.Show()


class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.frame = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        v_box = wx.BoxSizer()
        # create object for each panel
        self.files = FilesPanel(self, self.frame)

        v_box.Add(self.files)

        self.files.Show()

        self.SetSizer(v_box)
        self.Layout()


class FilesPanel(wx.Panel):
    def __init__(self, parent, frame):
        # wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500), style=wx.SIMPLE_BORDER)
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=wx.DisplaySize(), style=wx.SIMPLE_BORDER)
        self.frame = frame
        self.parent = parent
        self.file_select = None
        self.element = None
        self.Hide()
        self.SetBackgroundColour(wx.LIGHT_GREY)

        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        sizer = wx.BoxSizer(wx.VERTICAL)

        logoImg = wx.Image("Full logo.png", wx.BITMAP_TYPE_ANY).Rescale(600, 300)
        logoImg = wx.StaticBitmap(self, -1, wx.BitmapFromImage(logoImg))

        # sizer.AddSpacer(10)
        sizer.Add(logoImg, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        text = wx.StaticText(self, -1, label="Files in the system: ")
        text.SetFont(titlefont)
        sizer.AddSpacer(10)
        sizer.Add(text, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        # scrolled panel
        self.scrollP = scrolled.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER, size=(600, 300))
        # self.scrollP.Centre()
        self.scrollP.SetAutoLayout(1)
        self.scrollP.SetupScrolling()

        self.spSizer = wx.BoxSizer(wx.VERTICAL)

        files_list = ["pug.jpg", 'cat.jpg', "file1.png", "test", "a", "b", "c", "d"]

        # sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # add files to the available files' list
        for file in files_list:
            sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
            text = wx.StaticText(self.scrollP, -1, label=file)
            text.SetFont(titlefont)

            fileImg = wx.Image("file.png", wx.BITMAP_TYPE_ANY).Rescale(75, 75)
            fileImg = wx.StaticBitmap(self.scrollP, -1, wx.BitmapFromImage(fileImg))

            # downloadImg = wx.Image("download.jpg", wx.BITMAP_TYPE_ANY).Rescale(75, 75)
            # downloadImg = wx.StaticBitmap(self.scrollP, -1, wx.BitmapFromImage(downloadImg))
            #
            # upBtn = wx.BitmapButton(self.scrollP, name="download file", size=(75, 75), bitmap=downloadImg)
            # upBtn.Bind(wx.EVT_BUTTON, self.file_selected)
            # upBtn.SetToolTip("download file")
            # upBtn.SetBackgroundColour('light grey')

            # bottom_buttons_sizer.Add(upBtn)

            fileBtn = wx.Button(self.scrollP, id=1, label="Download", size=(100, 30), name=file)
            fileBtn.Bind(wx.EVT_BUTTON, self.file_selected)

            sub_sizer.Add(fileImg, 0, wx.ALL, 0)
            sub_sizer.AddSpacer(15)
            sub_sizer.Add(text, 0, wx.ALL, 0)
            sub_sizer.AddSpacer(30)
            sub_sizer.Add(fileBtn, 0, wx.ALL, 0)

            self.spSizer.Add(sub_sizer)

        self.scrollP.SetSizer(self.spSizer)
        self.scrollP.SetupScrolling()

        sizer.Add(self.scrollP, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        sizer.AddSpacer(10)

        bottom_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # load image button
        upImage = wx.Image("upload.png")
        upImage.Rescale(50, 50)
        upImage = wx.Bitmap(upImage)
        upBtn = wx.BitmapButton(self, name="upload file", size=(50, 50), bitmap=upImage, pos=(200, 800))
        upBtn.Bind(wx.EVT_BUTTON, self.uploadImage)
        upBtn.SetToolTip("upload file")
        upBtn.SetBackgroundColour('light grey')

        bottom_buttons_sizer.Add(upBtn)
        sizer.Add(bottom_buttons_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        self.SetSizer(sizer)

    def file_selected(self, event):
        print(event.GetEventObject().GetName())

    def uploadImage(self, event):
        print("in Upload")
        openFileDialog = wx.FileDialog(self, "Open", "", "", "", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        path = openFileDialog.GetPath()
        openFileDialog.Destroy()
        if path:
            fileName = path[path.rfind("\\")+1:]
            print(f"PATH-{path};;;;;NAME-{fileName}")
            new_text = wx.TextCtrl(self.scrollP, alue=fileName)
            self.spSizer.Add(new_text)
            self.scrollP.Layout()
            self.scrollP.SetupScrolling()

    def downImage(self, event):
        if self.file_select:
            resp = wx.MessageBox(f"You selected item {self.file_select} to delete", "Warning", wx.OK | wx.CANCEL | wx.ICON_WARNING)
            if resp == wx.OK:
                self.spSizer.Detach(self.element)
                self.file_select = None
                self.scrollP.Layout()
                self.scrollP.SetupScrolling()

        else:
            wx.MessageBox("You must select file before")


app = wx.App()
frame = MyFrame()
frame.Show()
app.MainLoop()


