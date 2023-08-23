from django.urls import path

from . import views

urlpatterns = [
    path('transaction-HISTORY/', views.transactionHISTORY, name='transactionHISTORY'),
    path('', views.generateBILL, name='generateBILL'),
    path('edit-bill/<int:bill_id>/', views.edit_bill, name='edit_bill'),
    path('view-invoice/', views.view_invoice, name='view_invoice'),
    path('view-invoice/<int:id>/', views.view_invoice, name='view_invoice'),
    path('export-csv/<str:param>/', views.export_data_to_csv, name='export_data_to_csv'),
    path('get-user/', views.get_user, name='get_user'),

]
