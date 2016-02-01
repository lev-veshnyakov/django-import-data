from django.core.management.base import BaseCommand
from lxml import etree, html
import urllib2
from os import path
import importlib

class Command(BaseCommand):
    help = 'Processes XSLT transformation on a fetched by URL resource and outputs the result'

    def add_arguments(self, parser):
        parser.add_argument('url', help='URL to fetch source XML')
        parser.add_argument('xslt_file', help='Path to XSLT transformation file')
        parser.add_argument('--validate', action='store_true', 
                             help='Validate against Relax NG schema after transformation')
        rng_file = path.join(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))), 'schema.rng')
        parser.add_argument('--rng_file', default=rng_file,
                             help='Path to RELAX NG file. Defaults to schema.rng in module dir. '
                                  'Used only if --validate is set')
        parser.add_argument('--save', action='store_true', 
                             help='Save data to the model. Successful validation against Relax NG '
                                  'schema is required. Model names and fields in transformed XML '
                                  'must represent existing models and fields. Otherwise import '
                                  'will break with an exception')

    def handle(self, *args, **options):
        response = urllib2.urlopen(options['url'])
        encoding = response.headers.getparam('charset')
        content_type = response.info().type
        if 'xml' in content_type:
            source_etree = etree.parse(response)
        elif 'html' in content_type:
            source_etree = html.parse(response)
        xslt_etree = etree.parse(options['xslt_file'])
        transform = etree.XSLT(xslt_etree)
        transformed_etree = transform(source_etree)
        output = etree.tostring(transformed_etree, pretty_print=True, encoding=encoding)
        print '<?xml version="1.0" encoding="' + encoding + '"?>\n' + output
        if options['validate'] or options['save']:
            rng_file_etree = etree.parse(options['rng_file'])
            relaxng = etree.RelaxNG(rng_file_etree)
            try:
                relaxng.assertValid(transformed_etree)
                print 'Document is valid'
                if options['save']:
                    saved_objects_count = 0
                    for model_element in transformed_etree.xpath('//model'):
                        application_name, model_name = model_element.attrib['model'].split('.')
                        models_import_str = application_name + '.models'
                        models = importlib.import_module(models_import_str)
                        model = getattr(models, model_name)
                        for item_element in model_element.xpath('.//item'):
                            obj = model()
                            for field_element in item_element.xpath('.//field'):
                                setattr(obj, field_element.attrib['name'], field_element.text)
                            for fk_element in item_element.xpath('.//fk'):
                                fk_item_element_selector = '//model[@model="{}"]//item[@key="{}"]'.format(
                                    fk_element.attrib['model'], 
                                    fk_element.attrib['key']
                                )
                                _application_name, _model_name = fk_element.attrib['model'].split('.')
                                _models_import_str = _application_name + '.models'
                                _models = importlib.import_module(_models_import_str)
                                _model = getattr(_models, _model_name)
                                fk_obj = _model()
                                fk_item_element = transformed_etree.xpath(fk_item_element_selector)[0]
                                for field_element in fk_item_element.xpath('.//field'):
                                    setattr(fk_obj, field_element.attrib['name'], field_element.text)
                                fk_obj.save()
                                for field in model._meta.get_fields():
                                    if field.related_model == _model:
                                        setattr(obj, field.name, fk_obj)
                            obj.save()
                            saved_objects_count += 1
                    print 'Saved objects: ' + str(saved_objects_count)
            except etree.DocumentInvalid as ex:
                print 'Document is not valid: ' + str(ex)
