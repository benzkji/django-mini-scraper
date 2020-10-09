# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from social_scraper.models import SocialSource


class Command(BaseCommand):
    help = 'let fetch'

    def add_arguments(self, parser):
        parser.add_argument('--source-id', type=int)

    def handle(self, *args, **options):
        source_id = options.get('source_id', None)
        try:
            source_id = int(source_id)
        except TypeError:
            pass
        sources = SocialSource.objects.filter(enabled=True)
        if source_id:
            sources = sources.filter(pk=source_id)
        for search in sources:
            search.fetch()
