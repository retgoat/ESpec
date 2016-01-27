import sublime, sublime_plugin
import os

class ESpecDetectFileTypeCommand(sublime_plugin.EventListener):
	'''
	Detects current file type if the file's extension
	'''

	def on_load(self, view):
		filename = view.file_name()

		if not filename: return # not saved

		name = os.path.basename(filename.lower())
		if name.endswith("_spec.exs"):
			set_syntax(view, "ESpec")
		elif name == "factories.exs":
			set_syntax(view, "ESpec")


def set_syntax(view, syntax, path=None):
	if path is None:
		path = syntax

	view.settings().set('syntax', 'Packages/'+ path + '/' + syntax + '.tmLanguage')
	print("Switched syntax to: " + syntax)
