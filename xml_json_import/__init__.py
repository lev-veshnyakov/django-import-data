from django.conf import settings

class XmlJsonImportModuleException(Exception):
    pass

if not hasattr(settings, 'XSLT_FILES_DIR'):
    raise XmlJsonImportModuleException('Settings must contain XSLT_FILES_DIR parameter')
