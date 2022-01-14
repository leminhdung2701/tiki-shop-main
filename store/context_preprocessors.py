from operator import le
from .models import Category, Cart, Notification



def store_menu(request):
    categories = Category.objects.filter(is_active=True)
    context = {
        'categories_menu': categories,
    }
    return context

def notification_list(request):    
    if request.user.is_authenticated:
        user = request.user
        notification = Notification.objects.filter(user=user)
        t=1
        if len(notification)==0: t=0
        if len(notification)>=6:
            result = reversed(list(notification[len(notification)-6:len(notification)]))
            res = result
        else:
            res=reversed(list(notification))
        
        context = {
            'notification_list': res, 
            'length' :t,         
        }         
    else:
        context = {            
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