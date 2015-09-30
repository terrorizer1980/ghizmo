from __future__ import print_function

from ghizmo.commands import lib

import os
import codecs
import yaml
import urllib

_ROLES_FILES = ["authors-info.yml", "authors-info.json", "admin/authors-info.yml", "admin/authors-info.json"]

def assemble_authors(config, args):
  """
  Assemble a list of authors as an AUTHORS.md file based on GitHub repo history and a
  authors-info.{yml,json} file.
  """
  github = config.github
  repo = config.repo
  roles_filename = None
  for filename in _ROLES_FILES:
    if os.path.isfile(filename):
      roles_filename = filename

  header = None
  footer = None
  roles = {}
  if roles_filename:
    yield lib.status("Info from: %s" % roles_filename)
    with codecs.open(roles_filename, "r", "utf-8") as f:
      info = yaml.safe_load(f)
      header = info.get("header")
      footer = info.get("footer")
      roles = info.get("roles")
  else:
    yield lib.status("No roles file")

  author_list = []
  for contributor in repo.contributors():
    user = github.user(contributor.login)
    author_list.append((user.login, user.name, roles.get(user.login)))

  # Sort alphabetically by login.
  author_list.sort()

  yield lib.status("Read %s authors" % len(author_list))

  def format_user(login, name):
    if login and name:
      return u"%s (%s)" % (name, login)
    elif login:
      return login
    else:
      raise ValueError("Missing login name")

  with codecs.open("AUTHORS.md", "w", "utf-8") as f:
    f.write(u"# Authors\n\n")
    if header:
      f.write(u"%s\n\n" % header)
    for (login, name, role) in author_list:
      user_url = "https://github.com/%s" % login
      # Link to commits by that author
      commits_url = "%s/commits?author=%s" % (repo.html_url, urllib.quote_plus(login))
      # Link to issues and PRs by that author.
      issues_url = "%s/issues?q=%s" % (repo.html_url, urllib.quote_plus("author:%s" % login))

      role_str = u" \u2014 _%s_" % role if role else ""
      f.write(u"* [%s](%s) [[commits](%s), [issues](%s)]%s\n" % (format_user(login, name), user_url, commits_url, issues_url, role_str))
    if footer:
      f.write(u"\n%s\n\n" % footer)

    f.write(u"\n(This file was auto-generated by [ghizmo assemble-authors](https://github.com/jlevy/ghizmo).)")