#GTorrent - Files Sharing System
### System requirements
* ##### Server side:
        1. The folder "classes" with all scripts within it.
        2. The script "main_server.py".
        3. Disk drive named "D" is needed.
* ##### Client side:
        1. The folder "classes" with all scripts within it.
        2. The scripts generalSetting.py, Graphics.py, and
           builder2.0.py.
        3. The png files downlaod2.png, file.png, Full logo.png,
           image.png, logo.png, upload.png and video.png.
        4. Disk drive named "D" is needed.
  The folder "classes" contains the following scripts:

    * Client.py
    * ClientProtocol.py
    * DB.py
    * FileHandler.py
    * Server.py
    * ServerProtocol.py
    * Torrent.py
    * TorrentHandlerServer.py
        
### Running instructions
* ##### Running the server:
        1. It is possible to change the directory where torrent
           files are stored. Changing the disk drive to C is not
           possible due to permissions.
        2. Run the "main_server.py" script and wait for clients
           to connect.
* ##### Running the client:
        1. In "generalSetting.py", change the TORRENT_SERVER_ADDRESS
           to store the ip address of the server's computer as a
           string.
        2. It is possible to change the directory where the system's
           files are stored. Changing the disk drive to C is not
           possible due to permissions.
        3. Run the "builder2.0.py" script, wait for the graphics
           to load up and using the system is available.
        
Enjoy! :)


### Known bugs
    1. Uploading certain file to the system does't work from one
       computer while from another one it does work.
    2. The complete hash received from the torrent file does'nt
       match the hash we get after downloading the whole file,
       even though the file is ok. It leads to "download failed"
       message.
