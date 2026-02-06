"""
Load 8 fictional transactions in varying statuses (active, under_contract, closed)
and representation (buyer, seller, dual). Uses existing properties and clients.
Adds sample parties, milestones, and notes.
"""
from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from crm.models import (
    Client,
    Property,
    Transaction,
    TransactionParty,
    TransactionMilestone,
    TransactionNote,
)


def main(apps=None):
    PropertyModel = Property if apps is None else apps.get_model("crm", "Property")
    ClientModel = Client if apps is None else apps.get_model("crm", "Client")
    TransactionModel = Transaction if apps is None else apps.get_model("crm", "Transaction")
    TransactionPartyModel = TransactionParty if apps is None else apps.get_model("crm", "TransactionParty")
    TransactionMilestoneModel = TransactionMilestone if apps is None else apps.get_model("crm", "TransactionMilestone")
    TransactionNoteModel = TransactionNote if apps is None else apps.get_model("crm", "TransactionNote")

    properties = list(PropertyModel.objects.all()[:8])
    clients = list(ClientModel.objects.all()[:10])
    if len(properties) < 8:
        raise ValueError("Need at least 8 properties. Run load_sample_properties first.")
    if len(clients) < 4:
        raise ValueError("Need at least 4 clients. Run load_sample_clients first.")

    today = date.today()
    created = []

    def add_listing_milestone(t, order=1):
        if t.listing_date:
            TransactionMilestoneModel.objects.create(
                transaction=t, kind="listing", date=t.listing_date, status="completed", order=order,
            )

    # 1. Active – seller
    t1 = TransactionModel.objects.create(
        property=properties[0],
        status="active",
        representation="seller",
        commission_percentage=Decimal("5.50"),
        file_number="TX-2024-001",
        lockbox_code="4421",
        showing_instructions="Appointment required. 24 hours notice.",
        listing_date=today - timedelta(days=14),
    )
    if clients:
        TransactionPartyModel.objects.create(transaction=t1, client=clients[0], role="primary_seller")
    TransactionPartyModel.objects.create(transaction=t1, client=None, role="home_inspector", display_name="Vallejo Home Inspections", phone="707-555-3000")
    add_listing_milestone(t1)
    TransactionMilestoneModel.objects.create(transaction=t1, kind="inspection", date=today + timedelta(days=21), status="pending", is_critical=True, order=2)
    TransactionNoteModel.objects.create(transaction=t1, body="Listing went live. Open house next Saturday 1–4 pm.")
    created.append(t1)

    # 2. Under contract – buyer
    t2 = TransactionModel.objects.create(
        property=properties[1],
        status="under_contract",
        representation="buyer",
        commission_percentage=Decimal("3.00"),
        file_number="TX-2024-002",
        listing_date=today - timedelta(days=45),
    )
    if len(clients) >= 2:
        TransactionPartyModel.objects.create(transaction=t2, client=clients[1], role="primary_buyer")
    if len(clients) >= 3:
        TransactionPartyModel.objects.create(transaction=t2, client=clients[2], role="primary_seller")
    add_listing_milestone(t2)
    TransactionMilestoneModel.objects.create(transaction=t2, kind="contract_agreement", date=today - timedelta(days=5), status="completed", order=2)
    TransactionMilestoneModel.objects.create(transaction=t2, kind="inspection", date=today + timedelta(days=7), status="pending", is_critical=True, order=3)
    TransactionNoteModel.objects.create(transaction=t2, body="Offer accepted. Earnest money received. Inspection due next week.")
    created.append(t2)

    # 3. Closed – dual
    t3 = TransactionModel.objects.create(
        property=properties[2],
        status="closed",
        representation="dual",
        commission_percentage=Decimal("6.00"),
        final_sales_price=Decimal("689000.00"),
        file_number="TX-2024-003",
        listing_date=today - timedelta(days=90),
    )
    if len(clients) >= 3:
        TransactionPartyModel.objects.create(transaction=t3, client=clients[2], role="primary_buyer")
    if len(clients) >= 4:
        TransactionPartyModel.objects.create(transaction=t3, client=clients[3], role="primary_seller")
    add_listing_milestone(t3)
    TransactionMilestoneModel.objects.create(transaction=t3, kind="closing", date=today - timedelta(days=12), status="completed", order=2)
    TransactionNoteModel.objects.create(transaction=t3, body="Closed. Keys delivered. File archived.")
    created.append(t3)

    # 4. Active – buyer (no listing date; buyer side)
    t4 = TransactionModel.objects.create(
        property=properties[3],
        status="active",
        representation="buyer",
        commission_percentage=Decimal("3.00"),
        file_number="TX-2024-004",
        listing_date=today - timedelta(days=7),
    )
    if len(clients) >= 4:
        TransactionPartyModel.objects.create(transaction=t4, client=clients[3], role="primary_buyer")
    TransactionPartyModel.objects.create(transaction=t4, client=None, role="listing_agent", display_name="Other Agent", email="listing@example.com")
    add_listing_milestone(t4)
    TransactionNoteModel.objects.create(transaction=t4, body="Buyer interested. Scheduling second showing.")
    created.append(t4)

    # 5. Under contract – seller
    t5 = TransactionModel.objects.create(
        property=properties[4],
        status="under_contract",
        representation="seller",
        commission_percentage=Decimal("5.00"),
        file_number="TX-2024-005",
        listing_date=today - timedelta(days=30),
    )
    if len(clients) >= 5:
        TransactionPartyModel.objects.create(transaction=t5, client=clients[4], role="primary_seller")
    if len(clients) >= 6:
        TransactionPartyModel.objects.create(transaction=t5, client=clients[5], role="primary_buyer")
    add_listing_milestone(t5)
    TransactionMilestoneModel.objects.create(transaction=t5, kind="contract_agreement", date=today - timedelta(days=3), status="completed", order=2)
    TransactionMilestoneModel.objects.create(transaction=t5, kind="closing", date=today + timedelta(days=25), status="pending", is_critical=True, order=3)
    TransactionNoteModel.objects.create(transaction=t5, body="Backup offer received. Primary in loan contingency.")
    created.append(t5)

    # 6. Under contract – dual
    t6 = TransactionModel.objects.create(
        property=properties[5],
        status="under_contract",
        representation="dual",
        commission_percentage=Decimal("5.50"),
        file_number="TX-2024-006",
        listing_date=today - timedelta(days=20),
    )
    if len(clients) >= 6:
        TransactionPartyModel.objects.create(transaction=t6, client=clients[5], role="primary_buyer")
    if len(clients) >= 7:
        TransactionPartyModel.objects.create(transaction=t6, client=clients[6], role="primary_seller")
    add_listing_milestone(t6)
    TransactionMilestoneModel.objects.create(transaction=t6, kind="contract_agreement", date=today - timedelta(days=2), status="completed", order=2)
    TransactionNoteModel.objects.create(transaction=t6, body="Dual rep. Both parties disclosed. Inspection passed.")
    created.append(t6)

    # 7. Closed – buyer
    t7 = TransactionModel.objects.create(
        property=properties[6],
        status="closed",
        representation="buyer",
        commission_percentage=Decimal("3.00"),
        final_sales_price=Decimal("549000.00"),
        file_number="TX-2024-007",
        listing_date=today - timedelta(days=60),
    )
    if len(clients) >= 7:
        TransactionPartyModel.objects.create(transaction=t7, client=clients[6], role="primary_buyer")
    if len(clients) >= 8:
        TransactionPartyModel.objects.create(transaction=t7, client=clients[7], role="primary_seller")
    add_listing_milestone(t7)
    TransactionMilestoneModel.objects.create(transaction=t7, kind="closing", date=today - timedelta(days=18), status="completed", order=2)
    TransactionNoteModel.objects.create(transaction=t7, body="Buyer rep deal closed. Smooth escrow.")
    created.append(t7)

    # 8. Closed – seller
    t8 = TransactionModel.objects.create(
        property=properties[7],
        status="closed",
        representation="seller",
        commission_percentage=Decimal("5.00"),
        final_sales_price=Decimal("895000.00"),
        file_number="TX-2024-008",
        listing_date=today - timedelta(days=75),
    )
    if len(clients) >= 8:
        TransactionPartyModel.objects.create(transaction=t8, client=clients[7], role="primary_seller")
    if len(clients) >= 9:
        TransactionPartyModel.objects.create(transaction=t8, client=clients[8], role="primary_buyer")
    add_listing_milestone(t8)
    TransactionMilestoneModel.objects.create(transaction=t8, kind="closing", date=today - timedelta(days=8), status="completed", order=2)
    TransactionNoteModel.objects.create(transaction=t8, body="Seller rep. Four-plex sold to investor.")
    created.append(t8)

    return created


class Command(BaseCommand):
    help = "Load 8 fictional transactions (active, under_contract, closed; buyer/seller/dual) using existing properties and clients."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing sample transactions (file_number starting with TX-2024-) before loading.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            deleted, _ = Transaction.objects.filter(file_number__startswith="TX-2024-").delete()
            if deleted:
                self.stdout.write(self.style.WARNING(f"Removed {deleted} existing sample transaction(s)."))
        try:
            transactions = main()
            statuses = ", ".join(t.get_status_display() for t in transactions)
            self.stdout.write(self.style.SUCCESS(f"Created {len(transactions)} transactions: {statuses}."))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(str(e)))
