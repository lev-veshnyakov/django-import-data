from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from lxml import etree

class Command(BaseCommand):
    help = 'Validates given XML file with RELAX NG schema'

    def add_arguments(self, parser):
        parser.add_argument('xml_file', help='path to XML file')
        parser.add_argument('rng_file', help='path to RELAX NG file')

    def handle(self, *args, **options):
        xml_file_etree = etree.parse(options['xml_file'])
        rng_file_etree = etree.parse(options['rng_file'])
        relaxng = etree.RelaxNG(rng_file_etree)
        try:
            relaxng.assertValid(xml_file_etree)
            self.stdout.write('Document is valid')
        except etree.DocumentInvalid as ex:
            self.stdout.write('Document is not valid: ' + str(ex))
