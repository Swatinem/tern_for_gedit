# vim: set shiftwidth=2 tabstop=2 noexpandtab textwidth=80 wrap :

import json
from urllib import request
from subprocess import Popen, PIPE
from difflib import SequenceMatcher

opener = request.build_opener(request.ProxyHandler({}))

def ensure_server(retry = False):
	try:
		return open('.tern-port').read()
	except IOError as e:
		if retry:
			raise e
		server = Popen("tern", stdin=PIPE, stdout=PIPE, stderr=PIPE)
		server.stdout.readline()
		return ensure_server(True)

def req(doc):
	port = ensure_server()
	doc = json.dumps(doc).encode("utf-8")

	r = opener.open("http://localhost:" + str(port) + "/", doc, 1)
	return json.loads(r.read().decode("utf-8"))


class TernBackend():
	def __init__(self, buffer):
		self.buffer = buffer

	def get_completions(self, iter, interactive):
		location = self.buffer.get_location()
		if location == None:
			filename = ""
		else:
			filename = location.get_path()
		(bufferstart, bufferend) = self.buffer.get_bounds()
		text = self.buffer.get_text(bufferstart, bufferend, False)

		file = {
			"type": "full",
			"name": filename,
			"text": text
		}
		query = {
			"type": "completions",
			"types": True,
			"depths": True,
			"filter": False,
			"omitObjectPrototype": False,
			"docs": True,
			#"urls": True,
			#"origins": True,
			#"includeKeywords": True,

			"file": "#0",
			"end": iter.get_offset()
		}
		res = req({
			"files": [file],
			"query": query
		})

		# TODO: moving this into CompletionProvider would make it a lot faster
		if interactive and res['end'] - res['start'] <= 2:
			return None
		return res

	def get_identifier_references(self, iter):
		return []
