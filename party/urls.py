from django.urls import path

from . import views

urlpatterns = [
    path('add-party/', views.add_party, name='add_product'),
    path('edit-party/<int:id>/', views.edit_party, name='edit_product'),
    path('delete-party/<int:id>/', views.delete_party, name='delete_product'),
    path('list-party/', views.party_list, name='product_list'),
]
