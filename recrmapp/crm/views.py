import json
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse, reverse_lazy
from .models import (
    AppSettings, ChoiceList,
    Client, Contact, Lead, Property, PropertyPhoto,
    Transaction, TransactionNote, TransactionParty, TransactionMilestone, TransactionTask,
)
from .choice_utils import get_choices_for_list
from .forms import (
    ClientForm, ClientNoteForm, ContactForm, ContactNoteForm,
    LeadForm, LeadNoteForm, PropertyForm, PropertyNoteForm,
    SignupForm,
    TransactionForm, TransactionNoteForm, TransactionPartyForm, TransactionMilestoneForm, TransactionTaskForm,
)

MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def _parse_chart_filter(get_params, prefix):
    """
    Parse GET params for a chart filter. Prefix is 'income' or 'sales'.
    Returns (start_date, end_date, list of (label, year, month)).
    """
    now = timezone.now()
    now_date = now.date()
    period = get_params.get(f'{prefix}_period', 'this_year')

    if period == 'month':
        try:
            year = int(get_params.get(f'{prefix}_year', now_date.year))
            month = int(get_params.get(f'{prefix}_month', now_date.month))
            start = timezone.make_aware(timezone.datetime(year, month, 1))
            if month == 12:
                end = timezone.make_aware(timezone.datetime(year, 12, 31, 23, 59, 59))
            else:
                end = timezone.make_aware(timezone.datetime(year, month + 1, 1)) - timezone.timedelta(seconds=1)
            months = [(MONTH_NAMES[month - 1], year, month)]
            return start, end, months
        except (ValueError, TypeError):
            pass
    elif period == 'custom':
        try:
            from_str = get_params.get(f'{prefix}_from', '')
            to_str = get_params.get(f'{prefix}_to', '')
            if from_str and to_str:
                from datetime import datetime
                start_d = datetime.strptime(from_str, '%Y-%m-%d').date()
                end_d = datetime.strptime(to_str, '%Y-%m-%d').date()
                if start_d > end_d:
                    start_d, end_d = end_d, start_d
                start = timezone.make_aware(timezone.datetime.combine(start_d, timezone.datetime.min.time()))
                end = timezone.make_aware(timezone.datetime.combine(end_d, timezone.datetime.max.time().replace(microsecond=0)))
                months = []
                y, m = start_d.year, start_d.month
                while (y, m) <= (end_d.year, end_d.month):
                    months.append((MONTH_NAMES[m - 1], y, m))
                    if m == 12:
                        y, m = y + 1, 1
                    else:
                        m += 1
                return start, end, months
        except (ValueError, TypeError):
            pass
    elif period == 'last_3':
        end = now
        start = end - timezone.timedelta(days=90)
        months = []
        d = date(start.year, start.month, 1)
        end_d = end.date()
        while d <= end_d:
            months.append((MONTH_NAMES[d.month - 1], d.year, d.month))
            if d.month == 12:
                d = date(d.year + 1, 1, 1)
            else:
                d = date(d.year, d.month + 1, 1)
        return start, end, months
    elif period == 'last_6':
        end = now
        start = end - timezone.timedelta(days=180)
        months = []
        d = date(start.year, start.month, 1)
        end_d = end.date()
        while d <= end_d:
            months.append((MONTH_NAMES[d.month - 1], d.year, d.month))
            if d.month == 12:
                d = date(d.year + 1, 1, 1)
            else:
                d = date(d.year, d.month + 1, 1)
        return start, end, months

    # default: this year
    start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    end = now
    months = [(MONTH_NAMES[m - 1], now_date.year, m) for m in range(1, 13)]
    return start, end, months


@login_required
def home(request):
    """Dashboard / home page with analytics and transaction charts."""
    from .models import AppSettings
    app_settings_obj = AppSettings.load()
    chart_colors = app_settings_obj.chart_colors or {}
    client_count = Client.objects.count()
    property_count = Property.objects.count()
    lead_count = Lead.objects.filter(converted_to_client__isnull=True).count()
    transaction_count = Transaction.objects.count()
    get_params = request.GET
    now = timezone.now()

    # Income chart filter
    income_start, income_end, income_months = _parse_chart_filter(get_params, 'income')
    month_labels_income = [m[0] for m in income_months]
    if len(income_months) == 1:
        month_labels_income = [f"{income_months[0][0]} {income_months[0][1]}"]

    # Sales chart filter
    sales_start, sales_end, sales_months = _parse_chart_filter(get_params, 'sales')
    month_labels_sales = [m[0] for m in sales_months]
    if len(sales_months) == 1:
        month_labels_sales = [f"{sales_months[0][0]} {sales_months[0][1]}"]

    # Sales by month and representation (buyer / seller / dual)
    sales_queryset = (
        Transaction.objects.filter(status='closed', updated_at__gte=sales_start, updated_at__lte=sales_end)
        .annotate(month=TruncMonth('updated_at'))
        .values('month', 'representation')
        .annotate(total=Sum('final_sales_price'))
        .order_by('month', 'representation')
    )
    sales_by_key = {}  # (y, m, rep) -> total
    for item in sales_queryset:
        key = (item['month'].year, item['month'].month, item['representation'])
        sales_by_key[key] = float(item['total'] or 0)
    sales_by_month = []
    sales_by_month_buyer = []
    sales_by_month_seller = []
    sales_by_month_dual = []
    for _, y, m in sales_months:
        by_rep = (
            sales_by_key.get((y, m, 'buyer'), 0),
            sales_by_key.get((y, m, 'seller'), 0),
            sales_by_key.get((y, m, 'dual'), 0),
        )
        sales_by_month.append(by_rep[0] + by_rep[1] + by_rep[2])
        sales_by_month_buyer.append(by_rep[0])
        sales_by_month_seller.append(by_rep[1])
        sales_by_month_dual.append(by_rep[2])

    # Income (GCI) by month and representation (buyer / seller / dual)
    closed_txns = Transaction.objects.filter(
        status='closed', updated_at__gte=income_start, updated_at__lte=income_end
    ).select_related('property')
    gci_by_key = {(y, m): Decimal('0') for _, y, m in income_months}
    gci_by_rep = {(y, m, rep): Decimal('0') for _, y, m in income_months for rep in ('buyer', 'seller', 'dual')}
    for t in closed_txns:
        if t.gci is not None:
            key = (t.updated_at.year, t.updated_at.month)
            rep = t.representation if t.representation in ('buyer', 'seller', 'dual') else 'buyer'
            rep_key = (t.updated_at.year, t.updated_at.month, rep)
            if key in gci_by_key:
                gci_by_key[key] += t.gci
            if rep_key in gci_by_rep:
                gci_by_rep[rep_key] += t.gci
    income_by_month = [float(gci_by_key[(y, m)]) for _, y, m in income_months]
    income_by_month_buyer = [float(gci_by_rep.get((y, m, 'buyer'), 0)) for _, y, m in income_months]
    income_by_month_seller = [float(gci_by_rep.get((y, m, 'seller'), 0)) for _, y, m in income_months]
    income_by_month_dual = [float(gci_by_rep.get((y, m, 'dual'), 0)) for _, y, m in income_months]

    total_income = sum(income_by_month)
    total_sales = sum(sales_by_month)

    # Current filter values for forms
    income_period = get_params.get('income_period', 'this_year')
    income_month = get_params.get('income_month', str(now.month))
    income_year = get_params.get('income_year', str(now.year))
    income_from = get_params.get('income_from', '')
    income_to = get_params.get('income_to', '')
    sales_period = get_params.get('sales_period', 'this_year')
    sales_month = get_params.get('sales_month', str(now.month))
    sales_year = get_params.get('sales_year', str(now.year))
    sales_from = get_params.get('sales_from', '')
    sales_to = get_params.get('sales_to', '')

    context = {
        'client_count': client_count,
        'property_count': property_count,
        'lead_count': lead_count,
        'transaction_count': transaction_count,
        'month_labels_income': month_labels_income,
        'month_labels_sales': month_labels_sales,
        'income_by_month': income_by_month,
        'sales_by_month': sales_by_month,
        'total_income': total_income,
        'total_sales': total_sales,
        'chart_data_json': json.dumps({
            'month_labels_income': month_labels_income,
            'month_labels_sales': month_labels_sales,
            'income_by_month': income_by_month,
            'income_by_month_buyer': income_by_month_buyer,
            'income_by_month_seller': income_by_month_seller,
            'income_by_month_dual': income_by_month_dual,
            'sales_by_month': sales_by_month,
            'sales_by_month_buyer': sales_by_month_buyer,
            'sales_by_month_seller': sales_by_month_seller,
            'sales_by_month_dual': sales_by_month_dual,
            'chart_colors': {
                'buyer': chart_colors.get('buyer') or chart_colors.get('income_bar', '#1e4976'),
                'seller': chart_colors.get('seller') or chart_colors.get('sales_bar', '#137333'),
                'dual': chart_colors.get('dual', '#b45309'),
            },
        }),
        'income_period': income_period,
        'income_month': income_month,
        'income_year': income_year,
        'income_from': income_from,
        'income_to': income_to,
        'sales_period': sales_period,
        'sales_month': sales_month,
        'sales_year': sales_year,
        'sales_from': sales_from,
        'sales_to': sales_to,
        'current_year': now.year,
        'year_choices': [now.year, now.year - 1],
        'month_choices': list(enumerate(MONTH_NAMES, 1)),
    }
    return render(request, 'crm/home.html', context)


def signup(request):
    """User registration. Redirects to home and logs in on success."""
    if request.user.is_authenticated:
        return redirect('crm:home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}.')
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = SignupForm()
    return render(request, 'crm/signup.html', {'form': form})


@login_required
def client_add_note(request, pk):
    """Add a timestamped note to a client. Redirects back to client detail."""
    client = get_object_or_404(Client, pk=pk)
    if request.method != 'POST':
        return redirect('crm:client_detail', pk=pk)
    form = ClientNoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.client = client
        note.save()
    return redirect('crm:client_detail', pk=pk)


@login_required
def property_add_note(request, pk):
    """Add a timestamped note to a property. Redirects back to property detail."""
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method != 'POST':
        return redirect('crm:property_detail', pk=pk)
    form = PropertyNoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.property = property_obj
        note.save()
    return redirect('crm:property_detail', pk=pk)


@login_required
def property_add_photos(request, pk):
    """Add one or more photos to a property. Redirects back to property detail."""
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method != 'POST':
        return redirect('crm:property_detail', pk=pk)
    files = request.FILES.getlist('images')
    created = 0
    if files:
        next_order = property_obj.photos.count()
        for f in files:
            if f and getattr(f, 'size', 0):
                PropertyPhoto.objects.create(property=property_obj, image=f, order=next_order)
                next_order += 1
                created += 1
        if created:
            messages.success(request, f'Added {created} photo(s).')
    return redirect('crm:property_detail', pk=pk)


@login_required
def property_delete_photo(request, pk, photo_pk):
    """Remove a photo from a property (POST only)."""
    if request.method != 'POST':
        return redirect('crm:property_detail', pk=pk)
    property_obj = get_object_or_404(Property, pk=pk)
    photo = get_object_or_404(PropertyPhoto, pk=photo_pk, property=property_obj)
    photo.delete()
    messages.success(request, 'Photo removed.')
    return redirect('crm:property_detail', pk=pk)


@login_required
def lead_add_note(request, pk):
    """Add a timestamped note to a lead. Redirects back to lead detail."""
    lead = get_object_or_404(Lead, pk=pk)
    if request.method != 'POST':
        return redirect('crm:lead_detail', pk=pk)
    form = LeadNoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.lead = lead
        note.save()
    return redirect('crm:lead_detail', pk=pk)


@login_required
def contact_add_note(request, pk):
    """Add a timestamped note to a contact. Redirects back to contact detail."""
    contact = get_object_or_404(Contact, pk=pk)
    if request.method != 'POST':
        return redirect('crm:contact_detail', pk=pk)
    form = ContactNoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.contact = contact
        note.save()
    return redirect('crm:contact_detail', pk=pk)


@login_required
def lead_convert_to_client(request, pk):
    """Convert a lead to a client. Creates Client from lead data, links lead, redirects to client detail. Works with GET (link) or POST (button)."""
    lead = get_object_or_404(Lead, pk=pk)
    if lead.converted_to_client_id:
        return redirect('crm:client_detail', pk=lead.converted_to_client_id)
    client = Client.objects.create(
        first_name=lead.first_name,
        last_name=lead.last_name,
        email=lead.email or '',
        phone=lead.phone or '',
        address=lead.address or '',
        city=lead.city or '',
        state=lead.state or '',
        zip_code=lead.zip_code or '',
        notes=lead.notes or '',
        client_type='buyer',
        status='potential',
    )
    lead.converted_to_client = client
    lead.save()
    return redirect('crm:client_detail', pk=client.pk)


# --- Client views ---

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    context_object_name = 'clients'
    template_name = 'crm/client_list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q)
                | Q(email__icontains=q) | Q(phone__icontains=q)
                | Q(city__icontains=q) | Q(address__icontains=q)
            )
        client_type = self.request.GET.get('client_type', '')
        if client_type:
            qs = qs.filter(client_type=client_type)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_copy = self.request.GET.copy()
        if 'page' in get_copy:
            del get_copy['page']
        context['pagination_querystring'] = get_copy.urlencode()
        context['current_q'] = self.request.GET.get('q', '')
        context['current_client_type'] = self.request.GET.get('client_type', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['client_type_choices'] = get_choices_for_list('client_type')
        context['client_status_choices'] = get_choices_for_list('client_status')
        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    context_object_name = 'client'
    template_name = 'crm/client_detail.html'


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'crm/client_form.html'
    success_url = reverse_lazy('crm:client_list')


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    context_object_name = 'client'
    template_name = 'crm/client_form.html'
    success_url = reverse_lazy('crm:client_list')


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    context_object_name = 'client'
    template_name = 'crm/client_confirm_delete.html'
    success_url = reverse_lazy('crm:client_list')


# --- Contact views ---

class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    context_object_name = 'contacts'
    template_name = 'crm/contact_list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q)
                | Q(email__icontains=q) | Q(phone__icontains=q)
                | Q(company__icontains=q) | Q(city__icontains=q)
            )
        contact_type = self.request.GET.get('contact_type', '')
        if contact_type:
            qs = qs.filter(contact_type=contact_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_copy = self.request.GET.copy()
        if 'page' in get_copy:
            del get_copy['page']
        context['pagination_querystring'] = get_copy.urlencode()
        context['current_q'] = self.request.GET.get('q', '')
        context['current_contact_type'] = self.request.GET.get('contact_type', '')
        context['contact_type_choices'] = get_choices_for_list('contact_type')
        return context


class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    context_object_name = 'contact'
    template_name = 'crm/contact_detail.html'


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'crm/contact_form.html'
    success_url = reverse_lazy('crm:contact_list')


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    context_object_name = 'contact'
    template_name = 'crm/contact_form.html'
    success_url = reverse_lazy('crm:contact_list')


class ContactDeleteView(LoginRequiredMixin, DeleteView):
    model = Contact
    context_object_name = 'contact'
    template_name = 'crm/contact_confirm_delete.html'
    success_url = reverse_lazy('crm:contact_list')


# --- Property views ---

class PropertyListView(LoginRequiredMixin, ListView):
    model = Property
    context_object_name = 'properties'
    template_name = 'crm/property_list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(address__icontains=q)
                | Q(city__icontains=q) | Q(state__icontains=q)
                | Q(zip_code__icontains=q) | Q(mls_number__icontains=q)
            )
        property_type = self.request.GET.get('property_type', '')
        if property_type:
            qs = qs.filter(property_type=property_type)
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_copy = self.request.GET.copy()
        if 'page' in get_copy:
            del get_copy['page']
        context['pagination_querystring'] = get_copy.urlencode()
        context['current_q'] = self.request.GET.get('q', '')
        context['current_property_type'] = self.request.GET.get('property_type', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['property_type_choices'] = Property.PROPERTY_TYPE_CHOICES
        context['property_status_choices'] = Property.STATUS_CHOICES
        return context


class PropertyDetailView(LoginRequiredMixin, DetailView):
    model = Property
    context_object_name = 'property'
    template_name = 'crm/property_detail.html'


class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'crm/property_form.html'
    success_url = reverse_lazy('crm:property_list')

    def get_initial(self):
        initial = super().get_initial()
        client_id = self.request.GET.get('client')
        if client_id:
            initial['owner'] = client_id
        return initial


class PropertyUpdateView(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    context_object_name = 'property'
    template_name = 'crm/property_form.html'
    success_url = reverse_lazy('crm:property_list')


class PropertyDeleteView(LoginRequiredMixin, DeleteView):
    model = Property
    context_object_name = 'property'
    template_name = 'crm/property_confirm_delete.html'
    success_url = reverse_lazy('crm:property_list')


# --- Lead views ---

class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    context_object_name = 'leads'
    template_name = 'crm/lead_list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.GET.get('show_all'):
            qs = qs.filter(converted_to_client__isnull=True)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q)
                | Q(email__icontains=q) | Q(phone__icontains=q)
                | Q(city__icontains=q)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        referral = self.request.GET.get('referral', '')
        if referral:
            qs = qs.filter(referral=referral)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_copy = self.request.GET.copy()
        if 'page' in get_copy:
            del get_copy['page']
        context['pagination_querystring'] = get_copy.urlencode()
        get_no_show_all = get_copy.copy()
        get_no_show_all.pop('show_all', None)
        context['querystring_without_show_all'] = get_no_show_all.urlencode()
        context['current_q'] = self.request.GET.get('q', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_referral'] = self.request.GET.get('referral', '')
        context['lead_status_choices'] = get_choices_for_list('lead_status')
        context['lead_referral_choices'] = get_choices_for_list('lead_referral')
        context['show_all'] = self.request.GET.get('show_all')
        return context


class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    context_object_name = 'lead'
    template_name = 'crm/lead_detail.html'


class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    form_class = LeadForm
    template_name = 'crm/lead_form.html'
    success_url = reverse_lazy('crm:lead_list')


class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    form_class = LeadForm
    context_object_name = 'lead'
    template_name = 'crm/lead_form.html'
    success_url = reverse_lazy('crm:lead_list')


class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    context_object_name = 'lead'
    template_name = 'crm/lead_confirm_delete.html'
    success_url = reverse_lazy('crm:lead_list')


# --- Transaction views ---

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    context_object_name = 'transactions'
    template_name = 'crm/transaction_list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('property')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(file_number__icontains=q)
                | Q(property__title__icontains=q)
                | Q(property__address__icontains=q)
                | Q(property__city__icontains=q)
                | Q(property__mls_number__icontains=q)
            )
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        representation = self.request.GET.get('representation', '')
        if representation:
            qs = qs.filter(representation=representation)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_copy = self.request.GET.copy()
        if 'page' in get_copy:
            del get_copy['page']
        context['pagination_querystring'] = get_copy.urlencode()
        context['current_q'] = self.request.GET.get('q', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_representation'] = self.request.GET.get('representation', '')
        context['transaction_status_choices'] = get_choices_for_list('transaction_status')
        context['transaction_representation_choices'] = get_choices_for_list('transaction_representation')
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    context_object_name = 'transaction'
    template_name = 'crm/transaction_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['party_form'] = TransactionPartyForm()
        context['milestone_form'] = TransactionMilestoneForm()
        context['task_form'] = TransactionTaskForm()
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'crm/transaction_form.html'

    def get_initial(self):
        initial = super().get_initial()
        property_id = self.request.GET.get('property')
        if property_id:
            initial['property'] = property_id
        return initial

    def get_success_url(self):
        return reverse('crm:transaction_detail', kwargs={'pk': self.object.pk})


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    context_object_name = 'transaction'
    template_name = 'crm/transaction_form.html'

    def get_success_url(self):
        return reverse('crm:transaction_detail', kwargs={'pk': self.object.pk})


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    context_object_name = 'transaction'
    template_name = 'crm/transaction_confirm_delete.html'
    success_url = reverse_lazy('crm:transaction_list')


@login_required
def transaction_add_note(request, pk):
    """Add a timestamped note to a transaction. Redirects back to transaction detail."""
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method != 'POST':
        return redirect('crm:transaction_detail', pk=pk)
    form = TransactionNoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.transaction = transaction
        note.save()
    return redirect('crm:transaction_detail', pk=pk)


@login_required
def transaction_add_party(request, pk):
    """Add a party to a transaction. Redirects back to transaction detail."""
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method != 'POST':
        return redirect('crm:transaction_detail', pk=pk)
    form = TransactionPartyForm(request.POST)
    if form.is_valid():
        party = form.save(commit=False)
        party.transaction = transaction
        party.save()
    return redirect('crm:transaction_detail', pk=pk)


@login_required
def transaction_delete_party(request, pk, party_pk):
    """Remove a party from a transaction (POST only)."""
    if request.method != 'POST':
        return redirect('crm:transaction_detail', pk=pk)
    transaction = get_object_or_404(Transaction, pk=pk)
    party = get_object_or_404(TransactionParty, pk=party_pk, transaction=transaction)
    party.delete()
    return redirect('crm:transaction_detail', pk=pk)


@login_required
def transaction_add_milestone(request, pk):
    """Add a milestone to a transaction."""
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method != 'POST':
        return redirect('crm:transaction_detail', pk=pk)
    form = TransactionMilestoneForm(request.POST)
    if form.is_valid():
        milestone = form.save(commit=False)
        milestone.transaction = transaction
        milestone.save()
    return redirect('crm:transaction_detail', pk=pk)


def _transaction_detail_tasks_url(pk):
    """Return transaction detail URL with #tasks so the Tasks tab is shown."""
    return reverse('crm:transaction_detail', kwargs={'pk': pk}) + '#tasks'


@login_required
def transaction_add_task(request, pk):
    """Add a task to a transaction."""
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method != 'POST':
        return redirect('crm:transaction_detail', pk=pk)
    form = TransactionTaskForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.transaction = transaction
        task.save()
        messages.success(request, "Task added.")
    else:
        messages.error(request, "Could not add task. Check the description and try again.")
    return redirect(_transaction_detail_tasks_url(pk))


@login_required
def transaction_toggle_task(request, pk, task_pk):
    """Toggle task completed state."""
    transaction = get_object_or_404(Transaction, pk=pk)
    task = get_object_or_404(TransactionTask, pk=task_pk, transaction=transaction)
    task.completed = not task.completed
    task.save()
    return redirect(_transaction_detail_tasks_url(pk))


@login_required
def transaction_delete_task(request, pk, task_pk):
    """Delete a task (POST only)."""
    if request.method != 'POST':
        return redirect('crm:transaction_detail', pk=pk)
    transaction = get_object_or_404(Transaction, pk=pk)
    task = get_object_or_404(TransactionTask, pk=task_pk, transaction=transaction)
    task.delete()
    return redirect(_transaction_detail_tasks_url(pk))


# --- Application admin (separate from Django admin) ---

def app_admin_dashboard(request):
    """Application admin: app name, logo, chart colors, and choice list CRUD."""
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL + '?next=' + request.path)
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access Application Admin.')
        return redirect('crm:home')
    from .choice_utils import invalidate_choice_cache
    from .forms import AppSettingsForm, ChoiceListForm
    settings_obj = AppSettings.load()
    if request.method == 'POST' and request.POST.get('form_type') == 'settings':
        form = AppSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            invalidate_choice_cache()
            messages.success(request, 'Application settings saved.')
            return redirect('crm:app_admin')
    else:
        form = AppSettingsForm(instance=settings_obj)
    choice_lists = {}
    for list_type, _ in ChoiceList.LIST_TYPE_CHOICES:
        choice_lists[list_type] = list(ChoiceList.objects.filter(list_type=list_type).order_by('order', 'label'))
    context = {
        'form': form,
        'choice_lists': choice_lists,
        'list_type_choices': ChoiceList.LIST_TYPE_CHOICES,
        'choice_form': ChoiceListForm(),
    }
    return render(request, 'crm/app_admin.html', context)


def app_admin_choice_add(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('crm:home')
    from .choice_utils import invalidate_choice_cache
    from .forms import ChoiceListForm
    if request.method != 'POST':
        return redirect('crm:app_admin')
    form = ChoiceListForm(request.POST)
    if form.is_valid():
        form.save()
        invalidate_choice_cache(form.cleaned_data['list_type'])
        messages.success(request, 'Choice added.')
    else:
        messages.error(request, 'Could not add choice. Check code and label.')
    return redirect('crm:app_admin' + '#list-' + request.POST.get('list_type', ''))


def app_admin_choice_edit(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('crm:home')
    from .choice_utils import invalidate_choice_cache
    from .forms import ChoiceListForm
    choice = get_object_or_404(ChoiceList, pk=pk)
    if request.method == 'POST':
        form = ChoiceListForm(request.POST, instance=choice)
        if form.is_valid():
            form.save()
            invalidate_choice_cache(choice.list_type)
            messages.success(request, 'Choice updated.')
            return redirect('crm:app_admin' + '#list-' + choice.list_type)
    else:
        form = ChoiceListForm(instance=choice)
    return render(request, 'crm/app_admin_choice_edit.html', {'form': form, 'choice': choice})


def app_admin_choice_delete(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('crm:home')
    if request.method != 'POST':
        return redirect('crm:app_admin')
    from .choice_utils import invalidate_choice_cache
    choice = get_object_or_404(ChoiceList, pk=pk)
    list_type = choice.list_type
    choice.delete()
    invalidate_choice_cache(list_type)
    messages.success(request, 'Choice removed.')
    return redirect('crm:app_admin' + '#list-' + list_type)
