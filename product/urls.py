from django.urls import path

from . import views

urlpatterns = [
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:id>/', views.delete_product, name='delete_product'),
    path('productLIST/', views.product_list, name='product_list'),

    path('add-category/', views.add_category, name='add_category'),
    path('category-list/', views.category_list, name='category_list'),
    path('edit-category/<int:id>/', views.edit_category, name='edit_category'),
    path('delete-category/<int:id>/', views.delete_category, name='delete_category'),

    path('search-product/', views.search_product, name='search_product'),

    path('export-party/<str:fromD>/<str:toD>/<str:search>/', views.export_party, name='export_party'),
    path('export-product/<str:fromD>/<str:toD>/<str:search>/', views.export_product, name='export_product'),
    path('export-trans-hostory/<str:fromD>/<str:toD>/<str:search>/', views.export_trans_hostory, name='export_trans_hostory'),
]
