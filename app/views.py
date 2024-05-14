
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from decimal import Decimal
import json
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect

def home(request):
    if request.user.is_authenticated:
        customer = request.user
        orders = Order.objects.filter(customer=customer, complete=False).exclude(status='delivered')
            
        # Khởi tạo giỏ hàng
        cart_items = []
            
        # Lặp qua tất cả các đơn hàng chưa hoàn thành của người dùng
        for order in orders:
            # Lấy tất cả các mục đơn hàng từ đơn hàng hiện tại
            order_items = order.orderitem_set.all()
                
            # Lặp qua từng mục đơn hàng và thêm vào giỏ hàng
            for item in order_items:
                cart_item = {
                    'product': item.product,
                    'quantity': item.quantity,
                    'price': "{:,.0f}".format(item.product.price),
                    'total_price': item.quantity * item.product.price
                }
                cart_items.append(cart_item)
            
        total_price = sum(item['total_price'] for item in cart_items)
        total_quantity = sum(item['quantity'] for item in cart_items)
        total_price_formatted = "{:,.0f}".format(total_price)
    else:
        total_quantity = 0  # Nếu người dùng không đăng nhập, số sản phẩm trong giỏ hàng sẽ là 0
        total_price_formatted = 0

    product = Product.objects.all()
    category = Category.objects.all()
    context={'products': product, 'categories': category, 'total_quantity': total_quantity}
    return render(request,'app/home.html',context)

@login_required
def cart(request):
    category = Category.objects.all()
    try:
        if request.user.is_authenticated:
            customer = request.user
            orders = Order.objects.filter(customer=customer, complete=False).exclude(status='delivered')
            
            # Khởi tạo giỏ hàng
            cart_items = []
            
            # Lặp qua tất cả các đơn hàng chưa hoàn thành của người dùng
            for order in orders:
                # Lấy tất cả các mục đơn hàng từ đơn hàng hiện tại
                order_items = order.orderitem_set.all()
               
                for item in order_items:
                    cart_item = {
                        'product': item.product,
                        'quantity': item.quantity,
                        'price': "{:,.0f}".format(item.product.price),
                        'total_price': item.quantity * item.product.price,
                    }
                    cart_items.append(cart_item)
            
            total_price = sum(item['total_price'] for item in cart_items)
            total_quantity = sum(item['quantity'] for item in cart_items)
            total_price_formatted = "{:,.0f}".format(total_price)
            
            context = {
                'items': cart_items,
                'total_price': total_price_formatted,
                'total_quantity': total_quantity,
                'categories': category
            }
            
            # Kiểm tra xem giỏ hàng có sản phẩm không
            if cart_items:
                context['order'] = None
                return render(request, 'app/cart.html', context)
            else:
                product = Product.objects.all()
                context1={'products': product}
                return render(request, 'app/home.html', context1)  # Trả về trang yêu cầu mua sản phẩm mới
            
        else:
            return HttpResponse("Bạn cần đăng nhập để xem giỏ hàng của mình.")
    except Customer.DoesNotExist:
        return HttpResponse("Bạn cần đăng nhập để xem giỏ hàng của mình.")

@login_required
def checkout(request):
    category = Category.objects.all()
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment-method')
        if payment_method == 'direct':
            # Nếu người dùng chọn thanh toán trực tiếp, trừ số lượng sản phẩm và chuyển hướng đến trang chủ
            reduce_product_quantity(request)
            return redirect('home')
        elif payment_method == 'online':    
            # Nếu người dùng chọn thanh toán online, chuyển hướng đến trang thanh toán
            return redirect('payment')

    # Xử lý khi người dùng truy cập trang checkout trực tiếp
    if request.user.is_authenticated:
        customer = request.user
        orders = Order.objects.filter(customer=customer, complete=False).exclude(status='delivered')
        
        # Khởi tạo giỏ hàng
        cart_items = []
        
        # Lặp qua tất cả các đơn hàng chưa hoàn thành của người dùng
        for order in orders:
            # Lấy tất cả các mục đơn hàng từ đơn hàng hiện tại
            order_items = order.orderitem_set.all()
            
            # Lặp qua từng mục đơn hàng và thêm vào giỏ hàng
            for item in order_items:
                cart_item = {
                    'product': item.product,
                    'quantity': item.quantity,
                    'price': "{:,.0f}".format(item.product.price),
                    'total_price': item.quantity * item.product.price,
                }
                cart_items.append(cart_item)
        
        total_price = sum(item['total_price'] for item in cart_items)
        total_quantity = sum(item['quantity'] for item in cart_items)
        total_price_formatted = "{:,.0f}".format(total_price)
        
        context = {
            'items': cart_items,
            'order': None,  # Bạn có thể muốn truyền một đối tượng order nếu cần thiết
            'total_price': total_price_formatted,
            'total_quantity': total_quantity,
            'categories': category,
            'total_price_value': total_price,  # Đẩy số tiền vào context
        }
        return render(request, 'app/checkout.html', context)
    else:
        return HttpResponse("Bạn cần đăng nhập để xem giỏ hàng của mình.")

def reduce_product_quantity(request):
    # Giảm số lượng sản phẩm trong kho
    customer = request.user
    orders = Order.objects.filter(customer=customer, complete=False).exclude(status='delivered')
    for order in orders:
        order_items = order.orderitem_set.all()
        for item in order_items:
            product = item.product
            quantity = item.quantity
            orders.update(status='packing', complete=True)
            product.number_product -= quantity
            product.save()

def register(request):
    category = Category.objects.all()
    form = CreateCustomer()
    if request.method == 'POST':
        form = CreateCustomer(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Tên người dùng đã tồn tại')
            else:
                form.save()
                messages.success(request, 'Đăng ký thành công')
                return redirect('home')  # Chuyển hướng đến trang chủ hoặc trang khác sau khi đăng ký thành công
        else:
            print(form.errors)  # In ra thông báo lỗi nếu có
    context = {'form': form,'categories': category}
    return render(request, 'app/register.html', context)

def loginPage(request):
    category = Category.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Đăng nhập thành công
            login(request, user)
            # Chuyển hướng đến trang sau khi đăng nhập thành công (nếu cần)
            return redirect('home')
        else:
            # Đăng nhập không thành công
            context = {'error_message': 'Tên người dùng hoặc mật khẩu không đúng'}
            return render(request, 'app/login.html', context)
    
    context = {'categories': category}
    return render(request, 'app/login.html', context)

def logoutPage(request):
    logout(request)
    return render(request, 'app/login.html')

def product_detail(request, product_id):
    category = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    context = {'product': product,'categories': category}
    return render(request, 'app/product_detail.html', context)

from django.db.models import Q

def searchPage(request):
    category = Category.objects.all()
    search_query = request.GET.get('search', '')
    sort_option = request.GET.get('sort', '')
    
    # Lọc sản phẩm phù hợp với từ khóa tìm kiếm
    products = Product.objects.filter(name__icontains=search_query)
    
    # Sắp xếp sản phẩm nếu có lựa chọn sắp xếp
    if sort_option == 'price_asc':
        products = products.order_by('price')
    elif sort_option == 'price_desc':
        products = products.order_by('-price')
    
    return render(request, 'app/searchPage.html', {'products': products, 'search_query': search_query,'categories': category}) 

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def updateItem(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        productId = data.get('productId')
        action = data.get('action')

        # Kiểm tra dữ liệu đầu vào
        if productId is None or action not in ['add', 'remove']:
            return JsonResponse({'error': 'Dữ liệu không hợp lệ'}, status=400)

        try:
            product = Product.objects.get(id=productId)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Sản phẩm không tồn tại'}, status=404)

        # Xác định người dùng hiện tại
        customer = request.user if request.user.is_authenticated else None

        # Tìm hoặc tạo mới đơn hàng cho người dùng hiện tại
        order, created = Order.objects.get_or_create(customer=customer, status='hoàn thành')

        # Tìm hoặc tạo mới mục đơn hàng cho sản phẩm này
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        # Cập nhật số lượng của mục đơn hàng dựa trên hành động
        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1

            # Xóa mục đơn hàng nếu số lượng là 0
            if orderItem.quantity <= 0:
                orderItem.delete()

        # Lưu lại mục đơn hàng
        orderItem.save()

        # Kiểm tra xem có còn bất kỳ mục đơn hàng nào khác trong đơn hàng hay không
        if not order.orderitem_set.exists():
            order.delete()

        return JsonResponse({'message': 'Cập nhật giỏ hàng thành công'}, status=200)
    else:
        return JsonResponse({'error': 'Yêu cầu không hợp lệ'}, status=400)
    
def product_category(request, category_name):
    # Lấy danh mục từ tên được truyền vào
    category = get_object_or_404(Category, category_name=category_name)
    # Lọc sản phẩm dựa trên danh mục đã chọn
    products = Product.objects.filter(category=category)
    # Lấy tất cả các danh mục
    all_categories = Category.objects.all()
    context = {
        'products': products,
        'selected_category': category,
        'categories': all_categories
    }
    return render(request, 'app/product_category.html', context)
@login_required
def manage_user(request):
    # Lấy đối tượng Customer dựa trên username của người dùng hiện tại
    customer = get_object_or_404(Customer, username=request.user.username)
    context = {
        'customer': customer
    }
    return render(request, 'app/manage_user.html', context)

import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import random
import requests
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import unquote

from app.models import PaymentForm
from app.vnpay import vnpay


def index(request):
    return render(request, "payment/index.html", {"title": "Danh sách demo"})


def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def payment(request):
    context = {}
    # Xử lý khi người dùng truy cập trang checkout trực tiếp
    if request.user.is_authenticated:
        customer = request.user
        orders = Order.objects.filter(customer=customer, complete=False).exclude(status='delivered')
        
        # Khởi tạo giỏ hàng
        cart_items = []
        
        # Lặp qua tất cả các đơn hàng chưa hoàn thành của người dùng
        for order in orders:
            # Lấy tất cả các mục đơn hàng từ đơn hàng hiện tại
            order_items = order.orderitem_set.all()
            
            # Lặp qua từng mục đơn hàng và thêm vào giỏ hàng
            for item in order_items:
                cart_item = {
                    'product': item.product,
                    'quantity': item.quantity,
                    'price': "{:,.0f}".format(item.product.price),
                    'total_price': item.quantity * item.product.price,
                }
                cart_items.append(cart_item)
        
        total_price = sum(item['total_price'] for item in cart_items)
        total_quantity = sum(item['quantity'] for item in cart_items)
        total_price_formatted = "{:,.0f}".format(total_price)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            order_id = form.cleaned_data['order_id']
            amount = total_price
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            amount = int(amount)
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            
            # Check language, default: vn
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
            
            # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            
            return redirect(vnpay_payment_url)  # Redirect to VNPAY payment URL
        else:
            # Nếu form không hợp lệ, hiển thị thông báo lỗi
            messages.error(request, 'Đã xảy ra lỗi. Vui lòng kiểm tra lại thông tin thanh toán.')
            context['form'] = form
            
    else:
        form = PaymentForm()  # Tạo một instance của PaymentForm để hiển thị cho người dùng
        context = {
            'form': form,
            'total_price' : total_price
        }

    return render(request, "payment/payment.html", context)


def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result


import logging

from django.db import transaction

@transaction.atomic
def payment_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = Decimal(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        if request.user.is_authenticated:
            customer = request.user
            orders = Order.objects.filter(customer=customer, complete=False).exclude(status='delivered')
        
        # Khởi tạo giỏ hàng
        cart_items = []
        
        # Lặp qua tất cả các đơn hàng chưa hoàn thành của người dùng
        for order in orders:
            # Lấy tất cả các mục đơn hàng từ đơn hàng hiện tại
            order_items = order.orderitem_set.all()
            
            # Lặp qua từng mục đơn hàng và thêm vào giỏ hàng
            for item in order_items:
                cart_item = {
                    'product': item.product,
                    'quantity': item.quantity,
                    'price': "{:,.0f}".format(item.product.price),
                    'total_price': item.quantity * item.product.price,
                }
                cart_items.append(cart_item)
        # Lấy danh sách sản phẩm từ request
        product_list = ""
        for key, value in inputData.items():
            if key.startswith('product_'):
                product_name = key.replace('product_', '')
                quantity = value
                product_list += f"{product_name} - {quantity}\n"

        # Validate the response
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            payment_vnpay = Payment_VNPay.objects.create(
                order_id=order_id,
                amount=amount,
                order_desc=order_desc,
                vnp_TransactionNo=vnp_TransactionNo,
                vnp_ResponseCode=vnp_ResponseCode,
                product_list=product_list  # Lưu danh sách sản phẩm vào hoá đơn
            )
            if vnp_ResponseCode == "00":
                payment_vnpay.complete_pay = True
                payment_vnpay.save()
                reduce_product_quantity(request)
            return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                                   "result": "Thành công", "order_id": order_id,
                                                                   "amount": amount,
                                                                   "order_desc": order_desc,
                                                                   "vnp_TransactionNo": vnp_TransactionNo,
                                                                   "vnp_ResponseCode": vnp_ResponseCode})
        else:
            return render(request, "payment/payment_return.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id,
                           "amount": amount,
                           "order_desc": order_desc,
                           "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán", "result": ""})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

n = random.randint(10**11, 10**12 - 1)
n_str = str(n)
while len(n_str) < 12:
    n_str = '0' + n_str


def query(request):
    if request.method == 'GET':
        return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_Version = '2.1.0'

    vnp_RequestId = n_str
    vnp_Command = 'querydr'
    vnp_TxnRef = request.POST['order_id']
    vnp_OrderInfo = 'kiem tra gd'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode,
        vnp_TxnRef, vnp_TransactionDate, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch", "response_json": response_json})

def refund(request):
    if request.method == 'GET':
        return render(request, "payment/refund.html", {"title": "Hoàn tiền giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_RequestId = n_str
    vnp_Version = '2.1.0'
    vnp_Command = 'refund'
    vnp_TransactionType = request.POST['TransactionType']
    vnp_TxnRef = request.POST['order_id']
    vnp_Amount = request.POST['amount']
    vnp_OrderInfo = request.POST['order_desc']
    vnp_TransactionNo = '0'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_CreateBy = 'user01'
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, vnp_TransactionType, vnp_TxnRef,
        vnp_Amount, vnp_TransactionNo, vnp_TransactionDate, vnp_CreateBy, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_Amount": vnp_Amount,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_TransactionType": vnp_TransactionType,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_CreateBy": vnp_CreateBy,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/refund.html", {"title": "Kết quả hoàn tiền giao dịch", "response_json": response_json})