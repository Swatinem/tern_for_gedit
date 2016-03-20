# vim: set shiftwidth=2 tabstop=2 noexpandtab textwidth=80 wrap :

from gi.repository import GObject, GtkSource

class TernCompletionProvider(GObject.Object, GtkSource.CompletionProvider):
	def __init__(self, backend):
		self.backend = backend
		self.last_result = None
		GObject.Object.__init__(self)

	def do_get_name(self):
		return "Tern Code Completion"

	def do_populate(self, context):
		err, iter = context.get_iter()
		interactive = context.get_activation() == GtkSource.CompletionActivation.INTERACTIVE

		self.last_result = self.backend.get_completions(iter, interactive)
		if self.last_result == None:
			return context.add_proposals(self, [], True)

		completions = self.last_result["completions"]
		completions = [Item(x) for x in completions]

		context.add_proposals(self, completions, True)

	def do_get_start_iter(self, context, proposal):
		return False, None # use default implementation

	def do_activate_proposal(self, proposal, iter):
		if self.last_result == None:
			return True

		buffer = iter.get_buffer()
		start = iter
		end = iter.copy()
		start.set_offset(self.last_result["start"])
		end.set_offset(self.last_result["end"])
		buffer.delete(start, end)
		buffer.insert(start, proposal.get_text())

def Item(completion):
	markup = completion["markup"]
	text = completion["name"]
	if "type" in completion:
		markup += " <i><small>" + completion["type"] + "</small></i>"
	icon = None
	info = None
	if "doc" in completion:
		info = completion["doc"] # TODO: maybe also add url, format properly?

	return GtkSource.CompletionItem.new_with_markup(markup, text, icon, info)

