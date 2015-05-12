from django.conf.urls.defaults import *
from django.conf import settings 
from django.contrib import admin
from django.contrib.auth.decorators import login_required

admin.autodiscover()
urlpatterns = patterns('',)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),)

urlpatterns += patterns('',
     (r'^admin/', include(admin.site.urls)),
     (r'^grappelli/', include('grappelli.urls')),
)

#Site views
urlpatterns += patterns('sqp_project.sqp.views_site',
     (r'^admin/', include(admin.site.urls)),
     (r'^accounts/register/$', 'register'),
     (r'^accounts/switch/$', 'switch_to_demo'),
)

#Using the default django views for resetting and changing passwords
urlpatterns += patterns('django.contrib.auth.views',
     (r'^logout[/]*', 'logout', {'template_name': 'sqp/account_logout.html'}),
     (r'^accounts/login/$', 'login', {'template_name': 'sqp/account_login.html'}),
     (r'^accounts/logout/$', 'logout', {'template_name': 'sqp/account_logout.html'}),
     
     #For users who forgot their password to solicit a reset email
     (r'^accounts/password-reset/$', 'password_reset', 
                                          {'template_name': 'sqp/account_password_reset_form.html'}),
     #For users who forgot their password to after correctly requesting a reset email                                     
     (r'^accounts/password-reset/done/$', 'password_reset_done', 
                                          {'template_name': 'sqp/account_password_reset_done.html'}),
     #For users who forgot their password being referred from an email
     (r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm',
                                          {'template_name': 'sqp/account_password_reset_confirm.html'}),
     #For users who forgot their password when done after referral from the email
     (r'^accounts/reset/done/$', 'password_reset_complete',
                                          {'template_name': 'sqp/account_password_reset_complete.html'}),
     #For logged in existing users
     (r'^accounts/change-password/$',   'password_change',
                                          {'template_name': 'sqp/account_password_change_form.html'}),
     #For logged in existing users
     (r'^accounts/change-password/done/$', 'password_change_done',
                                          {'template_name': 'sqp/account_password_change_done.html'}),
    ) 

urlpatterns += patterns('sqp_project.sqp.views_ui',
     (r'^loadui[/]*', 'load_ui'),
     (r'^sqp/api/doc/$', 'service_live_doc'),
     (r'^sqp/api/doc/(?P<function_name>[a-z0-9A-Z_-]+)/(?P<method>[a-z1-9A-Z_-]+)*/$', 'service_live_doc'),  
     (r'^sqp/api/(?P<function_name>[a-z1-9A-Z_-]+)*', 'http_json_service'),
)


urlpatterns += patterns('sqp_project.sqp.views_site',
 (r'^[/]*$', 'introduction'),
 (r'^enter-sqp[/]*$', 'enter_sqp_handler'),
 )

urlpatterns += patterns('sqp_project.sqp.views',
     (r'^chars[/]', 'char_list'),
     (r'^sqp/compare/items[/]*', 'compare_items'),
     (r'^sqp/get_one_listed_question/(?P<question_id>[0-9]+)[/]*', 
            'get_one_listed_question'),
     (r'^sqp/copy_form/(?P<question_id>[0-9]+)[/]*', 'copy_form'),
     (r'^sqp/overview[/]*', 'codebook_overview'),
     (r'^sqp/codebook/(?P<charset_id>[0-9]+)[/]*', 'codebook'),
     (r'^sqp/charset/(?P<charset_id>[0-9]+)[/]*', 'view_charset'),
     (r'^sqp/change_characteristic_set/(?P<set_id>[0-9]+)[/]*',
                                   'set_characteristic_set'),
     (r'^sqp/logout[/]*', 'logout_view'),
     (r'^sqp/syllable_tool[/]*', 'syllable_tool'),
     (r'^sqp/get_num_syllables[/]*', 'get_num_syllables'),
     (r'^sqp/get_num_words[/]*', 'get_num_words'),
     (r'^sqp/get_num_sentences[/]*', 'get_num_sentences'),
     (r'^sqp/get_num_nouns[/]*', 'get_num_nouns'),
     (r'^sqp/code/(?P<question_id>[0-9]+)[/]*', 'code'),
     (r'^sqp/export[/]*', 'export_data'),
     (r'^sqp[/]*', 'list_questions'),
    
     
    
     (r'^json/questionlist[/]*', 'questionList_json'),
     (r'^json/question[/]*', 'question_json'),
     (r'^admin/logout[/]*', 'logout_view'),
   )
