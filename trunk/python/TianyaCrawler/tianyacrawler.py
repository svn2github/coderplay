#!/usr/bin/env python
import urllib2


"""
This program takes an URL of tianya post and try to grab contents of all posts
by the original author.
"""
url = """http://www.tianya.cn/publicforum/content/no05/1/146711.shtml"""

req = urllib2.Request(url)

try:
    response = urllib2.urlopen(req)
except urllib2.URLError, e:
    print str(e)


page = response.read()

m = re.search(r"<em class=\"current\".*em>", page)

m.group(0)
