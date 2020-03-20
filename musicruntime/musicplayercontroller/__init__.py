import rubicon.objc as objc
import objc_util # pylint: disable=import-error
import threading

import time

class MusicPlayerController(object):
	
	def __init__(self):
		self.musicPlayer = objc.ObjCClass("MPMusicPlayerController").systemMusicPlayer
		self.requestController = self.musicPlayer.requestController

		self.reorderRequestCompletion = threading.Event()
		self.clearRequestCompletion = threading.Event()
		self.prepareCompletion = threading.Event()

		def reorderRequestHandler(arg1: objc.ObjCInstance, arg2: objc.ObjCInstance, arg3: objc.ObjCInstance, arg4: int) -> None:
			self.reorderRequestCompletion.set()
			pass
		self._reorderRequestHandler = objc.Block(reorderRequestHandler)

		def clearRequestHandler(arg1: objc.ObjCInstance, arg2: objc.ObjCInstance, arg3: objc.ObjCInstance, arg4: int) -> None:
			self.clearRequestCompletion.set()
			pass
		self._clearRequestHandler = objc.Block(clearRequestHandler)

		def prepareHandler(error: objc.ObjCInstance) -> None:
			self.prepareCompletion.set()
			pass
		self._prepareHandler = objc.Block(prepareHandler)
		pass

	def _getResponse(self):
		# Honestly I don't know why I need this but yea...
		self.musicPlayer.nowPlayingItemAtIndex(5000)

		self.musicPlayer._preflightRequestIfNeeded()
		return self.requestController.response
	
	def reorder(self, targetItemIndex: int, targetPositionIndex: int):
		"""Reorders the song at the targetItemIndex to the targetPositionIndex."""

		tracklist = self._getResponse().tracklist

		# convert the indices from the queue to the tracklist indices. 
		nowPlayingitemIndex = tracklist.playingItem.indexPath.row
		targetItemIndex += nowPlayingitemIndex + 1
		targetPositionIndex += nowPlayingitemIndex + 1

		collection = tracklist.items
		maxTargetPosition = collection.numberOfItemsInSection(0)
		
		if targetItemIndex > maxTargetPosition:
			raise IndexError(
				"targetItemIndex ({}) must be lower than {}.".format(
					targetItemIndex - (nowPlayingitemIndex + 1),
					maxTargetPosition - nowPlayingitemIndex
				)
			)
		elif targetPositionIndex > maxTargetPosition:
			raise IndexError(
				"targetPositionIndex ({}) must be lower than {}.".format(
					targetPositionIndex - (nowPlayingitemIndex + 1),
					maxTargetPosition - nowPlayingitemIndex
				)
			)
		elif targetPositionIndex < 0:
			raise IndexError(
				"targetPositionIndex ({}) must be 0 or higher.".format(
					targetPositionIndex - (nowPlayingitemIndex + 1)
				)
			)

		targetItemIndexPath = objc.ObjCClass("NSIndexPath").indexPathForRow(targetItemIndex, inSection=0)
		targetItem = collection.itemAtIndexPath(targetItemIndexPath)
		positionalItemIndexPath = objc.ObjCClass("NSIndexPath").indexPathForRow(targetPositionIndex - 1, inSection=0)
		positionalItem = collection.itemAtIndexPath(positionalItemIndexPath)

		reorderCommand = tracklist.reorderCommand()
		if reorderCommand.canMoveItem(targetItem) is False:
			raise RuntimeError("Unable to move item at targetItemIndex.")

		reorderRequest = reorderCommand.moveItem(targetItem, afterItem=positionalItem)

		self.reorderRequestCompletion.clear()
		objc.ObjCClass("MPCPlayerChangeRequest").performRequest(reorderRequest, completion=self._reorderRequestHandler)
		self.reorderRequestCompletion.wait()

		# wait for the command to actually take effect.
		time.sleep(0.1)
		pass

	def replaceQueue(self, songList: list):
		"""
		Clears the current queue and replaces it with the given list. This will preserve the currently playing song.

		parameters
		----------

		songList : list
			A list of MQVSong instances.
		"""

		songList = [song.songObject for song in songList]
		songList.insert(0, self.musicPlayer.nowPlayingItem)
		
		self.musicPlayer.pause()
		currentTime = self.musicPlayer.currentPlaybackTime

		clearRequest = self._getResponse().tracklist.resetCommand().clear()

		self.clearRequestCompletion.clear()
		objc.ObjCClass("MPCPlayerChangeRequest").performRequest(clearRequest, completion=self._clearRequestHandler)
		self.clearRequestCompletion.wait()

		self.musicPlayer.shuffleMode = 1
		songCollection = objc.ObjCClass("MPMediaItemCollection").collectionWithItems(songList)
		self.musicPlayer.setQueueWithItemCollection(songCollection)

		self.musicPlayer.prepareToPlay()

		self.prepareCompletion.clear()
		self.musicPlayer.prepareToPlayWithCompletionHandler(self._prepareHandler)
		self.prepareCompletion.wait()

		self.musicPlayer.play()
		self.musicPlayer.currentPlaybackTime = currentTime
		pass
	pass