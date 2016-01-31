from django.core.management.base import BaseCommand
from lxml import etree, html
import urllib2

class Command(BaseCommand):
    help = 'Processes XSLT transformation on a fetched by URL resource and outputs the result'

    def add_arguments(self, parser):
        parser.add_argument('url', help='URL to fetch source XML')
        parser.add_argument('xslt_file', help='path to XSLT transformation file')

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
        output = etree.tostring(transform(source_etree), pretty_print=True, encoding=encoding)
        print '<?xml version="1.0" encoding="' + encoding + '"?>\n' + output