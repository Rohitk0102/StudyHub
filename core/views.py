# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings 
import random
import datetime
from .forms import UserSignUpForm, EmailOTPForm
from .models import User
def generate_otp():
    """Generate a 6-digit OTP ensuring it's always exactly 6 digits"""
    otp = random.randint(100000, 999999)
    otp_str = str(otp)
    print(f"🔍 DEBUG: Generated OTP: '{otp_str}' (Type: {type(otp_str)}, Length: {len(otp_str)})")
    return otp_str
def send_otp_email(email, otp):
    subject = 'StudyHub - Your Login OTP'
    message = (
        f'Dear User,\n\n'
        f'Your One-Time Password (OTP) for EduStream login is: {otp}\n\n'
        f'This OTP is valid for 5 minutes. Please do not share it with anyone.\n\n'
        f'If you did not request this OTP, please ignore this email.'
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@edustream.com')
    recipient_list = [email]
    
    # ENHANCED TERMINAL OTP DISPLAY - matches README format exactly
    print("\n" + "="*60)
    print("🔐" + " OTP GENERATED FOR LOGIN ".center(56) + "🔐")
    print("="*60)
    print(f"👤 USER EMAIL: {email}")
    print(f"🔢 6-DIGIT OTP: {otp}")
    print(f"⏰ EXPIRES IN: 5 minutes")
    print(f"📋 COPY THIS OTP: {otp}")
    print(f"🖥️  ENTER IN BROWSER: {otp}")
    print("="*60)
    print("💡 INSTRUCTIONS:")
    print(f"   1. Copy the OTP above: {otp}")
    print("   2. Go to your browser OTP verification page")
    print("   3. Paste the OTP and submit")
    print("   4. Complete your login!")
    print("="*60)
    
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print(f"\n✅ OTP email sent successfully to {email}")
        print("\n" + "🔚" + " END OF OTP DISPLAY ".center(54, "=") + "🔚")
        print("📝 NOTE: Any logs below this line are Django HTTP requests, NOT the OTP!")
        print(f"🎯 Your OTP is: {otp} (in the large box above)")
        print("⚠️  Ignore HTTP response codes like '200 8053' - they are NOT the OTP!\n")
    except Exception as e:
        print(f"❌ Failed to send OTP email to {email}: {e}")
        print("🔧 Using terminal OTP display for development")
        print("\n" + "🔚" + " END OF OTP DISPLAY ".center(54, "=") + "🔚\n")
def signup_view(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'teacher':
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'There was an error with your submission. Please correct the highlighted fields.')
    else:
        form = UserSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
def login_view(request):
    """Handles user login and initiates 2FA OTP process."""
    if request.user.is_authenticated:
        if request.user.user_type == 'teacher':
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # User authenticated, now send OTP for 2FA
                print("\n" + "🚀" + " START OF OTP GENERATION ".center(54, "=") + "🚀")
                print("🚨 LOGIN DETECTED - TRIGGERING OTP GENERATION 🚨")
                print(f"👤 User: {user.username} ({user.email})")
                print("🔐 Starting 2FA OTP process...")
                
                otp = generate_otp()
                user.email_otp = otp
                user.otp_created_at = timezone.now()
                user.save()
                send_otp_email(user.email, otp)
                # Store user ID in session temporarily for OTP verification
                request.session['user_id_for_otp'] = user.id
                messages.info(request, 'An OTP has been sent to your email. Please check the terminal and enter it to complete your login.')
                return redirect('verify_otp')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def verify_otp_view(request):
    """Handles 2FA OTP verification."""
    user_id = request.session.get('user_id_for_otp')

    if not user_id:
        messages.error(request, 'Authentication session expired or invalid. Please log in again.')
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        # Clear the session key if user doesn't exist to prevent looping
        if 'user_id_for_otp' in request.session:
            del request.session['user_id_for_otp']
        return redirect('login')

    if request.method == 'POST':
        form = EmailOTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            if user.email_otp == entered_otp:
                # Check OTP expiry (5 minutes)
                if user.otp_created_at and (timezone.now() - user.otp_created_at) < datetime.timedelta(minutes=5):
                    # OTP is valid and not expired
                    user.email_otp = None  # Clear OTP after successful verification
                    user.otp_created_at = None
                    user.save()
                    login(request, user) 
                    del request.session['user_id_for_otp']
                    messages.success(request, 'Login successful!')
                    if user.user_type == 'teacher':
                        return redirect('teacher_dashboard')
                    else:
                        return redirect('student_dashboard')
                else:
                    messages.error(request, 'OTP expired. Please try logging in again.')
                    # Clear session key to force new login process
                    if 'user_id_for_otp' in request.session:
                        del request.session['user_id_for_otp']
                    return redirect('login')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = EmailOTPForm()

    return render(request, 'registration/verify_otp.html', {'form': form, 'email': user.email})


def logout_view(request):
    """Logs out the current user."""
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('home')
