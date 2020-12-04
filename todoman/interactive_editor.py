"Use $EDITOR to edit todos in yaml representation"
import humanize
import tempfile
import subprocess
import os
import ruamel.yaml
yaml = ruamel.yaml.YAML()

import sys
from pprint import pprint

YAML_STR = """\
summary: summary
description: description
location: location
start: start
due: due                        # %(date)s
completed: completed
priority: priority              # low, medium, high, none
list: list                      # %(lists)s
"""

# credit: https://chase-seibert.github.io/blog/2012/10/31/python-fork-exec-vim-raw-input.html
def raw_input_editor(default=None, editor=None):
    ''' like the built-in raw_input(), except that it uses a visual
    text editor for ease of editing. Unlike raw_input() it can also
    take a default value. '''
    with tempfile.NamedTemporaryFile(mode='r+', suffix=".yml") as tmpfile:
        if default:
            #  if isinstance(default, dict):
            #      # use "sort_keys" for normal yaml package
            #      tmpfile.write(yaml.dump(default, sort_keys=False))
            #  else:
            #      tmpfile.write(default)
            #  tmpfile.flush()

            #  tmpfile.write(yaml.dump(default))
            yaml.dump(default, tmpfile)
            tmpfile.flush()
        subprocess.check_call([editor or get_editor(), tmpfile.name])
        tmpfile.seek(0)
        return tmpfile.read().strip()

def get_editor():
    '''Get default editor'''
    return (os.environ.get('VISUAL')
            or os.environ.get('EDITOR')
            or 'vi')

def save_todo(todo, updated_todo, formatter, lists):
    '''Save todo'''
    todo.summary = updated_todo["summary"]
    todo.description = updated_todo["description"]
    todo.location = updated_todo["location"]
    todo.due = formatter.parse_datetime(updated_todo["due"])
    todo.start = formatter.parse_datetime(updated_todo["start"])
    if not todo.is_completed and updated_todo["is_completed"]:
        todo.complete()
    elif todo.is_completed and not updated_todo["is_completed"]:
        todo.status = "NEEDS-ACTION"
        todo.completed_at = None
    todo.priority = formatter.parse_priority(updated_todo["priority"])

    todo_index = next((index for (index, d) in enumerate(lists) if d.name == updated_todo["list"]), None)
    todo.list = lists[todo_index]


def edit_in_editor(todo, lists, formatter):
    '''Edit todo in editor as yaml'''
    todo_lists = list(lists)

    todo_yaml_str = YAML_STR
    #  for _list in (todo_lists):
    #      if not any(char.isdigit() for char in _list.name):
    #          todo_yaml_str += "# list: " + _list.name + "\n"

    list_suggestions = ""
    for _list in (todo_lists):
        if not any(char.isdigit() for char in _list.name):
            list_suggestions += _list.name + ", "

    #  yaml_todo = yaml.load(todo_yaml_str)
    yaml_todo = yaml.load(todo_yaml_str % {'date': humanize.naturaldate(todo.due) or 'e.g. 2020-11-09 12:30', 'lists': list_suggestions[:-2]})

    yaml_todo["summary"] = todo.summary or None
    yaml_todo["description"] = todo.description or None
    yaml_todo["location"] = todo.location or None
    yaml_todo["start"] = formatter.format_datetime(todo.start) or None
    yaml_todo["due"] = formatter.format_datetime(todo.due) or None
    yaml_todo["is_completed"] = todo.is_completed
    yaml_todo["priority"] = formatter.format_priority(todo.priority)
    yaml_todo["list"] = str(todo.list)

    result = raw_input_editor(yaml_todo)
    updated_todo = yaml.load(result)

    save_todo(todo, updated_todo, formatter, todo_lists)
