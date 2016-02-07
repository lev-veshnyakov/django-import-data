from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from . import process_xslt

class Command(BaseCommand):
    help = 'Converts JSON file to XML and prints the output'

    def add_arguments(self, parser):
        parser.add_argument('url', help='URL to fetch source JSON')
        parser.add_argument('--encoding', help='Encoding of a source file. Content-type HTTP header is used to '
                                               'detect it. For local files it defaults to UTF-8', default='UTF-8')

    def handle(self, *args, **options):
        etree, encoding = process_xslt.load_source_by_url(options['url'])
        process_xslt.print_xml(etree, encoding or options['encoding'], self)