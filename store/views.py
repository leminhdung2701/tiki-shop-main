from multiprocessing import context
import string
import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Lastseen_Product, Notification, Order, Product,Comment,Profile,ProductReview,Favorite,Invoice,Voucher,UserVoucher
from django.shortcuts import redirect, render, get_object_or_404
from .forms import LoginForm, RegistrationForm, AddressForm,CommentForm,ProfileForm,RatingForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.db.models import Q,F
from django.views.generic import ListView
from datetime import datetime
from django.db.models import Avg
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Q

def home(request):
    user = request.user
    categories = Category.objects.filter(is_active=True, is_featured=True).order_by('-count')[:4]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    products_popular = Product.objects.all().order_by('-count')[:8]
    all_categories = Category.objects.all()
    all_product = Product.objects.all() 
    all_products = []
    count_item_show = 8
    for category in all_categories:
        i = 0
        for product in all_product:
            if i < count_item_show and product.category == category:
                all_products.append(product)
                i+=1

    # all_products = Product.objects.all() 
    gmail = request.GET.get('gmail', '')    
    if (gmail):
        messages.success(request, "Đăng kí nhận thông báo vào gmail thành công!")
    context = {
        'categories': categories,
        'products': products,
        'products_popular':products_popular,
        'all_categories': all_categories,
        'all_products': all_products,
    }
    if request.user.is_authenticated:
        lastseen= Lastseen_Product.objects.filter(user=request.user).order_by('-created_at')[:4]
        lastseen_products = []
        for i in lastseen:
            lastseen_products.append(i.product)
        context['lastseen_products'] = lastseen_products
    return render(request, 'store/index.html', context)


def detail(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    Product.objects.filter(slug=slug).update(count = F('count')+1)  # category count view +1
    Category.objects.filter(title=product.category.title).update(count = F('count')+1) #categor count view +1
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)[:8]
    form = CommentForm(instance=product)
    form1 =  RatingForm(instance=product)
    avg = ProductReview.objects.filter(product=product).aggregate(Avg('review_rating'))
    count_buy = Order.objects.filter(product = product,status='Delivered').count()
    checklike = None
    # them lastseen_product
    if request.user.is_authenticated:
        if(Lastseen_Product.objects.filter(user=user,product=product).exists()):
            Lastseen_Product.objects.get(user=user,product=product).delete()        
        Lastseen_Product(user=user,product=product).save()
    # them lastseen_product
    if request.user.is_authenticated:
        checklike = Favorite.objects.filter(user=user,product=product)
    context = {
        'form': form,
        'form1': form1,
        'product': product,
        'related_products': related_products,
        'avg':avg,
        'checklike':checklike,
        'count':count_buy,
    }
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=product)
        form1 = RatingForm(request.POST, instance=product)
        if form.is_valid():
            name = request.user.username
            body = form.cleaned_data['content']
            c = Comment(product=product,user = user, commenter_name=name, comment_body=body, date_added=datetime.now())
            c.save()          
        elif form1.is_valid():
            if(not Order.objects.filter(user=user,product=product).exists()):
                messages.error(request, "Bạn không được đánh giá vì chưa mua hàng")
                form1 = RatingForm()
            else:
                review_text = form1.cleaned_data['review_text']
                review_rating = form1.cleaned_data['review_rating']
                if(ProductReview.objects.filter(user=user,product=product).exists()):
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

def introduce(request):
    return render(request, 'store/introduce.html')


def price__range(min_price,max_price):
    
    product=Product.objects.price < max_price and Product.objects.price > min_price

    return product

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)    
    categories = Category.objects.filter(is_active=True)
    filter_price = request.GET.get('filter_price', '')
    sorting = request.GET.get('sorting', '')
    min_price=0
    max_price=99999999999
    # Lọc theo giá
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
            'type':1,
            'category': category,
            'all':products,
            'products': products,
            'categories': categories,
            'filter_price': filter_price,
        }   
        return render(request, 'store/category_products.html', context) 
    # Sắp xếp
    if sorting != '':        
        if sorting == "high-low":
            products = Product.objects.filter(is_active=True, category=category,price__lte=max_price,price__gte=min_price).order_by('-price')
        if sorting == "low-high":
            products = Product.objects.filter(is_active=True, category=category,price__lte=max_price,price__gte=min_price).order_by('-price').reverse()
            # products = reversed(list(Product.objects.filter(is_active=True, category=category,price__lte=max_price,price__gte=min_price).order_by('-price')))
        if sorting == "popularity":
            products = list(Product.objects.filter(is_active=True, category=category,price__lte=max_price,price__gte=min_price))
            count = [None]*len(products)
            i=0
            for product in products:
                count[i] = Order.objects.filter(product = product).count()
                i=i+1
            n = len(count)
            i=0
            for i in range(n-1):
                for j in range(0, n-i-1):
                    if count[j] < count[j + 1] :
                        count[j], count[j + 1] = count[j + 1], count[j]
                        products[j], products[j + 1] = products[j + 1], products[j]
        context = {
            'type':1,
            'category': category,
            'all':products,
            'products': products,
            'categories': categories,
            'sorting':sorting,
        }
        return render(request, 'store/category_products.html', context)
    # Product     
    p = Paginator(products, 9)
    page_num = request.GET.get('page',1)
    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)
    context = {
        'type':0,
        'all':products,
        'category': category,
        'products': page,
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
            messages.success(request, "Bạn đã đăng ký tài khoản thành công")
            form.save()
            return redirect('store:login')
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
        messages.success(request, "Đã cập nhật ảnh đại diện.")
    
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
            messages.success(request, "Bạn đã thêm một địa chỉ mới.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Địa chỉ đã được xoá.")
    return redirect('store:profile')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)
    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = 35000
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
    # Customer Addresses
    addresses = Address.objects.filter(user=user)
    #kiem tra voucher
    code = request.GET.get('voucher')
    print(code)
    boolean_check = False
    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
        
    }
     #kiem tra voucher
    if(code):
        if(Voucher.objects.filter(code=code).exists()): #kiem tra xem voucher có tồn tại không
            voucher = Voucher.objects.get(code=code)
            if(voucher.is_active):          # ma giam gia hoạt động -> kiểm tra số lượt user dùng mã giảm giá
                if(UserVoucher.objects.filter(voucher=voucher,user=user).exists()):
                    uservoucher =UserVoucher.objects.get(voucher=voucher,user=user)
                    if(uservoucher.count==3): messages.error(request, "Đã quá lượt sử dụng mã giảm giá này")
                    else :
                        uservoucher.count=uservoucher.count+1 
                        messages.success(request, "Sử dụng mã giảm giá thành công")
                        boolean_check = True
                        context['voucher'] = code
                else:
                    uservoucher = UserVoucher(voucher=voucher,user=user,count=1)
                    uservoucher.save()
                    messages.success(request, "Sử dụng mã giảm giá thành công")
                    boolean_check= True                    
        else:
            messages.error(request, "Mã giảm giá sai! Vui lòng kiểm tra lại")

        if(boolean_check):
            if(voucher.type == 1):
                if voucher.code=="TIKIXINCHAO":
                    context['shipping_amount']= 5000
                    shipping_amount = 5000
                else:
                    context['shipping_amount']= 0
                    shipping_amount = 0 
                context['total_amount']  = amount +shipping_amount 
            else:
                if voucher.code=="TIKILAMQUEN":
                    amount = amount - decimal.Decimal(float(voucher.discount))                 
                else:                    
                    amount = amount - decimal.Decimal(float(amount)* voucher.discount )
                context['amount']  = amount
                context['total_amount'] = amount +shipping_amount             

    
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Sản phẩm đã được xóa trong giỏ hàng")
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
    if(not request.GET.get('address')):
        messages.error(request, "Bạn không có địa chỉ giao hàng!")
    user = request.user
    total_amount = request.GET.get('total_amount')
    code = request.GET.get('voucher')
    
    address_id = request.GET.get('address')
    address = get_object_or_404(Address, id=address_id)
    content=""  
    title = "Bạn đã đặt hàng thành công " 
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    invoice = Invoice(user=user,price=total_amount)
    invoice.save()
    if code !="": 
            voucher = Voucher.objects.get(code=code)
            uservoucher =UserVoucher.objects.get(voucher=voucher,user=user)
            uservoucher.count=uservoucher.count+1
            uservoucher.save()
    for c in cart:
        title = title + str(c.product.title)+", "
        order = Order(user=user, address=address, product=c.product, quantity=c.quantity,ordered_date=invoice.ordered_date)
        order.save()
        invoice.order.add(order)
        invoice.save()
        c.delete()
    # Notification
    if request.method == 'GET':
        title=title[:-2] 
        slug = ""
        if len(title)>70:  
            i=70          
            while title[i] != " ":
                i=i-1
            content=title[:i]+" ..."
        else:
            content=title
        Notification(user=user,slug=slug, content =content ,type=0).save()
    return redirect('store:orders')

@login_required
def checkout_test(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    tong = request.GET.get('total_amount')
    content=""  
    title = "Bạn đã đặt hàng thành công "
    code = request.GET.get('voucher')
    print(tong)
    print(type(tong))
    price = decimal.Decimal(float(tong))   
    invoice = Invoice(user=user,price=price )
    if request.method == 'POST':
        locality = request.POST.get('locality', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        if(locality and city and state):
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            user = request.user
            # Get all the products of User in Cart
            cart = Cart.objects.filter(user=user)
            invoice.save()
            if code !="": 
                voucher = Voucher.objects.get(code=code)
                uservoucher =UserVoucher.objects.get(voucher=voucher,user=user)
                uservoucher.count=uservoucher.count+1
                uservoucher.save()
            for c in cart:
                title = title + str(c.product.title)+", "
                order = Order(user=user, address=reg, product=c.product, quantity=c.quantity,ordered_date=invoice.ordered_date)
                order.save()
                invoice.order.add(order)
                invoice.save()
                c.delete()
            title=title[:-2] 
            slug = ""
            if len(title)>70:  
                i=70          
                while title[i] != " ":
                    i=i-1
                content=title[:i]+" ..."
            else:
                content=title
            Notification(user=user,slug=slug, content =content ,type=0).save()
            return redirect('store:orders')
        else:
            messages.error(request, "Địa chỉ của bạn đang để trống!")
    context = {
        'user' : user,
        'cart' : cart,
        'tong' : tong,
    }
    # Notification
    return render(request, 'store/checkout.html',context)

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

        if(Favorite.objects.filter(user=user,product=product)): #tồn tại like rồi
            Notification.objects.filter(user=user,slug=product.slug,type=1).delete()
            Favorite.objects.filter(user=user,product=product).delete()
            product.likes -= 1
            product.user_likes.remove(user)
            product.save()
        else:
            Notification(user=user,slug=slug, content =content ,type=1).save()
            Favorite(user=user,product=product).save()
            product.likes += 1
            product.user_likes.add(user)
            product.save()
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

        if(Favorite.objects.filter(user=user,product=product)): #tồn tại like rồi
            Notification.objects.filter(user=user,slug=product.slug,type=1).delete()
            Favorite.objects.filter(user=user,product=product).delete()
            product.likes -= 1
            product.user_likes.remove(user)
            product.save()
        else:
            Notification(user=user,slug=slug, content =content ,type=1).save()
            Favorite(user=user,product=product).save()
            product.likes += 1
            product.user_likes.add(user)
            product.save()
    return redirect('store:category-products',cate_slug) 

@login_required
def add_notifi_like_p(request):
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
        if(Favorite.objects.filter(user=user,product=product)): #tồn tại like rồi
            Notification.objects.filter(user=user,slug=product.slug,type=1).delete()
            Favorite.objects.filter(user=user,product=product).delete()
            product.likes -= 1
            product.user_likes.remove(user)
            product.save()
        else:
            Notification(user=user,slug=slug, content =content ,type=1).save()
            Favorite(user=user,product=product).save()
            product.likes += 1
            product.user_likes.add(user)
            product.save()
    return redirect('store:product-detail',product.slug) 
    
@login_required
def add_notifi_like_rp(request):
    user = request.user
    product_id = request.GET.get('related_prod_id')
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
        if(Favorite.objects.filter(user=user,product=product)): #tồn tại like rồi
            Notification.objects.filter(user=user,slug=product.slug,type=1).delete()
            Favorite.objects.filter(user=user,product=product).delete()
            product.likes -= 1
            product.user_likes.remove(user)
            product.save()
        else:
            Notification(user=user,slug=slug, content =content ,type=1).save()
            Favorite(user=user,product=product).save()
            product.likes += 1
            product.user_likes.add(user)
            product.save()
    return redirect('store:product-detail',product.slug) 


@login_required
def orders(request):    
    user = request.user
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    order = ['Pending', 'Accepted', 'Packed','On The Way','Delivered','Cancelled']
    order = {key: i for i, key in enumerate(order)}
    ordered_sections = sorted(all_orders, key=lambda all_orders: order.get(all_orders.status, 0))   
    return render(request, 'store/orders.html', {'orders': ordered_sections})

@login_required
def billing(request): 
    billing = [1, 2]   
    context = {'billings':billing}
    return render(request, 'store/billing.html',context)


@login_required
def purchase_orders(request):
    all_orders = Order.objects.filter(user=request.user,status='Delivered').order_by('-ordered_date')
    return render(request, 'store/purchase_orders.html', {'orders': all_orders})
@login_required
def invoice(request): 
    billing = Invoice.objects.filter(user=request.user).order_by('-ordered_date')
    context = {'billings':billing}
    return render(request, 'store/invoice.html',context)
@login_required
def like_products(request):
    user = request.user
    favorites=Favorite.objects.filter(user=user)
    context={
        'favorites':favorites,
    }
    return render(request, 'store/like_products.html',context)

def shop(request):
    return render(request, 'store/shop.html')

def test(request):
    return render(request, 'store/test.html')

@login_required
def remove_like(request, favorite_id):
    user = request.user
    if request.method == 'GET':
        c = get_object_or_404(Favorite, id=favorite_id)
        nameproduct = c.product.title
        product = c.product
        product.likes -= 1
        product.user_likes.remove(user)
        product.save()
        c.delete()
        messages.success(request, "Bạn đã bỏ thích sản phẩm "+nameproduct)
    return redirect('store:like-products')
class SearchView(ListView):
    model = Product
    template_name = 'store/search.html'
    context_object_name = 'all_search_results'

    def get_queryset(self):
        result = super(SearchView, self).get_queryset()
        query = self.request.GET.get('query')
        if query:
            postresult = Product.objects.filter(Q(title__icontains=query)  | Q(category__title__icontains=query )|Q(slug__icontains=query ))
            result = postresult
        else:
            result = None
        return result



