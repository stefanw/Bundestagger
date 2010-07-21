from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.conf import settings

from protocolparser import TopExtractor, DebateExtractor

class Command(BaseCommand):
    help = 'Parses XML protocol'
    args = ''

    def handle(self, filename, *args, **options):
        print filename
        xmlfile = file(filename)
        topextractor = TopExtractor()
        debateextractor = DebateExtractor()
        xml = xmlfile.read()
        print topextractor.parse(xml)
        print "-" * 20
        print debateextractor.parse(xml)
        
