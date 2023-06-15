from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http  import HttpResponse
from .forms import *
from django.core.mail import send_mail
import random
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
 

# Create your views here.

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))



def index_function(request):
    try:
        u_obj = User.objects.get(username = request.session['username'])
        return render(request, 'index.html', {'userdata': u_obj})
    except:
        return render(request,'index.html')

def contact(request):
    try:
        u_obj = User.objects.get(username = request.session['username'])
        return render(request, 'contact.html', {'userdata': u_obj})
    except:
        return render(request,'contact.html')

def fashion(request):
    l1 = Blog.objects.filter(category = 'fashion')
    try:
        u_obj = User.objects.get(username = request.session['username'])
        return render(request, 'fashion.html', {'userdata': u_obj, 'fashion_blogs': l1})
    except:
        return render(request,'fashion.html', {'fashion_blogs': l1})
    
def food(request):
    l1 = Blog.objects.filter(category = 'food')

    try:
        u_obj = User.objects.get(username = request.session['username'])
        return render(request, 'food.html', {'userdata':u_obj, 'food_blogs': l1})
    except:
        return render(request, 'food.html', {'food_blogs': l1})
    
def lifestyle(request):
    l1 = Blog.objects.filter(category = 'lifestyle')

    try:
        u_obj = User.objects.get(username = request.session['username'])
        return render(request, 'lifestyle.html', {'userdata':u_obj, 'lifestyle_blogs': l1})
    except:
        return render(request, 'lifestyle.html', {'lifestyle_blogs': l1})

def beauty(request):
    l1 = Blog.objects.filter(category = 'beauty')
    try:
        u_obj = User.objects.get(username = request.session['username'])
        return render(request, 'beauty.html', {'userdata': u_obj, 'beauty_blogs': l1})
    except:
        return render(request,'beauty.html', {'beauty_blogs': l1})

def register(request):
    f_obj = UserForm()
    if request.method == 'GET':
        return render(request,'register.html',{'form': f_obj})
    else:
        try:
         u1 = User.objects.get(email = request.POST['email'])
         return render(request, 'register.html', {'msg': 'Email Already Exists', 'form': f_obj})
        except:
            try:
              User.objects.get(username = request.POST['username'])
              return render(request, 'register.html', {'msg': 'Username Already Exists', 'form': f_obj})
            except:
                global c_otp
                c_otp = random.randint(100000,999999)
                subject = "Email Verification"
                message = f"Hello!!\nYour OTP is {c_otp}"
                from_em = settings.EMAIL_HOST_USER
                rec = [request.POST['email']]
                send_mail(subject, message, from_em, rec)
                global user_data
                user_data = [
                  request.POST['first_name'],
                  request.POST['last_name'],
                  request.POST['email'],
                  request.POST['username'],
                  request.POST['password']]                    
                return render(request,'otp.html')
            
def otp(request):
    f_obj = UserForm()
    if int(request.POST['u_otp']) == c_otp:
        User.objects.create(
            first_name = user_data[0],
            last_name = user_data[1],
            email = user_data[2],
            username = user_data[3],
            password = user_data[4]
        )
        return render(request, 'register.html',{'form': f_obj, 'msg': 'Sucessfully Created'})
    else:
        return render(request, 'otp.html', {'msg': 'Wrong OTP, Enter again'})
              
    
def login(request):
    if request.method == 'POST':
        try:
          u_obj = User.objects.get(username = request.POST['username'])
          if u_obj.password == request.POST['password']:
              request.session['username'] = request.POST['username']
              return render(request, 'index.html', {'userdata': u_obj })
          else:
              return render(request, 'login.html',{'msg': 'Invalid Password'})
        except:
            return render(request, 'login.html' ,{'msg': 'Username Does Not Exist!!'})
            
    else:
        return render(request, 'login.html',{'msg': 'Welcome to Login Page'})
    

def logout(request):
    del request.session['username']
    return redirect('index')



def add_blog(request):
    b_form = BlogForm()
    try:
        u_obj = User.objects.get(username = request.session['username'])
        if request.method == 'GET':
                return render(request, 'add_blog.html', {'form': b_form, 'userdata': u_obj})
        else:
            #blog hai wo db mein entry karwana hai
            # template pe se data request.POST naam ki dictionary mein aata hai
            Blog.objects.create(
                title = request.POST['title'],
                des = request.POST['des'],
                pic = request.FILES['pic'],
                user = u_obj,   #user variable pe FOREIGNKEY field liya hai isiliye User ka obj dena hai
                category = request.POST['category']
            )
            
            return render(request, 'add_blog.html', {'form': b_form, 'userdata': u_obj, 'msg': 'Sucessfully Created'})
    except:
        return redirect('login')
    
    
def my_blogs(request):
    try:
        #u_obj wo hai jisne login kiya hai...
        u_obj = User.objects.get(username = request.session['username'])
        l1 = Blog.objects.filter(user = u_obj)
        return render(request, 'my_blogs.html', {'userdata': u_obj, 'user_blogs': l1})
    except:
        return redirect('login')
    
    
    
def single_blog(request,bid):
    b1 = Blog.objects.get(id = bid)
    f_list = Comment.objects.filter(blog = b1)
    try:
        u_obj = User.objects.get(username = request.session['username'])
        d_list = Donate.objects.filter(blog = b1)
        total_donations = 0
        for i in d_list:
            total_donations += i.amount
        return render(request, 'single_blog.html', {'userdata':u_obj, 'blog_data': b1, 'f_comments':f_list, 't_amount': total_donations})
    except:
        return render(request, 'single_blog.html', {'blog_data': b1,'f_comments':f_list, 't_amount': total_donations})

    
    
def add_comment(request, pk):  #pk mein wo blog ka id aa rha hai
    try:
        u_obj = User.objects.get(username = request.session['username'])
        b1 = Blog.objects.get(id = pk)
        Comment.objects.create(
            message = request.POST['troll'],
            user = u_obj,  #yahan pe foreign key field hone ki wajah se OBJ diya
            blog = b1 
        )
        f_list = Comment.objects.filter(blog = b1)
        return render(request, 'single_blog.html', {'userdata':u_obj, 'blog_data':b1,'f_comments':f_list})
    except:
        return redirect('login')
    
    
def donate(request, bid):
    try:
        u_obj = User.objects.get(username = request.session['username'])
        global b1
        b1 = Blog.objects.get(id = bid)
        return render(request, 'donate.html', {'userdata':u_obj,'blogdata':b1})
    except:
        return redirect('login')
    
    
    
    
#--------------------------COPIED CODE PAYMENT---------------------------------------#



def pay_init(request):
    global amount_rupee
    amount_rupee = int(request.POST['paymount'])
    currency = 'INR'
    amount = amount_rupee*100  # Rs. 200
 
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
 
    return render(request, 'payment.html', context=context)
 
 
 
 





@csrf_exempt
def paymenthandler(request):
 
    # only accept POST request.
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = amount_rupee * 100  # Rs. 200
                try:
 
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    u_obj = User.objects.get(username = request.session['username'])
                    Donate.objects.create(
                        user = u_obj,
                        blog = b1,
                        amount = amount_rupee
                    )
                    # render success page on successful caputre of payment
                    return render(request, 'success.html')
                except:
 
                    # if there is an error while capturing payment.
                    return render(request, 'fail.html')
            else:
 
                # if signature verification fails.
                return render(request, 'fail.html')
        except:
 
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()