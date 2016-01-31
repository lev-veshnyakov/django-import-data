from django.core.management.base import BaseCommand
from lxml import etree, html
import urllib2
from os import path

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
        if options['validate']:
            rng_file_etree = etree.parse(options['rng_file'])
            relaxng = etree.RelaxNG(rng_file_etree)
            try:
                relaxng.assertValid(transformed_etree)
                print 'Document is valid'
            except etree.DocumentInvalid as ex:
                print 'Document is not valid: ' + str(ex)
