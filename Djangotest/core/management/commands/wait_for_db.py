from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time

class Command(BaseCommand):
    help = "Block until the database is available"

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.cursor()  # Try to get a cursor
            except OperationalError:
                self.stdout.write("Database unavailable, sleeping 1s...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database available!"))
