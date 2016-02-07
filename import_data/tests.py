from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.utils.six import StringIO
from os import path
from import_data.management.commands import json_to_xml, process_xslt, validate_xml
from import_data import models
from lxml import etree, html

app_dir = path.dirname(path.abspath(__file__))
test_data_dir = path.join(app_dir, 'test_data')
html_path = path.join(test_data_dir, 'stackoverflow.html')
xslt_path = path.join(test_data_dir, 'stackoverflow.xslt')
rng_schema_path = path.join(app_dir, 'schema.rng')
valid_xml_path = path.join(test_data_dir, 'valid.xml')
valid_json_path = path.join(test_data_dir, 'valid.json')
valid_xml_source_etree = etree.parse(valid_xml_path)

class ProcessXsltCommandTests(TestCase):
    
    def test_entire_command(self):
        out = StringIO()
        call_command('process_xslt', html_path, xslt_path, '--save', stdout=out)
        
    def test_get_model(self):
        self.assertIs(process_xslt.get_model('import_data.User'), models.User)
        
    def test_get_related_item_element(self):
        fk_element = valid_xml_source_etree.xpath('//fk[@key="idp1408854340"]')[0]
        related_element = valid_xml_source_etree.xpath('//model[@model="import_data.User"]/item[@key="idp1408854340"]')[0]
        self.assertIs(process_xslt.get_related_item_element(fk_element), related_element)
        
    def test_get_model_elements(self):
        model_elements = valid_xml_source_etree.xpath('//model')
        self.assertListEqual(process_xslt.get_model_elements(valid_xml_source_etree), model_elements)
        
    def test_get_item_elements(self):
        model_element = valid_xml_source_etree.xpath('//model')[0]
        item_elements = model_element.xpath('.//item')
        self.assertListEqual(process_xslt.get_item_elements(model_element), item_elements)
        
    def test_get_field_elements(self):
        item_element = valid_xml_source_etree.xpath('//item')[0]
        field_elements = item_element.xpath('.//field')
        self.assertListEqual(process_xslt.get_field_elements(item_element), field_elements)
        
    def test_get_fk_elements(self):
        item_element = valid_xml_source_etree.xpath('//item')[0]
        fk_elements = item_element.xpath('.//fk')
        self.assertListEqual(process_xslt.get_fk_elements(item_element), fk_elements)
        
    def test_get_m2m_elements(self):
        item_element = valid_xml_source_etree.xpath('//item')[0]
        m2mk_elements = item_element.xpath('.//m2mk')
        self.assertListEqual(process_xslt.get_m2m_elements(item_element), m2mk_elements)
        
class ValidateXmlCommandTests(TestCase):
    def test_entire_command(self):
        out = StringIO()
        call_command('validate_xml', valid_xml_path, rng_schema_path, stdout=out)
        
class JsonToXmlCommandTests(TestCase):
    def test_entire_command(self):
        out = StringIO()
        call_command('json_to_xml', valid_json_path, stdout=out)
