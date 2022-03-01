import wx

def onButton(event):
    print("Button pressed.")

app = wx.App()

frame = wx.Frame(None, -1, 'win.py')
frame.SetSize(800, 600)

# Create open file dialog
openFileDialog = wx.FileDialog(frame, "Upload File", "", "",
      "",
       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

x=openFileDialog.ShowModal()
print(openFileDialog.GetPath())
openFileDialog.Destroy()
