import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Notification, Order, Product,Comment,Profile,ProductReview
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm,CommentForm,ProfileForm,RatingForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.db.models import Q,F
from django.views.generic import ListView
from datetime import datetime
from django.db.models import Avg
# Create your views here.

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True).order_by('-count')[:4]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    products_popular = Product.objects.all().order_by('-count')[:8]
    all_categories = Category.objects.all()
    all_products = Product.objects.all()     
   
    context = {
        'categories': categories,
        'products': products,
        'products_popular':products_popular,
        'all_categories': all_categories,
        'all_products': all_products,
    }
    
    return render(request, 'store/index.html', context)


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    Product.objects.filter(slug=slug).update(count = F('count')+1)  # category count view +1
    Category.objects.filter(title=product.category.title).update(count = F('count')+1) #categor count view +1
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    form = CommentForm(instance=product)
    form1 =  RatingForm(instance=product)
    avg = ProductReview.objects.filter(product=product).aggregate(Avg('review_rating'))
    context = {
        'form': form,
        'form1': form1,
        'product': product,
        'related_products': related_products,
        'avg':avg,
    }
    # avg= product.productReview_set.aggregate(Avg('review_rating')).values()[0]
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=product)
        form1 = RatingForm(request.POST, instance=product)
        if form.is_valid():
            name = request.user.username
            user = request.user
            body = form.cleaned_data['content']
            c = Comment(product=product,user = user, commenter_name=name, comment_body=body, date_added=datetime.now())
            c.save()          
        elif form1.is_valid():
            user = request.user
            review_text = form1.cleaned_data['review_text']
            review_rating = form1.cleaned_data['review_rating']
            if(ProductReview.objects.filter(user=user).exists()):
                c =  ProductReview.objects.get(user =user,product=product)
                c.review_text=review_text
                c.review_rating = review_rating
                c.save()
            else:
                c = ProductReview(user = user,product=product,review_text=review_text,review_rating=review_rating)
                c.save()
        avg = ProductReview.objects.filter(product=product).aggregate(Avg('review_rating'))
        context['avg']=avg
    else:
        form = CommentForm()    
        form1 = RatingForm()

    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})

def price__range(min_price,max_price):
    
    product=Product.objects.price < max_price and Product.objects.price > min_price

    return product

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category, )
    categories = Category.objects.filter(is_active=True)
    filter_price = request.GET.get('filter_price', '')
    sorting = request.GET.get('sorting', '')
    min_price=0
    max_price=99999999999
    if filter_price !='':
        if filter_price == '1':
                min_price=0
                max_price=100000
        if filter_price == '2':
                min_price=100000
                max_price=200000
        if filter_price == '3':
                min_price=200000
                max_price=400000
        if filter_price == '4':
                min_price=400000
                max_price=1000000
        if filter_price == '5':
                min_price=1000000

        products = Product.objects.filter(is_active=True, category=category,price__lte=max_price,price__gte=min_price).order_by('-price')
        context = {
            'category': category,
            'products': products,
            'categories': categories,
            'filter_price': filter_price,
        }   
        return render(request, 'store/category_products.html', context)   




    if sorting != '':        
        if sorting == "high-low":
            products = Product.objects.filter(is_active=True, category=category,price__lte=max_price,price__gte=min_price).order_by('-price')
        if sorting == "low-high":
            products = reversed(list(Product.objects.filter(is_active=True, category=category,price__lte=max_price,price__gte=min_price).order_by('-price')))
        if sorting == "popularity":
            products == []
        context = {
            'category': category,
            'products': products,
            'categories': categories,
            'sorting':sorting,
        }
        return render(request, 'store/category_products.html', context)


    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }   

    return render(request, 'store/category_products.html', context)



# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    order = ['Pending', 'Accepted', 'Packed','On The Way','Delivered','Cancelled']
    order = {key: i for i, key in enumerate(order)}
    ordered_sections = sorted(orders, key=lambda orders: order.get(orders.status, 0))
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES,instance=profile)
        if form.is_valid():
            form.save()
    
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':ordered_sections,'form':form})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)
    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
    # Customer Addresses
    addresses = Address.objects.filter(user=user)
    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    user = request.user
    address_id = request.GET.get('address')
    
    address = get_object_or_404(Address, id=address_id)
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
        # And Deleting from Cart
        c.delete()
    return redirect('store:orders')


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)
    # Notification
    if request.method == 'GET':      
        content=""  
        title = "Bạn" +" đã thêm sản phẩm " +  product.title + " vào giỏ hàng."
        slug=product.slug
        if len(title)>70:  
            i=70          
            while title[i] != " ":
                i=i-1
            content=title[:i]+" ..."
        else:
            content=title
        Notification(user=user,slug=slug, content =content ,type=1).save()
    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()    
    return redirect('store:cart')


@login_required
def add_notifi_like_home(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'GET':      
        content=""  
        title = "Bạn" +" đã thích sản phẩm " +  product.title 
        slug=product.slug
        if len(title)>70:  
            i=70          
            while title[i] != " ":
                i=i-1
            content=title[:i]+" ..."
        else:
            content=title

        Notification(user=user,slug=slug, content =content ,type=1).save()

    return redirect('store:home')


@login_required
def add_notifi_like_cp(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)
    cate_slug=product.category.slug
    if request.method == 'GET':      
        content=""  
        title = "Bạn" +" đã thích sản phẩm " +  product.title 
        slug=product.slug
        if len(title)>70:  
            i=70          
            while title[i] != " ":
                i=i-1
            content=title[:i]+" ..."
        else:
            content=title

        Notification(user=user,slug=slug, content =content ,type=1).save()

    return redirect('store:category-products',cate_slug) 
    

@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    order = ['Pending', 'Accepted', 'Packed','On The Way','Delivered','Cancelled']
    order = {key: i for i, key in enumerate(order)}
    ordered_sections = sorted(all_orders, key=lambda all_orders: order.get(all_orders.status, 0))
    return render(request, 'store/orders.html', {'orders': ordered_sections})

def shop(request):
    return render(request, 'store/shop.html')

@login_required
def checkout_test(request):
    return render(request, 'store/checkout.html')


def test(request):
    return render(request, 'store/test.html')


class SearchView(ListView):
    model = Product
    template_name = 'store/search.html'
    context_object_name = 'all_search_results'

    def get_queryset(self):
        result = super(SearchView, self).get_queryset()
        query = self.request.GET.get('query')
        if query:
            postresult = Product.objects.filter(title__icontains=query)
            result = postresult
        else:
            result = None
        return result



