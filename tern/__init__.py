# vim: set shiftwidth=2 tabstop=2 noexpandtab textwidth=80 wrap :

from gi.repository import GObject, Gedit
from .completionprovider import TernCompletionProvider
from .backend import TernBackend

class TernViewActivatable(GObject.Object, Gedit.ViewActivatable):
	view = GObject.property(type=Gedit.View)

	def __init__(self):
		GObject.Object.__init__(self)
		self.completionprovider = None
		self.backend = None

	def do_activate(self):
		buffer = self.view.get_buffer()
		buffer.connect("notify::language", self.on_language_change)
		self.on_language_change(None, None)

	def on_language_change(self, obj = None, gparamstring = None):
		buffer = self.view.get_buffer()
		lang = buffer.get_language()
		if lang != None and lang.get_id() == 'js':
			self.enable()
		else:
			self.do_deactivate()

	def enable(self):
		self.backend = TernBackend(self.view.get_buffer())
		self.completionprovider = TernCompletionProvider(self.backend)

		completion = self.view.get_completion()
		completion.add_provider(self.completionprovider)

	def do_deactivate(self):
		if self.completionprovider != None:
			completion = self.view.get_completion()
			completion.remove_provider(self.completionprovider)
			self.completionprovider = None

		self.backend = None

