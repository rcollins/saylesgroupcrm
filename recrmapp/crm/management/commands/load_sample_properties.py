"""
Load 10 fictional properties in Solano County, California.
Varying pipeline status (available, under_contract, sold, off_market) and property types.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from crm.models import Client, Property

User = get_user_model()


SAMPLE_PROPERTIES = [
    {
        "title": "Vallejo Craftsman with Yard",
        "property_type": "single_family",
        "status": "available",
        "address": "847 Ohio St",
        "city": "Vallejo",
        "state": "CA",
        "zip_code": "94590",
        "price": Decimal("549000.00"),
        "bedrooms": 3,
        "bathrooms": Decimal("2.0"),
        "square_feet": 1420,
        "lot_size": Decimal("5200.00"),
        "year_built": 1948,
        "mls_number": "324-001",
        "mls_service": "bareis",
        "mls_url": "https://example.com/listings/324-001",
        "description": "Charming craftsman on quiet street. Updated kitchen, original hardwood. Large backyard.",
        "features": "Hardwood floors, updated kitchen, detached garage, large lot",
        "featured": True,
    },
    {
        "title": "Fairfield Townhouse Near I-80",
        "property_type": "townhouse",
        "status": "under_contract",
        "address": "2100 Gateway Blvd",
        "city": "Fairfield",
        "state": "CA",
        "zip_code": "94533",
        "price": Decimal("485000.00"),
        "bedrooms": 2,
        "bathrooms": Decimal("2.5"),
        "square_feet": 1180,
        "lot_size": None,
        "year_built": 2006,
        "mls_number": "324-002",
        "mls_service": "matrix",
        "mls_url": "",
        "description": "End-unit townhouse, low HOA. Easy freeway access.",
        "features": "End unit, 2-car garage, patio",
        "featured": False,
    },
    {
        "title": "Vacaville Ranch-Style 4BR",
        "property_type": "single_family",
        "status": "sold",
        "address": "1522 Alamo Dr",
        "city": "Vacaville",
        "state": "CA",
        "zip_code": "95687",
        "price": Decimal("689000.00"),
        "bedrooms": 4,
        "bathrooms": Decimal("3.0"),
        "square_feet": 2100,
        "lot_size": Decimal("7500.00"),
        "year_built": 1992,
        "mls_number": "324-003",
        "mls_service": "bareis",
        "mls_url": "",
        "description": "Spacious ranch on quiet cul-de-sac. Sold to Okonkwo family.",
        "features": "Primary suite, pool, RV parking",
        "featured": False,
    },
    {
        "title": "Benicia Waterfront Condo",
        "property_type": "condo",
        "status": "available",
        "address": "450 First St",
        "city": "Benicia",
        "state": "CA",
        "zip_code": "94510",
        "price": Decimal("625000.00"),
        "bedrooms": 2,
        "bathrooms": Decimal("2.0"),
        "square_feet": 1350,
        "lot_size": None,
        "year_built": 2004,
        "mls_number": "324-004",
        "mls_service": "paragon",
        "mls_url": "",
        "description": "Water views from living room. Walk to downtown Benicia.",
        "features": "Water view, balcony, gated",
        "featured": True,
    },
    {
        "title": "Dixon Fixer on Large Lot",
        "property_type": "single_family",
        "status": "off_market",
        "address": "355 N First St",
        "city": "Dixon",
        "state": "CA",
        "zip_code": "95620",
        "price": Decimal("425000.00"),
        "bedrooms": 3,
        "bathrooms": Decimal("2.0"),
        "square_feet": 1280,
        "lot_size": Decimal("10000.00"),
        "year_built": 1965,
        "mls_number": "",
        "mls_service": "",
        "mls_url": "",
        "description": "Pulled from market. Seller may relist in 6 months.",
        "features": "Large lot, workshop, needs cosmetic updates",
        "featured": False,
    },
    {
        "title": "Suisun City Duplex",
        "property_type": "duplex",
        "status": "available",
        "address": "701 Main St",
        "city": "Suisun City",
        "state": "CA",
        "zip_code": "94585",
        "price": Decimal("575000.00"),
        "bedrooms": 4,
        "bathrooms": Decimal("4.0"),
        "square_feet": 2400,
        "lot_size": Decimal("6000.00"),
        "year_built": 1988,
        "mls_number": "324-006",
        "mls_service": "matrix",
        "mls_url": "",
        "description": "Owner-occupy one side, rent the other. Both units updated.",
        "features": "2 units, separate meters, fenced yard",
        "featured": False,
    },
    {
        "title": "Vallejo 3BR Condo",
        "property_type": "condo",
        "status": "under_contract",
        "address": "1000 Redwood St",
        "city": "Vallejo",
        "state": "CA",
        "zip_code": "94591",
        "price": Decimal("399000.00"),
        "bedrooms": 3,
        "bathrooms": Decimal("2.0"),
        "square_feet": 1150,
        "lot_size": None,
        "year_built": 2002,
        "mls_number": "324-007",
        "mls_service": "redfin",
        "mls_url": "",
        "description": "Great first-time buyer or investor. Low HOA.",
        "features": "Assigned parking, laundry in unit",
        "featured": False,
    },
    {
        "title": "Vacaville Buildable Land",
        "property_type": "land",
        "status": "available",
        "address": "0 Nut Tree Rd",
        "city": "Vacaville",
        "state": "CA",
        "zip_code": "95687",
        "price": Decimal("185000.00"),
        "bedrooms": None,
        "bathrooms": None,
        "square_feet": None,
        "lot_size": Decimal("43560.00"),
        "year_built": None,
        "mls_number": "324-008",
        "mls_service": "bareis",
        "mls_url": "",
        "description": "One-acre parcel. Utilities at street. Build your dream home.",
        "features": "Level, utilities available",
        "featured": False,
    },
    {
        "title": "Fairfield 4-Plex Investment",
        "property_type": "fourplex",
        "status": "sold",
        "address": "1821 Texas St",
        "city": "Fairfield",
        "state": "CA",
        "zip_code": "94533",
        "price": Decimal("895000.00"),
        "bedrooms": 8,
        "bathrooms": Decimal("4.0"),
        "square_feet": 3200,
        "lot_size": Decimal("8000.00"),
        "year_built": 1972,
        "mls_number": "324-009",
        "mls_service": "matrix",
        "mls_url": "",
        "description": "Four-unit building. All units leased. Sold to investor.",
        "features": "4 units, laundry, off-street parking",
        "featured": False,
    },
    {
        "title": "Rio Vista River View",
        "property_type": "single_family",
        "status": "available",
        "address": "50 Main St",
        "city": "Rio Vista",
        "state": "CA",
        "zip_code": "94571",
        "price": Decimal("529000.00"),
        "bedrooms": 3,
        "bathrooms": Decimal("2.0"),
        "square_feet": 1580,
        "lot_size": Decimal("6000.00"),
        "year_built": 1978,
        "mls_number": "324-010",
        "mls_service": "paragon",
        "mls_url": "",
        "description": "Delta access. Boat dock possible. Quiet community.",
        "features": "River area, large lot, shed",
        "featured": True,
    },
    {"title": "American Canyon 3BR Condo", "property_type": "condo", "status": "available", "address": "100 Watson Ranch Rd", "city": "American Canyon", "state": "CA", "zip_code": "94503", "price": Decimal("475000.00"), "bedrooms": 3, "bathrooms": Decimal("2.0"), "square_feet": 1220, "lot_size": None, "year_built": 2010, "mls_number": "324-011", "mls_service": "matrix", "mls_url": "", "description": "Family-friendly complex. Pool and playground.", "features": "2-car garage, patio", "featured": False},
    {"title": "Fairfield Under-Contract Duplex", "property_type": "duplex", "status": "under_contract", "address": "2500 N Texas St", "city": "Fairfield", "state": "CA", "zip_code": "94533", "price": Decimal("599000.00"), "bedrooms": 4, "bathrooms": Decimal("4.0"), "square_feet": 2200, "lot_size": Decimal("5000.00"), "year_built": 1985, "mls_number": "324-012", "mls_service": "bareis", "mls_url": "", "description": "Both units updated. In escrow.", "features": "2 units, separate meters", "featured": False},
    {"title": "Vallejo Sold Starter Home", "property_type": "single_family", "status": "sold", "address": "600 Arkansas St", "city": "Vallejo", "state": "CA", "zip_code": "94590", "price": Decimal("425000.00"), "bedrooms": 2, "bathrooms": Decimal("1.0"), "square_feet": 980, "lot_size": Decimal("4500.00"), "year_built": 1952, "mls_number": "324-013", "mls_service": "matrix", "mls_url": "", "description": "Sold to first-time buyer. Closed last month.", "features": "Corner lot, garage", "featured": False},
    {"title": "Vacaville Off-Market Land", "property_type": "land", "status": "off_market", "address": "0 Vaca Valley Pkwy", "city": "Vacaville", "state": "CA", "zip_code": "95687", "price": Decimal("220000.00"), "bedrooms": None, "bathrooms": None, "square_feet": None, "lot_size": Decimal("21780.00"), "year_built": None, "mls_number": "", "mls_service": "", "mls_url": "", "description": "Half-acre. Seller holding. Not actively listed.", "features": "Utilities at street", "featured": False},
    {"title": "Suisun City Townhouse", "property_type": "townhouse", "status": "available", "address": "400 Main St", "city": "Suisun City", "state": "CA", "zip_code": "94585", "price": Decimal("435000.00"), "bedrooms": 2, "bathrooms": Decimal("2.5"), "square_feet": 1100, "lot_size": None, "year_built": 2008, "mls_number": "324-015", "mls_service": "paragon", "mls_url": "", "description": "Waterfront community. Low HOA.", "features": "Balcony, 1-car garage", "featured": True},
]


def get_owner_by_last_name(user, last_name: str):
    """Return first matching Client by user and last_name or None."""
    return Client.objects.filter(user=user, last_name=last_name).first()


class Command(BaseCommand):
    help = "Load 15 fictional Solano County (CA) properties with varying status and type."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing sample properties (by MLS number prefix 324-) before loading.",
        )

    def handle(self, *args, **options):
        user = User.objects.order_by('pk').first()
        if not user:
            self.stdout.write(self.style.ERROR("No users in database. Create a user (e.g. in Django admin) first."))
            return
        if options["clear"]:
            deleted, _ = Property.objects.filter(user=user, mls_number__startswith="324-").delete()
            if deleted:
                self.stdout.write(self.style.WARNING(f"Removed {deleted} existing sample property(ies)."))

        # Link a couple of properties to sample clients for realism
        okonkwo = get_owner_by_last_name(user, "Okonkwo")  # closed client - sold property
        santos = get_owner_by_last_name(user, "Santos")    # inactive - off_market property

        # Map title -> owner for linking
        owner_by_title = {
            "Vacaville Ranch-Style 4BR": okonkwo,
            "Dixon Fixer on Large Lot": santos,
        }

        created = 0
        for data in SAMPLE_PROPERTIES:
            title = data["title"]
            owner = owner_by_title.get(title)
            defaults = {**data, "owner": owner, "user": user}
            _, was_created = Property.objects.get_or_create(
                user=user,
                title=title,
                address=data["address"],
                city=data["city"],
                defaults=defaults,
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Sample properties loaded: {created} created."))
        if created < len(SAMPLE_PROPERTIES):
            self.stdout.write(
                self.style.NOTICE(
                    f"{len(SAMPLE_PROPERTIES) - created} already existed (skipped). Use --clear to replace."
                )
            )
