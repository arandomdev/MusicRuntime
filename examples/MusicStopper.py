"""
Allows the user to select the last song to be played. 

Best launched by URL through Siri Shortcuts widgets
"""

import rubicon.objc as objc

from musicruntime.musicqueueviewer import MusicQueueViewer
from musicruntime.musicplayercontroller import MusicPlayerController

def callback(selected: list, sender: MusicQueueViewer):
	songList = []
	for i in range(0, selected[0][0] + 1):
		songList.append(sender.songList[i])
		pass

	MusicPlayerController().replaceQueue(songList)
	pass

viewer = MusicQueueViewer(callback)
viewer.present()
viewer.waitModal()

app = objc.ObjCClass("UIApplication").sharedApplication
nav = app._systemNavigationAction()
if nav:
	nav.sendResponseForDestination(0)
	pass