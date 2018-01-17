# XML Parsing
from xml.etree.ElementTree import parse


def _xml_to_code(filename):
    doc = parse(filename)
    code = ''
    for structure in doc.findall('structure'):
        clscode = _struct_to_class(structure)
        code += clscode
    return code


def _struct_to_class(structure):
    name = structure.get('name')
    code = 'class %s(Structure):\n' % name
    for field in structure.findall('field'):
        dtype = field.get('type')

        options = ['%s=%s' % (key, val) for key, val in field.items()
                   if key != 'type'
                   ]
        name = field.text.strip()

        code += '    %s = %s(%s)\n' % (
            name, dtype, ', '.join(options)
        )
    return code


import sys
import os


class StructFinder:

    @classmethod
    def find_module(cls, fullname, path):
        for dirname in sys.path:
            filename = os.path.join(dirname, fullname + '.xml')

            if os.path.exists(filename):
                print('Loading XML: ', filename)
                # Now what?
                return StructXMLLoader(filename)
        return None


import imp
class StructXMLLoader:
    def __init(self, filename):
        self.filename = filename

    def load_module(self, fullname):
        # Carry out the import steps
        if fullname in sys.modules:
            mod = sys.modules[fullname]
        else:
            mod = imp.new_module(fullname)
            sys.modules[fullname] = mod
        mod.__file__ = self.filename
        mod.__loader = self
        code = _xml_to_code(self.filename)
        exec(code, mod.__dict__, mod.__dict__)
        return mod


def install_importer():
    sys.meta_path.append(StructFinder)
