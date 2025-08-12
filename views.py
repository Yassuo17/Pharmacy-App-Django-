from django.utils.timezone import now, timedelta
import io
import os
import profile
from django.shortcuts import render, get_object_or_404
from .models import CartItem, Product, Cart, UserProfile
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from .models import Testimonial
from .forms import TestimonialForm
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import InvoiceInfo
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CartItem, Order, OrderItem
from reportlab.pdfgen import canvas
from django.conf import settings
import uuid
from django.contrib.auth.decorators import user_passes_test


@login_required

def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})


def shop(request):
    products = Product.objects.all()
    testimonials = Testimonial.objects.all().order_by('-created_at')[:6]
    return render(request, 'index.html', {'products': products, 'testimonials': testimonials,})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'shop-single.html', {'product': product})


@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.total_price for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


def home(request):
    return render(request, 'home.html')

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import UserProfile  
from django.contrib import messages

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            messages.error(request, "Profil utilisateur introuvable.")
            return redirect('login')
        if profile.role == 'client':
            return redirect('shop')
        elif profile.role == 'admin':
            return redirect('admin_dashboard')
        elif profile.role == 'Livreur':
            return redirect('liveur_dashboard')
        else:
            messages.error(request, "Rôle non reconnu.")
            return redirect('login')

    return render(request, 'login.html', {'form': form})

from django.contrib.auth import login
from .forms import ProductForm, SignUpForm

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()                        
            role = form.cleaned_data['role']           
            UserProfile.objects.create(user=user, role=role)
            return redirect('login')                
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def is_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all()
    products = Product.objects.all()
    return render(request, 'admin/dashboard.html', {'users': users, 'products': products})
@login_required
def user_management(request):
    users = User.objects.all()
    return render(request, 'admin/users_list.html', {'users': users})

@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user_management')
    return render(request, 'admin/user_confirm_delete.html', {'user': user})

@login_required
def product_management(request):
    products = Product.objects.all()
    return render(request, 'admin/products_list.html', {'products': products})

@login_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_management')
    else:
        form = ProductForm()
    return render(request, 'admin/product_form.html', {'form': form, 'mode': 'add'})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_management')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin/product_form.html', {'form': form, 'mode': 'edit'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_management')
    return render(request, 'admin/product_confirm_delete.html', {'product': product})

@login_required
def manage_users(request):
    users = User.objects.all()
    return render(request, 'admin/manage_users.html', {'users': users})

@login_required
def manage_products(request):
    products = Product.objects.all()
    return render(request, 'admin/manage_products.html', {'products': products})


@login_required

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user if request.user.is_authenticated else None

    item, created = CartItem.objects.get_or_create(user=user, product=product)
    if not created:
        item.quantity += 1
        item.save()

    return redirect('cart') 

def about(request):
    return render(request, 'about.html')


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    return render(request, 'checkout.html') 


def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.total_price for item in cart_items)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })

@login_required

def update_cart(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                try:
                    item_id = int(key.split('_')[1])
                    quantity = int(value)
                    item = CartItem.objects.get(id=item_id)
                    item.quantity = quantity
                    item.save()
                except (ValueError, CartItem.DoesNotExist):
                    continue
    return redirect('cart')

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        messages.success(request, "Coupon applied successfully!")
    return redirect('cart')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop-single.html', {'product': product})

def contact(request):
    return render(request, 'contact.html')


def some_view(request):
    cart_items = []
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    ...
    return render(request, 'template.html', {
        'cart_items': cart_items,
    })
def boutique_view(request):
    products = Product.objects.all()
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)
    sort_by = request.GET.get('sort')
    if sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    elif sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'boutique.html', {'products': products})

def about_view(request):
    return render(request, 'about.html')

def testimonials_view(request):
    testimonials = Testimonial.objects.order_by('-created_at')[:10]
    form = TestimonialForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('testimonials') 
    return render(request, 'testimonials.html', {
        'testimonials': testimonials,
        'form': form,
    })

def thankyou(request):
    path = request.session.get('facture_path')
    return render(request, 'thankyou.html', {'facture_path': path})


@login_required
def create_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.save()
            return redirect('testimonials')  
    else:
        form = TestimonialForm()
    return render(request, 'create_testimonial.html', {'form': form})

@login_required
def submit_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.save()
            return redirect('shop')  
    else:
        form = TestimonialForm()
    return render(request, 'submit_testimonial.html', {'form': form})


from .forms import InvoiceForm

def checkout_view(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user if request.user.is_authenticated else None
            invoice.save()

            # Rediriger vers une page qui génère une facture PDF
            return redirect('generate_invoice_pdf', invoice_id=invoice.id)
    else:
        form = InvoiceForm()
    return render(request, 'checkout.html', {'form': form})


def generate_invoice_pdf(request, invoice_id):
    invoice = InvoiceInfo.objects.get(id=invoice_id)
    template = get_template('invoice_pdf.html')
    html = template.render({'invoice': invoice})
    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)
    return response



from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_CENTER
@login_required
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('shop')

    total = sum(item.total_price for item in cart_items)
    order = Order.objects.create(user=request.user, total=total)

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    cart_items.delete()

    # Génération du PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'website', 'images', 'logo.png')  # adapte le chemin
    if os.path.exists(logo_path):
        p.drawImage(logo_path, x=width / 2 - 2*cm, y=height - 4*cm, width=4*cm, height=4*cm, preserveAspectRatio=True)

    # Titre
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 5.2*cm, f"Facture - Yass Pharmacy")

    # Infos client
    p.setFont("Helvetica", 12)
    p.drawString(2*cm, height - 6.5*cm, f"Client : {request.user.get_full_name() or request.user.username}")
    p.drawString(2*cm, height - 7.2*cm, f"Email  : {request.user.email}")
    p.drawString(2*cm, height - 7.9*cm, f"Date   : {order.created_at.strftime('%d/%m/%Y à %H:%M')}")

    # Tableau des articles
    data = [["Produit", "Quantité", "Prix unitaire", "Total"]]
    for item in order.items.all():
        data.append([
            item.product.name,
            str(item.quantity),
            f"{item.price:.2f} MAD",
            f"{item.price * item.quantity:.2f} MAD"
        ])
    data.append(["", "", "Total à payer :", f"{order.total:.2f} MAD"])

    table = Table(data, colWidths=[7*cm, 3*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f81bd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d9edf7")),
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 2*cm, height - 12*cm - len(order.items.all())*1.2*cm)

    p.showPage()
    p.save()

    buffer.seek(0)
    filename = f"facture_{uuid.uuid4().hex}.pdf"
    facture_path = os.path.join(settings.MEDIA_ROOT, 'factures', filename)
    os.makedirs(os.path.dirname(facture_path), exist_ok=True)
    with open(facture_path, 'wb') as f:
        f.write(buffer.read())

    request.session['facture_path'] = f'factures/{filename}'

    return redirect('thankyou')

from django.http import FileResponse
from django.conf import settings

@login_required
def download_invoice(request):
    facture_path = request.session.get('facture_path')
    if not facture_path:
        return HttpResponse("Aucune facture disponible.", status=404)

    full_path = os.path.join(settings.MEDIA_ROOT, facture_path)
    if not os.path.exists(full_path):
        return HttpResponse("Le fichier n'existe pas.", status=404)

    return FileResponse(open(full_path, 'rb'), as_attachment=True, filename=os.path.basename(facture_path))

from django.db.models import Q
from .models import CartItem
@login_required

def shopp(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'boutique.html', {
        'products': products,
        'query': query
    })
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"""
        Nouveau message de contact :
        
        Nom : {name}
        Email : {email}
        Sujet : {subject}
        Message :
        {message}
        """

        send_mail(
            subject=f"[Contact Site] {subject}",
            message=full_message,
            from_email=email,
            recipient_list=['yassinelkhantour@gmail.com'],
            fail_silently=False,
        )

        messages.success(request, "Votre message a été envoyé avec succès.")
        return redirect('contact')  

    return render(request, 'contact.html')


def test_email(request):
    send_mail(
        'Test Email',
        'Ceci est un test depuis Django.',
        'yassinelkhantour@gmail.com',
        ['yassinelkhantour@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse("Email envoyé.")

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import Product


def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.userprofile.role == "admin":
            login(request, user)
            return redirect("admin_dashboard")
        else:
            return render(request, "admin_login.html", {"error": "Identifiants invalides."})
    return render(request, "admin_login.html")

@login_required
def admin_dashboard(request):
    products = Product.objects.all()
    User = auth_models.User
    users = User.objects.filter(is_active=True)
    return render(request, "admin_dashboard.html", {"products": products})

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm

def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    products = Product.objects.all()
    User = auth_models.User
    users = User.objects.filter(is_active=True)
    return render(request, 'dashboard.html', {'products': products})


@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form, 'title': 'Ajouter un produit'})

@login_required
@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form, 'title': 'Modifier le produit'})


def admin_login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'admin_login.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_dashboard')
    return render(request, 'confirm_delete.html', {'product': product})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, CartItem
from .forms import ProductForm
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'admin'



def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Accès refusé.")
    return render(request, 'admin_login.html')
from django.db.models import Sum
from django.db.models.functions import TruncDate
from .models import CartItem
from django.db.models import Sum
from django.db.models.functions import TruncDate
from .models import CartItem, Product, UserProfile
from django.contrib.auth.models import User
from django.db.models.functions import TruncDate
from django.db.models import Sum
import json

import json
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import UserProfile, Product, CartItem


import json
from django.shortcuts        import render
from django.contrib.auth     import models as auth_models
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models        import Sum
from django.contrib.auth.models import User

from .models import Product, CartItem

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_view(request):
    users = User.objects.filter(is_active=True)  

    products = Product.objects.all()

    stats = (
        CartItem.objects
        .values('product__name')
        .annotate(total=Sum('quantity'))
    )
    labels = [s['product__name'] for s in stats]
    data   = [s['total']            for s in stats]

    return render(request, 'dashboard.html', {
        'users':        users,
        'products':     products,
        'chart_labels': json.dumps(labels),
        'chart_data':   json.dumps(data),
    })






from django.shortcuts import get_object_or_404

@login_required
@user_passes_test(lambda u: u.is_staff)
def supprimer_produit(request, produit_id):
    produit = get_object_or_404(Product, id=produit_id)
    produit.delete()
    return redirect('admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_staff)
def modifier_produit(request, produit_id):
    produit = get_object_or_404(Product, id=produit_id)
    if request.method == "POST":
        produit.nom = request.POST['nom']
        produit.prix = request.POST['prix']
        produit.save()
        return redirect('admin_dashboard')
    return render(request, 'modifier_produit.html', {'produit': produit})



@login_required
def search_view(request):
    q = request.GET.get('q', '').strip()
    products = users = cartitems = []

    if q:
       
        products = Product.objects.filter(name__icontains=q)

       
        users = User.objects.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q)
        )

       
        cartitems = CartItem.objects.filter(
            product__name__icontains=q
        )

    return render(request, 'search_results.html', {
        'query': q,
        'products': products,
        'users': users,
        'cartitems': cartitems,
    })

from django.shortcuts      import render, redirect
from django.core.mail      import send_mail
from django.contrib        import messages
from .forms                import ContactForm
from django.conf           import settings

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(
                subject= cd['subject'],
                message= f"De : {cd['name']} <{cd['email']}>\n\n{cd['message']}",
                from_email= settings.DEFAULT_FROM_EMAIL,
                recipient_list= [ admin_email for _, admin_email in settings.ADMINS ],
            )
            messages.success(request, "Votre message a bien été envoyé ! Merci 😊")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})