from django.urls import path
from .views import (Products, AddProduct, ProductDetail, UpdateProduct,
                    DeleteProduct, ProposalList, CreateExchangeProposal,
                    UpdateExchangeProposal, ArchiveView)

urlpatterns = [
    path('', Products.as_view(), name='products'),
    path('product_detail/<int:pk>', ProductDetail.as_view(), name='product_detail'),
    path('create_ad/', AddProduct.as_view(), name='create_ad'),
    path('edit/<int:pk>/', UpdateProduct.as_view(), name='edit_page'),
    path('delete/<int:pk>/', DeleteProduct.as_view(), name='delete_page'),
    path('exchange_proposal/', ProposalList.as_view(), name='exchange_proposal'),
    path('create_exchange/', CreateExchangeProposal.as_view(), name='create_exchange'),
    path('update_exchange/<int:pk>/', UpdateExchangeProposal.as_view(), name='update_exchange'),
    path('archive/', ArchiveView.as_view(), name='archive'),
]