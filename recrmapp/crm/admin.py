from django.contrib import admin
from .models import (
    Client, ClientNote, Contact, ContactNote, Lead, LeadNote, Property, PropertyNote, PropertyPhoto,
    Transaction, TransactionNote, TransactionParty, TransactionMilestone, TransactionTask,
    UserProfile,
)


class ClientNoteInline(admin.TabularInline):
    model = ClientNote
    extra = 0
    ordering = ['-created_at']


class PropertyNoteInline(admin.TabularInline):
    model = PropertyNote
    extra = 0
    ordering = ['-created_at']


class PropertyPhotoInline(admin.TabularInline):
    model = PropertyPhoto
    extra = 0
    ordering = ['order', 'uploaded_at']


class LeadNoteInline(admin.TabularInline):
    model = LeadNote
    extra = 0
    ordering = ['-created_at']


class ContactNoteInline(admin.TabularInline):
    model = ContactNote
    extra = 0
    ordering = ['-created_at']


def _admin_queryset_user_scoped(queryset, request, user_field='user'):
    """Restrict queryset to current user's records unless superuser."""
    if request.user.is_superuser:
        return queryset
    return queryset.filter(**{user_field: request.user})


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'contact_type', 'company', 'email', 'phone', 'city', 'user', 'created_at')
    list_filter = ('contact_type', 'state', 'user')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'company')
    ordering = ('last_name', 'first_name')
    inlines = [ContactNoteInline]

    def get_queryset(self, request):
        return _admin_queryset_user_scoped(super().get_queryset(request), request)

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'phone', 'client_type', 'status', 'city', 'user', 'created_at')
    list_filter = ('client_type', 'status', 'state', 'user')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'spouse_first_name', 'spouse_last_name')
    ordering = ('last_name', 'first_name')
    inlines = [ClientNoteInline]

    def get_queryset(self, request):
        return _admin_queryset_user_scoped(super().get_queryset(request), request)

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'phone', 'referral', 'status', 'city', 'converted_to_client', 'user', 'created_at')
    list_filter = ('referral', 'status', 'state', 'user')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    ordering = ('last_name', 'first_name')
    raw_id_fields = ('converted_to_client',)
    inlines = [LeadNoteInline]

    def get_queryset(self, request):
        return _admin_queryset_user_scoped(super().get_queryset(request), request)

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'address', 'city', 'property_type', 'status', 'formatted_price', 'owner', 'user', 'featured', 'created_at')
    list_filter = ('property_type', 'status', 'state', 'featured', 'user')
    search_fields = ('title', 'address', 'city', 'state', 'zip_code', 'mls_number')
    raw_id_fields = ('owner',)
    ordering = ('-created_at',)
    inlines = [PropertyPhotoInline, PropertyNoteInline]

    def get_queryset(self, request):
        return _admin_queryset_user_scoped(super().get_queryset(request), request)

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)


class TransactionPartyInline(admin.TabularInline):
    model = TransactionParty
    extra = 0
    raw_id_fields = ('client',)


class TransactionMilestoneInline(admin.TabularInline):
    model = TransactionMilestone
    extra = 0


class TransactionTaskInline(admin.TabularInline):
    model = TransactionTask
    extra = 0


class TransactionNoteInline(admin.TabularInline):
    model = TransactionNote
    extra = 0
    ordering = ['-created_at']


def _transaction_gci(obj):
    if obj.gci is None:
        return "—"
    return f"${obj.gci:,.2f}"


_transaction_gci.short_description = "GCI"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_signature', 'has_signature_image', 'has_mailchimp', 'has_constant_contact')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)

    def has_signature(self, obj):
        return bool(obj.email_signature and obj.email_signature.strip())
    has_signature.short_description = 'Has signature'
    has_signature.boolean = True

    def has_signature_image(self, obj):
        return bool(obj.signature_image)
    has_signature_image.short_description = 'Has image'
    has_signature_image.boolean = True

    def has_mailchimp(self, obj):
        return obj.has_mailchimp_connected()
    has_mailchimp.short_description = 'Mailchimp'
    has_mailchimp.boolean = True

    def has_constant_contact(self, obj):
        return obj.has_constant_contact_connected()
    has_constant_contact.short_description = 'Constant Contact'
    has_constant_contact.boolean = True


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('property', 'status', 'representation', 'commission_percentage', 'final_sales_price', _transaction_gci, 'listing_date', 'created_at')
    list_filter = ('status', 'representation')
    search_fields = ('property__title', 'property__address', 'file_number')
    raw_id_fields = ('property',)
    ordering = ('-created_at',)
    inlines = [TransactionPartyInline, TransactionMilestoneInline, TransactionTaskInline, TransactionNoteInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(property__user=request.user)
