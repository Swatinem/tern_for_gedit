# vim: set shiftwidth=2 tabstop=2 noexpandtab textwidth=80 wrap :

from gi.repository import GObject, Gio, Gedit
from .completionprovider import TernCompletionProvider
from .backend import TernBackend

class TernAppActivatable(GObject.Object, Gedit.AppActivatable):
	app = GObject.property(type=Gedit.App)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		self.app.add_accelerator("<Alt>F3", "win.selectidentifiers", None)

		self.menu_ext = self.extend_menu("search-section")
		item = Gio.MenuItem.new(_("Select all references"), "win.selectidentifiers")
		self.menu_ext.append_menu_item(item)

	def do_deactivate(self):
		self.app.remove_accelerator("win.selectidentifiers", None)
		self.menu_ext = None

class TernWindowActivatable(GObject.Object, Gedit.WindowActivatable):
	window = GObject.property(type=Gedit.Window)

	def do_activate(self):
		action = Gio.SimpleAction.new("selectidentifiers", None)
		action.connect("activate", self.on_activate)
		self.window.add_action(action)

	def do_deactivate(self):
		self.window.remove_action("selectidentifiers")

	def on_activate(self, action, parameter):
		view = self.window.get_active_view()
		if hasattr(view, "tern_view_activatable"):
			view.tern_view_activatable.do_selectidentifiers()

class TernViewActivatable(GObject.Object, Gedit.ViewActivatable):
	view = GObject.property(type=Gedit.View)

	def do_activate(self):
		buffer = self.view.get_buffer()
		self.completionprovider = None
		self.backend = None
		self.signal = buffer.connect("notify::language", self.on_language_change)
		self.on_language_change(None, None)

		self.view.tern_view_activatable = self

	def do_deactivate(self):
		buffer = self.view.get_buffer()
		buffer.disconnect(self.signal)

		delattr(self.view, 'tern_view_activatable')

	def on_language_change(self, obj = None, gparamstring = None):
		buffer = self.view.get_buffer()
		lang = buffer.get_language()
		if lang != None and lang.get_id() == "js":
			self.enable()
		else:
			self.disable()

	def enable(self):
		self.backend = TernBackend(self.view.get_buffer())
		self.completionprovider = TernCompletionProvider(self.backend)

		completion = self.view.get_completion()
		completion.add_provider(self.completionprovider)

	def disable(self):
		if self.completionprovider != None:
			completion = self.view.get_completion()
			completion.remove_provider(self.completionprovider)
			self.completionprovider = None

		self.backend = None

	def do_selectidentifiers(self):
		if (not hasattr(self.view, "multiedit_view_activatable") or
		    self.backend == None):
			return

		buffer = self.view.get_buffer()
		mark = buffer.get_insert()
		iter = buffer.get_iter_at_mark(mark)

		multiedit = self.view.multiedit_view_activatable
		multiedit.toggle_multi_edit(True)
		refs = self.backend.get_identifier_references(iter)["refs"]

		start = iter.copy()
		for ref in refs:
			if (start.get_offset() >= ref["start"] and
			    start.get_offset() <= ref["end"]):
				currentref = ref
				continue # do not add one for the current point
			iter.set_offset(ref["start"])
			buffer.place_cursor(iter)
			multiedit.do_toggle_edit_point(None)

		start.set_offset(currentref["start"])
		end = start.copy()
		end.set_offset(currentref["end"])
		buffer.place_cursor(iter)
		buffer.select_range(start, end)

