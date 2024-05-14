from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django import forms

class Customer(models.Model):
    username = models.CharField(max_length=200, verbose_name='Tên đăng nhập', blank=False)
    email = models.EmailField(max_length=255, verbose_name='Email', blank=False)
    full_name = models.CharField(max_length=200, blank=False, verbose_name='Họ và tên')
    address = models.CharField(max_length=200, null=True, verbose_name='Địa chỉ')
    phone_number = models.CharField(max_length=200, null=True, verbose_name='Số điện thoại')
    created_at = models.DateField(default=timezone.now, verbose_name='Ngày tạo')

    def __str__(self):
        return self.full_name
    class Meta:
        verbose_name = 'Quản lý tài khoản'
        verbose_name_plural = 'Quản lý tài khoản'
    
class CreateCustomer(forms.ModelForm):
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Xác nhận mật khẩu', widget=forms.PasswordInput)

    class Meta:
        model = Customer
        fields = ('username', 'email', 'password1', 'password2', 'full_name', 'address', 'phone_number')

    def save(self, commit=True):
        customer = super().save(commit=False)
        user = User.objects.create_user(username=self.cleaned_data['username'], email=self.cleaned_data['email'], password=self.cleaned_data['password1'])
        customer.user = user
        if commit:
            customer.save()
        return customer

class Category(models.Model):
    category_name = models.CharField(max_length=200, null=True, verbose_name='Tên danh mục')
    created_Category = models.DateField(default=timezone.now, verbose_name='Ngày tạo')

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'Quản lý danh mục'
        verbose_name_plural = 'Quản lý danh mục'

class Product(models.Model):
    name = models.CharField(max_length=200, null=True, verbose_name='Tên sản phẩm')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Danh mục')
    price = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal('0'), verbose_name='Giá')
    description = models.TextField(max_length=2000, null=True, verbose_name='Mô tả')
    image = models.ImageField(null=True, blank=True, verbose_name='Hình ảnh')
    number_product = models.PositiveIntegerField(default=0, verbose_name='Số lượng sản phẩm')
    created_Product = models.DateField(default=timezone.now, verbose_name='Ngày tạo')
    
    @property
    def formatted_price(self):
        return '{:,.0f}'.format(self.price).replace(',', '.')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Quản lý sản phẩm'
        verbose_name_plural = 'Quản lý sản phẩm'

class Order(models.Model):
    STATUS_CHOICES = (
        ('packing', 'Đang gói hàng'),
        ('shipping', 'Đang vận chuyển'),
        ('delivering', 'Đang giao'),
        ('delivered', 'Đã giao'),
    )
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Khách hàng')
    status = models.CharField(max_length=200, null=True, choices=STATUS_CHOICES, verbose_name='Trạng thái')
    complete = models.BooleanField(default=False, blank=True, null=False, verbose_name='Đã hoàn thành')
    created_order = models.DateField(default=timezone.now, verbose_name='Ngày tạo')

    def __str__(self):
        return 'Đơn hàng số {}'.format(self.id)

    class Meta:
        verbose_name = 'Quản lý đơn hàng'
        verbose_name_plural = 'Quản lý đơn hàng'
    
    def get_total_price(self):
        total_price = sum(Decimal(item.product.price) * item.quantity for item in self.orderitem_set.all())
        return total_price

    def get_total_quantity(self):
        total_quantity = sum(item.quantity for item in self.orderitem_set.all())
        return total_quantity

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Đơn hàng')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Sản phẩm')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Số lượng')
    created_OrderItem = models.DateField(default=timezone.now, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Quản lý giỏ hàng'
        verbose_name_plural = 'Quản lý giỏ hàng'
    def __str__(self):
        return f"sản phẩm: {self.product} - số lượng: {self.quantity} - Đơn hàng: {self.order}"

class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Khách hàng')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Sản phẩm')
    rating = models.IntegerField(default=0, verbose_name='Đánh giá')
    comment = models.TextField(verbose_name='Bình luận')
    created_Review = models.DateField(default=timezone.now, verbose_name='Ngày tạo')

    def __str__(self):
        return self.comment
    class Meta:
        verbose_name = 'Quản lý nhận xét'
        verbose_name_plural = 'Quản lý nhận xét'

class Payment_VNPay(models.Model):
    order_id = models.CharField(max_length=255,default=0, null=True ,blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), verbose_name='Giá')
    order_desc = models.TextField(max_length=255, null=True, blank=True)
    vnp_TransactionNo = models.CharField(max_length=255, null=True, blank=True)
    vnp_ResponseCode = models.CharField(max_length=255, null=True, blank=True)
    product_list = models.TextField(null=True, blank=True, verbose_name='Danh sách sản phẩm')
    complete_pay = models.BooleanField(default=False, blank=True, null=False, verbose_name='Đã hoàn thành')
    def __str__(self):
        return str(self.order_id)
    class Meta:
        verbose_name = 'Hoá đơn'
        verbose_name_plural = 'Hoá đơn'    

class PaymentForm(forms.Form):
    order_id = forms.CharField(max_length=250)
    order_type = forms.CharField(max_length=20)
    amount = forms.IntegerField()
    order_desc = forms.CharField(max_length=100)
    bank_code = forms.CharField(max_length=20, required=False)
    language = forms.CharField(max_length=2)
