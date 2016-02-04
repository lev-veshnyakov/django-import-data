from django.core.management.base import BaseCommand
from lxml import etree, html
import urllib2
from os import path
import importlib
from django.db.models.fields import related

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
        source_etree, encoding = self.load_source_by_url(options['url'])
        transformed_etree = self.xslt_transform(source_etree, options['xslt_file'])
        output = etree.tostring(transformed_etree, pretty_print=True, encoding=encoding)
        print '<?xml version="1.0" encoding="' + (encoding or '') + '"?>\n' + output
        if options['validate'] or options['save']:
            try:
                self.assert_valid_rng_schema(transformed_etree, options['rng_file'])
                print 'Document is valid'
                if options['save']:
                    saved_objects_count = 0
                    for model_element in self.get_model_elements(transformed_etree):
                        model = self.get_model(model_element.attrib['model'])
                        for item_element in self.get_item_elements(model_element):
                            obj = model()
                            for field_element in self.get_field_elements(item_element):
                                if field_element.attrib.get('unique') and not self.is_unique(model, field_element):
                                    break
                                setattr(obj, field_element.attrib['name'], field_element.text.strip())
                            else:
                                for fk_element in self.get_fk_elements(item_element):
                                    related_obj = self.save_related_item(fk_element)
                                    self.set_related(obj, related_obj)
                                obj.save()
                                for m2m_element in self.get_m2m_elements(item_element):
                                    related_obj = self.save_related_item(m2m_element)
                                    self.set_related(obj, related_obj)
                                saved_objects_count += 1
                    print 'Saved objects: ' + str(saved_objects_count)
            except etree.DocumentInvalid as ex:
                print 'Document is not valid: ' + str(ex)
    
    def get_model(self, model_path_string):
        '''
        Returns model object by string, containing its path
        
        Path is in format: application_name.ModelName
        The same format like by manage.py dumpdata
        '''
        application_name, model_name = model_path_string.split('.')
        models_import_str = application_name + '.models'
        models = importlib.import_module(models_import_str)
        model = getattr(models, model_name)
        return model
        
    def get_related_item_element(self, fk_element):
        '''
        Returns related element by its foreign key
        
        It takes <fk /> element and finds related <item />
        element by attributes
        '''
        fk_item_element_selector = '//model[@model="{}"]//item[@key="{}"]'.format(
            fk_element.attrib['model'], 
            fk_element.attrib['key']
        )
        fk_item_element = fk_element.xpath(fk_item_element_selector)[0]
        return fk_item_element
        
    def get_model_elements(self, transformed_etree):
        return transformed_etree.xpath('//model')
        
    def get_item_elements(self, model_element):
        return model_element.xpath('.//item')
        
    def get_field_elements(self, item_element):
        return item_element.xpath('.//field')
        
    def get_fk_elements(self, item_element):
        return item_element.xpath('.//fk')
    
    def get_m2m_elements(self, item_element):
        return item_element.xpath('.//m2mk')
        
    def save_related_item(self, fk_element):
        '''
        Finds and saves related <item /> element by given <fk /> element
        '''
        fk_model = self.get_model(fk_element.attrib['model'])
        obj = fk_model()
        related_item_element = self.get_related_item_element(fk_element)
        for field_element in self.get_field_elements(related_item_element):
            setattr(obj, field_element.attrib['name'], field_element.text.strip())
        obj.save()
        return obj
        
    def set_related(self, obj, related_obj):
        '''
        Finds and saves related model object
        
        It finds appropriate foreign key by related
        objects type. It means that you can't use 
        two different foreign key fields to the same model
        '''
        fk_field = [
            field 
            for field 
            in type(obj)._meta.get_fields()
            if field.related_model == type(related_obj)
        ][0]
        if type(fk_field) is related.ForeignKey:
            setattr(obj, fk_field.name, related_obj)
        else:
            getattr(obj, fk_field.name).add(related_obj)
        
    def load_source_by_url(self, url):
        '''
        Gets soure etree and content encoding by given url
        
        file:// schema is also supported
        '''
        headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; rv:44.0) Gecko/20100101 Firefox/44.0' }
        req = urllib2.Request('http://stackoverflow.com', None, headers)
        response = urllib2.urlopen(req)
        encoding = response.headers.getparam('charset')
        content_type = response.info().type
        if 'xml' in content_type:
            source_etree = etree.parse(response)
        elif 'html' in content_type:
            source_etree = html.parse(response)
        else:
            raise Exception('Unsupported content type for source URL ' + url)
        return source_etree, encoding
        
    def xslt_transform(self, source_etree, xslt_file_path):
        '''
        Transforms source XML by given XSLT file
        '''
        xslt_etree = etree.parse(xslt_file_path)
        transform = etree.XSLT(xslt_etree)
        transformed_etree = transform(source_etree)
        return transformed_etree
        
    def assert_valid_rng_schema(self, transformed_etree, rng_file_path):
        '''
        Validates source XML against given Relax NG schema
        
        If validation falls raises an etree.DocumentInvalid exception
        '''
        rng_file_etree = etree.parse(rng_file_path)
        relaxng = etree.RelaxNG(rng_file_etree)
        relaxng.assertValid(transformed_etree)
    
    def is_unique(self, model, field_element):
        '''
        Checks uniqueness of given field_element value after it will
        be saved in the database
        
        This straightforward check lets to avoid duplicates in the database
        without need to set unique constraints there
        '''
        params = {field_element.attrib['name']: field_element.text}
        return not model.objects.filter(**params).count()
