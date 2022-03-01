import wx
import wx.lib.scrolledpanel as scrolled


class MyFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MyFrame, self).__init__(parent, title="Example for SDI", size=(500, 500))
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


class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.frame = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        v_box = wx.BoxSizer()
        # create object for each panel
        # self.login = LoginPanel(self, self.frame)
        # self.registration = RegistrationPanel(self, self.frame)
        self.files = FilesPanel(self, self.frame)

        v_box.Add(self.files)

        self.files.Show()

        self.SetSizer(v_box)
        self.Layout()


class FilesPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500), style=wx.SIMPLE_BORDER)
        self.frame = frame
        self.parent = parent
        self.file_select = None
        self.element = None
        self.Hide()
        self.SetBackgroundColour(wx.LIGHT_GREY)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # title
        title = wx.StaticText(self, -1, label="Files Panel")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)

        # scrolled panel
        self.scrollP = scrolled.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER, size=(500, 300))
        self.scrollP.SetAutoLayout(1)
        self.scrollP.SetupScrolling()
        words = "A Quick Brown Insane Fox Jumped Over the Fence and Ziplined to Cover".split()
        self.spSizer = wx.BoxSizer(wx.VERTICAL)
        for word in words:
            text = wx.TextCtrl(self.scrollP, value=word)
            text.Bind(wx.EVT_CHILD_FOCUS, self.file_selected)
            self.spSizer.Add(text)
        self.scrollP.SetSizer(self.spSizer)

        # load image button
        upImage = wx.Image("upload.png")
        upImage.Rescale(50, 50)
        upImage = wx.Bitmap(upImage)
        upBtn = wx.BitmapButton(self, name="upload file", size = (50, 50), bitmap = upImage)
        upBtn.Bind(wx.EVT_BUTTON, self.uploadImage)
        upBtn.SetToolTip("upload file")
        upBtn.SetBackgroundColour('light grey')

    def file_selected(self, event):
        print(event.GetWindow().GetValue())

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

    def file_selected(self, event):
        self.file_select = event.GetWindow().GetValue()
        self.element = event.GetWindow()


