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
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=wx.DisplaySize(), style=wx.SIMPLE_BORDER)
        self.frame = frame
        self.parent = parent
        self.file_select = None
        self.element = None
        self.Hide()
        self.SetBackgroundColour(wx.LIGHT_GREY)

        # text font
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        # main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # GTorrent logo at the top
        logoImg = wx.Image("Full logo.png", wx.BITMAP_TYPE_ANY).Rescale(600, 300)
        logoImg = wx.StaticBitmap(self, -1, wx.BitmapFromImage(logoImg))

        # sizer.AddSpacer(10)
        # text
        text = wx.StaticText(self, -1, label="Files in the system: ")
        text.SetFont(titlefont)
        sizer.AddSpacer(10)

        sizer.Add(logoImg, 0, wx.ALIGN_CENTER | wx.ALL, 0)
        sizer.Add(text, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        # scrolled panel
        self.scrollP = scrolled.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER, size=(600, 300))
        # self.scrollP.Centre()
        self.scrollP.SetAutoLayout(1)
        self.scrollP.SetupScrolling()

        # the sizer for the scrolled panel
        self.spSizer = wx.BoxSizer(wx.VERTICAL)

        files_list = ["pug.jpg", 'cat.jpg', "file1.png", "test", "a", "b", "c", "d"]

        # add files to the available files' list
        for file in files_list:
            # sub sizer for each file
            sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

            # the file name
            text = wx.StaticText(self.scrollP, -1, label=file)
            text.SetFont(titlefont)

            # the file icon
            fileImg = wx.Image("file.png", wx.BITMAP_TYPE_ANY).Rescale(75, 75)
            fileImg = wx.StaticBitmap(self.scrollP, -1, wx.BitmapFromImage(fileImg))

            # the download button
            downloadImg = wx.Image("download.png", wx.BITMAP_TYPE_ANY).Rescale(75, 75)
            downloadImg = wx.Bitmap(downloadImg)
            downBtn = wx.BitmapButton(self.scrollP, name=file, size=(75, 75), bitmap=downloadImg)
            downBtn.Bind(wx.EVT_BUTTON, self.file_selected)

            # add everything
            sub_sizer.Add(fileImg, 0, wx.ALL, 0)
            sub_sizer.AddSpacer(15)
            sub_sizer.Add(text, 0, wx.ALL, 0)
            sub_sizer.AddSpacer(30)
            sub_sizer.Add(downBtn, 0, wx.ALL, 0)

            # add the file's sizer to the scrolled panel's sizer
            self.spSizer.Add(sub_sizer)

        # add the scrolled panel's sizer to the main sizer
        self.scrollP.SetSizer(self.spSizer)
        self.scrollP.SetupScrolling()

        sizer.Add(self.scrollP, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        sizer.AddSpacer(10)

        # the bottom buttons' sizer
        bottom_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # load image button
        upImage = wx.Image("upload.png")
        upImage.Rescale(50, 50)
        upImage = wx.Bitmap(upImage)
        upBtn = wx.BitmapButton(self, name="upload file", size=(50, 50), bitmap=upImage, pos=(200, 800))
        upBtn.Bind(wx.EVT_BUTTON, self.uploadImage)
        # upBtn.SetToolTip("upload file")
        # upBtn.SetBackgroundColour('light grey')

        # change GTorrent's directory button
        changeDirBtn = wx.Button(self, id=1, label="Change Directory", size=(200, 100), name="changeDir")
        changeDirBtn.Bind(wx.EVT_BUTTON, self.updateDir)

        # update the sizers
        bottom_buttons_sizer.Add(upBtn)
        bottom_buttons_sizer.AddSpacer(30)
        bottom_buttons_sizer.Add(changeDirBtn)

        sizer.Add(bottom_buttons_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        self.SetSizer(sizer)

    def file_selected(self, event):
        '''
        handles case where one of the files' buttons is selected
        '''
        print(event.GetEventObject().GetName())

    def uploadImage(self, event):
        '''
        handles a case where the upload file button is clicked
        '''
        print("in Upload")
        openFileDialog = wx.FileDialog(self, "Open", "", "", "", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        path = openFileDialog.GetPath()
        openFileDialog.Destroy()
        if path:
            fileName = path[path.rfind("\\")+1:]
            print(f"PATH-{path};;;;;NAME-{fileName}")

    def updateDir(self, event):
        '''
        handles change for the GTorrent's directory
        '''
        print("in UpdateDir")
        openDirDialog = wx.DirDialog(None, "Choose input directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        openDirDialog.ShowModal()
        path = openDirDialog.GetPath()
        openDirDialog.Destroy()
        if path:
            print(f"PATH-{path}")


app = wx.App()
frame = MyFrame()
frame.Show()
app.MainLoop()


