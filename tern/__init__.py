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
		self.app.add_accelerator("<Alt>period", "win.gotodefinition", None)

		self.menu_ext = self.extend_menu("search-section")
		item = Gio.MenuItem.new(_("Select all references"), "win.selectidentifiers")
		self.menu_ext.append_menu_item(item)
		item = Gio.MenuItem.new(_("Go to definition"), "win.gotodefinition")
		self.menu_ext.append_menu_item(item)

	def do_deactivate(self):
		self.app.remove_accelerator("win.selectidentifiers", None)
		self.app.remove_accelerator("win.gotodefinition", None)
		self.menu_ext = None

class TernWindowActivatable(GObject.Object, Gedit.WindowActivatable):
	window = GObject.property(type=Gedit.Window)

	def do_activate(self):
		action = Gio.SimpleAction.new("selectidentifiers", None)
		action.connect("activate", self.on_selectidentifiers)
		self.window.add_action(action)
		action = Gio.SimpleAction.new("gotodefinition", None)
		action.connect("activate", self.on_gotodefinition)
		self.window.add_action(action)

	def do_deactivate(self):
		self.window.remove_action("selectidentifiers")

	def on_selectidentifiers(self, action, parameter):
		view = self.window.get_active_view()
		if hasattr(view, "tern_view_activatable"):
			view.tern_view_activatable.do_selectidentifiers()
	def on_gotodefinition(self, action, parameter):
		view = self.window.get_active_view()
		if hasattr(view, "tern_view_activatable"):
			view.tern_view_activatable.do_gotodefinition(self.window)

class TernViewActivatable(GObject.Object, Gedit.ViewActivatable):
	view = GObject.property(type=Gedit.View)

	def do_activate(self):
		buffer = self.view.get_buffer()
		self.completionprovider = None
		self.backend = None
		self.signal = buffer.connect("notify::language", self.on_language_change)
		self.on_language_change(None, None)
		self.bh_handler = 0;

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

	def get_iter(self):
		buffer = self.view.get_buffer()
		mark = buffer.get_insert()
		return buffer.get_iter_at_mark(mark)

	def get_file(self):
		buffer = self.view.get_buffer()
		location = buffer.get_location()
		if location == None:
			filename = ""
		else:
			filename = location.get_path()
		return filename

	def do_selectidentifiers(self):
		if (not hasattr(self.view, "multiedit_view_activatable") or
		    self.backend == None):
			return

		buffer = self.view.get_buffer()
		iter = self.get_iter()

		try:
			refs = self.backend.get_identifier_references(iter)["refs"]
		except:
			return
		multiedit = self.view.multiedit_view_activatable
		multiedit.toggle_multi_edit(True)

		start = iter.copy()
		file = self.get_file()
		for ref in refs:
			if file != ref["file"]:
				continue
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

	def do_gotodefinition(self, window):
		if self.backend == None:
			return

		iter = self.get_iter()
		file = self.get_file()
		try:
			definition = self.backend.get_definition(iter)
		except:
			return

		if definition["file"] == file:
			new_view = self.view
		else:
			gfile = Gio.File.new_for_path(definition["file"])
			tab = window.get_tab_from_location(gfile)
			if tab == None:
				tab = window.create_tab_from_location(gfile, None, 0, 20, False, True)

			self.bh_handler = tab.connect("draw", self.do_gotodefinition_bh, None,
				                            definition)
			window.set_active_tab(tab)
			return

		self.do_gotodefinition_bh(self, None, self.view, definition)

	def do_gotodefinition_bh(self, caller, state, new_view, definition):
		if new_view == None:
			new_view = caller.get_view()
			caller.disconnect(self.bh_handler)

		buffer = new_view.get_buffer()
		start = buffer.get_iter_at_offset(definition["start"])
		end = buffer.get_iter_at_offset(definition["end"])
		buffer.select_range(start, end)

		new_view.scroll_to_mark(buffer.get_insert(), 0.1, False, 0, 0)

