import json
from xml.dom.minidom import parse
import xml.dom.minidom


def print_as_json(value):
  print(json.dumps(value, indent=2))


def node_to_dict(node):
  attrs = node.attributes
  return dict(attrs.items())


def get_fundamental_types(tree):
  fundamental_types = tree.getElementsByTagName("FundamentalType")
  res = []
  for each in fundamental_types:
    res.append(node_to_dict(each))
  return res

def get_methods(tree):
  methods = tree.getElementsByTagName("Method")
  res = []
  for each in methods:
    res.append(node_to_dict(each))
  return res



tree = xml.dom.minidom.parse("ctp.xml")
document = tree.documentElement
res = get_methods(tree)

print_as_json(res)



"""
if collection.hasAttribute("shelf"):
   print "Root element : %s" % collection.getAttribute("shelf")

# 在集合中获取所有电影
movies = collection.getElementsByTagName("movie")

# 打印每部电影的详细信息
for movie in movies:
   print "*****Movie*****"
   if movie.hasAttribute("title"):
      print "Title: %s" % movie.getAttribute("title")

   type = movie.getElementsByTagName('type')[0]
   print "Type: %s" % type.childNodes[0].data
   format = movie.getElementsByTagName('format')[0]
   print "Format: %s" % format.childNodes[0].data
   rating = movie.getElementsByTagName('rating')[0]
   print "Rating: %s" % rating.childNodes[0].data
   description = movie.getElementsByTagName('description')[0]
   print "Description: %s" % description.childNodes[0].data
"""
