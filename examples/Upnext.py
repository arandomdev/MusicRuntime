"""
Allows the user to select multiple songs to be played next.

Best launched by URL through Siri Shortcuts widgets
"""

import rubicon.objc as objc

from musicruntime.musicqueueviewer import MusicQueueViewer
from musicruntime.musicplayercontroller import MusicPlayerController

def callback(selected: list, sender: MusicQueueViewer):
	controller = MusicPlayerController()

	currentIndex = 0
	for selection in selected:
		try:
			controller.reorder(selection[0], currentIndex)
			pass
		except Exception as e:
			print("Unable to move song ({}), Exception({})".format(selection[1].title, e))
			pass
		currentIndex += 1
		pass
	pass

viewer = MusicQueueViewer(callback, allowMultiple=True)
viewer.present()
viewer.waitModal()

app = objc.ObjCClass("UIApplication").sharedApplication
nav = app._systemNavigationAction()
if nav:
	nav.sendResponseForDestination(0)
	pass