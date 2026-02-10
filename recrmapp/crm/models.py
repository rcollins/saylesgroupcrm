import builtins
from django.conf import settings
from django.db import models


class Client(models.Model):
    """A client or contact in the real estate CRM."""

    CLIENT_TYPE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('both', 'Buyer & Seller'),
    ]

    CLIENT_STATUS_CHOICES = [
        ('potential', 'Potential Client'),
        ('active', 'Active Client'),
        ('closed', 'Closed Client'),
        ('lost', 'Lost Client'),
        ('inactive', 'Inactive Client'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    spouse_first_name = models.CharField(
        max_length=100, blank=True, help_text="Spouse's first name"
    )
    spouse_last_name = models.CharField(
        max_length=100, blank=True, help_text="Spouse's last name"
    )
    spouse_email = models.EmailField(blank=True, help_text="Spouse's email address")
    spouse_phone = models.CharField(
        max_length=20, blank=True, help_text="Spouse's phone number"
    )
    client_type = models.CharField(
        max_length=10,
        choices=CLIENT_TYPE_CHOICES,
        default='buyer',
    )
    status = models.CharField(
        max_length=20,
        choices=CLIENT_STATUS_CHOICES,
        default='potential',
        help_text="Current status of the client",
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    budget_min = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    budget_max = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def spouse_full_name(self):
        if self.spouse_first_name or self.spouse_last_name:
            return f"{self.spouse_first_name} {self.spouse_last_name}".strip()
        return ""


class Lead(models.Model):
    """A lead (prospect). No spouse info. Convertible to Client."""

    STATUS_CHOICES = [
        ('new', 'New'),
        ('attempted', 'Attempted to Contact'),
        ('in_progress', 'In Progress'),
        ('connected', 'Connected'),
        ('unqualified', 'Unqualified'),
        ('bad_timing', 'Bad Timing'),
    ]

    REFERRAL_CHOICES = [
        ('office_lead', 'Office Lead'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telephone', 'Telephone'),
        ('postcard', 'Postcard'),
        ('open_house', 'Open House'),
        ('walk_in', 'Walk In'),
        ('website', 'Website'),
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('text', 'Text'),
        ('other', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    referral = models.CharField(
        max_length=20,
        choices=REFERRAL_CHOICES,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    converted_to_client = models.OneToOneField(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='converted_from_lead',
    )

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_converted(self):
        return self.converted_to_client_id is not None


class LeadNote(models.Model):
    """A date/time-stamped note for a lead. Newest first."""
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='additional_notes',
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lead} – {self.created_at:%Y-%m-%d %H:%M}"


class ClientNote(models.Model):
    """A date/time-stamped note for a client. Newest first."""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='additional_notes',
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client} – {self.created_at:%Y-%m-%d %H:%M}"


class Contact(models.Model):
    """A professional contact: vendor, lender, agent, etc. Same list/detail/notes flow as clients."""

    CONTACT_TYPE_CHOICES = [
        ('vendor', 'Vendor'),
        ('lender', 'Lender'),
        ('agent', 'Agent'),
        ('title_company', 'Title Company'),
        ('inspector', 'Inspector'),
        ('attorney', 'Attorney'),
        ('other', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    contact_type = models.CharField(
        max_length=20,
        choices=CONTACT_TYPE_CHOICES,
        default='other',
    )
    company = models.CharField(
        max_length=200,
        blank=True,
        help_text="Company or business name",
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class ContactNote(models.Model):
    """A date/time-stamped note for a contact. Newest first."""
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='additional_notes',
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contact} – {self.created_at:%Y-%m-%d %H:%M}"


class Property(models.Model):
    """A property listing or record in the CRM."""

    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('commercial', 'Commercial'),
        ('condo', 'Condo'),
        ('duplex', 'Duplex'),
        ('fourplex', 'Fourplex'),
        ('land', 'Land'),
        ('mobile_home', 'Mobile Home'),
        ('single_family', 'Single Family'),
        ('townhouse', 'Townhouse'),
        ('triplex', 'Triplex'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('under_contract', 'Under Contract'),
        ('sold', 'Sold'),
        ('off_market', 'Off Market'),
    ]

    MLS_SERVICE_CHOICES = [
        ('bareis', 'BAREIS'),
        ('paragon', 'Paragon'),
        ('matrix', 'Matrix'),
        ('mlslistings', 'MLSListings'),
        ('redfin', 'Redfin'),
        ('zillow', 'Zillow'),
        ('realtor', 'Realtor.com'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
    )
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
    )
    square_feet = models.PositiveIntegerField(null=True, blank=True)
    lot_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    year_built = models.PositiveIntegerField(null=True, blank=True)
    mls_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="MLS listing number",
    )
    mls_service = models.CharField(
        max_length=20,
        choices=MLS_SERVICE_CHOICES,
        blank=True,
        help_text="MLS service provider",
    )
    mls_url = models.URLField(blank=True, help_text="Direct link to MLS listing")
    photo = models.FileField(
        upload_to='property_photos/',
        null=True,
        blank=True,
        help_text="Main property photo",
    )
    description = models.TextField(blank=True)
    features = models.TextField(blank=True)
    images = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='properties',
        null=True,
        blank=True,
    )
    featured = models.BooleanField(
        default=False,
        help_text="Mark this property as featured",
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'

    def __str__(self):
        return f"{self.title} - {self.address}"

    def formatted_price(self):
        """US format with commas for admin/list display."""
        if self.price is None:
            return "—"
        return f"${self.price:,.0f}"

    formatted_price.short_description = "Price"


class PropertyPhoto(models.Model):
    """An additional photo for a property. Property can have multiple photos."""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='photos',
    )
    image = models.FileField(upload_to='property_photos/%Y/%m/', blank=False)
    order = models.PositiveSmallIntegerField(default=0, help_text='Display order (lower first)')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']


class PropertyNote(models.Model):
    """A date/time-stamped note for a property. Newest first."""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='additional_notes',
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.property.title} – {self.created_at:%Y-%m-%d %H:%M}"


class Transaction(models.Model):
    """A real estate transaction linking a property to parties, milestones, and notes."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('under_contract', 'Under Contract'),
        ('closed', 'Closed'),
        ('canceled', 'Canceled'),
    ]

    REPRESENTATION_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('dual', 'Dual Agent'),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
    )
    representation = models.CharField(
        max_length=10,
        choices=REPRESENTATION_CHOICES,
        default='buyer',
        help_text="Your role in this transaction",
    )
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Agreed commission %",
    )
    final_sales_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final sales price (used for GCI when closed)",
    )
    file_number = models.CharField(max_length=50, blank=True)
    lockbox_code = models.CharField(max_length=50, blank=True)
    showing_instructions = models.TextField(blank=True)
    listing_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date property was listed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.property.title} – {self.get_status_display()}"

    @builtins.property
    def gci(self):
        """
        Gross Commission Income: agreed commission % of final sales price.
        Calculated only when transaction status is closed and both commission_percentage
        and final_sales_price are set.
        """
        if self.status != 'closed':
            return None
        if self.commission_percentage is None or self.final_sales_price is None:
            return None
        from decimal import Decimal
        return (self.commission_percentage / Decimal('100')) * self.final_sales_price

class TransactionParty(models.Model):
    """A party (client or other contact) linked to a transaction with a role."""

    ROLE_CHOICES = [
        ('primary_buyer', 'Primary Buyer'),
        ('primary_seller', 'Primary Seller'),
        ('buyers_agent', "Buyer's Agent"),
        ('sellers_agent', "Seller's Agent"),
        ('home_inspector', 'Home Inspector'),
        ('sellers_lawyer', "Seller's Lawyer"),
        ('buyers_lawyer', "Buyer's Lawyer"),
        ('lender', 'Lender'),
        ('title_company', 'Title Company'),
        ('other', 'Other'),
    ]

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='parties',
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='transaction_parties',
        null=True,
        blank=True,
        help_text="Link to existing client; leave blank for non-client (e.g. inspector).",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # For parties without a Client (e.g. inspector, lawyer): store name/contact here
    display_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['role', 'display_name']
        verbose_name_plural = 'Transaction parties'

    def __str__(self):
        name = self.client.full_name if self.client else (self.display_name or 'Unknown')
        return f"{name} – {self.get_role_display()}"

    @property
    def full_name(self):
        return self.client.full_name if self.client else (self.display_name or '—')

    @property
    def display_email(self):
        if self.client and self.client.email:
            return self.client.email
        return self.email or '—'

    @property
    def display_phone(self):
        if self.client and self.client.phone:
            return self.client.phone
        return self.phone or '—'


class TransactionMilestone(models.Model):
    """A key date in the transaction (listing, contract, inspection, etc.)."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]

    MILESTONE_KIND_CHOICES = [
        ('listing', 'Listing'),
        ('contract_agreement', 'Contract Agreement'),
        ('offer', 'Offer'),
        ('offer_expiration', 'Offer Expiration'),
        ('expiration_reminder', 'Expiration Reminder'),
        ('inspection', 'Inspection'),
        ('appraisal', 'Appraisal'),
        ('closing', 'Closing'),
        ('expiration', 'Expiration'),
        ('other', 'Other'),
    ]

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='milestones',
    )
    kind = models.CharField(
        max_length=20,
        choices=MILESTONE_KIND_CHOICES,
        default='other',
    )
    label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Override label (e.g. 'Final walk-through')",
    )
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    is_critical = models.BooleanField(
        default=False,
        help_text="Show as deadline/reminder (e.g. offer expiration)",
    )
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order")

    class Meta:
        ordering = ['order', 'date']

    def __str__(self):
        label = self.label or self.get_kind_display()
        return f"{label} – {self.date}"

    @property
    def display_label(self):
        return self.label or self.get_kind_display()


class TransactionTask(models.Model):
    """A to-do task tied to the transaction."""

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    description = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'due_date', 'id']

    def __str__(self):
        return self.description


class TransactionNote(models.Model):
    """A date/time-stamped note for a transaction. Newest first."""
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='notes',
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction} – {self.created_at:%Y-%m-%d %H:%M}"


# --- User profile (per-user settings such as email signature) ---

class UserProfile(models.Model):
    """Per-user profile: email signature and optional Mailchimp/Constant Contact connection for email marketing."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    email_signature = models.TextField(
        blank=True,
        help_text='HTML signature appended to your outgoing emails. Use <a href="url"> for links and <img src="url"> for images.',
    )
    signature_image = models.FileField(
        upload_to='user_profiles/signature/',
        blank=True,
        null=True,
        help_text='Optional image (e.g. logo or photo) shown at the end of your email signature.',
    )
    # Mailchimp (optional): API key + Audience (list) ID. Leave blank if you use Constant Contact or neither.
    mailchimp_api_key = models.CharField(
        max_length=100,
        blank=True,
        help_text='Mailchimp API key (Account → Extras → API keys). Leave blank to keep current or disable.',
    )
    mailchimp_audience_id = models.CharField(
        max_length=50,
        blank=True,
        help_text='Mailchimp Audience (list) ID from Audience → Settings.',
    )
    # Constant Contact (optional): OAuth2-style credentials. Leave blank if you use Mailchimp or neither.
    constant_contact_api_key = models.CharField(
        max_length=200,
        blank=True,
        help_text='Constant Contact App Key (client ID from developer portal).',
    )
    constant_contact_api_secret = models.CharField(
        max_length=200,
        blank=True,
        help_text='Constant Contact App Secret. Leave blank to keep current.',
    )
    constant_contact_access_token = models.TextField(
        blank=True,
        help_text='Constant Contact OAuth2 access token. Leave blank to keep current.',
    )
    constant_contact_refresh_token = models.TextField(
        blank=True,
        help_text='Constant Contact OAuth2 refresh token. Leave blank to keep current.',
    )

    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'User profiles'

    def __str__(self):
        return f'Profile for {self.user.get_username()}'

    def has_mailchimp_connected(self):
        return bool(self.mailchimp_api_key and self.mailchimp_audience_id)

    def has_constant_contact_connected(self):
        return bool(
            self.constant_contact_api_key
            and (self.constant_contact_access_token or self.constant_contact_refresh_token)
        )


# --- Application admin (separate from Django admin) ---

class AppSettings(models.Model):
    """Singleton: application name, logo, chart colors, and app admin inactivity logout. Edited via Application Admin UI."""
    app_name = models.CharField(max_length=100, default='RE CRM')
    logo = models.FileField(upload_to='app_admin/', blank=True, null=True, help_text='Logo image (e.g. PNG, SVG)')
    # Chart colors: JSON e.g. {"buyer": "#1e4976", "seller": "#137333", "dual": "#b45309"}
    chart_colors = models.JSONField(
        default=dict,
        blank=True,
        help_text='Keys: buyer, seller, dual (hex colors for dashboard charts)',
    )
    # App-wide: log out after this many minutes of inactivity. 0 = disabled. Set in App Admin.
    inactivity_timeout_minutes = models.PositiveIntegerField(
        default=0,
        blank=True,
        help_text='Log out after this many minutes of no mouse/keyboard activity (entire app). Set to 0 to disable.',
    )

    class Meta:
        verbose_name = 'Application settings'
        verbose_name_plural = 'Application settings'

    def save(self, *args, **kwargs):
        # Enforce single row
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'app_name': 'RE CRM'})
        return obj


class ChoiceList(models.Model):
    """Editable choice lists for status, contact type, etc. Used by Application Admin and forms."""
    LIST_TYPE_CHOICES = [
        ('client_type', 'Client type'),
        ('client_status', 'Client status'),
        ('lead_status', 'Lead status'),
        ('lead_referral', 'Lead referral source'),
        ('transaction_status', 'Transaction status'),
        ('transaction_representation', 'Transaction representation'),
        ('contact_type', 'Contact type'),
    ]
    list_type = models.CharField(max_length=30, choices=LIST_TYPE_CHOICES, db_index=True)
    code = models.CharField(max_length=50)  # stored in DB (e.g. 'active', 'buyer')
    label = models.CharField(max_length=100)  # display label (e.g. 'Active Client')
    order = models.PositiveSmallIntegerField(default=0, help_text='Display order')

    class Meta:
        ordering = ['list_type', 'order', 'label']
        unique_together = [('list_type', 'code')]
        verbose_name_plural = 'Choice lists'

    def __str__(self):
        return f"{self.get_list_type_display()}: {self.label}"
