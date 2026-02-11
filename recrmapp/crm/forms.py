from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    AppSettings, ChoiceList, UserProfile,
    Client, ClientNote, Contact, ContactNote, Lead, LeadNote, Property, PropertyNote,
    Transaction, TransactionNote, TransactionParty, TransactionMilestone, TransactionTask,
)
from .choice_utils import get_choices_for_list


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class ClientNoteForm(forms.ModelForm):
    class Meta:
        model = ClientNote
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a note…'}),
        }


class ContactNoteForm(forms.ModelForm):
    class Meta:
        model = ContactNote
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a note…'}),
        }


class SendEmailForm(forms.Form):
    """Simple form to send an email (subject + body) to a contact, client, or lead. Attachments handled in view."""
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Message…'}),
    )


class SendTransactionEmailForm(forms.Form):
    """Send email to one or more transaction parties and/or additional addresses. Multiple attachments supported."""
    recipients = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    )
    other_emails = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Additional emails (comma-separated)',
        }),
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Message…'}),
    )

    def __init__(self, *args, transaction=None, **kwargs):
        super().__init__(*args, **kwargs)
        if transaction:
            parties_with_email = [
                p for p in transaction.parties.all()
                if getattr(p, 'display_email', None) and p.display_email != '—'
            ]
            choices = [(p.display_email, f'{p.full_name} ({p.display_email})') for p in parties_with_email]
            self.fields['recipients'].choices = choices

    def _parse_emails(self, raw):
        """Parse comma/newline-separated string into list of stripped, non-empty emails."""
        from django.core.exceptions import ValidationError as CoreValidationError
        from django.core.validators import validate_email
        if not raw or not raw.strip():
            return []
        emails = []
        for part in raw.replace('\n', ',').split(','):
            email = part.strip()
            if not email:
                continue
            try:
                validate_email(email)
                emails.append(email)
            except CoreValidationError:
                continue
        return emails

    def clean(self):
        from django.core.exceptions import ValidationError
        data = super().clean()
        selected = list(data.get('recipients') or [])
        other_raw = (data.get('other_emails') or '').strip()
        other_list = self._parse_emails(other_raw)
        to_emails = list(dict.fromkeys(selected + other_list))  # preserve order, no duplicates
        if not to_emails:
            raise ValidationError(
                'Select at least one recipient and/or enter one or more email addresses (comma-separated).'
            )
        data['to_emails'] = to_emails
        return data


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'contact_type', 'company',
            'address', 'city', 'state', 'zip_code',
            'newsletter_opt_in',
            'notes',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_type': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'newsletter_opt_in': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_type'].choices = [('', '---------')] + get_choices_for_list('contact_type')


class PropertyNoteForm(forms.ModelForm):
    class Meta:
        model = PropertyNote
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a note…'}),
        }


class LeadNoteForm(forms.ModelForm):
    class Meta:
        model = LeadNote
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a note…'}),
        }


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'referral', 'status',
            'address', 'city', 'state', 'zip_code', 'newsletter_opt_in', 'notes',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'referral': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'newsletter_opt_in': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['referral'].choices = [('', '---------')] + get_choices_for_list('lead_referral')
        self.fields['status'].choices = [('', '---------')] + get_choices_for_list('lead_status')


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'spouse_first_name', 'spouse_last_name', 'spouse_email', 'spouse_phone',
            'client_type', 'status',
            'address', 'city', 'state', 'zip_code',
            'budget_min', 'budget_max',
            'newsletter_opt_in',
            'notes',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Spouse's first name"}),
            'spouse_last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Spouse's last name"}),
            'spouse_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Spouse's email"}),
            'spouse_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Spouse's phone"}),
            'client_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'budget_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Min'}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Max'}),
            'newsletter_opt_in': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client_type'].choices = [('', '---------')] + get_choices_for_list('client_type')
        self.fields['status'].choices = [('', '---------')] + get_choices_for_list('client_status')


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'property_type', 'status',
            'address', 'city', 'state', 'zip_code',
            'price', 'bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'year_built',
            'mls_number', 'mls_service', 'mls_url',
            'photo', 'description', 'features', 'owner', 'featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Property title'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'square_feet': forms.NumberInput(attrs={'class': 'form-control'}),
            'lot_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'year_built': forms.NumberInput(attrs={'class': 'form-control'}),
            'mls_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MLS #'}),
            'mls_service': forms.Select(attrs={'class': 'form-select'}),
            'mls_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'features': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Key features, one per line or comma-separated'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['owner'].queryset = Client.objects.filter(user=user).order_by('last_name', 'first_name')


# --- Transaction forms ---

class TransactionNoteForm(forms.ModelForm):
    class Meta:
        model = TransactionNote
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a note…'}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'property', 'status', 'representation',
            'commission_percentage', 'final_sales_price', 'file_number', 'lockbox_code',
            'showing_instructions', 'listing_date',
        ]
        widgets = {
            'property': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'representation': forms.Select(attrs={'class': 'form-select'}),
            'commission_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g. 6'}),
            'final_sales_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g. 550000'}),
            'file_number': forms.TextInput(attrs={'class': 'form-control'}),
            'lockbox_code': forms.TextInput(attrs={'class': 'form-control'}),
            'showing_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'listing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [('', '---------')] + get_choices_for_list('transaction_status')
        self.fields['representation'].choices = [('', '---------')] + get_choices_for_list('transaction_representation')
        if user is not None:
            self.fields['property'].queryset = Property.objects.filter(user=user).order_by('-created_at')


class TransactionPartyForm(forms.ModelForm):
    class Meta:
        model = TransactionParty
        fields = ['client', 'role', 'display_name', 'email', 'phone']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name (if not a client)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['client'].queryset = Client.objects.filter(user=user).order_by('last_name', 'first_name')


class TransactionMilestoneForm(forms.ModelForm):
    class Meta:
        model = TransactionMilestone
        fields = ['kind', 'label', 'date', 'status', 'is_critical', 'order']
        widgets = {
            'kind': forms.Select(attrs={'class': 'form-select'}),
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional custom label'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_critical': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class TransactionTaskForm(forms.ModelForm):
    """Minimal form for adding a task (description + due_date). completed/order set in view."""
    class Meta:
        model = TransactionTask
        fields = ['description', 'due_date']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task description'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


# --- Import form (CSV/Excel upload) ---

class ImportForm(forms.Form):
    file = forms.FileField(
        label='File',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx,.xls'}),
    )
    format_type = forms.ChoiceField(
        label='Format',
        choices=[('csv', 'CSV'), ('xlsx', 'Excel (.xlsx)')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='csv',
    )


# --- User profile forms ---

class UserProfileForm(forms.ModelForm):
    clear_signature_image = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = UserProfile
        fields = [
            'email_signature', 'signature_image',
            'mailchimp_api_key', 'mailchimp_audience_id',
            'constant_contact_api_key', 'constant_contact_api_secret',
            'constant_contact_access_token', 'constant_contact_refresh_token',
            'constant_contact_list_id',
        ]
        widgets = {
            'email_signature': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'rows': 8,
                'placeholder': 'e.g. <p>Best regards,<br>Jane Smith</p>\n<a href="https://example.com">My website</a>\n<img src="https://example.com/logo.png" alt="Logo">',
            }),
            'signature_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'mailchimp_api_key': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank to keep current',
                'autocomplete': 'off',
            }),
            'mailchimp_audience_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. abc123def4'}),
            'constant_contact_api_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'App Key (client ID)'}),
            'constant_contact_api_secret': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank to keep current',
                'autocomplete': 'off',
            }),
            'constant_contact_access_token': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank to keep current',
                'autocomplete': 'off',
            }),
            'constant_contact_refresh_token': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank to keep current',
                'autocomplete': 'off',
            }),
            'constant_contact_list_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'List ID (required for sync)'}),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.cleaned_data.get('clear_signature_image'):
            obj.signature_image = None
        # Don't overwrite secret fields with empty when user left them blank (password-style fields)
        if obj.pk:
            for field_name in ('mailchimp_api_key', 'constant_contact_api_secret',
                              'constant_contact_access_token', 'constant_contact_refresh_token'):
                if not self.cleaned_data.get(field_name):
                    setattr(obj, field_name, getattr(self.instance, field_name, '') or '')
        if commit:
            obj.save()
        return obj


# --- Application admin forms ---

class AppSettingsForm(forms.ModelForm):
    clear_logo = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = AppSettings
        fields = ['app_name', 'logo', 'inactivity_timeout_minutes']
        widgets = {
            'app_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Application name'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'inactivity_timeout_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 120}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        colors = (self.instance.chart_colors or {}) if self.instance.pk else {}
        # Support legacy keys (income_bar/sales_bar) for backward compatibility
        self.fields['buyer_color'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '#1e4976', 'maxlength': '20'}),
            initial=colors.get('buyer') or colors.get('income_bar', '#1e4976'),
        )
        self.fields['seller_color'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '#137333', 'maxlength': '20'}),
            initial=colors.get('seller') or colors.get('sales_bar', '#137333'),
        )
        self.fields['dual_color'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '#b45309', 'maxlength': '20'}),
            initial=colors.get('dual', '#b45309'),
        )

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.cleaned_data.get('clear_logo'):
            obj.logo = None
        obj.chart_colors = {
            'buyer': (self.cleaned_data.get('buyer_color') or '#1e4976').strip() or '#1e4976',
            'seller': (self.cleaned_data.get('seller_color') or '#137333').strip() or '#137333',
            'dual': (self.cleaned_data.get('dual_color') or '#b45309').strip() or '#b45309',
        }
        if commit:
            obj.save()
        return obj


class ChoiceListForm(forms.ModelForm):
    class Meta:
        model = ChoiceList
        fields = ['list_type', 'code', 'label', 'order']
        widgets = {
            'list_type': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. active'}),
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Display label'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
