from django.conf import settings
from os import path, listdir
from lxml import etree

class XmlJsonImportModuleException(Exception):
    pass

if not hasattr(settings, 'XSLT_FILES_DIR'):
    raise XmlJsonImportModuleException('Settings must contain XSLT_FILES_DIR parameter')

if not path.exists(settings.XSLT_FILES_DIR):
    raise XmlJsonImportModuleException('Directory specified by XSLT_FILES_DIR does not exist')

for filename in listdir(settings.XSLT_FILES_DIR):
    filepath = path.join(settings.XSLT_FILES_DIR, filename)
    if path.isfile(filepath):
        try:
            xslt_etree = etree.parse(filepath)
        except etree.XMLSyntaxError as er:
            raise XmlJsonImportModuleException('File ' + filepath + ' is not a valid XML file: ' + str(er))
        try:
            transform = etree.XSLT(xslt_etree)
        except etree.XSLTParseError as er:
            raise XmlJsonImportModuleException('File ' + filepath + ' is not a valid XSLT file: ' + str(er))
