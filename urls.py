from django.shortcuts import render
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.home, name='home'),  
    path('index/', views.index, name='index'),  
    path('shop/', views.shop, name='shop'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/users/', views.user_management, name='user_management'),
    path('admin-dashboard/users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('admin-dashboard/products/', views.product_management, name='product_management'),
    path('admin-dashboard/products/add/', views.product_add, name='product_add'),
    path('admin-dashboard/products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('admin-dashboard/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/products/', views.manage_products, name='manage_products'),
    path('about/', views.about, name='about'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('contact/', lambda request: render(request, 'contact.html'), name='contact'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('product/add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('boutique/', views.boutique_view, name='boutique'),
    path('about/', views.about_view, name='about'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('testimonials/', views.testimonials_view, name='testimonials'),
    path('submit-testimonial/', views.submit_testimonial, name='submit_testimonial'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('invoice/<int:invoice_id>/pdf/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('place-order/', views.place_order, name='place_order'),
    path('thankyou/', views.thankyou, name='thankyou'),
    path('download-invoice/', views.download_invoice, name='download_invoice'),
    path('contact/', views.contact, name='contact'),
    path('shopp/', views.shopp, name='shopp'),
    path('contact/', views.contact_view, name='contact'),
    path('test-email/', views.test_email),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/produit/<int:produit_id>/modifier/', views.modifier_produit, name='modifier_produit'),
    path('admin-dashboard/produit/<int:produit_id>/supprimer/', views.supprimer_produit, name='supprimer_produit'),
    path('contact/', views.contact_view, name='contact'),
]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
