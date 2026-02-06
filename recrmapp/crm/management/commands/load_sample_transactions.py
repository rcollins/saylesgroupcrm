"""
Load 3 fictional transactions in varying statuses (active, under_contract, closed).
Uses existing properties and clients. Adds sample parties, milestones, and notes.
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
    TransactionTask,
    TransactionNote,
)


def main(apps=None):
    PropertyModel = Property if apps is None else apps.get_model("crm", "Property")
    ClientModel = Client if apps is None else apps.get_model("crm", "Client")
    TransactionModel = Transaction if apps is None else apps.get_model("crm", "Transaction")
    TransactionPartyModel = TransactionParty if apps is None else apps.get_model("crm", "TransactionParty")
    TransactionMilestoneModel = TransactionMilestone if apps is None else apps.get_model("crm", "TransactionMilestone")
    TransactionNoteModel = TransactionNote if apps is None else apps.get_model("crm", "TransactionNote")

    properties = list(PropertyModel.objects.all()[:5])
    clients = list(ClientModel.objects.all()[:5])
    if len(properties) < 3:
        raise ValueError("Need at least 3 properties. Run load_sample_properties first.")
    if len(clients) < 2:
        raise ValueError("Need at least 2 clients. Run load_sample_clients first.")

    today = date.today()

    # 1. Active listing – seller rep
    t1 = TransactionModel.objects.create(
        property=properties[0],
        status="active",
        representation="seller",
        commission_percentage=Decimal("5.50"),
        file_number="TX-2024-001",
        lockbox_code="4421",
        showing_instructions="Appointment required. Give listing agent 24 hours notice. No lockbox – key at office.",
        listing_date=today - timedelta(days=14),
    )
    if clients:
        TransactionPartyModel.objects.create(
            transaction=t1,
            client=clients[0],
            role="primary_seller",
        )
    TransactionPartyModel.objects.create(
        transaction=t1,
        client=None,
        role="home_inspector",
        display_name="Vallejo Home Inspections",
        phone="707-555-3000",
    )
    TransactionMilestoneModel.objects.create(
        transaction=t1,
        kind="listing",
        date=t1.listing_date,
        status="completed",
        order=1,
    )
    TransactionMilestoneModel.objects.create(
        transaction=t1,
        kind="inspection",
        date=today + timedelta(days=21),
        status="pending",
        is_critical=True,
        order=2,
    )
    TransactionNoteModel.objects.create(
        transaction=t1,
        body="Listing went live. Open house scheduled for next Saturday 1–4 pm.",
    )

    # 2. Under contract – buyer rep
    t2 = TransactionModel.objects.create(
        property=properties[1] if len(properties) > 1 else properties[0],
        status="under_contract",
        representation="buyer",
        commission_percentage=Decimal("3.00"),
        file_number="TX-2024-002",
        lockbox_code="",
        showing_instructions="",
        listing_date=today - timedelta(days=45),
    )
    if len(clients) >= 2:
        TransactionPartyModel.objects.create(
            transaction=t2,
            client=clients[1],
            role="primary_buyer",
        )
    if len(clients) >= 3:
        TransactionPartyModel.objects.create(
            transaction=t2,
            client=clients[2],
            role="primary_seller",
        )
    TransactionMilestoneModel.objects.create(
        transaction=t2,
        kind="listing",
        date=t2.listing_date,
        status="completed",
        order=1,
    )
    TransactionMilestoneModel.objects.create(
        transaction=t2,
        kind="contract_agreement",
        date=today - timedelta(days=5),
        status="completed",
        order=2,
    )
    TransactionMilestoneModel.objects.create(
        transaction=t2,
        kind="inspection",
        date=today + timedelta(days=7),
        status="pending",
        is_critical=True,
        order=3,
    )
    TransactionNoteModel.objects.create(
        transaction=t2,
        body="Offer accepted. Earnest money received. Inspection contingency due next week.",
    )

    # 3. Closed – dual agent
    t3 = TransactionModel.objects.create(
        property=properties[2] if len(properties) > 2 else properties[0],
        status="closed",
        representation="dual",
        commission_percentage=Decimal("6.00"),
        file_number="TX-2024-003",
        lockbox_code="",
        showing_instructions="",
        listing_date=today - timedelta(days=90),
    )
    if len(clients) >= 3:
        TransactionPartyModel.objects.create(
            transaction=t3,
            client=clients[2],
            role="primary_buyer",
        )
    if len(clients) >= 4:
        TransactionPartyModel.objects.create(
            transaction=t3,
            client=clients[3],
            role="primary_seller",
        )
    TransactionMilestoneModel.objects.create(
        transaction=t3,
        kind="listing",
        date=t3.listing_date,
        status="completed",
        order=1,
    )
    TransactionMilestoneModel.objects.create(
        transaction=t3,
        kind="closing",
        date=today - timedelta(days=12),
        status="completed",
        order=2,
    )
    TransactionNoteModel.objects.create(
        transaction=t3,
        body="Closed. Keys delivered. File archived.",
    )

    return [t1, t2, t3]


class Command(BaseCommand):
    help = "Load 3 fictional transactions (active, under_contract, closed) using existing properties and clients."

    def handle(self, *args, **options):
        try:
            transactions = main()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created 3 transactions: {transactions[0].get_status_display()}, "
                    f"{transactions[1].get_status_display()}, {transactions[2].get_status_display()}."
                )
            )
        except ValueError as e:
            self.stdout.write(self.style.ERROR(str(e)))
