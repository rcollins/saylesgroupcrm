from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile_edit, name='profile'),
    # Clients
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    path('clients/<int:pk>/notes/add/', views.client_add_note, name='client_add_note'),
    path('clients/<int:pk>/send-email/', views.send_email_to_client, name='client_send_email'),
    # Contacts
    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/add/', views.ContactCreateView.as_view(), name='contact_add'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact_detail'),
    path('contacts/<int:pk>/edit/', views.ContactUpdateView.as_view(), name='contact_edit'),
    path('contacts/<int:pk>/delete/', views.ContactDeleteView.as_view(), name='contact_delete'),
    path('contacts/<int:pk>/notes/add/', views.contact_add_note, name='contact_add_note'),
    path('contacts/<int:pk>/send-email/', views.send_email_to_contact, name='contact_send_email'),
    # Properties
    path('properties/', views.PropertyListView.as_view(), name='property_list'),
    path('properties/add/', views.PropertyCreateView.as_view(), name='property_add'),
    path('properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('properties/<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='property_edit'),
    path('properties/<int:pk>/delete/', views.PropertyDeleteView.as_view(), name='property_delete'),
    path('properties/<int:pk>/notes/add/', views.property_add_note, name='property_add_note'),
    path('properties/<int:pk>/photos/add/', views.property_add_photos, name='property_add_photos'),
    path('properties/<int:pk>/photos/<int:photo_pk>/delete/', views.property_delete_photo, name='property_delete_photo'),
    # Leads
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/add/', views.LeadCreateView.as_view(), name='lead_add'),
    path('leads/<int:pk>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('leads/<int:pk>/edit/', views.LeadUpdateView.as_view(), name='lead_edit'),
    path('leads/<int:pk>/delete/', views.LeadDeleteView.as_view(), name='lead_delete'),
    path('leads/<int:pk>/notes/add/', views.lead_add_note, name='lead_add_note'),
    path('leads/<int:pk>/send-email/', views.send_email_to_lead, name='lead_send_email'),
    path('leads/<int:pk>/convert/', views.lead_convert_to_client, name='lead_convert'),
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='transaction_add'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path('transactions/<int:pk>/notes/add/', views.transaction_add_note, name='transaction_add_note'),
    path('transactions/<int:pk>/send-email/', views.send_email_to_transaction, name='transaction_send_email'),
    path('transactions/<int:pk>/parties/add/', views.transaction_add_party, name='transaction_add_party'),
    path('transactions/<int:pk>/parties/<int:party_pk>/delete/', views.transaction_delete_party, name='transaction_delete_party'),
    path('transactions/<int:pk>/milestones/add/', views.transaction_add_milestone, name='transaction_add_milestone'),
    path('transactions/<int:pk>/tasks/add/', views.transaction_add_task, name='transaction_add_task'),
    path('transactions/<int:pk>/tasks/<int:task_pk>/toggle/', views.transaction_toggle_task, name='transaction_toggle_task'),
    path('transactions/<int:pk>/tasks/<int:task_pk>/delete/', views.transaction_delete_task, name='transaction_delete_task'),
    # Application admin (separate from Django admin)
    path('app-admin/', views.app_admin_dashboard, name='app_admin'),
    path('app-admin/choices/add/', views.app_admin_choice_add, name='app_admin_choice_add'),
    path('app-admin/choices/<int:pk>/edit/', views.app_admin_choice_edit, name='app_admin_choice_edit'),
    path('app-admin/choices/<int:pk>/delete/', views.app_admin_choice_delete, name='app_admin_choice_delete'),
]
