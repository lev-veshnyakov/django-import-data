from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.utils.six import StringIO
from os import path

app_dir = path.dirname(path.abspath(__file__))
test_data_dir = path.join(app_dir, 'test_data')

class ProcessXsltCommandTests(TestCase):
    def test_entire_command(self):
        html_path = path.join(test_data_dir, 'stackoverflow.html')
        xslt_path = path.join(test_data_dir, 'stackoverflow.xslt')
        out = StringIO()
        call_command('process_xslt', html_path, xslt_path, '--save', stdout=out)
        
class ValidateXmlCommandTests(TestCase):
    def test_entire_command(self):
        valid_xml_path = path.join(test_data_dir, 'valid.xml')
        rng_schema_path = path.join(app_dir, 'schema.rng')
        out = StringIO()
        call_command('validate_xml', valid_xml_path, rng_schema_path, stdout=out)
        
class JsonToXmlCommandTests(TestCase):
    def test_entire_command(self):
        valid_json_path = path.join(test_data_dir, 'valid.json')
        out = StringIO()
        call_command('json_to_xml', valid_json_path, stdout=out)
