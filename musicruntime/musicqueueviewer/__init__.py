import rubicon.objc as objc
import objc_util  # pylint: disable=import-error
import threading

from .mqv_datasource import MQVDataSource
from .mqv_navigationcontroller import MQVNavigationController

from .mqv_song import MQVSong


class MusicQueueViewer(object):
	"""
	A viewer that shows the current queue.

	Allows the user to select songs, and a button to shuffle the queue.
	Note: This does not show the song that is currently playing.

	Parameters
	----------
	
	callback : callable
		A callable that has accepts two arguments, one which contains a list of tuples, which contains a row index and a MQVSong instance, and one with the viewer instance. i.e. ([(rowIndex: int, song: MQVSong)]: list, sender: MusicQueueViewer).
	allowMultiple = False
		Controls if the user can select multiple items
	"""

	def __init__(self, callback, allowMultiple=False):
		self.callback = callback
		
		self.tableViewController = objc.ObjCClass("UITableViewController").alloc().initWithStyle(0)
		self.tableViewController.tableView.allowsMultipleSelection = allowMultiple

		self.dataSource = objc.ObjCClass("MQVDataSource").alloc().initWithTableView(self.tableViewController.tableView)
		self.tableViewController.tableView.dataSource = self.dataSource
		

		self.navigationController = objc.ObjCClass("MQVNavigationController").alloc().initWithRootViewController(self.tableViewController)
		self.navigationController.MQVDelegate = self

		self.closeEvent = threading.Event()
		pass

	@property
	def songList(self):
		return self.dataSource.songList

	@objc_util.on_main_thread
	def present(self):
		"""Presents the viewer."""

		application = objc.ObjCClass("UIApplication").sharedApplication
		rootViewController = application.keyWindow.rootViewController
		rootViewController.presentViewController(self.navigationController, animated=True, completion=None)
		
		self.closeEvent.clear()
		pass

	def closeAction(self):
		self.dataSource.disposeDataSource()

		if callable(self.callback):
			self.callback([], self)
			pass
		self.closeViewer()
		pass

	def reloadAction(self):
		self.dataSource.beginEnumeratingSongs()
		pass

	def shuffleAction(self):
		musicPlayer = objc.ObjCClass("MPMusicPlayerController").systemMusicPlayer
		musicPlayer.shuffleMode = 1
		musicPlayer.shuffleMode = 2
		pass

	def doneAction(self):
		self.dataSource.disposeDataSource()

		if callable(self.callback):
			if self.tableViewController.tableView.indexPathsForSelectedRows:
				selectedIndexPaths = sorted(self.tableViewController.tableView.indexPathsForSelectedRows, key = lambda indexPath: indexPath.row)
				selectedRows = [indexPath.row for indexPath in selectedIndexPaths]

				formatted = [(row, self.dataSource.songList[row]) for row in selectedRows]
				self.callback(formatted, self)
				pass
			else:
				self.callback([], self)
				pass
			pass
		self.closeViewer()
		pass

	def closeViewer(self):
		self.navigationController.dismissModalViewControllerAnimated(True)
		self.closeEvent.set()
		pass

	def waitModal(self):
		self.closeEvent.wait()
		pass
	pass