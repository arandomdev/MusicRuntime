import rubicon.objc as objc

_warnForDefinedClass = False

try:
	MQVSong = objc.ObjCClass("MQVSong")
	if _warnForDefinedClass:
		print("MQVSong already defined")
except NameError:
	class MQVSong(objc.NSObject):

		@objc.objc_method
		def initWithSong_(self, songObject):
			self.songObject = songObject.copy()

			self.title = str(songObject.title)
			self.artist = str(songObject.artist)
			self.exists = bool(songObject.existsInLibrary())

			self.obtainArtwork()
			return self

		@objc.objc_method
		def obtainArtwork(self):
			artObject = self.songObject.artwork
			if artObject:
				size = artObject.bounds.size
				size.height = 57
				size.width = 57
				self.art = artObject.imageWithSize(size)
			else:
				self.art = None
			pass
		pass