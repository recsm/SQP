#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin, TabularInline
from sqp_project.sqp.models import *
from django.shortcuts import render_to_response
from django import template
from django.contrib.admin import helpers

from django.contrib.admin.options import csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.contrib.admin.util import unquote,get_deleted_objects
from django.utils.html import escape
from django.db import transaction, router
from django.http import Http404,  HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper


admin.site.register(Widget)

class ValidationRuleAdmin(ModelAdmin):
    list_display = ('name','failure_message', 'type', 'rule')
    search_fields = ('name', 'failure_message')
admin.site.register(ValidationRule,  ValidationRuleAdmin)


class LabelInline(TabularInline):
    model = Label
    extra = 5


class CharacteristicAdmin(ModelAdmin):
    list_display = ('name', 'short_name', 'widget', 'suggestion', 'auto_fill_suggestion', 'validations')
    search_fields = ('name', 'short_name')
    filter_horizontal = ('validation_rules',)
    inlines = (LabelInline, )
admin.site.register(Characteristic,  CharacteristicAdmin)

class CompletionAdmin(ModelAdmin):
    raw_id_fields = ("question",)
    list_display = ('question', 'question__country_prediction', 'user', 'characteristic_set','complete', 'authorized')
    exclude = ('predictions', 'potential_improvements', 'out_of_date' )
    list_filter = ('complete', 'authorized', 'user', 'characteristic_set', 'question__item__study', 'question__item', 'question__country','question__country_prediction', 'question__language')
    readonly_fields = ('complete', 'coding_list_tree', 'coding_list_all')
    actions = ['mark_as_authorized', 'mark_as_not_authorized', 'assign_codings_to_other_user']


    def assign_codings_to_other_user(self, request, queryset):
        
        #Make sure that there are some selected rows 
        n = queryset.count()
        if not n:
            return None
        
        existing_completions = []
        existing_codings = []
        error = False

        # The user has already confirmed the assignment
        # Do the change and return a None to display the change list view again.
        if request.POST.get('post') and request.POST.get('user_id'):
            """
            Loop through all objects the user has selected and call our custom function.
            """
            user = User.objects.get(pk=int(request.POST.get('user_id')))
            #Dry run to check
            
            for obj in queryset:
                try:
                    completion = Completion.objects.get(user=user,
                                                        question = obj.question,
                                                        characteristic_set = obj.characteristic_set)
                    existing_completions.append(completion)                    
                except Completion.DoesNotExist:
                    #ok, doesn't exist so we are ok to copy it
                    pass

                
                codings = Coding.objects.filter(user=user,
                                               question = obj.question)
                if codings.count():
                    for coding in codings:
                        existing_codings.append(coding)                    
               
            if len(existing_completions) != 0 or len(existing_codings) != 0:
                error = True

            if not error:
                for obj in queryset:

                    obj.assign_to_user(user)
                    obj.save()
                
                self.message_user(request, "%s completions were assigned correctly" % (len(queryset)))
                return None
            
        opts = self.model._meta
        app_label = opts.app_label
        
            
        context = { "title": 'Assign Codings to Other User',
                    'queryset': queryset,
                    "all_users" : User.objects.all(),
                    "opts": opts,
                    "root_path": self.admin_site.root_path,
                    "app_label": app_label,
                    'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
                    'error' : error,
                    'existing_completions' : existing_completions,
                    'existing_codings': existing_codings}
        
        return render_to_response('admin/assign_codings_to_other_user.html', context,
                                  context_instance=template.RequestContext(request))

    assign_codings_to_other_user.short_description = 'Assign Codings to Other User'

    def mark_as_authorized(self, request, queryset):
        
        #Make sure that there are some selected rows 
        n = queryset.count()
        if not n:
            return None

        for completion in queryset:
            completion.authorized = True
            completion.save()
    mark_as_authorized.short_description = 'Mark coding completion records as authorized'

    def mark_as_not_authorized(self, request, queryset):
        
        #Make sure that there are some selected rows 
        n = queryset.count()
        if not n:
            return None

        for completion in queryset:
            completion.authorized = False
            completion.save()
    mark_as_not_authorized.short_description = 'Mark coding completion records as NOT authorized'

admin.site.register(Completion, CompletionAdmin)

class BranchInline(admin.TabularInline):
    model = Branch
    extra = 3

class BranchAdmin(ModelAdmin):
    list_display = ('label', 'to_characteristic')
    search_fields = ('label__name', 'label__characteristic__name', 
            'to_characteristic__name')
#Commented out of admin to prevent changes to branches by non programmers
#since changing the branch structure can break the prediction engine    
#admin.site.register(Branch, BranchAdmin)


class StudyAdmin(ModelAdmin):
    filter_horizontal = ('coders',)
admin.site.register(Study, StudyAdmin)


class ItemAdmin(ModelAdmin):
    list_display = ('id', 'name', 'admin', 'concept', 'study')    
    search_fields = ('admin','name','concept',  )
    list_filter = ('study', )
admin.site.register(Item, ItemAdmin)


class LanguageAdmin(ModelAdmin):
    filter_horizontal = ('coders',)
admin.site.register(Language, LanguageAdmin)


class CountryAdmin(ModelAdmin):
    list_display = ('iso','name', )
    search_fields = ('iso', 'name',)

admin.site.register(Country, CountryAdmin)


class QuestionAdmin(ModelAdmin):
    list_display = ('item', 'language', 'country', 'country_prediction', 'created_by')
    list_filter = ('item__study', 'item', 'language', 'country', 'country_prediction')
    search = ('introduction_text', 'rfa_text', 'answer_text', 'created_by__name')

admin.site.register(Question, QuestionAdmin)

class UserQuestionAdmin(ModelAdmin):
    list_display = ('user', 'question', 'can_edit_text', 'can_edit_details')
    search_fields = ('user__username', 'question__item__name',)
    raw_id_fields = ("question",)
    list_filter  = ('user', 'can_edit_text', 'can_edit_details')
    
admin.site.register(UserQuestion, UserQuestionAdmin)


class ItemGroupAdmin(ModelAdmin):
    list_display = ('name', 'item_sample_list' )
    filter_horizontal = ('items',)
admin.site.register(ItemGroup, ItemGroupAdmin)


class QuestionBulkAssignmentsAdmin(ModelAdmin):
    list_display = ('item_group', 'country', 'language', 'assign_to_users', 'has_been_run', 'assignments_count', 'last_run_date', 'options')
    filter_horizontal = ('users',)
    readonly_fields = ('has_been_run', 'last_run_date', 'assignments')
    
    actions = ['run_assignments']
    
    #Add in some custom templates for deleting files
    delete_confirmation_template = 'admin/bulk_assignment_delete_confirmation.html'
    
    class Media:
        js = ['js/admin/CustomAdminRowActions.js']
    
    def get_actions(self, request):
        """We remove the default admin action of deleting, since we can't customize
           the output to inform on questions that will be deleted"""
        actions = super(QuestionBulkAssignmentsAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
    
    def delete_view(self, request, object_id, extra_context=None):
        """The delete view is customized to show which related questions will be deleted"""
        extra_context = extra_context or {}
        obj = QuestionBulkAssignments.objects.get(pk=object_id)
        extra_context['assignments_to_be_deleted'] = obj.assignments_to_be_deleted()
        # if request.POST is set, the user already confirmed deletion
        if request.POST:
            counter = obj.delete_assignments()
            if counter:
                self.message_user(request, u"%s assignment(s)  from bulk assignment '%s' were deleted" %(counter, obj))
        return super(QuestionBulkAssignmentsAdmin, self).delete_view(request, object_id, extra_context)
    
    def run_assignments(self, request, queryset):
        
        #Make sure that there are some selected rows 
        n = queryset.count()
        if not n:
            return None
        
        
        # The user has already confirmed the assignment
        # Do the creation and return a None to display the change list view again.
        if request.POST.get('post'):
            """
            Loop through all objects the user has selected and call our custom function.
            """
            
            for obj in queryset:
                obj.run_assignment()
                obj.save()
            
            self.message_user(request, "%s assignments were run correctly" % (len(queryset)))
            return None
            
        opts = self.model._meta
        app_label = opts.app_label
        
        assignments_exist_to_change = False
        missing_questions = False
        #Make sure there are questions to create
        for obj in queryset:
            if len(obj.question_list()['to_assign']) or len(obj.question_list()['changed_questions']) :
                assignments_exist_to_change = True
            if len(obj.question_list()['missing_questions']):
                missing_questions  = True
        
        show_submit_form = False
        
        if missing_questions:
            title = 'Unable to run assignment, not all required question records exist'        
        elif assignments_exist_to_change:
            title = 'Please confirm you would like to make the the following actions:'
            show_submit_form = True
        else:
            title = 'Nothing to do - No assignments would be changed.'
            
            
            
        context = { "title": title,
                    'queryset': queryset,
                    'show_submit_form' : show_submit_form, #if there are no assignment we hide the submit form
                    "opts": opts,
                    "root_path": self.admin_site.root_path,
                    "app_label": app_label,
                    'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME}
        
        return render_to_response('admin/bulk_assignment_confirm.html', context,
                                  context_instance=template.RequestContext(request))

    run_assignments.short_description = 'Run Selected Assignments'
    
admin.site.register(QuestionBulkAssignments, QuestionBulkAssignmentsAdmin)


class QuestionBulkCreationAdmin(ModelAdmin):
    list_display = ('item_group', 'country', 'language', 'copy_text_from_study','has_been_run', 'last_run_date', 'questions_created', 'created_questions_with_text', 'options')
    readonly_fields = ('has_been_run', 'last_run_date', 'created_questions')
    
    #Add in some custom templates for deleting files
    delete_confirmation_template = 'admin/bulk_question_delete_confirmation.html'
    
    actions = ['run_creations']
  
    class Media:
        js = ['js/admin/CustomAdminRowActions.js']

    def delete_view(self, request, object_id, extra_context=None):
        """The delete view is customized to show hich related questions will be deleted"""
        extra_context = extra_context or {}
        obj = QuestionBulkCreation.objects.get(pk=object_id)
        extra_context['questions_to_be_deleted'] = obj.questions_to_be_deleted()
        extra_context['questions_not_deleted'] = obj.questions_not_deleted()
        # if request.POST is set, the user already confirmed deletion
        if request.POST:
            counter = obj.delete_related_questions()
            if counter:
                self.message_user(request, u"%s questions created by task '%s' were deleted" %(counter, obj))
        return super(QuestionBulkCreationAdmin, self).delete_view(request, object_id, extra_context)
    
    
    def get_actions(self, request):
        """We remove the default admin action of deleting, since we can't customize
           the output to inform on questions that will be deleted"""
        actions = super(QuestionBulkCreationAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
    
    def run_creations(self, request, queryset):
         
        #Make sure that there are some selected rows 
        n = queryset.count()
        if not n:
            return None
        
        # The user has already confirmed the creation
        # Do the creation and return a None to display the change list view again.
        if request.POST.get('post'):
            for obj in queryset:
                obj.run_creation()
                obj.save()
                
            self.message_user(request, "%s creation task(s) were run correctly" % (len(queryset)))
            # Return None to display the change list page again.
            
            if obj.copied_questions_count != 0:
                self.message_user(request, "%s question(s) had text copied from study %s" % (obj.copied_questions_count, obj.copy_text_from_study.name))

            
            return None
        
        opts = self.model._meta
        app_label = opts.app_label
        
        questions_exist_to_create = False
        #Make sure there are questions to create
        for obj in queryset:
            if len(obj.question_list()['to_create']):
                questions_exist_to_create = True
                
        if questions_exist_to_create:
            title = 'Please confirm you would like to create the following questions:'
        else:
            title = 'Nothing to do - No additional questions would be created.'
            
        context = { "title": title,
                    'queryset': queryset,
                    'show_submit_form' :  questions_exist_to_create , #if there are no questions we hide the submit form
                    "opts": opts,
                    "root_path": self.admin_site.root_path,
                    "app_label": app_label,
                    'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME}
        
        return render_to_response('admin/bulk_question_confirm.html', context,
                                  context_instance=template.RequestContext(request))

    run_creations.short_description = 'Run Selected Creation Tasks'
    
   
    

    

admin.site.register(QuestionBulkCreation, QuestionBulkCreationAdmin)



class PredictionAdmin(ModelAdmin):
    list_display = ('paramater', 'view', 'function_name', 'key')


admin.site.register(Prediction, PredictionAdmin)



class ViewAdmin(ModelAdmin):
    list_display = ('name', 'expects', 'template', 'order')

admin.site.register(View, ViewAdmin)



class ParameterAdmin(ModelAdmin):
    list_display = ('name', 'description', 'order')

admin.site.register(Parameter, ParameterAdmin)




#admin.site.register(MTMMModelType)
#class MTMMModelVersionAdmin(ModelAdmin):
#    list_display = ('name','pattern')
#admin.site.register(MTMMModelVersion, MTMMModelVersionAdmin)

#admin.site.register(ParameterName)


#class CodingAdmin(ModelAdmin):
#    list_display = ('characteristic', 'question', 'choice')
#    list_filter = ('characteristic', 'question')

#admin.site.register(Coding, CodingAdmin)

class HistoryAdmin(ModelAdmin):
    list_display = ('action_description', 'actor', 'user_name', 'object_model', 'object_id', 'object_name', 'action_type', 'time', )
    list_filter  = ('object_model', 'actor', 'action_type',)

admin.site.register(History, HistoryAdmin)

class FAQAdmin(ModelAdmin):
    list_display = ('asker','question', 'answer', 'date_added', 'date_modified')
    search_fields = ('question', 'answer')
admin.site.register(FAQ,  FAQAdmin)

class UserProfileAdmin(ModelAdmin):
    list_display = ('user','default_characteristic_set',  'options')
    search_fields = ('user__email', 'user__username')
    list_filter  = ('default_characteristic_set',)
admin.site.register(UserProfile,  UserProfileAdmin)

class CodingChangeAdmin(ModelAdmin):
    list_display = ('change_summary','coding_change_group', 'question_id','coding_user', 'characteristic', 'processed', 'error_occured')
    search_fields = ('question_id','coding_user','characteristic','notes')
    
    actions = ['process_changes']
    
    class Media:
        js = ('/media/v2/admin/coding_change.js',)
 

    def process_changes(self, request, queryset):
        """
        Loop through all objects the user has selected and call our custom function.
        """
        errors = 0
        already_done = 0
        add_text = ''
        for obj in queryset:
            try:
                obj.process()
            except CodingChangeException:
                errors = errors + 1
            except CodingChangeAlreadyProcessed:
                already_done  = already_done +1
                
        if already_done >0:
            add_text = u"(%s changes were skipped because they were already processed)" % already_done
                
        self.message_user(request, "%s changes were processed with %s errors %s" % (len(queryset), errors, add_text))

    process_changes.short_description = 'Process Selected Changes'
    
    
admin.site.register(CodingChange, CodingChangeAdmin)

class CodingChangeGroupAdmin(ModelAdmin):
    list_display = ('name','description')
admin.site.register(CodingChangeGroup, CodingChangeGroupAdmin)