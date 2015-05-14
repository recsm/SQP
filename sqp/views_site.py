
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.mail import EmailMultiAlternatives
from sqp import forms
from models import UserProfile
import hashlib, datetime, random
from django.template.loader import get_template
from email.MIMEImage import MIMEImage
import os
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


def introduction(request):
    return render_to_response('sqp/intro.html',
                              context_instance=RequestContext(request))

def enter_sqp_handler(request):
    """Redirect to either the login/register page or to the load ui if the user is logged in"""
    if request.user.is_authenticated():
        return HttpResponseRedirect('/loadui/',
                                    context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/accounts/login/', 
                                    context_instance=RequestContext(request))

def register(request):
    
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        
        if form.is_valid():
            form.save()
            #login user
            login_user = authenticate(username=request.POST.get('username'), password=request.POST.get('password1'))
            # Create and save user profile 
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]  
            activation_key = hashlib.sha1(salt+login_user.email).hexdigest()            
            key_expires = datetime.datetime.today() + datetime.timedelta(7) #7: days before the key expires                                                                                                                               
            UserProfile.create_profile_for_user(user=login_user, key=activation_key, 
                expires=key_expires)
            if login_user.is_active:
                login(request, login_user)
                return HttpResponseRedirect('/loadui/')
            else:
                # Send email with activation key
                data= Context({'username': login_user.username,
                               'activation_key': activation_key,
                               'first_name' : login_user.first_name,
                               'last_name' : login_user.last_name,})
                html_template = get_template('sqp/confirmation_email.html')
                
                from_email="sqp@upf.edu"
                email_subject = 'SQP account confirmation'
                text_content = "Congratulations %s %s, thanks for signing up. To activate your account, click this link http://local-sqp.upf.edu/accounts/confirm/%s/" % (login_user.first_name,login_user.last_name, activation_key)
                html_render = html_template.render(data)
                html_content= html_render.replace("activation_key_string", activation_key)

                msg = EmailMultiAlternatives(email_subject, text_content, from_email, [login_user.email])
                msg.attach_alternative(html_content, "text/html")

                msg.mixed_subtype = 'related'

                for f in ['emailImages/sqp.png', 'emailImages/activate_button.png']:
                    fp = open(os.path.join(os.path.dirname(__file__), f), 'rb')
                    msg_img = MIMEImage(fp.read())
                    fp.close()
                    msg_img.add_header('Content-ID', '<{}>'.format(f))
                    msg.attach(msg_img)

                msg.send()
                #send_mail(email_subject, email_body, 'myemail@example.com',[login_user.email], fail_silently=False)

            return HttpResponseRedirect('/accounts/register_success/')
    else:
        # neither POST nor GET with key
        form = forms.RegistrationForm() 
    
    return render_to_response('sqp/account_register.html',
                             {'form': form},
                               context_instance=RequestContext(request))
    

def register_success(request):
    return render_to_response('sqp/account_register_success.html',{},
                              context_instance=RequestContext(request))
    
def confirm(request, activation_key):
    #check if user is already logged in and if he is redirect him to some other url, e.g. home
    if request.user.is_authenticated():
        HttpResponseRedirect('/loadui/')

    # check if there is UserProfile which matches the activation key (if not then display 404)
    user_profile = get_object_or_404(UserProfile, activation_key=activation_key)

    #check if the activation key has expired, if it hase then render confirm_expired.html
    if user_profile.key_expires < datetime.datetime.now():
        return render_to_response('sqp/account_confirm_expired.html')
    #if the key hasn't expired save user and set him as active and render some template to confirm activation
    user = user_profile.user
    user.is_active = True
    user.save()
    #uncomment to automatically login the user
    #user.backend = 'django.contrib.auth.backends.ModelBackend'
    #login(request, user)
    return HttpResponseRedirect('/loadui/')
    

@login_required
def logout(request):
    
    "Logs out the user and displays 'You are logged out' message."
    from django.contrib.auth import logout
    logout(request)
    
    return HttpResponseRedirect('/')

@login_required
def switch_to_demo(request):
    
    "Logs out the user and logs in demo user."
    from django.contrib.auth import logout
    logout(request)
    login_user = authenticate(username='demouser', password='demouser')
    login(request, login_user)
    return HttpResponseRedirect('/loadui/')
    
