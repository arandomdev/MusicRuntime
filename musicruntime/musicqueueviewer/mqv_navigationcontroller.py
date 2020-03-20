import rubicon.objc as objc

_warnForDefinedClass = False

try:
	MQVNavigationController = objc.ObjCClass("MQVNavigationController")
	if _warnForDefinedClass:
		print("MQVNavigationController already defined")
except NameError:
	UINavigationController = objc.ObjCClass("UINavigationController")
	class MQVNavigationController(UINavigationController):

		@objc.objc_method
		def initWithRootViewController_(self, rootController):
			self = objc.ObjCInstance(objc.send_super(__class__, self, "initWithRootViewController:", rootController)) # pylint: disable=undefined-variable
			if self:
				self.MQVDelegate = None
				self.modalPresentationStyle = 0

				stopButton = objc.ObjCClass("UIBarButtonItem").alloc().initWithBarButtonSystemItem(14, target=self, action=objc.SEL("closeAction"))
				reloadButton = objc.ObjCClass("UIBarButtonItem").alloc().initWithTitle("Reload", style=0, target=self, action=objc.SEL("reloadAction"))
				shuffleButton = objc.ObjCClass("UIBarButtonItem").alloc().initWithTitle("Shuffle", style=0, target=self, action=objc.SEL("shuffleAction"))
				doneButton = objc.ObjCClass("UIBarButtonItem").alloc().initWithTitle("Done", style=2, target=self, action=objc.SEL("doneAction"))
				
				self.navigationBar.topItem.leftBarButtonItem = stopButton
				self.navigationBar.topItem.rightBarButtonItems = [doneButton, shuffleButton, reloadButton]
				pass
			return self

		@objc.objc_method
		def closeAction(self):
			callback = getattr(self.MQVDelegate, "closeAction", None)
			if callable(callback):
				callback() # pylint: disable=not-callable
			pass

		@objc.objc_method
		def reloadAction(self):
			callback = getattr(self.MQVDelegate, "reloadAction", None)
			if callable(callback):
				callback() # pylint: disable=not-callable
			pass

		@objc.objc_method
		def shuffleAction(self):
			callback = getattr(self.MQVDelegate, "shuffleAction", None)
			if callable(callback):
				callback() # pylint: disable=not-callable
			pass

		@objc.objc_method
		def doneAction(self):
			callback = getattr(self.MQVDelegate, "doneAction", None)
			if callable(callback):
				callback() # pylint: disable=not-callable
			pass
		
		@objc.objc_method
		def supportedInterfaceOrientations(self) -> int:
			return 2
		pass
