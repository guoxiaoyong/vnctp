import functools
import pathlib
import json
from lxml import etree
import jinja2
import enum


class CtpClass(enum.Enum):
  MD_API = 'CThostFtdcMdApi'
  MD_SPI = 'CThostFtdcMdSpi'
  TD_API = 'CThostFtdcTraderApi'
  TD_SPI = 'CThostFtdcTraderSpi'


def transform_param_name(name):
  for idx, c in enumerate(name):
    if c.isupper():
      return name[idx:]


def transform_param_list(param_list):
  res = []
  for param in param_list:
    res.append(f"{param['type']} {param['name']}")
  return ', '.join(res)


def transform_call_param_list(param_list):
  res = []
  for param in param_list:
    res.append(f"{param['name']}")
  return ', '.join(res)



def print_as_json(value):
  print(json.dumps(value, indent=2))


def node_to_dict(node):
  res = dict(node.items())
  res.pop('line', None)
  res.pop('file', None)
  res.pop('location', None)
  res.pop('mangled', None)
  return res


SCRIPT_PATH = pathlib.Path(__file__).absolute()


class CtpApiParser(object):
    def __init__(self):
        search_path = SCRIPT_PATH.parent.joinpath('template')
        loader = jinja2.FileSystemLoader(searchpath=search_path.as_posix())
        template_env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        template_env.filters['transform_param_name'] = transform_param_name;
        template_env.filters['transform_param_list'] = transform_param_list;
        template_env.filters['transform_call_param_list'] = transform_call_param_list;
        xml_path = SCRIPT_PATH.parent.joinpath('ctp.xml')
        self._tree = etree.parse(xml_path.as_posix())
        self._template_env =  template_env

    @functools.lru_cache(maxsize=4096)
    def resolve_type(self, elem_id):
        node = self._tree.findall(f'.//*[@id="{elem_id}"]')
        assert len(node) == 1, len(node)
        node = node[0]

        if node.tag in ('Class', 'Struct', 'FundamentalType'):
            return node.attrib['name']
        elif node.tag == 'PointerType':
            return self.resolve_type(node.attrib['type']) + '*';
        elif node.tag == 'CvQualifiedType':
            return 'const ' + self.resolve_type(node.attrib['type']);
        else:
            return elem_id

    @functools.lru_cache(maxsize=4096)
    def resolve_class(self, elem_id):
        node = self._tree.findall(f'.//*[@id="{elem_id}"]')
        assert len(node) == 1, len(node)
        node = node[0]
        return node.attrib['name']

    def get_methods(self, class_name):
        methods = self._tree.xpath("//Method")
        res = []
        for each in methods:
            node_dict = node_to_dict(each)
            node_dict['params'] = []
            node_dict['context'] = self.resolve_class(node_dict['context'])
            if node_dict['context'] != class_name:
                continue

            node_dict['returns'] = self.resolve_type(node_dict['returns'])
            for arg in each:
                arg_dict = node_to_dict(arg)
                arg_dict['type'] = self.resolve_type(arg_dict['type'])
                node_dict['params'].append(arg_dict)
            res.append(node_dict)
        return res

    def get_struct(self):
        struct_list = self._tree.xpath('//Struct[@members]')
        res = []
        for each in struct_list:
          res.append(node_to_dict(each))
        return res

    def get_md(self):
        req_method_list = parser.get_methods(class_name=CtpClass.MD_API.value)
        on_rsp_method_list = parser.get_methods(class_name=CtpClass.MD_SPI.value)
        template = self._template_env.get_template('xyctpmd.cc.jinja')
        text = template.render(
            on_rsp_method_list=on_rsp_method_list,
            req_method_list=req_method_list,
            struct_list=struct_list)
        return text


parser = CtpApiParser()
text = parser.get_md()
print(text)
