from django.core.management.base import BaseCommand
import process_xslt

class Command(BaseCommand):
    help = 'Converts JSON file to XML and prints the output'

    def add_arguments(self, parser):
        parser.add_argument('url', help='URL to fetch source JSON')

    def handle(self, *args, **options):
        etree, encoding = process_xslt.load_source_by_url(options['url'])
        process_xslt.print_xml(etree, encoding)