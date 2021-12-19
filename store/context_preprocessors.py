from .models import Category, Cart, Notification



def store_menu(request):
    categories = Category.objects.filter(is_active=True)
    context = {
        'categories_menu': categories,
    }
    return context

def notification_list(request):    
    user = request.user
    notification = Notification.objects.filter(user=user)[:8]
    context = {
        'notification_list': notification,
    }  
    return context

def cart_menu(request):
    if request.user.is_authenticated:
        cart_items= Cart.objects.filter(user=request.user)
        context = {
            'cart_items': cart_items,
        }
    else:
        context = {}
    return context