from collections import namedtuple

from docutils.core import publish_doctree
from jinja2 import Environment, PackageLoader, ChoiceLoader, FileSystemLoader

import clearest

_loader = ChoiceLoader([PackageLoader("clearest", "templates")])
Parameter = namedtuple("Parameter", ["name", "type", "docs"])


def set_templates_path(path):
    new_loader = FileSystemLoader(path, followlinks=True)
    if len(_loader.loaders) == 1:
        _loader.loaders.insert(0, new_loader)
    else:
        assert len(_loader.loaders) == 2
        _loader.loaders[0] = new_loader


def parse(doc_string):  # TODO: rewrite (really ugly)
    if not doc_string:
        return {}

    def _paragraph(node_):
        return str(node_.children[0])

    def _is_node(node_, name):
        return node_ and node_.tagname == name

    def _is_paragraph(node_, value):
        return _is_node(node_, "paragraph") and _paragraph(node_) == value

    def _fields(node_):
        fields = []
        returns = None
        for field in node_:
            name, body = None, None
            for child in field:
                if _is_node(child, "field_name"):
                    name = str(child.children[0])
                elif _is_node(child, "field_body"):
                    body = _paragraph(child.children[0])
            name_pieces = name.split(" ")
            if len(name_pieces) == 3:
                fields.append(Parameter(name_pieces[2], name_pieces[1], body))
            elif len(name_pieces) == 2:
                fields.append(Parameter(name_pieces[1], None, body))
            elif name_pieces[0] == "return":
                returns = body
        return fields, returns

    result = {}
    text = []
    root = publish_doctree(doc_string).children[0]
    if len(root.children) == 1 and root.children[0].tagname == "#text":
        text.append(_paragraph(root))
    else:
        for index, (node, next_node) in enumerate(zip(root.children, root.children[1:] + [None])):
            if index == 0 and _is_node(node, "paragraph"):
                text.append(str(node.children[0]))
            else:
                if _is_node(next_node, "literal_block") and _is_paragraph(node, ":example:"):
                    result["example"] = str(next_node.children[0])
                elif _is_node(next_node, "literal_block") and _is_paragraph(node, ":rexample:"):
                    result["result_example"] = str(next_node.children[0])
                elif _is_node(node, "field_list"):
                    result["params"], result["return"] = _fields(node)
    result["text"] = "".join(text)
    return result


def generate_single(doc_string):
    to_render = {
        "clearest_version": clearest.__version__,
        "clearest_home": clearest.__homepage__,
    }
    to_render.update(parse(doc_string))
    env = Environment(loader=_loader)
    template = env.get_template("single.html")
    return template.render(to_render)


def generate_index(all_):
    urls = [(desc, method, path, generate_single(doc_string)) for desc, method, path, doc_string in all_]
    env = Environment(loader=_loader)
    template = env.get_template("index.html")
    return template.render({"urls": urls})
