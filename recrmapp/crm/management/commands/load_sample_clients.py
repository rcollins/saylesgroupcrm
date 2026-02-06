"""
Load 5 fictional clients in Solano County, California.
Varying pipeline status and demographics (single vs married).
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from crm.models import Client


SAMPLE_CLIENTS = [
    {
        "first_name": "Marcus",
        "last_name": "Chen",
        "email": "marcus.chen@email.com",
        "phone": "707-555-0123",
        "spouse_first_name": "",
        "spouse_last_name": "",
        "spouse_email": "",
        "spouse_phone": "",
        "client_type": "buyer",
        "status": "potential",
        "address": "1200 Tennessee St",
        "city": "Vallejo",
        "state": "CA",
        "zip_code": "94590",
        "budget_min": Decimal("450000.00"),
        "budget_max": Decimal("550000.00"),
        "notes": "First-time buyer. Pre-approved. Looking for 3br/2ba, good schools. Prefers Vallejo or Benicia.",
    },
    {
        "first_name": "Jennifer",
        "last_name": "Torres",
        "email": "j.torres@email.com",
        "phone": "707-555-0145",
        "spouse_first_name": "David",
        "spouse_last_name": "Torres",
        "spouse_email": "david.t@email.com",
        "spouse_phone": "707-555-0146",
        "client_type": "seller",
        "status": "active",
        "address": "2847 Harvest Way",
        "city": "Fairfield",
        "state": "CA",
        "zip_code": "94533",
        "budget_min": None,
        "budget_max": None,
        "notes": "Upsizing. Listing current home in spring. Want to be in escrow by June.",
    },
    {
        "first_name": "Patricia",
        "last_name": "Okonkwo",
        "email": "patricia.o@email.com",
        "phone": "707-555-0189",
        "spouse_first_name": "James",
        "spouse_last_name": "Okonkwo",
        "spouse_email": "james.okonkwo@email.com",
        "spouse_phone": "707-555-0190",
        "client_type": "both",
        "status": "closed",
        "address": "1522 Alamo Dr",
        "city": "Vacaville",
        "state": "CA",
        "zip_code": "95687",
        "budget_min": Decimal("620000.00"),
        "budget_max": Decimal("720000.00"),
        "notes": "Closed on 4br in Vacaville (Alamo area). Great experience, may refer.",
    },
    {
        "first_name": "Ryan",
        "last_name": "Foster",
        "email": "ryan.foster@email.com",
        "phone": "707-555-0221",
        "spouse_first_name": "",
        "spouse_last_name": "",
        "spouse_email": "",
        "spouse_phone": "",
        "client_type": "buyer",
        "status": "lost",
        "address": "90 Military E",
        "city": "Benicia",
        "state": "CA",
        "zip_code": "94510",
        "budget_min": Decimal("580000.00"),
        "budget_max": Decimal("650000.00"),
        "notes": "Went with another agent after 2 showings. Wanted faster response time.",
    },
    {
        "first_name": "Maria",
        "last_name": "Santos",
        "email": "maria.santos@email.com",
        "phone": "707-555-0255",
        "spouse_first_name": "Carlos",
        "spouse_last_name": "Santos",
        "spouse_email": "carlos.s@email.com",
        "spouse_phone": "707-555-0256",
        "client_type": "seller",
        "status": "inactive",
        "address": "355 N First St",
        "city": "Dixon",
        "state": "CA",
        "zip_code": "95620",
        "budget_min": None,
        "budget_max": None,
        "notes": "Paused listing. Family health issue. Will re-engage in 6 months.",
    },
]


class Command(BaseCommand):
    help = "Load 5 fictional Solano County (CA) clients with varying status and demographics."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing sample clients (by matching emails) before loading.",
        )

    def handle(self, *args, **options):
        emails = [c["email"] for c in SAMPLE_CLIENTS]
        if options["clear"]:
            deleted, _ = Client.objects.filter(email__in=emails).delete()
            if deleted:
                self.stdout.write(self.style.WARNING(f"Removed {deleted} existing sample client(s)."))

        created = 0
        for data in SAMPLE_CLIENTS:
            _, was_created = Client.objects.get_or_create(
                email=data["email"],
                defaults=data,
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Sample clients loaded: {created} created."))
        if created < len(SAMPLE_CLIENTS):
            self.stdout.write(
                self.style.NOTICE(f"{len(SAMPLE_CLIENTS) - created} already existed (skipped). Use --clear to replace.")
            )
