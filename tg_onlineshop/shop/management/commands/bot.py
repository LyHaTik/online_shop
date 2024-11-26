from ...main import run_updater
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Telegram bot "Privolzhsk_online_store_Bot"'
    
    def handle(self, *args, **options):
        run_updater()