from jinja2 import Environment, PackageLoader, ChoiceLoader, FileSystemLoader

import clearest

_loader = ChoiceLoader([PackageLoader("clearest", "templates")])


def set_templates_path(path):
    new_loader = FileSystemLoader(path, followlinks=True)
    if len(_loader.loaders) == 1:
        _loader.loaders.insert(0, new_loader)
    else:
        assert len(_loader.loaders) == 2
        _loader.loaders[0] = new_loader


def generate_single(method, path, doc_string, **kwargs):
    to_render = kwargs.copy()
    to_render.update({
        "clearest_version": clearest.__version__,
        "clearest_home": clearest.__homepage__,
        "method": method,
        "path": path
    })

    env = Environment(loader=_loader)
    template = env.get_template("single.html")
    return template.render(to_render)
