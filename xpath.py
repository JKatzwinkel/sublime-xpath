import sublime
import sublime_plugin
import re


def buildPath(view, selection):
  """
  Walks through XMl file from first line to end of given selection
  and assembles xpath expression along the way.
  """
  path = ['']
  lines = []
  # region spans from beginning of document to end of selection
  region = sublime.Region(0, selection.end())
  # copy lines in region
  for line in view.lines(region):
      contents = view.substr(line)
      lines.append(contents)
  # lvl of indentation
  level = -1
  spaces = re.compile('^\s+')
  for line in lines:
      space = spaces.findall(line)
      current = len(space[0]) if len(space) else 0
      # extract node name from element
      node = re.sub(r'\s*<\??([\w\-.]+)(\s.*)?>.*', r'\1', line)
      # this is why xml has to have proper indentation for this to work
      if current == level:
          path.pop()
          path.append(node)
      elif current > level:
          path.append(node)
          level = current
      elif current < level:
          path.pop()
          level = current
  # done
  return path


def updateStatus(view):
    path = buildPath(view, view.sel()[0])
    response = '/'.join(path)
    sublime.status_message(response)


def isXML(view):
    ext = ''
    if view.file_name():
      ext = re.sub(
          r'.*\.(\w+)$',
          r'\1',
          view.file_name()
      )
    return ext == 'xml'


class XpathCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        if isXML(view):
            response = ''
            selections = view.sel()
            for s, selection in enumerate(selections):
                path = buildPath(view, selection)
                response += '/'.join(path)
                if s != len(selections) - 1:
                    response += '\n'
            sublime.set_clipboard(response)


class XpathListener(sublime_plugin.EventListener):
    def on_text_command(self, view, command, args):
        if(isXML(view) and command == "move"):
            updateStatus(view)
