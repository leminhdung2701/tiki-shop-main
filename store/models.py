from django.db import models
from django.contrib.auth.models import User
from annoying.fields import AutoOneToOneField
# Create your models here.
class Address(models.Model):
    user = models.ForeignKey(User, verbose_name="Tên người dùng", on_delete=models.CASCADE)
    locality = models.CharField(max_length=150, verbose_name="Địa chỉ cụ thể")
    city = models.CharField(max_length=150, verbose_name="Huyện/Thành phố")
    state = models.CharField(max_length=150, verbose_name="Tỉnh")

    def __str__(self):
        return self.locality


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=55, verbose_name="Slug danh mục")
    description = models.TextField(blank=True, verbose_name="Miêu tả danh mục")
    category_image = models.ImageField(upload_to='category', blank=True, null=True, verbose_name="Hình ảnh danh mục")
    is_active = models.BooleanField(verbose_name="Có hoạt động?")
    is_featured = models.BooleanField(verbose_name="Có đề xuất?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('-created_at', )

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = AutoOneToOneField(User, primary_key=True,on_delete=models.CASCADE)
    phone = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default="avatar/anna.jpg", null=True, blank=True,upload_to='avatar')
class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=160, verbose_name="Slug sản phẩm")
    sku = models.CharField(max_length=255, unique=True, verbose_name="Mã sản phẩm")
    short_description = models.TextField(verbose_name="Miêu tả ngắn")
    detail_description = models.TextField(blank=True, null=True, verbose_name="Miêu tả chi tiết")
    product_image = models.ImageField(upload_to='product', blank=True, null=True, verbose_name="Hình ảnh sản phẩm")
    price = models.DecimalField(max_digits=8, decimal_places=2,verbose_name="Giá")
    category = models.ForeignKey(Category, verbose_name="Danh mục sản phẩm", on_delete=models.CASCADE)
    is_active = models.BooleanField(verbose_name="Có hoạt động?")
    is_featured = models.BooleanField(verbose_name="Có đề xuất?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật")

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created_at', )

    def __str__(self):
        return self.title

class Comment(models.Model):
    product = models.ForeignKey(Product, related_name="comments", on_delete=models.CASCADE)
    commenter_name = models.CharField(max_length=200)
    user = models.ForeignKey(User, related_name="users", on_delete=models.CASCADE)
    comment_body = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.product.title)

class Notification(models.Model):
    user = models.ForeignKey(User, verbose_name="tên người dùng", on_delete=models.CASCADE)
    type = models.PositiveIntegerField(default=1)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user)
        
class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name="tên người dùng", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="sản phẩm", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật")

    def __str__(self):
        return str(self.user)
    
    # Creating Model Property to calculate Quantity x Price
    @property
    def total_price(self):
        return self.quantity * self.product.price


STATUS_CHOICES = (
    ('Pending', 'Đang xử lý'),
    ('Accepted', 'Đã xác nhận đơn'),
    ('Packed', 'Đã đóng gói'),
    ('On The Way', 'Đang vận chuyển'),
    ('Delivered', 'Đã giao hàng'),
    ('Cancelled', 'Đã huỷ')
)

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="Tên tài khoản", on_delete=models.CASCADE)
    address = models.ForeignKey(Address, verbose_name="Địa chỉ", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Sản phẩm", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    ordered_date = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian đặt")
    status = models.CharField(
        choices=STATUS_CHOICES,
        verbose_name="Trạng thái",
        max_length=50,
        default="Đang xử lý"
        )
