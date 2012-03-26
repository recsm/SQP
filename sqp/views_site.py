
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect

from sqp import forms

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
            login(request, login_user)
            return HttpResponseRedirect('/loadui/')
    else:
        # neither POST nor GET with key
        form = forms.RegistrationForm() 
    
    return render_to_response('sqp/account_register.html',
                             {'form': form},
                               context_instance=RequestContext(request))
    

@login_required
def logout(request):
    
    "Logs out the user and displays 'You are logged out' message."
    from django.contrib.auth import logout
    logout(request)
    
    return HttpResponseRedirect('/')