import sublime, sublime_plugin
import re

def buildPath(view, selection):
	word = view.word(selection)

	path = ['']
	lines = []

	region = sublime.Region(0, selection.end())
	for line in view.lines(region):
		contents = view.substr(line)
		lines.append(contents)

	level = -1
	spaces = re.compile('^\s+')
	for line in lines:
		space = spaces.findall(line)
		current = len(space[0]) if len(space) else 0
		if current == level:
			path.pop()
			path.append(line)
		elif current > level:
			path.append(line)
			level = current
		elif current < level:
			path.pop()
			level = current

	path = map(lambda x: re.sub(r'\s*<(\w+)(\s.*)?>.*', r'\1', x), path)

	return path

def updateStatus(view):
	path = buildPath(view, view.sel()[0])
	response = '/'.join(path)
	sublime.status_message(response)

def isXML(view):
	filename = re.sub(r'^.*/(\w+\.\w+)$', r'\1', view.file_name())
	ext = re.sub(r'^\w+\.(\w+)$', r'\1', filename)
	return ext == 'xml'

class XpathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view

		if isXML(view):
			response = ''
			selections = view.sel()
			for s,selection in enumerate(selections):
				path = buildPath(selection)
				response += '/'.join(path)
				if s != len(selections) - 1:
					response += '\n'
			sublime.set_clipboard(response)

class XpathCommandListener(sublime_plugin.EventListener):
	def on_text_command(self, view, command, args):
		if(isXML(view) and command == "move"):
			updateStatus(view)