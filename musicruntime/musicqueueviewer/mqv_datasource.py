import rubicon.objc as objc
import objc_util # pylint: disable=import-error
import threading

import time

from .mqv_song import MQVSong
from .mqv_songchangedetector import MQVSongChangeDetector

_warnForDefinedClass = False

NSLog = objc_util.c.NSLog
NSLog.argtypes = [objc_util.c_void_p]

try:
	MQVDataSource = objc.ObjCClass("MQVDataSource")
	if _warnForDefinedClass:
		print("MQVDataSource already defined")
except NameError:
	UITableViewDataSource = objc.ObjCProtocol("UITableViewDataSource")
	class MQVDataSource(objc.NSObject, protocols=[UITableViewDataSource]):

		@objc.objc_method
		def initWithTableView_(self, tableView):
			self.musicPlayer = objc.ObjCClass("MPMusicPlayerController").systemMusicPlayer
			self.tableView = tableView

			self.songList = []

			self.isEnumerating = False
			self.enumerationLock = threading.Lock()

			self.beginEnumeratingSongs()

			self.changeDetector = objc.ObjCClass("MQVSongChangeDetector").alloc().init()
			self.changeDetector.MQVCallback = self.beginEnumeratingSongs
			self.changeDetector.start()
			return self

		@objc.objc_method
		def enumerateSongs(self):
			newSongList = []

			currentIndex = self.musicPlayer.indexOfNowPlayingItem + 1
			maxIndex = self.musicPlayer.numberOfItems()

			for index in range(currentIndex, maxIndex):
				song = self.musicPlayer.nowPlayingItemAtIndex(index)
				if song and "MPModelObjectMediaItem" in song.debugDescription and song.title is None:
					break
				else:
					newSongList.append(objc.ObjCClass("MQVSong").alloc().initWithSong(song))
					pass
				pass
			
			self.songList = newSongList

			self.enumerationLock.release()
			self.isEnumerating = False
			
			self.reloadTable()
			pass

		@objc.objc_method
		def beginEnumeratingSongs(self):
			self.enumerationLock.acquire(True)

			self.isEnumerating = True
			self.reloadTable()

			threading.Thread(target=self.enumerateSongs).start()
			pass

		@objc.objc_method
		@objc_util.on_main_thread
		def reloadTable(self):
			self.tableView.reloadData()

			if self.tableView.numberOfRowsInSection(0) != 0:
				indexZero = objc.ObjCClass("NSIndexPath").indexPathForRow(0, inSection=0)
				self.tableView.scrollToRowAtIndexPath(indexZero, atScrollPosition=1, animated=True)
				pass
			pass

		@objc.objc_method
		def tableView_numberOfRowsInSection_(self, tableView, section: int) -> int:
			if self.isEnumerating:
				return 1
			else:
				return len(self.songList)

		@objc.objc_method
		def tableView_cellForRowAtIndexPath_(self, tableView, indexPath):
			if self.isEnumerating:
				cellIdentifer = "MQVActivityCell"
				cell = tableView.dequeueReusableCellWithIdentifier(cellIdentifer)
				if cell is None:
					cell = objc.ObjCClass("UITableViewCell").alloc().initWithStyle(0, reuseIdentifier=cellIdentifer)
					pass

				cell.userInteractionEnabled = False

				activityIndicator = objc.ObjCClass("UIActivityIndicatorView").alloc().initWithActivityIndicatorStyle(100)
				activityIndicator.hidesWhenStopped = True
				activityIndicator.center = objc.NSPoint(
					self.tableView.frame.size.width / 2,
					cell.frame.size.height / 2
				)
				
				cell.contentView.addSubview(activityIndicator)
				activityIndicator.startAnimating()
				return cell

			cellIdentifer = "MQVSongCell"
			cell = tableView.dequeueReusableCellWithIdentifier(cellIdentifer)
			if cell is None:
				cell = objc.ObjCClass("UITableViewCell").alloc().initWithStyle(3, reuseIdentifier=cellIdentifer)
				pass

			if len(self.songList) < indexPath.row:
				return cell
			
			song = self.songList[indexPath.row]

			cell.textLabel.text = song.title
			cell.detailTextLabel.text = song.artist
			cell.imageView.image = song.art

			if song.exists:
				cell.userInteractionEnabled = True
				cell.textLabel.enabled = True
				cell.detailTextLabel.enabled = True
				pass
			else:
				cell.userInteractionEnabled = False
				cell.textLabel.enabled = False
				cell.detailTextLabel.enabled = False
				pass
			return cell
		pass

		@objc.objc_method
		def disposeDataSource(self):
			self.changeDetector.stop()
			pass
