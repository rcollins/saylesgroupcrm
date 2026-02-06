"""
Load 15 fictional clients in Solano County, California.
Varying pipeline status (potential, active, closed, lost, inactive) and client type (buyer, seller, both).
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from crm.models import Client


SAMPLE_CLIENTS = [
    {"first_name": "Marcus", "last_name": "Chen", "email": "marcus.chen@email.com", "phone": "707-555-0123", "spouse_first_name": "", "spouse_last_name": "", "spouse_email": "", "spouse_phone": "", "client_type": "buyer", "status": "potential", "address": "1200 Tennessee St", "city": "Vallejo", "state": "CA", "zip_code": "94590", "budget_min": Decimal("450000.00"), "budget_max": Decimal("550000.00"), "notes": "First-time buyer. Pre-approved. Looking for 3br/2ba, good schools."},
    {"first_name": "Jennifer", "last_name": "Torres", "email": "j.torres@email.com", "phone": "707-555-0145", "spouse_first_name": "David", "spouse_last_name": "Torres", "spouse_email": "david.t@email.com", "spouse_phone": "707-555-0146", "client_type": "seller", "status": "active", "address": "2847 Harvest Way", "city": "Fairfield", "state": "CA", "zip_code": "94533", "budget_min": None, "budget_max": None, "notes": "Upsizing. Listing current home in spring. Want to be in escrow by June."},
    {"first_name": "Patricia", "last_name": "Okonkwo", "email": "patricia.o@email.com", "phone": "707-555-0189", "spouse_first_name": "James", "spouse_last_name": "Okonkwo", "spouse_email": "james.okonkwo@email.com", "spouse_phone": "707-555-0190", "client_type": "both", "status": "closed", "address": "1522 Alamo Dr", "city": "Vacaville", "state": "CA", "zip_code": "95687", "budget_min": Decimal("620000.00"), "budget_max": Decimal("720000.00"), "notes": "Closed on 4br in Vacaville. Great experience, may refer."},
    {"first_name": "Ryan", "last_name": "Foster", "email": "ryan.foster@email.com", "phone": "707-555-0221", "spouse_first_name": "", "spouse_last_name": "", "spouse_email": "", "spouse_phone": "", "client_type": "buyer", "status": "lost", "address": "90 Military E", "city": "Benicia", "state": "CA", "zip_code": "94510", "budget_min": Decimal("580000.00"), "budget_max": Decimal("650000.00"), "notes": "Went with another agent after 2 showings. Wanted faster response time."},
    {"first_name": "Maria", "last_name": "Santos", "email": "maria.santos@email.com", "phone": "707-555-0255", "spouse_first_name": "Carlos", "spouse_last_name": "Santos", "spouse_email": "carlos.s@email.com", "spouse_phone": "707-555-0256", "client_type": "seller", "status": "inactive", "address": "355 N First St", "city": "Dixon", "state": "CA", "zip_code": "95620", "budget_min": None, "budget_max": None, "notes": "Paused listing. Family health issue. Will re-engage in 6 months."},
    {"first_name": "Daniel", "last_name": "Hayes", "email": "daniel.hayes@email.com", "phone": "707-555-0301", "spouse_first_name": "", "spouse_last_name": "", "spouse_email": "", "spouse_phone": "", "client_type": "buyer", "status": "potential", "address": "2100 Pennsylvania Ave", "city": "Fairfield", "state": "CA", "zip_code": "94533", "budget_min": Decimal("400000.00"), "budget_max": Decimal("500000.00"), "notes": "Just pre-approved. Wants to see condos and townhomes."},
    {"first_name": "Lisa", "last_name": "Park", "email": "lisa.park@email.com", "phone": "707-555-0302", "spouse_first_name": "Tom", "spouse_last_name": "Park", "spouse_email": "tom.park@email.com", "spouse_phone": "707-555-0303", "client_type": "seller", "status": "active", "address": "1800 West Texas St", "city": "Fairfield", "state": "CA", "zip_code": "94533", "budget_min": None, "budget_max": None, "notes": "Listing in 30 days. Need staging and photos."},
    {"first_name": "Omar", "last_name": "Hassan", "email": "omar.hassan@email.com", "phone": "707-555-0304", "spouse_first_name": "", "spouse_last_name": "", "spouse_email": "", "spouse_phone": "", "client_type": "buyer", "status": "active", "address": "500 Couch St", "city": "Vallejo", "state": "CA", "zip_code": "94590", "budget_min": Decimal("350000.00"), "budget_max": Decimal("420000.00"), "notes": "Investor. Looking for 2–3 units, Vallejo or American Canyon."},
    {"first_name": "Nicole", "last_name": "Bennett", "email": "nicole.bennett@email.com", "phone": "707-555-0305", "spouse_first_name": "", "spouse_last_name": "", "spouse_email": "", "spouse_phone": "", "client_type": "seller", "status": "closed", "address": "3200 Alamo Dr", "city": "Vacaville", "state": "CA", "zip_code": "95687", "budget_min": None, "budget_max": None, "notes": "Sold in 12 days. Very happy. Referral source."},
    {"first_name": "Victor", "last_name": "Ramos", "email": "victor.ramos@email.com", "phone": "707-555-0306", "spouse_first_name": "Ana", "spouse_last_name": "Ramos", "spouse_email": "ana.ramos@email.com", "spouse_phone": "707-555-0307", "client_type": "both", "status": "potential", "address": "800 2nd St", "city": "Benicia", "state": "CA", "zip_code": "94510", "budget_min": Decimal("700000.00"), "budget_max": Decimal("850000.00"), "notes": "Sell current, then buy larger. Timeline 4–6 months."},
    {"first_name": "Karen", "last_name": "Wong", "email": "karen.wong@email.com", "phone": "707-555-0308", "spouse_first_name": "", "spouse_last_name": "", "spouse_email": "", "spouse_phone": "", "client_type": "buyer", "status": "lost", "address": "100 Lopes Rd", "city": "Suisun City", "state": "CA", "zip_code": "94585", "budget_min": Decimal("480000.00"), "budget_max": Decimal("550000.00"), "notes": "Chose new construction in another county."},
    {"first_name": "Thomas", "last_name": "Ellis", "email": "thomas.ellis@email.com", "phone": "707-555-0309", "spouse_first_name": "Julie", "spouse_last_name": "Ellis", "spouse_email": "julie.ellis@email.com", "spouse_phone": "707-555-0310", "client_type": "seller", "status": "inactive", "address": "450 Peabody Rd", "city": "Vacaville", "state": "CA", "zip_code": "95687", "budget_min": None, "budget_max": None, "notes": "Decided to stay put. May list in 2026."},
    {"first_name": "Sofia", "last_name": "Martinez", "email": "sofia.martinez@email.com", "phone": "707-555-0311", "spouse_first_name": "", "spouse_last_name": "", "spouse_email": "", "spouse_phone": "", "client_type": "buyer", "status": "active", "address": "600 Main St", "city": "Suisun City", "state": "CA", "zip_code": "94585", "budget_min": Decimal("520000.00"), "budget_max": Decimal("600000.00"), "notes": "Writing offer on Harbor Island property."},
    {"first_name": "Greg", "last_name": "Norris", "email": "greg.norris@email.com", "phone": "707-555-0312", "spouse_first_name": "", "spouse_last_name": "", "spouse_email": "", "spouse_phone": "", "client_type": "seller", "status": "potential", "address": "1100 E Tabor Ave", "city": "Fairfield", "state": "CA", "zip_code": "94533", "budget_min": None, "budget_max": None, "notes": "Considering listing in spring. Wants CMA first."},
    {"first_name": "Yuki", "last_name": "Tanaka", "email": "yuki.tanaka@email.com", "phone": "707-555-0313", "spouse_first_name": "Ken", "spouse_last_name": "Tanaka", "spouse_email": "ken.tanaka@email.com", "spouse_phone": "707-555-0314", "client_type": "both", "status": "closed", "address": "200 N 1st St", "city": "Dixon", "state": "CA", "zip_code": "95620", "budget_min": Decimal("550000.00"), "budget_max": Decimal("650000.00"), "notes": "Sold Dixon, bought in Davis. Dual rep, smooth close."},
]


class Command(BaseCommand):
    help = "Load 15 fictional Solano County (CA) clients with varying status and client type."

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
