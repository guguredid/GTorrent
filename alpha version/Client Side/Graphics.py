from pubsub import pub
import subprocess
import wx.lib.scrolledpanel as scrolled
import wx


class MyFrame(wx.Frame):
    """
    class representing the main window the GUI is going to be at
    """

    def __init__(self, parent=None):
        super(MyFrame, self).__init__(parent, title="GTorrent", size=wx.DisplaySize())
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

        self.Maximize(True)


class MainPanel(wx.Panel):
    """
    class representing the main panel of the GUI
    """

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
    """
    class representing the main panel of the system
    """

    def __init__(self, parent, frame, download='D:\\'):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=wx.DisplaySize(), style=wx.SIMPLE_BORDER)
        self.frame = frame
        self.parent = parent
        self.file_select = None
        self.element = None
        self.Hide()
        self.SetBackgroundColour(wx.LIGHT_GREY)
        # the root to download the file to
        self.download_root = download
        # flag - download is happening or not
        self.is_downloading = False
        # saving the current downloaded file's download button
        self.fileBtn = None

        # text font
        self.titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        # dictionary saving all the files' sizers in the scrolled panel
        self.file_sizers = {}

        # help text sizer
        help_sizer = wx.BoxSizer(wx.VERTICAL)
        help_text = wx.StaticText(self, -1, label="Help:\nTo upload a file to the system, click on the file button.\nTo change the directory the file will be downloaded to, click on 'Change direcory' button.\nTo open this directory, click on 'Open' button.\nTo download a file from the system, click on the download image next to the file name.")
        help_text.SetFont(self.titlefont)
        help_sizer.AddSpacer(320)
        help_sizer.Add(help_text, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        # main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # GTorrent logo at the top
        logoImg = wx.Image("Full logo.png", wx.BITMAP_TYPE_ANY).Rescale(600, 300)
        logoImg = wx.StaticBitmap(self, -1, wx.BitmapFromImage(logoImg))

        # text
        text = wx.StaticText(self, -1, label="Files in the system: ")
        text.SetFont(self.titlefont)
        self.sizer.AddSpacer(10)

        self.sizer.Add(logoImg, 0, wx.ALIGN_CENTER | wx.ALL, 0)
        self.sizer.Add(text, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        # scrolled panel
        self.scrollP = scrolled.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER, size=(600, 300))
        self.scrollP.SetAutoLayout(1)
        self.scrollP.SetupScrolling()

        # the sizer for the scrolled panel
        self.spSizer = wx.BoxSizer(wx.VERTICAL)

        # add the scrolled panel's sizer to the main sizer
        self.scrollP.SetSizer(self.spSizer)
        self.scrollP.SetupScrolling()

        self.sizer.Add(self.scrollP, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        self.sizer.AddSpacer(10)

        # the bottom buttons' sizer
        self.bottom_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # load image button
        upImage = wx.Image("upload.png")
        upImage.Rescale(50, 50)
        upImage = wx.Bitmap(upImage)
        upBtn = wx.BitmapButton(self, name="upload file", size=(75, 75), bitmap=upImage, pos=(200, 800))
        upBtn.Bind(wx.EVT_BUTTON, self.uploadImage)
        upBtn.SetToolTip("Upload file")

        # change the directory to download to button
        changeDirBtn = wx.Button(self, id=1, label="Change Directory", size=(100, 75), name="changeDir")
        changeDirBtn.Bind(wx.EVT_BUTTON, self.updateDir)
        changeDirBtn.SetToolTip("Change download directory")
        current_download_text = wx.StaticText(self, -1, label=f"Current download directory: {self.download_root} ")
        current_download_text.SetFont(self.titlefont)
        # open download directory button
        open_download_dir_btn = wx.Button(self, id=1, label="Open", size=(60, 30), name="changeDir")
        open_download_dir_btn.Bind(wx.EVT_BUTTON, self.openDownloadDir)
        open_download_dir_btn.SetToolTip("Open Download Directory")
        download_sizer = wx.BoxSizer(wx.VERTICAL)
        download_sizer.Add(current_download_text)
        download_sizer.AddSpacer(5)
        download_sizer.Add(open_download_dir_btn, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        # update the sizers
        self.bottom_buttons_sizer.Add(upBtn)
        self.bottom_buttons_sizer.AddSpacer(30)
        self.bottom_buttons_sizer.Add(changeDirBtn)
        self.bottom_buttons_sizer.AddSpacer(15)
        self.bottom_buttons_sizer.Add(download_sizer)

        self.sizer.Add(self.bottom_buttons_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        # creator text
        guy_text = wx.StaticText(self, -1, label="Created by Guy Redid")
        guy_text.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))

        self.sizer.AddSpacer(30)
        self.sizer.Add(guy_text, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        # main sizer
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.AddSpacer(10)
        self.main_sizer.Add(help_sizer)
        self.main_sizer.AddSpacer(10)
        self.main_sizer.Add(self.sizer)

        self.SetSizer(self.main_sizer)

        # connect the UI with the logic via pubsub
        pub.subscribe(self.add_file, "add_file")
        pub.subscribe(self.remove_file, "remove_file")
        pub.subscribe(self.popup, "pop_up")

    def add_file(self, filename):
        """
        adds file name to the scrolled bar
        :param filename: str
        """
        # sub sizer for each file
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # the file name
        text = wx.StaticText(self.scrollP, -1, label=filename)
        text.SetFont(self.titlefont)

        # text file icon
        if filename.endswith('.txt'):
            fileImg = wx.Image("file.png", wx.BITMAP_TYPE_ANY).Rescale(75, 75)
        # video file icon
        elif filename.endswith('.mp4'):
            fileImg = wx.Image("video.png", wx.BITMAP_TYPE_ANY).Rescale(75, 75)
        # image file icon
        else:
            fileImg = wx.Image("image.png", wx.BITMAP_TYPE_ANY).Rescale(75, 75)

        fileImg = wx.StaticBitmap(self.scrollP, -1, wx.BitmapFromImage(fileImg))

        # the download button
        downloadImg = wx.Image("download2.png", wx.BITMAP_TYPE_ANY).Rescale(75, 75)

        # downloadImg = wx.Image("download.jpg", wx.BITMAP_TYPE_ANY).Rescale(75, 75)
        downloadImg = wx.Bitmap(downloadImg)
        downBtn = wx.BitmapButton(self.scrollP, name=filename, size=(75, 75), bitmap=downloadImg)
        downBtn.Bind(wx.EVT_BUTTON, self.file_selected)

        downBtn.SetBackgroundColour(wx.LIGHT_GREY)
        downBtn.SetWindowStyleFlag(wx.NO_BORDER)
        downBtn.SetToolTip("Download file")

        spaceFromLeft = downloadImg.GetSize()[0] / 2 + downloadImg.GetSize()[0]
        spaceFromRight = fileImg.GetSize()[0] + text.GetSize()[0]

        # add everything
        sub_sizer.Add(fileImg, 0, wx.ALL, 0)
        sub_sizer.AddSpacer(15)
        sub_sizer.Add(text, 0, wx.ALL, 0)
        sub_sizer.AddSpacer(600 - (spaceFromLeft + spaceFromRight))
        sub_sizer.Add(downBtn, 0, wx.ALL, 0)

        # save the file's sizer in the dictionary
        self.file_sizers[filename] = sub_sizer

        # add the file's sizer to the scrolled panel's sizer
        self.spSizer.Add(sub_sizer)

        self.scrollP.SetSizer(self.spSizer)
        self.scrollP.SetupScrolling()
        self.scrollP.Layout()

    def remove_file(self, filename):
        """
        removes the file from the scrolled panel
        :param filename: str
        """
        self.file_sizers[filename].Clear(True)

        self.scrollP.Layout()

    def popup(self, message, flag=None):
        """
        pops the given message to the screen
        :param message: str
        :param flag: bool
        """
        # flag argument is used to tell if the pop up is related to a download, if not no need to change button's color
        # and is downloading status
        if flag:
            self.is_downloading = False
            # check if a file is downloading (if so fileBtn is not None). If so, stop the download
            if self.fileBtn:
                self.fileBtn.SetBackgroundColour(wx.LIGHT_GREY)
                self.fileBtn = None
        wx.MessageBox(message, " ", wx.OK)

    def file_selected(self, event):
        """
        handles case where one of the files' buttons is selected
        :param event: Event
        """
        if not self.is_downloading:
            self.is_downloading = True
            self.popup("Downloading, please wait...")
            self.fileBtn = event.GetEventObject()
            self.fileBtn.SetBackgroundColour(wx.GREEN)
            # update the logic that a file was selected
            wx.CallAfter(pub.sendMessage, "panel_listener", message=f"1{event.GetEventObject().GetName()}")
        else:
            self.popup("Downloading already in process...")

    def uploadImage(self, event):
        """
        handles a case where the upload file button is clicked
        :param event: Event
        """
        openFileDialog = wx.FileDialog(self, "Open", "", "", "", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        path = openFileDialog.GetPath()
        openFileDialog.Destroy()
        if path:
            # update the logic that a file was uploaded
            wx.CallAfter(pub.sendMessage, "panel_listener", message=f"2{path}")

    def updateDir(self, event):
        """
        handles change for the GTorrent's directory
        :param event: Event
        """
        if not self.is_downloading:
            openDirDialog = wx.DirDialog(None, "Choose input directory", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
            openDirDialog.ShowModal()
            path = openDirDialog.GetPath()
            openDirDialog.Destroy()
            if path:
                # update the logic that the download path had changed
                wx.CallAfter(pub.sendMessage, "panel_listener", message=f"3{path}")
                # update the graphics that the download path had changed
                self.download_root = path
                current_download_text = wx.StaticText(self, -1, label=f"Current download directory: {self.download_root}")
                current_download_text.SetFont(self.titlefont)
                self.bottom_buttons_sizer.Remove(4)
                self.bottom_buttons_sizer.Add(current_download_text)
                self.bottom_buttons_sizer.Layout()
                self.Sizer.Layout()
        else:
            self.popup("Can't change download directory while downloading...")

    def openDownloadDir(self, event):
        """
        opens the current download directory
        :param event: Event
        """
        print("OPEN DIR ", self.download_root)
        subprocess.Popen(f'explorer "{self.download_root}"')


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
