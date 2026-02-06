"""
Load 10 fictional contacts: vendors, lenders, agents, title, inspector, attorney, etc.
"""
from django.core.management.base import BaseCommand

from crm.models import Contact


SAMPLE_CONTACTS = [
    {
        "first_name": "Sarah",
        "last_name": "Mitchell",
        "email": "sarah.mitchell@firstcal.com",
        "phone": "707-555-1001",
        "contact_type": "lender",
        "company": "First Cal Mortgage",
        "address": "1600 Gateway Blvd",
        "city": "Fairfield",
        "state": "CA",
        "zip_code": "94533",
        "notes": "Preferred lender. Great rates, quick turnaround. Use for VA and conventional.",
    },
    {
        "first_name": "Michael",
        "last_name": "Reyes",
        "email": "mreyes@vallejorealty.com",
        "phone": "707-555-1002",
        "contact_type": "agent",
        "company": "Vallejo Realty Group",
        "address": "500 Marin St",
        "city": "Vallejo",
        "state": "CA",
        "zip_code": "94590",
        "notes": "Buyer's agent. Easy to coordinate showings. Often brings clients to Solano.",
    },
    {
        "first_name": "Pacific",
        "last_name": "Title",
        "email": "escrow@pacifictitle-solano.com",
        "phone": "707-555-1003",
        "contact_type": "title_company",
        "company": "Pacific Title of Solano County",
        "address": "1200 Travis Blvd",
        "city": "Fairfield",
        "state": "CA",
        "zip_code": "94533",
        "notes": "Reliable title and escrow. Ask for Lisa in escrow.",
    },
    {
        "first_name": "David",
        "last_name": "Nguyen",
        "email": "david@nguyeninspections.com",
        "phone": "707-555-1004",
        "contact_type": "inspector",
        "company": "Nguyen Home Inspections",
        "address": "",
        "city": "Benicia",
        "state": "CA",
        "zip_code": "94510",
        "notes": "Thorough inspections, same-week scheduling. Good with first-time buyers.",
    },
    {
        "first_name": "Jennifer",
        "last_name": "Walsh",
        "email": "jwalsh@walshrealestatelaw.com",
        "phone": "707-555-1005",
        "contact_type": "attorney",
        "company": "Walsh Real Estate Law",
        "address": "300 Capitol Mall",
        "city": "Sacramento",
        "state": "CA",
        "zip_code": "95814",
        "notes": "Real estate attorney. Use for complex or commercial deals.",
    },
    {
        "first_name": "Carlos",
        "last_name": "Mendoza",
        "email": "carlos@mendozalandscaping.com",
        "phone": "707-555-1006",
        "contact_type": "vendor",
        "company": "Mendoza Landscaping & Staging",
        "address": "890 Industrial Way",
        "city": "Vacaville",
        "state": "CA",
        "zip_code": "95687",
        "notes": "Staging and curb appeal. Fair pricing, fast availability.",
    },
    {
        "first_name": "Amanda",
        "last_name": "Foster",
        "email": "afoster@solanocredit.org",
        "phone": "707-555-1007",
        "contact_type": "lender",
        "company": "Solano Credit Union",
        "address": "2200 N Texas St",
        "city": "Fairfield",
        "state": "CA",
        "zip_code": "94533",
        "notes": "Local credit union. Good for first-time and down-payment assistance programs.",
    },
    {
        "first_name": "James",
        "last_name": "Park",
        "email": "james.park@dixonproperties.com",
        "phone": "707-555-1008",
        "contact_type": "agent",
        "company": "Dixon Properties",
        "address": "200 N First St",
        "city": "Dixon",
        "state": "CA",
        "zip_code": "95620",
        "notes": "Listing agent. Often has inventory in Dixon and Davis area.",
    },
    {
        "first_name": "Valley",
        "last_name": "Home Services",
        "email": "office@valleyhomeservices.com",
        "phone": "707-555-1009",
        "contact_type": "vendor",
        "company": "Valley Home Services",
        "address": "1500 Enterprise Dr",
        "city": "Fairfield",
        "state": "CA",
        "zip_code": "94533",
        "notes": "HVAC, plumbing, electrical. Preferred vendor for repair negotiations.",
    },
    {
        "first_name": "Rachel",
        "last_name": "Torres",
        "email": "rtorres@beniciaescrow.com",
        "phone": "707-555-1010",
        "contact_type": "title_company",
        "company": "Benicia Escrow & Title",
        "address": "720 First St",
        "city": "Benicia",
        "state": "CA",
        "zip_code": "94510",
        "notes": "Small local office. Very responsive. Good for Benicia and Vallejo closings.",
    },
    {"first_name": "Brian", "last_name": "O'Connor", "email": "brian@solanoappraisals.com", "phone": "707-555-1011", "contact_type": "vendor", "company": "Solano Appraisal Co", "address": "1400 Travis Blvd", "city": "Fairfield", "state": "CA", "zip_code": "94533", "notes": "Appraisals. Turnaround 5–7 days. Good for FHA/VA."},
    {"first_name": "Diana", "last_name": "Lopez", "email": "dlopez@northbaylending.com", "phone": "707-555-1012", "contact_type": "lender", "company": "North Bay Lending", "address": "900 Adams St", "city": "Vallejo", "state": "CA", "zip_code": "94590", "notes": "Jumbo and conventional. Competitive rates."},
    {"first_name": "Frank", "last_name": "Wei", "email": "fwei@vacavillerealty.com", "phone": "707-555-1013", "contact_type": "agent", "company": "Vacaville Realty", "address": "500 Merchant St", "city": "Vacaville", "state": "CA", "zip_code": "95687", "notes": "Listing agent. Often co-brokes on Vacaville listings."},
    {"first_name": "Gina", "last_name": "Santos", "email": "gina@centralvalleytitle.com", "phone": "707-555-1014", "contact_type": "title_company", "company": "Central Valley Title", "address": "300 Capitol Mall", "city": "Sacramento", "state": "CA", "zip_code": "95814", "notes": "Escrow and title. Good for Sacramento-area refis."},
    {"first_name": "Hector", "last_name": "Vega", "email": "hector@vegainspections.com", "phone": "707-555-1015", "contact_type": "inspector", "company": "Vega Home Inspections", "address": "", "city": "Fairfield", "state": "CA", "zip_code": "94533", "notes": "General and pest. Same-week scheduling. Detailed reports."},
    {"first_name": "Ivy", "last_name": "Chen", "email": "ichen@chenrealestatelaw.com", "phone": "707-555-1016", "contact_type": "attorney", "company": "Chen Real Estate Law", "address": "100 B St", "city": "Davis", "state": "CA", "zip_code": "95616", "notes": "Residential and 1031. Yolo and Solano."},
    {"first_name": "Jake", "last_name": "Morton", "email": "jake@mortonroofing.com", "phone": "707-555-1017", "contact_type": "vendor", "company": "Morton Roofing", "address": "600 Industrial Way", "city": "Vacaville", "state": "CA", "zip_code": "95687", "notes": "Roof repair and replacement. Licensed. Quick quotes."},
    {"first_name": "Keisha", "last_name": "Williams", "email": "kwilliams@benicialending.com", "phone": "707-555-1018", "contact_type": "lender", "company": "Benicia Home Loans", "address": "400 First St", "city": "Benicia", "state": "CA", "zip_code": "94510", "notes": "First-time buyer programs. Down payment assistance."},
    {"first_name": "Leo", "last_name": "Garcia", "email": "leo@riovistarealty.com", "phone": "707-555-1019", "contact_type": "agent", "company": "Rio Vista Realty", "address": "50 Main St", "city": "Rio Vista", "state": "CA", "zip_code": "94571", "notes": "Delta area specialist. Listings and buyers."},
    {"first_name": "Maya", "last_name": "Patel", "email": "maya@solanoinsurance.com", "phone": "707-555-1020", "contact_type": "other", "company": "Solano Insurance Group", "address": "1800 Texas St", "city": "Fairfield", "state": "CA", "zip_code": "94533", "notes": "Home and umbrella. Often needed at closing."},
]


class Command(BaseCommand):
    help = "Load 20 fictional contacts (lenders, agents, title, inspector, attorney, vendors, other) with varying types."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing sample contacts (by matching emails) before loading.",
        )

    def handle(self, *args, **options):
        emails = [c["email"] for c in SAMPLE_CONTACTS]
        if options["clear"]:
            deleted, _ = Contact.objects.filter(email__in=emails).delete()
            if deleted:
                self.stdout.write(self.style.WARNING(f"Removed {deleted} existing sample contact(s)."))

        created = 0
        for data in SAMPLE_CONTACTS:
            _, was_created = Contact.objects.get_or_create(
                email=data["email"],
                defaults=data,
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Sample contacts loaded: {created} created."))
        if created < len(SAMPLE_CONTACTS):
            self.stdout.write(
                self.style.NOTICE(f"{len(SAMPLE_CONTACTS) - created} already existed (skipped). Use --clear to replace.")
            )
