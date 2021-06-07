# -*- coding=UTF-8 -*-
"""generate typing from module help.  

Usage: "$PYTHON" ./scripts/full_help.py $MODULE | "$PYTHON" ./scripts/typing_from_help.py -
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import cast_unknown as cast
import re


_CLASS_MRO_START = "Method resolution order:"
_CLASS_METHODS_START = "Methods defined here:"
_CLASS_CLASS_METHODS_START = "Class methods defined here:"
_CLASS_STATIC_METHODS_START = "Static methods defined here:"
_CLASS_DATA_ATTR_START = "Data and other attributes defined here:"
_CLASS_READ_ONLY_PROPERTY_START = "Readonly properties defined here:"
_CLASS_DATA_DESC_START = "Data descriptors defined here:"
_CLASS_INHERITED_METHODS_START = "Methods inherited from (.+):"
_CLASS_INHERITED_CLASS_METHODS_START = "Class methods inherited from (.+):"
_CLASS_INHERITED_STATIC_METHODS_START = "Static methods inherited from (.+):"
_CLASS_INHERITED_DATA_ATTR_START = "Data and other attributes inherited from (.+):"
_CLASS_INHERITED_DATA_DESC_START = "Data descriptors inherited from (.+):"
_CLASS_SECTION_END = "-{20,}"

TYPE_MAP = {
    "__builtin__.object": "",
    "__builtin__.Knob": "",
    "object": "",
    "exceptions.Exception": "Exception",
    "String": "typing.Text",
    "string": "typing.Text",
    "str": "typing.Text",
    "Float": "float",
    "Floating point value": "float",
    "Bool": "bool",
    "Boolean": "bool",
    "Int": "int",
    "Integer": "int",
    "integer": "int",
    "Integer value": "int",
    "void": "None",
    "list of strings or single string": "typing.Union[typing.List[typing.Text], typing.Text]",
    "List of strings": "typing.List[typing.Text]",
    "list of str": "typing.List[typing.Text]",
    "String list": "typing.List[typing.Text]",
    "List of int": "typing.List[int]",
    "list of int": "typing.List[int]",
    "[int]": "typing.List[int]",
    "List": "list",
    "(x, y, z)": "typing.Tuple",
    "list of (x,y,z) tuples": "typing.List",
    "list of floats": "typing.List[float]",
}


def _iter_class_sections(lines):
    lines = iter(lines)
    section_type = "docstring"
    section_values = []
    for line in lines:
        if re.match(_CLASS_MRO_START, line):
            yield (section_type, section_values)
            section_type = "mro"
            section_values = []
        elif re.match(_CLASS_METHODS_START, line):
            yield (section_type, section_values)
            section_type = "methods"
            section_values = []
        elif re.match(_CLASS_STATIC_METHODS_START, line):
            yield (section_type, section_values)
            section_type = "static-methods"
            section_values = []
        elif re.match(_CLASS_CLASS_METHODS_START, line):
            yield (section_type, section_values)
            section_type = "class-methods"
            section_values = []
        elif re.match(_CLASS_DATA_ATTR_START, line):
            yield (section_type, section_values)
            section_type = "data"
            section_values = []
        elif re.match(_CLASS_DATA_DESC_START, line):
            yield (section_type, section_values)
            section_type = "data"
            section_values = []
        elif re.match(_CLASS_READ_ONLY_PROPERTY_START, line):
            yield (section_type, section_values)
            section_type = "data"
            section_values = []
        elif re.match(_CLASS_INHERITED_METHODS_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_METHODS_START, line)
            section_type = "inherited-methods"
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_CLASS_METHODS_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_CLASS_METHODS_START, line)
            section_type = "inherited-class-methods"
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_STATIC_METHODS_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_STATIC_METHODS_START, line)
            section_type = "inherited-static-methods"
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_DATA_ATTR_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_DATA_ATTR_START, line)
            section_type = "inherited-data"
            section_values = [match.group(1)]
        elif re.match(_CLASS_INHERITED_DATA_DESC_START, line):
            yield (section_type, section_values)
            match = re.match(_CLASS_INHERITED_DATA_DESC_START, line)
            section_type = "inherited-data"
            section_values = [match.group(1)]
        elif re.match(_CLASS_SECTION_END, line):
            yield (section_type, section_values)
            section_type = ""
            section_values = []
        else:
            section_values.append(line)
    if section_values:
        yield (section_type, section_values)


def _strip_lines(lines):
    return "\n".join(lines).strip("\n").splitlines()


def _parse_by_indent(lines, indent="    "):
    key = ""  # type: str
    values = []
    for line in lines:
        line = cast.text(line)
        if line.startswith(indent) or line == indent.rstrip(" "):
            values.append(line[len(indent) :])
        else:
            if key:
                yield (key, values)
                key = ""
                values = []
            key = line
    if values:
        yield (key, values)


def _parse_class_data(lines):
    for k, v in _parse_by_indent(lines):
        data_def = _parse_data_description(k)
        if v:
            data_def["docstring"] = _strip_lines(v)
        yield data_def


def _parse_args(args):
    args = (args or "").split(",")
    args = [i.strip() for i in args]
    args = [TYPE_MAP.get(i, i) for i in args]
    args = [i for i in args if i]
    if "..." in args:
        args = ["*args", "**kwargs"]

    ret = []
    for i in args:
        match = re.match(r"\((.+)\)(.+)$", i)
        if match:
            ret.append("%s: %s" % (match.group(2), match.group(1)))
            continue
        ret.append(i)

    return ret


def _parse_class_method(lines):
    for k, v in _parse_by_indent(lines):
        match = re.match(r"^(.+?)(?:\((.+)\))?(?: from (.+))?$", k)
        if not match:
            raise NotImplementedError(k, v)
        name = match.group(1)
        args = _parse_args(match.group(2))
        docstring = v
        return_type = ""
        match = (
            len(docstring) > 0
            and re.match(
                r"(?:self\.)?" + re.escape(name) + r"\((.*)\) ?-> ?(.+?)\.? *:?$",
                docstring[0],
            )
            or None
        )
        if match:
            docstring = docstring[1:]
            args = _parse_args(match.group(1))
            return_type = match.group(2) or ""
        args = [i.strip() for i in args]
        args = [TYPE_MAP.get(i, i) for i in args]
        args = [i for i in args if i]
        return_type = TYPE_MAP.get(return_type, return_type)
        docstring = _strip_lines(docstring)

        yield dict(name=name, args=args, return_type=return_type, docstring=docstring)


def _iter_classes(lines):
    for class_key, class_values in _parse_by_indent(lines, " |  "):

        if not class_values:
            # Ignore summary list and empty lines
            continue

        match = re.match(r"(.+?) = class (.+?)(?:\((.+)\))?$", class_key)
        if match:
            g3 = match.group(3)
            yield dict(
                name=match.group(1),
                inherits=g3.split(",") if g3 else [],
                real_name=match.group(2),
            )
            continue
        match = re.match(r"class (.+?)(?:\((.+)\))?$", class_key)
        if not match:
            raise NotImplementedError(
                "_iter_classes: %s: %s" % (class_key, class_values)
            )
        g2 = match.group(2)
        class_def = dict(
            name=match.group(1),
            inherits=g2.split(",") if g2 else [],
            static_methods=[],
            class_methods=[],
            methods=[],
            data=[],
            docstring=[],
        )
        for (section_key, section_values) in _iter_class_sections(class_values):
            if section_key == "" and section_values == []:
                continue
            elif section_key == "inherited-data":
                continue
            elif section_key == "inherited-methods":
                continue
            elif section_key == "inherited-class-methods":
                continue
            elif section_key == "inherited-static-methods":
                continue
            elif section_key == "mro":
                continue
            elif section_key == "docstring":
                class_def["docstring"] = section_values
            elif section_key == "data":
                class_def["data"] = list(_parse_class_data(section_values))
            elif section_key == "methods":
                class_def["methods"] = list(_parse_class_method(section_values))
            elif section_key == "static-methods":
                class_def["static_methods"] = list(_parse_class_method(section_values))
            elif section_key == "class-methods":
                class_def["class_methods"] = list(_parse_class_method(section_values))
            else:
                raise NotImplementedError(section_key, section_values)
        class_def["docstring"] = _strip_lines(class_def["docstring"])
        yield class_def


def _iter_functions(lines):
    for k, v in _parse_by_indent(lines):
        match = re.match(r"(.+?) = (.+?)(?:\((.+)\))?$", k)
        if match:
            g3 = match.group(3)
            yield dict(
                name=match.group(1),
                inherits=g3.split(",") if g3 else [],
                real_name=match.group(2),
            )
            continue

        match = re.match(r"(.+?) lambda (.*)$", k)
        if match:
            yield dict(
                name=match.group(1),
                args=_parse_args(match.group(2)),
                docstring=_strip_lines(v),
                return_type="",
            )
            continue

        match = re.match(r"(.+?)\((.*)\)$", k)
        if not match:
            raise NotImplementedError(k, v)
        name = match.group(1)
        args = _parse_args(match.group(2))
        docstring = _strip_lines(v)
        match = (
            len(docstring) > 0
            and re.match(re.escape(name) + r"\((.*)\) ?-> ?(.+?)\.? *$", docstring[0])
            or None
        )
        return_type = ""
        if match:
            docstring = docstring[1:]
            args = _parse_args(match.group(1))
            return_type = match.group(2) or ""
        return_type = TYPE_MAP.get(return_type, return_type)
        docstring = _strip_lines(docstring)
        yield dict(name=name, args=args, docstring=docstring, return_type=return_type)


def _typing_from_class(class_def):
    name = class_def["name"]
    real_name = class_def.get("real_name")
    if real_name is not None:
        yield "%s = %s" % (name, real_name)
        return
    docstring = class_def["docstring"]
    inherits = class_def["inherits"]
    inherits = [TYPE_MAP.get(i, i) for i in inherits]
    inherits = [i for i in inherits if i]
    methods = class_def["methods"]
    class_methods = class_def["class_methods"]
    static_methods = class_def["static_methods"]
    data = class_def["data"]
    yield "class %s%s:" % (name, "(%s)" % ",".join(inherits) if inherits else "")
    if docstring:
        yield '    """'
        for i in docstring:
            yield ("    %s" % i).rstrip()
        yield '    """'
        yield ""
    if data:
        for i in data:
            yield "    %s: ...%s" % (
                i["name"],
                " = %s" % i["value"] if i["value"] else "",
            )
            yield '    """'
            for j in i["docstring"]:
                yield ("    %s" % j).rstrip()
            yield '    """'
            yield ""
    if static_methods:
        for i in static_methods:
            yield "    @staticmethod"
            yield "    def %s(%s)%s:" % (
                i["name"],
                ", ".join(i["args"]),
                " -> %s" % i["return_type"] if i["return_type"] else "",
            )
            yield '        """'
            for j in i["docstring"]:
                yield ("        %s" % j).rstrip()
            yield '        """'
            yield "        ..."
            yield ""
    if class_methods:
        for i in class_methods:
            if "cls" not in i["args"]:
                i["args"].insert(0, "cls")
            yield "    @classmethod"
            yield "    def %s(%s)%s:" % (
                i["name"],
                ", ".join(i["args"]),
                " -> %s" % i["return_type"] if i["return_type"] else "",
            )
            yield '        """'
            for j in i["docstring"]:
                yield ("        %s" % j).rstrip()
            yield '        """'
            yield "        ..."
            yield ""
    if methods:
        for i in methods:
            if "self" not in i["args"]:
                i["args"].insert(0, "self")
            yield "    def %s(%s)%s:" % (
                i["name"],
                ", ".join(i["args"]),
                " -> %s" % i["return_type"] if i["return_type"] else "",
            )
            yield '        """'
            for j in i["docstring"]:
                yield ("        %s" % j).rstrip()
            yield '        """'
            yield "        ..."
            yield ""

    yield "    ..."


def _typing_from_function(func_def):
    name = func_def["name"]
    real_name = func_def.get("real_name")
    if real_name is not None:
        yield "%s = %s" % (name, real_name)
        return
    args = func_def["args"]
    return_type = func_def["return_type"]
    docstring = func_def["docstring"]
    yield "def %s(%s)%s:" % (
        name,
        ", ".join(args),
        " -> %s" % return_type if return_type else "",
    )
    yield '    """'
    for i in docstring:
        yield ("    %s" % i).rstrip()
    yield '    """'
    yield "    ..."
    yield ""


def _typing_from_functions(lines):
    for i in _iter_functions(lines):
        for j in _typing_from_function(i):
            yield j
        yield ""


def _typing_from_classes(lines):
    for i in _iter_classes(lines):
        for j in _typing_from_class(i):
            yield j
        yield ""


def _parse_data_description(i):
    match = re.match(r"^(.+?)(?: ?= ?(.+))?$", i)
    if not match:
        raise NotImplementedError(i)
    name = match.group(1)
    value = match.group(2) or ""
    value_type = "..."
    docstring = []
    if value.endswith("..."):
        docstring.append(value)
        value = ""
    elif value.startswith("<"):
        docstring.append(value)
        value = ""
    elif value.startswith(("'", '"')):
        docstring.append(value)
        value_type = "typing.Text"
        value = ""
    elif value.startswith("["):
        docstring.append(value)
        value = ""
        value_type = "list"
    elif value.startswith("{"):
        docstring.append(value)
        value = ""
        value_type = "dict"
    elif value in ("True", "False"):
        docstring.append(value)
        value = ""
        value_type = "bool"
    elif re.match(r"-?\d+", value):
        value_type = "int"
    return dict(name=name, value=value, value_type=value_type, docstring=docstring)


def _iter_data(lines):
    for i in lines:
        if i == "":
            continue
        yield _parse_data_description(i)


def _typing_from_datum(datum_def):
    name = datum_def["name"]
    value = datum_def["value"]
    value_type = datum_def["value_type"]
    docstring = datum_def["docstring"]

    yield "%s: %s%s" % (name, value_type, " = %s" % value if value else "")
    if docstring:
        yield '"""'
        for i in docstring:
            yield i
        yield '"""'


def _typing_from_data(lines):
    for i in _iter_data(lines):
        for j in _typing_from_datum(i):
            yield j
        yield ""


def _handle_windows_line_ending(lines):
    for i in lines:
        i = cast.text(i)
        yield i.strip("\r\n")


def iterate_typing_from_help(lines):
    yield "# -*- coding=UTF-8 -*-"
    yield "# This typing file was generated by typing_from_help.py"
    for k, v in _parse_by_indent(lines):
        if k == "NAME":
            yield '"""'
            for i in v:
                yield i
            yield '"""'
            yield ""
            yield "import typing"
            yield ""
        elif k == "DATA":
            for i in _typing_from_data(v):
                yield i
        elif k == "CLASSES":
            for i in _typing_from_classes(v):
                yield i
        elif k == "FILE":
            pass
        elif k == "PACKAGE CONTENTS":
            pass
        elif k == "DESCRIPTION":
            yield '"""'
            for i in v:
                yield i
            yield '"""'
        elif k == "SUBMODULES":
            for i in v:
                yield "from . import %s" % i
        elif k == "VERSION":
            yield "# version: %s" % cast.one(v)
        elif k == "FUNCTIONS":
            for i in _typing_from_functions(v):
                yield i
        elif not v:
            pass
        else:
            raise NotImplementedError(k, v)


def typing_from_help(text):
    return "\n".join(iterate_typing_from_help(cast.text(text).splitlines()))


if __name__ == "__main__":
    import argparse
    import sys
    import codecs

    parser = argparse.ArgumentParser()
    _ = parser.add_argument("--type", dest="type")
    _ = parser.add_argument("file")
    args = parser.parse_args()
    should_close = False
    if args.file == "-":
        f = sys.stdin
    else:
        f = codecs.open(args.file, "r", encoding="utf-8")
        should_close = True

    try:
        lines = _handle_windows_line_ending(f)
        if args.type == "class":
            for i in _typing_from_classes(lines):
                print(i)
        else:
            for i in iterate_typing_from_help(lines):
                print(i)
    finally:
        if should_close:
            f.close()
