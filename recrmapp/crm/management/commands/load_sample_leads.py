"""
Load 10 fictional leads from Northern California.
Varying pipeline status (new, attempted, in_progress, connected, unqualified, bad_timing) and referral source.
"""
from django.core.management.base import BaseCommand

from crm.models import Lead


SAMPLE_LEADS = [
    {"first_name": "Sandra", "last_name": "Nguyen", "email": "sandra.nguyen.lead@email.com", "phone": "415-555-1001", "referral": "facebook", "status": "new", "address": "2200 Mission St", "city": "San Francisco", "state": "CA", "zip_code": "94110", "notes": "Inquired about condo listings in Mission District."},
    {"first_name": "Michael", "last_name": "Rodriguez", "email": "m.rodriguez.lead@email.com", "phone": "510-555-1002", "referral": "open_house", "status": "attempted", "address": "4500 Broadway", "city": "Oakland", "state": "CA", "zip_code": "94611", "notes": "Attended open house. Left voicemail, no callback yet."},
    {"first_name": "Priya", "last_name": "Sharma", "email": "priya.s.lead@email.com", "phone": "408-555-1003", "referral": "office_lead", "status": "in_progress", "address": "1200 El Camino Real", "city": "Santa Clara", "state": "CA", "zip_code": "95050", "notes": "Walk-in. First-time buyer, pre-approval in progress."},
    {"first_name": "James", "last_name": "Wu", "email": "james.wu.lead@email.com", "phone": "916-555-1004", "referral": "telephone", "status": "connected", "address": "1600 J St", "city": "Sacramento", "state": "CA", "zip_code": "95814", "notes": "Referred by past client. Wants to list midtown condo in 60 days."},
    {"first_name": "Elena", "last_name": "Vasquez", "email": "elena.v.lead@email.com", "phone": "559-555-1005", "referral": "instagram", "status": "unqualified", "address": "2300 Tulare St", "city": "Fresno", "state": "CA", "zip_code": "93721", "notes": "Out-of-area; looking in LA. Not a fit for our market."},
    {"first_name": "David", "last_name": "Kim", "email": "david.kim.lead@email.com", "phone": "707-555-1006", "referral": "postcard", "status": "bad_timing", "address": "1200 First St", "city": "Napa", "state": "CA", "zip_code": "94559", "notes": "Received postcard. Wants to revisit in 12 months."},
    {"first_name": "Rachel", "last_name": "Thompson", "email": "rachel.t.lead@email.com", "phone": "707-555-1007", "referral": "open_house", "status": "new", "address": "500 4th St", "city": "Santa Rosa", "state": "CA", "zip_code": "95401", "notes": "Signed in at open house. Interested in Sonoma County."},
    {"first_name": "Carlos", "last_name": "Mendoza", "email": "carlos.m.lead@email.com", "phone": "510-555-1008", "referral": "office_lead", "status": "attempted", "address": "2800 Telegraph Ave", "city": "Berkeley", "state": "CA", "zip_code": "94705", "notes": "Called office twice. No answer on callback attempts."},
    {"first_name": "Amy", "last_name": "Liu", "email": "amy.liu.lead@email.com", "phone": "650-555-1009", "referral": "facebook", "status": "in_progress", "address": "400 University Ave", "city": "Palo Alto", "state": "CA", "zip_code": "94301", "notes": "FB ad lead. Viewing 3 properties this week."},
    {"first_name": "Marcus", "last_name": "Johnson", "email": "marcus.j.lead@email.com", "phone": "209-555-1010", "referral": "telephone", "status": "connected", "address": "3020 Pacific Ave", "city": "Stockton", "state": "CA", "zip_code": "95204", "notes": "Relocating from Bay Area. Wants 4br in Stockton area."},
]


class Command(BaseCommand):
    help = "Load 10 fictional Northern California leads with varying status and referral."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing sample leads (by matching emails) before loading.",
        )

    def handle(self, *args, **options):
        emails = [lead["email"] for lead in SAMPLE_LEADS]
        if options["clear"]:
            deleted, _ = Lead.objects.filter(email__in=emails).delete()
            if deleted:
                self.stdout.write(self.style.WARNING(f"Removed {deleted} existing sample lead(s)."))

        created = 0
        for data in SAMPLE_LEADS:
            _, was_created = Lead.objects.get_or_create(
                email=data["email"],
                defaults=data,
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Sample leads loaded: {created} created."))
        if created < len(SAMPLE_LEADS):
            self.stdout.write(
                self.style.NOTICE(
                    f"{len(SAMPLE_LEADS) - created} already existed (skipped). Use --clear to replace."
                )
            )
