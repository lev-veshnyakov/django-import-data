from django.conf import settings
from os import path

class XmlJsonImportModuleException(Exception):
    pass

if not hasattr(settings, 'XSLT_FILES_DIR'):
    raise XmlJsonImportModuleException('Settings must contain XSLT_FILES_DIR parameter')

if not path.exists(settings.XSLT_FILES_DIR):
    raise XmlJsonImportModuleException('Directory specified by XSLT_FILES_DIR does not exist')
