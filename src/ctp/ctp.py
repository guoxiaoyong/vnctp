import json
from lxml import etree


class CppStruct(object):
  def __init__(self):
    self.name = None
    self.fields = []


def print_as_json(value):
  print(json.dumps(value, indent=2))


def node_to_dict(node):
  return dict(node.items())


def get_fundamental_types(tree):
  fundamental_types = tree.xpath('//FundamentalType')
  res = []
  for each in fundamental_types:
    res.append(node_to_dict(each))
  return res

def get_array_types(tree):
  array_types = tree.xpath('//ArrayType')
  res = []
  for each in array_types:
    res.append(node_to_dict(each))
  return res


def get_methods(tree):
  methods = tree.xpath("//Method")
  print(tree)
  res = []
  for each in methods:
    print(each)
    res.append(node_to_dict(each))
  return res


def get_struct(tree):
  struct_list = tree.xpath('//Struct[@members]')
  res = []
  for each in struct_list:
    res.append(node_to_dict(each))
  return res


def get_by_id(tree, elem_id):
  node = tree.findall(f'.//*[@id="{elem_id}"]')[0]
  return node_to_dict(node)



tree = etree.parse('ctp.xml')
method_list = get_methods(tree)
#print_as_json(method_list)
