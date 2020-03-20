import rubicon.objc as objc
import objc_util # pylint: disable=import-error

_warnForDefinedClass = False

try:
	MQVSongChangeDetector = objc.ObjCClass("MQVSongChangeDetector")
	if _warnForDefinedClass:
		print("MQVSongChangeDetector already defined")
except NameError:
	class MQVSongChangeDetector(objc.NSObject):
		lastSong = objc.objc_property()

		@objc.objc_method
		def init(self):
			"""set attribute MQVCallback to receive notifications."""
			self.musicPlayer = objc.ObjCClass("MPMusicPlayerController").systemMusicPlayer
			
			self.MQVCallback = None

			index = self.musicPlayer.indexOfNowPlayingItem + 1
			song = self.musicPlayer.nowPlayingItemAtIndex(index)
			if song:
				self.lastSong = song.copy()
			return self

		@objc.objc_method
		def pollControllerWithSender_(self, sender):
			index = self.musicPlayer.indexOfNowPlayingItem + 1
			currentSong = self.musicPlayer.nowPlayingItemAtIndex(index)

			if self.lastSong:
				if not self.lastSong.isEqual(currentSong):
					self.lastSong = currentSong.copy()

					if callable(self.MQVCallback):
						self.MQVCallback() # pylint: disable=not-callable
						pass
					pass
				pass
			pass

		@objc.objc_method
		@objc_util.on_main_thread
		def start(self):
			self.timer = objc.ObjCClass("NSTimer").timerWithTimeInterval(0.1, target=self, selector=objc.SEL("pollControllerWithSender:"), userInfo=None, repeats=True)
			objc.ObjCClass("NSRunLoop").currentRunLoop().addTimer(self.timer, forMode="kCFRunLoopCommonModes")
			pass

		@objc.objc_method
		def stop(self):
			self.timer.invalidate()
			pass
		pass


if __name__ == "__main__":
	detect = MQVSongChangeDetector.alloc().init()
	detect.MQVCallback = lambda: print("change")
	detect.start()

	input("press enter\n")
	detect.stop()
	pass