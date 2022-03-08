from pubsub import pub
import wx
from test1 import MyFrame


def handle_ui_events(message):
    '''
    handles the events that occurs on the graphic (clicks on buttons)
    :return: None
    '''
    code = message[0]
    info = message[1:]

    # asked to download a file
    if code == "1":
        print(f"ASKED TO DOWNLOAD FILE {info}")
        # wx.CallAfter(pub.sendMessage, "add_file", filename="TEST PUBSUB")
        pass
    # asked to upload a file
    elif code == "2":
        print(f"ASKED TO UPLOAD FILE {info}")
        pass
    # asked to change directory
    elif code == "3":
        print(f"ASKED TO CHANGE DIR TO {info}")
        pass


pub.subscribe(handle_ui_events, "panel_listener")

app = wx.App()
frame = MyFrame()
frame.Show()
app.MainLoop()


