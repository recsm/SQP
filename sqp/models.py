#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy

from datetime import datetime

from sqp.views_ui_utils import get_branch, get_label

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core import serializers
from django.core.cache import cache
from django.conf import settings

import re # for validation
import os
from sqp_project.sqp.log import logging
from django.utils.safestring import mark_safe

from django.db.models.query import QuerySet
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete, m2m_changed

from django.db.models import Q

from django.template import Context
from django.template.loader import get_template

from sqp.fields import PickledObjectField

def dwrap(text):
    from textwrap import wrap
    return '\n'.join(wrap(text, width=12))

class History(models.Model):
    """Keeps track of basic history of changes made to objects."""

    ACTION_ITEM_CREATED   = 1
    ACTION_ITEM_DELETED   = 2
    ACTION_ITEM_CHANGED   = 3
    ACTION_ITEM_INDIRECT  = 4 #for example if an item was sent, submitted etc.

    ACTION_CHOICES = ((ACTION_ITEM_CREATED,  'Created'),
                      (ACTION_ITEM_DELETED,  'Deleted'),
                      (ACTION_ITEM_CHANGED,  'Changed'),
                      (ACTION_ITEM_INDIRECT, 'Indirect')
                      )

    #The user who made the change
    actor               = models.IntegerField()
    #the time the action happened
    time                = models.DateTimeField(auto_now=True)
    #the template for the action message
    action_description  = models.TextField()
    #the type of action
    action_type         = models.IntegerField(choices=ACTION_CHOICES)
    #the related object id
    object_id           = models.IntegerField()
    #the related object model
    object_model        = models.CharField(max_length=90)
    #the name of the object in case it was deleted
    object_name         = models.CharField(max_length=170)

    #a json serialization of the old values of the object (only if changed or deleted)
    previous_values = models.TextField()

    #get the db values of an object before it is going to be saved or deleted
    @staticmethod
    def get_db_values(model, object):
        return serializers.serialize('json', [model.objects.get(pk=object.id)])

    def user_name(self):
        try:
            user = User.objects.get(id=self.actor)
            return user
        except:
            return 'Unknown User'


class Widget(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name

class InvalidCode(Exception):
    """Raised if a choice made is not valid for the characteristic for
        some reason"""
    def __init__(self, choice, characteristic, reason):
        self.choice = choice
        self.characteristic = characteristic
        self.reason = reason
    def __str__(self):
        return """The choice %s is not valid for this characteristic because
            %s""" % (self.choice, self.reason)

class ValidationRule(models.Model):
    """A validation rule applied to a choice made for a Characteristic.
       May cause error or warning (force recoding or not)."""
    name = models.CharField(max_length = 16)
    rule = models.TextField('''Python code to validate. You can use "value",
         "question", "re".''')
    failure_message = models.TextField('''The message to be displayed if
        the rule evaluates to False.''')
    type = models.CharField(max_length = 7,
            choices = (('ERROR', 'Error'), ('WARNING', 'Warning')))

    def __unicode__(self): return self.name

    def validate(self, value, question, user):
        """Perform the actual validation given the question and the value
            to be validated."""

        valid = True
        try: exec(self.rule.replace('\r', '\n'))
        except Exception as e:
            print e
            pass # stuff is liable to go wrong, just ignore it
        return valid



class Characteristic(models.Model):
    """A characteristic of the Question, such as number of answer categories,
        social desirability, etc."""
    name    = models.CharField(max_length=100)
    short_name = models.CharField(max_length=32)
    desc    = models.TextField('Description, will appear as help text',
                blank=True, db_column = 'description')
    widget  = models.ForeignKey(Widget)
    suggestion = models.CharField(max_length=50, null=True, blank=True)
    auto_fill_suggestion = models.BooleanField(default=False, help_text="For new codings, auto fill the coding value in the ui with the suggested value")
    validation_rules = models.ManyToManyField(ValidationRule, null=True, blank=True)



    def __unicode__(self):
        return self.name

    def check_labels(self, warn=True):
        """Check that
            1. I have >= 1 label
            2country1 = forms.ModelSelect(). All labels have codes
            3. All label codes are unique for this characteristic."""

        labels = Label.objects.filter(characteristic = self)
        has_label = len(labels) > 0
        if warn and not has_label: print "%s does not have any label!" % self.name
        if not self.is_categorical(): return has_label
        codes = [lab.code for lab in labels if lab.code]
        all_codes = len(codes) is len(labels)
        if warn and not all_codes:
            print "%s's labels do not all have codes!" % self.name
        unique_codes = len(set(codes)) is len(codes)
        if warn and not unique_codes: print "%s's codes are not unique!" % self.name

        return (has_label and all_codes and unique_codes)

    def make_all_labels_branch_to(self, to_characteristic):
        "Utility function to create or update all labels to go to to_char"

        labels = self.label_set.all()
        for label in labels:
            (branch, created) = Branch.objects.get_or_create(label = label,
                    defaults = {'to_characteristic' : to_characteristic})
            if not created: branch.to_characteristic = to_characteristic
            branch.save()


    def get_variable_name(self):
        if self.short_name:
            return self.short_name
        return "char_%d" % self.id

    def is_categorical(self):
        """Determine whether this is an open question type characteristic
           or a categorical choice, based on the widget used."""
        return self.widget.name not in ('textfield', 'numeric', 'just_a_text')

    def is_valid_choice(self, choice, question, user):
        """Numeric choices selected be numeric. Number of abstract nouns
            should not exceed number of nouns, etc.

           choice: string w/ the choice to be validated
           raises InvalidCode exception if not valid"""
        rules = self.validation_rules.filter(type = 'ERROR')
        # TODO: handle warnings (large number of words etc)
        for rule in rules:
            print "CHECKING %s" % rule.name
            valid = rule.validate(choice, question, user)
            print "%s %s" % (rule.name, valid)
            if not valid:
                raise InvalidCode(choice, self, rule.failure_message)
        return True

    def validations(self):
        """A utility function to display validation rules inside the admin
           Returns a csv list of rule names
        """
        rules = []
        for rule in self.validation_rules.all():
            rules.append(rule.name)

        return ', '.join(rules)

    class Meta:
        ordering = ['name',]


class Label(models.Model):
    """A label is an answer option, something like yes/no, a bit/a lot.

        name:    the text of the label
        code:    the numeric or character code used in the datafile
                 for this choice.
        compute: a boolean indicating whether this label should be displayed
                 as a choice or is only used to determine skipping rules (see below)
        characteristic: The label belongs to exactly one characteristic.

        If the parent Characteristic is not a categorical choice, but for example
            numerical or text then the characteristic should
            also have at least one label with the 'compute' bit set to True.
            The name of this label will be parsed to
            determine skipping rules. The default 'True' will always
            skip to the 'next' characteristic. Other examples might be
            '{{value}} > 5' or '{{value}}.find("don't know") >= 0'.
        Compute Labels can also be used to provide defaults for numerical choices."""
    name = models.CharField(max_length=150, default='True')
    code = models.CharField(max_length=10, blank=True, null=True)
    characteristic = models.ForeignKey(Characteristic)
    compute = models.BooleanField(default=False)

    #Implement the cache for lookups by primary key
    #Note that the object cache is initialized later as Label.object_cache = ObjectCache(Label)
    #objects = ObjectCacheModelManager()

    def lookup_branch(self, charset_id):
        """Find the branch for this label and CharacteristicSet. Return None if not
            found (--> end of tree)"""
        branches = self.branch_set.filter(characteristicset = charset_id)
        if len(branches) > 0: return branches[0]
        else: return None

    def __unicode__(self):
        return "%s --> %s" % (self.characteristic.name, self.name)

    class Meta: # DebUG!
        ordering = ('characteristic__name', 'id')




class LabelInline(admin.TabularInline):
    model = Label
    extra = 5




class FakeBranch():
    "Ugly hack necessary to get the last coding in question.iter_branches"
    def __init__(self, coding):
        try: #might go wrong if faulty coding or no label for numeric char.
            if coding.characteristic.is_categorical():
                self.label = Label.objects.get(code = coding.choice,
                        characteristic = coding.characteristic)
            else: self.label = Label.objects.\
                             filter(characteristic=coding.characteristic)[0]
        except Exception, err:
            self.label = None
            logging.debug('Error while looking for Label: %s' % str(err))
        self.coding_choice = coding.choice
    def __unicode__(self):
        "Fake Branch for %s with coding %s." % (self.label.characteristic,
                self.coding_choice)

class Branch(models.Model):
    """ A branch is a rule that determines which label makes
        which Characteristic come next.

        label: the label (linked to an _originating_ Characteristic).
        to_characteristic: the Characteristic this label will take you to.

        Branches are used to define CharacteristicSets.
        See also Label."""
    label =  models.ForeignKey(Label)
    to_characteristic = models.ForeignKey(Characteristic)

    #Implement the cache for lookups by primary key
    #Note that the object cache is initialized later such as Label.object_cache = ObjectCache(Label)
    #objects = ObjectCacheModelManager()

    def __unicode__(self):
        return "%s --> %s" % (unicode(self.label),
                              unicode(self.to_characteristic))

    class Meta:
        ordering = ('label__characteristic__name', 'label__id')

class BranchInline(admin.TabularInline):
    model = Branch
    extra = 3

class BranchAdmin(admin.ModelAdmin):
    list_display = ('label', 'to_characteristic')
    search_fields = ('label__name', 'label__characteristic__name',
            'to_characteristic__name')


class CharacteristicSet(models.Model):
    """A CharacteristicSet (CSet) defines a set of rules (Branches) for conducting
        the SQP interview. It can be assigned to coders so that only those coders
        can use this CharacteristicSet. Different CSets may contain the same
        Characteristics with different branching rules.
        Note that a branch for Question (the source node/Characteristic) should
        always be a part of a CSet.

        One can obtain a set() of all Characteristics that are reachable in principle
        from this CharacteristicSet by calling get_characteristics(). Note that it is
        not guaranteed that all these Characteristics will be reached."""
    name     = models.CharField(max_length=100)
    branches = models.ManyToManyField(Branch)
    coders   = models.ManyToManyField(User)

    class Meta:
        ordering = ['id',]

    def __unicode__(self):
        return self.name

    def slugname(self):
        "Version of name without spaces"
        return self.name.replace(' ', '_')

    def get_characteristics(self):
        """Returns a sorted list of all Characteristics reachable from this
            CharacteristicSet."""
        import operator
        chars = set(self.branches.values_list('to_characteristic__name',
                            'to_characteristic__short_name'))
        return sorted(chars, key=operator.itemgetter(1))

    def get_characteristic_dict(self):
        """Returns a dictionary of characteristics in this CSET with keys
           equal to the characteristic.id and values the characteristic.
           Reads all characteristics into memory, provides O(1) lookup of
           chars without additional database queries"""
        # chars INNER JOIN on branches --> requires DISTINCT
        print type(Characteristic)
        characteristics = Characteristic.objects.filter(\
                label__branch__characteristicset = self).select_related().distinct()
        chardict = {} # cache in dict for fast lookup
        for char in characteristics: chardict[char.id] = char
        return chardict
    
    def get_branch_dict(self):
        """Returns a dictionary of characteristics in this CSET with keys
           equal to the characteristic.id and values the characteristic.
           Reads all characteristics into memory, provides O(1) lookup of
           chars without additional database queries"""
        # chars INNER JOIN on branches --> requires DISTINCT
        branches = self.branches.all()
        branchdict = {} # cache in dict for fast lookup
        for branch in branches: branchdict[branch.id] = branch
        return branchdict

    def apply_to_tree(self, cur_char = None, apply_func=None, end_func=None,
            start_from='question', done = set()):
        """Walk all branches of the characteristic set and apply apply_func to each
           branch."""
        if not cur_char: # first time
            cur_char = Characteristic.objects.get(short_name__exact = start_from)
        labels = cur_char.label_set.all()
        done_chars = set()
        for label in labels:
            try:
                cur_branch = self.branches.get(label = label)
                # Avoid walking repeatedly down the same part of the tree when
                # different branches of the same node lead to the same characteristic
                # Note that done_chars is local to this instance of the function
                #   so it only avoids repeating to_chars from the same origin char.
                if (cur_branch.to_characteristic not in done_chars):
                    if apply_func: apply_func(cur_branch)
                    self.apply_to_tree(cur_char = cur_branch.to_characteristic,
                        apply_func = apply_func, end_func = end_func)
                    done_chars.add(cur_branch.to_characteristic)
            except Branch.DoesNotExist: # end of interview from this label
                if end_func: end_func(label)

    def apply_to_width(self, cur_char = None, apply_func=None, start_from='question',
            done = set(), done_chars= set()):
        """Sort of the same as before, but width first."""
        if not cur_char: # first time
            cur_char = Characteristic.objects.get(short_name__exact = start_from)
        labels = cur_char.label_set.all()

        for label in labels:
            try:
                cur_branch = self.branches.get(label = label)
                if (cur_branch.to_characteristic not in done_chars):
                    if apply_func: apply_func(cur_branch.to_characteristic)
                    done_chars.add(cur_branch.to_characteristic)
            except Branch.DoesNotExist: # end of interview from this label
                pass

        for label in labels:
            try:
                cur_branch = self.branches.get(label = label)
                if cur_branch not in done:
                    self.apply_to_width(cur_char = cur_branch.to_characteristic,
                        apply_func = apply_func, done=done, done_chars=done_chars)
                    done.add(cur_branch)
            except Branch.DoesNotExist: # end of interview from this label
                pass


    def to_dot(self, start_from='question'):
        """Output diagram in GraphViz dot language of this set."""
        graph = """digraph "%s" {\n\tgraph [rankdir = "TB"];""" % self.name
        graph += "\n\tratio = auto;"
        if start_from == 'question':
            graph += """\n\t"Question text" [shape = box];\n"""
        graph += """\n\t{rank = sink;
            "END" [style=filled, color=black, fontcolor=white, shape = box]; };\n"""

        # filled with strings for each branch and characteristic by apply_to_tree:
        glist = []
        done_branch = set() # keep track of branches drawn
        done_labels = set() # keep track of labels drawn

        def add_to_glist(branch):
            "Add a dot string for each branch and characteristic to the glist"
            # prevent double arrows for nodes below intro-available split:
            if not branch in done_branch:
                # The dot string for drawing a box with the char name:
                glist.append(""""%s" [label = "%s" shape = box
                        URL="/admin/sqp/characteristic/%d/"];""" % \
                  (branch.to_characteristic.name,
                   branch.to_characteristic.name,
                   branch.to_characteristic.id))
                # Dot string for arrow from one char to the next:
                glist.append(""""%s" -> "%s" [label = "%s",
                        URL="/admin/sqp/branch/%d/"];""" % \
                  (branch.label.characteristic.name,
                   branch.to_characteristic.name,
                   branch.label.name.replace('True', ''),
                   branch.id))
            done_branch.add(branch) # register this branch

        def end_node_found(label):
            "Add a dot string to signify the end of the interview "
            if not label in done_labels:
                glist.append(""""%s" -> "END" [label = "%s",
                        URL="/admin/sqp/branch/add/"];""" % \
                  (label.characteristic.name,
                   label.name.replace('True', '')))
                done_labels.add(label) # register this label

        # Call add_to_glist on all branches of this characteristic set:
        self.apply_to_tree(apply_func = add_to_glist, end_func=end_node_found,
                start_from = start_from)
        graph += '\n\t'.join(glist)
        graph += "\n}"

        return graph

    def to_graph(self, path = "/home/daob/webapps/django/sqp_project/media/img/sqp",
            type = "svg", cmd = "", start_from='question'):
        """Write graph in <type> format. Assumes graphviz is installed.
           Returns full filename of the graphics file written to."""
        outpath = os.path.join(path, '%s_graph.dot' % self.slugname())
        outfile = file(outpath, 'w')
        outfile.write(self.to_dot(start_from = start_from))
        outfile.close()
        graphics_path = "%s.%s" % (os.path.splitext(outpath)[0], type)
        os.system("dot -T%s %s %s > %s" % (type, cmd, outpath, graphics_path))
        return graphics_path


class Study(models.Model):
    name              = models.CharField(max_length=70)
    coders            = models.ManyToManyField(User, blank=True, help_text="Deprecated")
    created_by        = models.ForeignKey(User, blank=True, null=True, related_name="created_study_set")
    company           = models.CharField(max_length=70, null=True)
    year              = models.CharField(max_length=70, null=True)
    country           = models.CharField(max_length=70, null=True)

    def can_delete(self, user):

        #Users can only delete studies they created
        if self.created_by != user:
            return False

        #Test to see if there are any questions from this study not by this user
        if Question.objects.filter(Q(item__study = self),  ~Q(created_by=user)).count() :
            return False

        return True


    def can_access(self, user):

        """If a user can read or code this question"""
        #If the user is the created_by or this study is public then we return true
        if not self.created_by or (self.created_by == user or self.created_by.profile.is_trusted):
            return True

        #Default return false
        return False


    def can_edit(self, user):
        """If a user can edit this study"""
        #If the user is the created_by or this study we return true
        if self.created_by == user:
            return True

        #Default return false
        return False


    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',);

class Item(models.Model):
    name         = models.CharField(max_length=8)
    admin        = models.CharField(max_length=8, default='')
    concept      = models.CharField(max_length=300, default='')
    study        = models.ForeignKey(Study)
    admin_letter = models.CharField(max_length=8, blank=True, null=True)
    admin_number = models.IntegerField(blank=True, null=True)
    admin_subletter= models.CharField(max_length=8, blank=True, null=True)
    created_by   = models.ForeignKey(User, blank=True, null=True, related_name="created_item_set")

    #choices made of characteristics for this item
    #calc_choices = models.CharField(max_length=255, blank=True, null=True)

    #Mean for characteristic in item
    #calc_mean            = models.FloatField(blank=True, null=True)
    #Mode for characteristic in item
    #calc_mode            = models.CharField(blank=True, null=True, max_length=255)
    #sterr for characteristic in item
    #calc_sterr           = models.FloatField(blank=True, null=True)
    #stdev for characteristic in item
    #calc_stdev           = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return self.unique_name
    def main_or_supplementary(self):
        return (self.name.lower().find('test') == -1) and "main" or "supp"
    def _unique_name(self):
        ad = self.admin and self.admin + ". " or ''
        return("%s %s, %s" % (ad, self.name, self.study))
    unique_name = property(_unique_name)

    def code (self):
        return("%s%s" % (self.admin_letter, self.admin_number, self.admin_subletter))

    #Called before saving
    #Don't call save here, you will cause an infinite loop
    #This method is called before save by some script at the bottom of sqp/models.py
    def on_before_save(self):
        #Set the admin if none exists
        if not self.admin and (self.admin_letter and self.admin_number):
            self.admin = self.code();
        if re.match(r'^[A-Za-z]*[0-9]+[A-Za-z]*$', self.admin):
            letters=re.split('\d+', self.admin)
            self.admin_letter=letters[0]
            self.admin_number=filter(None,re.split('[A-Za-z]+',self.admin))[0]
            self.admin_subletter=letters[1]
        elif re.match(r'^[A-Za-z]*$',self.admin): #just letters
            self.admin_letter=self.admin
            self.admin_number=None
            self.admin_subletter=None
        else: # numbers letters numbers or whatever
            self.admin_letter=self.admin
            self.admin_number=None
            self.admin_subletter=None


    class Meta:
        ordering = ('study', 'admin_letter', 'admin_number', 'admin_subletter', 'id')


    def can_edit(self, user):

        """If a user can edit item description, item code, associated with this item"""
        #If created by this user we return true
        if self.created_by == user:
            return True

        #Check to see if this is a user owned item with the same name, with only
        #the user's own questions assigned to it. If so then the user
        #can change the item still and we don't create a new one.This is important
        #since it is required to enable the user change the description or admin for an existing item
        item_has_other_users_questions = Question.objects.filter(~Q(created_by=user), Q(item=self)).count()

        if not item_has_other_users_questions:
            return True

        return False


class Language(models.Model):
    name = models.CharField(max_length=100)
    iso =  models.CharField(max_length=3)
    iso2 =  models.CharField(max_length=2, null=True, blank=True)
    coders = models.ManyToManyField(User)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ('name',)


class Country(models.Model):
    iso       = models.CharField(max_length=2, primary_key=True)
    name      = models.CharField(max_length=80)
    iso_three = models.CharField(max_length=3, blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name',]


characteristic_trees = {}



class Question(models.Model):
    item     = models.ForeignKey(Item)
    language = models.ForeignKey(Language)
    country  = models.ForeignKey(Country)
    introduction_text = models.TextField(blank=True, null=True)
    rfa_text = models.TextField(blank=True, null=True)
    answer_text = models.TextField(blank=True, null=True)

    val     = models.FloatField(blank=True, null=True)
    val_lo  = models.FloatField(blank=True, null=True)
    val_hi  = models.FloatField(blank=True, null=True)
    valz    = models.FloatField(blank=True, null=True)
    valz_se = models.FloatField(blank=True, null=True)
    rel     = models.FloatField(blank=True, null=True)
    rel_lo  = models.FloatField(blank=True, null=True)
    rel_hi  = models.FloatField(blank=True, null=True)
    relz    = models.FloatField(blank=True, null=True)
    relz_se = models.FloatField(blank=True, null=True)

    created_by  = models.ForeignKey(User, blank=True, null=True, related_name="created_question_set")
    imported_from = models.CharField(null=True, blank=True, max_length=120)

    def has_text(self):
        return bool(self.introduction_text or self.rfa_text or self.answer_text)


    def can_edit_text(self, user):
        """If a user can edit the introduction_text, rfa_text, and answer_text"""
        #If the user is the created_by then we return true
        if self.created_by == user:
            return True
        #Otherwise we check for a many to many relationship with can_edit_text = True
        if self.userquestion_set.filter(user=user, can_edit_text=True).count():
            return True
        return False

    def can_edit_details(self, user):
        """If a user can edit the country, language, item, and study"""
        #If the user is the created_by then we return true
        if self.created_by == user:
            return True
        #Otherwise we check for a many to many relationship with can_edit_details = True
        if self.userquestion_set.filter(user=user, can_edit_details=True).count():
            return True
        return False

    def can_delete(self, user):
        #If the user is the created_by then we return true
        if self.created_by == user:
            return True
        #There is no can delete many to many
        return False

    def can_access(self, user):

        """If a user can read or code this question
        #If the user is the created_by then we return true
        #have a null created_by value
        if not self.created_by or (self.created_by == user or self.created_by.profile.is_trusted):
            return True

        #Otherwise we check for a many to many relationship
        #Any existing many to many relationship implies the question can be accessed by the user
        if self.userquestion_set.filter(user=user).count():
            return True

        #Default return false
        return False
        """

        return True

    def update_completion(self, request=None, user=None, for_charset=None):

        if user is None:
            user = request.user

        """Marks the question as completed or not by user in the database.
         Automatically updates all CharSets."""
        for charset in CharacteristicSet.objects.iterator():
            if for_charset is None or for_charset == charset:
                try:
                    complete = self.get_completeness(user, charset)  == 'completely-coded'
                    self.set_completion(user, for_charset, complete)

                except Exception, err:
                    print "Encountered an exception for charset %s and user %s: %s"\
                         % (str(charset), user, str(err))

    def set_completion(self, user, charset, complete, authorized=None):
       
        completion, created = Completion.objects.get_or_create(\
                   question = self, user=user,
                   characteristic_set = charset)
                
        #Mark this completion record as being up to date
        completion.complete = complete
        
        if authorized is not None:
            completion.authorized = authorized
            
        completion.out_of_date = False
        completion.save()

    def set_completion_out_of_date(self, user, for_charset=None):
        """Called by Coding.save(), this just invalidated our completion record for this question
           If for_charset is passed, we just set that charset as out of date
           Otherwise we set all charsets as out of date
        """

        missed_sets = []

        if for_charset is None:
            #Invalidate all completion objects when this coding was saved from the admin panel... or
            #somewhere else if that is possible
            completions = Completion.objects.filter(question=self, user=user)

            charsets = CharacteristicSet.objects.all()
            for cs in charsets:
                missed = True
                for complete in completions:
                    if complete.characteristic_set == cs:
                        missed = False
                        break
                if missed:
                    missed_sets.append(cs)

        else:
            completions = Completion.objects.filter(question=self, user=user, characteristic_set= for_charset)
            if len(completions) == 0:
                missed_sets.append(for_charset)


        for missed_charset in missed_sets:
            #The completion invalid record is important so we create it here.
            Completion.objects.get_or_create(\
               question = self, user=user,
               characteristic_set = missed_charset,
               out_of_date = True)

        for complete in completions:
            complete.out_of_date = True
            complete.predictions = None
            complete.save()



    def update_suggestions(self):
        """Update the range of suggestions for codings of this question
           called whenever the question is saved
        """

        from sqp_project.sqp import suggestions
        #The suggestions don't need a request now
        #Ideally the request argument should be deleted

        for char in Characteristic.objects.all():
            if char.suggestion:

                #print
                #print char.suggestion

                if char.suggestion not in dir(suggestions):
                    #print """Warning: for suggestion type %s no suggestion function was found in suggestions.py""" % char.suggestion
                    continue

                try:

                    suggestion_function = eval('suggestions.' + char.suggestion)

                    #Delete any old suggestions
                    coding_suggestions = CodingSuggestion.objects.filter(question=self, characteristic=char)
                    for cs in coding_suggestions:
                        cs.delete()

                    suggestion, explanation = suggestion_function (self, char)
                    #print "For %s suggestion is %s explained by %s" % (char.suggestion, suggestion, explanation)

                    coding_suggestion = CodingSuggestion.objects.get_or_create(question=self, characteristic=char)[0]
                    coding_suggestion.value = suggestion
                    coding_suggestion.explanation = explanation
                    coding_suggestion.save()

                except:
                    pass
                    #print 'Error %s' % err



    def get_codes(self, user, charset):
        codes = []

        for branch in self.iter_branches(user=user, charset=charset):
            try:
                if branch:
                    if str(branch.label.name) == 'True':
                        choice_text     = branch.coding_choice
                    else:
                        choice_text     = branch.label.name

                    characteristic      = branch.label.characteristic
                    choice              = branch.coding_choice

                    codes.append({'characteristic'   : characteristic,
                                  'short_name    '   : characteristic.short_name,
                                  'code'             : choice,
                                  'choice'           : choice_text,
                                                        })
            except Exception as e:
                pass


        return codes


    def iter_branches(self, request=None, user=None, charset=None, start='question'):
        """Not really an iterator anymore as an entire array is returned
           The last element is a branch for the last char if the interview is
                complete. Otherwise the last branch is None.
           You can safely use branch.label and branch.coding_choice. These and
            branch.label.characteristic will not result in additional db queries.

           The iterations stop when the end of the interview is reached or when
            an uncoded but needed characteristic is found.  """
        if not request: # Input checking
            if not user and charset:
                raise Exception('Should have either request or user & charset')
        else:
            user = request.user
            charset = CharacteristicSet.objects.get(pk = \
                request.session['characteristic_set'])
        
        try:
            tree = characteristic_trees[charset.id]
        except:
            #Trees have not been initialized yet, initialize them all here
            for cset in CharacteristicSet.objects.all():
                characteristic_trees[cset.id] = CharacteristicTree(cset)
            tree = characteristic_trees[charset.id]
                
        codes = Coding.objects.filter(question = self, user = user)
        return tree.iter_branches(codes)

            
  

    def get_previous_characteristic(self, request, characteristic,
            default='question'):
        """Given a question and characteristic, figure out which characteristic
            came before it."""
        prev_char = Characteristic.objects.get(short_name__exact = default)
        for branch in self.iter_branches(request = request):
            if branch:
                if characteristic == branch.label.characteristic: return prev_char
                prev_char =  branch.label.characteristic
        return prev_char

    def get_completeness(self, user, charset):
        """Returns the completeness status of the question for this coder
           and charset: 'Not coded', 'Partially coded', or 'Completely coded'.
           the return value is used in list_questions as a css class."""
        ncodings = Coding.objects.filter(question = self, user = user).count()
        if ncodings == 0: return 'not-coded'
        for branch in self.iter_branches(user=user, charset=charset): pass
        return branch and 'completely-coded' or 'partially-coded'


    def get_coding_for(self, characteristic_short_name, user):
        """Given characteristic and user, return the coding
            for that characteristic (if any) or None."""
        coding = Coding.objects.filter(question = self,
            characteristic__short_name__exact = characteristic_short_name,
            user = user)

        print characteristic_short_name

        return coding and coding[0] or None


    def save(self, *args, **kwargs):

        if 'create_suggestions' in kwargs.keys():
            create_suggestions = kwargs['create_suggestions']
            del kwargs['create_suggestions']
        else:
            create_suggestions = True
            
        super(Question,self).save(*args, **kwargs)


        #On save we update the suggestions for the question
        if create_suggestions == True:
            self.update_suggestions()


    class Meta:
        permissions = (('can_compare', 'Can create comparison report'),
        ('can_export', 'Can export codes to CSV'),)
        ordering = ('item__study', 'country', 'language',
                'item__admin_letter',
                'item__admin_number', 'item__id')
        permissions = (('can_compare', 'Can use SQP Compare'),
                ('can_export', 'Can export codings') )

    def __unicode__(self):
        return u'%s - %s %s' % (self.item, self.country, self.language)

#    def copy_codes(to_question, request):
#        """Handles copying of codes for question specified in request.POST
#           to codes of from_question. Returns a message describing what
#           happened."""
#        #Find the from_question using from_data, look for errors
#        try:
#            from_question = Question.objects.get(item = request.POST['item'],
#                country = request.POST['country'],
#                language = request.POST['language'])
#        except:
#            message = """Could not find a question corresponding to that combination
#                         of item, language, and country to copy from."""
#            message_class = "warning"
#            return message, message_class
#
#        copied = []
#        branch = None
#        try:
#            for branch in from_question.iter_branches(request = request):
#                (newcoding, created) = Coding.objects.get_or_create(\
#                                question=to_question,
#                                characteristic=branch.label.characteristic,
#                                user=request.user)
#                copied.append(branch.label.characteristic)
#                newcoding.choice = branch.coding_choice
#                newcoding.save()
#        except Exception, e:
#            message = "An error occurred trying to copy codes: %s" % (str(e))
#            message_class = "warning"
#        if branch:
#            message = """Copied %d codes from %s. Complete coding from
#            beginning to end. """ % (len(copied), from_question)
#            message_class = "success"
#        else:
#            message = """Copied %d codes from %s. The coding for the source
#              question is not complete.""" % (len(copied), from_question)
#            message_class = "success"
#
#        to_question.update_completion(request)
#
#        return message, message_class
#
#    def check_codings_complete(self, request):
#        """Given the request.user, walk the tree from the beginning to
#           see if all codings have been made. If so return True."""
#        return False
#
#    def get_next_question_id(question):
#        """Figure out which question id is next in line to be coded.
#           Used in views.py:430"""
#        question_ids = Question.objects.filter(country=question.country,
#                language=question.language).values('id')
#        for i, cur in enumerate(question_ids):
#            if cur['id'] == question.id:
#                try: return question_ids[i+1]['id']
#                except (ValueError, IndexError): return -1
#
#    def save_question_rfa(question, request):
#        """Given a POST request containing RFA ao info, save it in the question,
#            return a message describing what happened"""
#        question.rfa_text = request.POST['rfa_text']
#        question.introduction_text = request.POST['introduction_text']
#        question.answer_text = request.POST['answer_text']
#        question.save()
#        return "Successfully updated the request for an answer, introduction," +\
#           " and answer categories for this question."
#        def get_done_dict(self, request):
#            if not self.__dict__.has_key('percent_done'):
#                self._init_done(request)
#            return {'done' : self.done, 'to_do':self.to_do,
#                    'percent_done':self.percent_done,
#                    'percent_pos':self.percent_pos
#                   }
#
#    def _init_done(self, request):
#        self.done,self.to_do,self.percent_done = self._get_percent_done(request)
#        self.percent_pos = -120.5 + (float(self.percent_done) / 100.0) * 121.5
#
#    def __unicode__(self):
#       s = unicode(self.item) + ' (' + unicode(self.country) + '; ' + \
#            unicode(self.language)  + ')'
#        return self.item.main_or_supplementary() + ": " + s
#
#    def _get_percent_done(self, request):
#        """ Calculates how many codings remain to be done as well as a percentage.
#            Returns amount done, amount to be done, and percentage as a tuple.
#            Skipping patterns, the current user, and the current
#            CharacteristicSet are taken into account."""
#        needed_codings = []
#        needed_characteristics = []
#
#
#        char_set = request.session.get('characteristic_set', default = 1)
#
#        all_codings = self.coding_set.filter(user = request.user,
#                        characteristic__characteristicset__id = char_set)
#        all_characteristics = Characteristic.objects.\
#                                filter(characteristicset__id = char_set)
#
#        if not (all_codings and all_characteristics):
#            return (0, 0, 0.0) # we already know the answer will be zero
#
#
#        skip = False
#        skip_to = False
#        num_cods = 0
#        num_chars = 0
#
#        for char in all_characteristics:
#            if char == skip_to:
#                skip_to, skip = False, False
#
#            if not skip:
#                #needed_characteristics.append(char.id)
#                num_chars += 1
#
#
#                # returns a list, empty (False) if not coded:
#                corresponding = all_codings.filter(characteristic = char)
#
#                if corresponding:
#                    # remembered _which_ codings are needed/coded.
#                    #needed_codings.append(corresponding[0].id)
#                    num_cods += 1
#
#                    # figure out whether we need to start skipping
#                    label = Label.objects.filter(code = corresponding[0].choice,
#                                characteristics = char)
#                    if label:
#                        skip_to, skip = label[0].skip_to, True
#
#        if num_chars: # prevent division by 0
#            #num_cods = len(needed_codings)
#            #num_chars = len(needed_characteristics)
#            return (num_cods, num_chars,
#                    round(100.0 * float(num_cods) / float(num_chars)))
#        else:
#            return (0, 0, 0.0)
#



class UserQuestion(models.Model):
    """Questions that have been assigned to a user for coding"""
    user             = models.ForeignKey(User)
    question         = models.ForeignKey(Question)
    can_edit_text    = models.BooleanField(default=False, verbose_name="Can edit text (intro, rfa, answer options)")
    can_edit_details = models.BooleanField(default=False, verbose_name="Can edit details (country, language, and item)")

    class Meta:
        verbose_name = 'User Assigned Question'
        verbose_name_plural = 'User Assigned Questions'

    def __unicode__(self):
        return "%s assigned to %s" % (self.question, self.user)




class ItemGroup(models.Model):
    """A group of items that can later be assigned to a group of users to code"""
    name              = models.CharField(max_length=80, help_text="Name this group for easy reference ")
    items             = models.ManyToManyField(Item, help_text="Items for this group")

    def item_sample_list(self):
        item_sample = [(u"%s" % item).replace(',', ' ') for item in self.items.all()[0:4]]

        summary = ', '.join(item_sample)

        if self.items.count() > 5:
            summary += ' and %s more' % (self.items.count() - 4)

        return summary

    def __unicode__(self):
        return self.name

    @staticmethod
    def m2m_changed(**kwargs):
        """If the item group changes for the bulk question creation or bulk 
	assignment then we mark those items as not run"""

        if isinstance(kwargs['instance'], ItemGroup)\
          and kwargs['action'] in ['post_add',  'post_remove', 'post_clear']:

            for question_bulk_creation in QuestionBulkCreation.objects.filter(item_group=kwargs['instance']):
                question_bulk_creation.has_been_run = False
                question_bulk_creation.save()
       
            for question_bulk_assignment in QuestionBulkAssignments.objects.filter(item_group=kwargs['instance']):
                question_bulk_assignment.has_been_run = False
                question_bulk_assignment.save()
            
#Bind the static method m2m_changed of the ItemGroup model so we can update related objects
m2m_changed.connect(ItemGroup.m2m_changed, weak=False)





class QuestionBulkCreation(models.Model):
    """A bulk question creation tool"""
    item_group              = models.ForeignKey(ItemGroup, help_text ='Create questions for all items in the selected item group')
    country                 = models.ForeignKey(Country, help_text ='Question will be created only for this country')
    language                = models.ForeignKey(Language, help_text='Question will be created only for this language')
    copy_text_from_study    = models.ForeignKey(Study, blank=True, null=True, help_text='Optional: Copy the intro, rfa text, and answer options from another study - when matching questions by variable name (TVTOT), country, and language are available in that study.')
    created_questions       = models.ManyToManyField(Question, blank=True)
    has_been_run            = models.BooleanField(default=False,  verbose_name="Run and up to date")
    last_run_date           = models.DateField(blank=True, null=True, help_text = "The last time this assignment was run")

    def __init__(self, *args, **kwargs):
        self._run = False #Keep track if this instance was run to prevent multiple runs on save
        self._list = None #Cache of the question list for the model admin
        self.copied_questions_count = 0   
        return super(QuestionBulkCreation, self).__init__(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Bulk Question Creation Task'
        verbose_name_plural = 'Bulk Question Creation Tasks'


    def created_questions_with_text(self):
        total = 0
        with_text = 0
        for q in self.created_questions.all():
            total += 1
            if q.has_text():
                with_text += 1
        
        return "%s / %s" % (with_text, total)

    def is_deletable(self, question):
        if question.introduction_text or question.rfa_text or question.answer_text:
            return False
        return True

    def questions_to_be_deleted(self):
        to_be_deleted = []
        """Used by the model admin to show which questions would be deleted when the question is deleted.
            The logic here is that empty questions are fine to delete, but questions with content alread filled out
            will not be deleted
        """
        for q in self.created_questions.all():
            if self.is_deletable(q):
                to_be_deleted.append(q)

        return to_be_deleted


    def questions_not_deleted(self):
        not_to_be_deleted = []
        """Used by the model admin to show which questions would be deleted when the question is deleted."""
        for q in self.created_questions.all():
            if not self.is_deletable(q):
                not_to_be_deleted.append(q)

        return not_to_be_deleted


    def questions_created(self):
        """Used by the model admin to show the total number of questions created"""
        return self.created_questions.count()

    def question_list(self):
        """Used by the model admin to show which questions would be created in the confirm screen"""
        if self._list is None: #If none on the first call we create the list
            self._list = {'to_create' : [],
                          'already_exist' : []}
            for item in self.item_group.items.iterator():
                question_summary = "%s in %s for country %s" % (item, self.language, self.country)
                try:
                    Question.objects.get(item=item, language=self.language, country=self.country)
                    self._list['already_exist'].append(question_summary)
                except Question.DoesNotExist:
                    self._list['to_create'].append(question_summary)
        return self._list

    def get_copy_from_question(self, to_question):
        if not self.copy_text_from_study:
            return None
         
        
        items = Item.objects.filter(study=self.copy_text_from_study, name=to_question.item.name)
        for item in items:
            for q in Question.objects.filter(item=item, country=to_question.country, language=to_question.language):
                if q.rfa_text:
                    return q
        
        #There was no text from the SOURCE in a previous study so we copy it from the UK    
        if to_question.country.name == 'SOURCE':
            uk = Country.objects.get(iso='GB')
            for item in items:
                for q in Question.objects.filter(item=item, country=uk, language=to_question.language):
                    if q.rfa_text:
                        return q
            
    
        return None
        
    def options(self):
        """Return some option buttons to link directly to the admin action"""

        options =  """
            <input type="submit" value="Run" onclick="do_action('run_creations', %s); return false;"/>
            """ % (self.id)

        if self.has_been_run:
            options += """
            <input type="submit" value="Undo and Delete Task" onclick="window.location.href='/admin/sqp/questionbulkcreation/%s/delete/'; return false;"/>
            """ % self.id

        return options

    options.allow_tags=True

    def run_creation(self):
        self._run   = True
        all_questions = self.created_questions.all()
        #Create any missing question objects
        for item in self.item_group.items.iterator():
            question, created = Question.objects.get_or_create(item=item, language=self.language, country=self.country)
            if created:
                copy_from_question = self.get_copy_from_question(question)
                if copy_from_question:
                    question.introduction_text = copy_from_question.introduction_text
                    question.rfa_text = copy_from_question.rfa_text
                    question.answer_text = copy_from_question.answer_text
                    question.save(create_suggestions = False)
                    self.copied_questions_count += 1
                if question not in all_questions:
                    self.created_questions.add(question)
                    
        self.has_been_run = True
        self.last_run_date = datetime.now()

    def __unicode__(self):
        return "%s creation task in %s for %s" % (self.item_group, self.language, self.country)

    _related_deleted = False
    def delete_related_questions(self):
        """Deleted the questions created by this task"""
        counter = 0
        if not self._related_deleted:
            self._related_deleted = True
            for q in self.created_questions.all():
                if self.is_deletable(q):
                    q.delete()
                    counter += 1
        return counter


    def on_before_delete(self):
        self.delete_related_questions()



class QuestionBulkAssignments(models.Model):
    """A bulk assignment tool to assign questions to users"""
    users                   = models.ManyToManyField(User, help_text = "Users who will be assigned this group of questions")
    item_group              = models.ForeignKey(ItemGroup, null=True, help_text ='Assign Items from this group')
    country                 = models.ForeignKey(Country, null=True, help_text ='Assign Question from this country')
    language                = models.ForeignKey(Language, null=True,help_text='Assign Question from this language')
    can_edit_text           = models.BooleanField(default=True, help_text = 'If the users can edit the intro, rfa, and answer texts or not for the assigned questions')
    can_edit_details        = models.BooleanField(default=False, help_text = 'If the users can edit the country, language, and item or not for the assigned questions')
    has_been_run            = models.BooleanField(default=False,  verbose_name="Run and up to date")
    last_run_date           = models.DateField(blank=True, null=True, help_text = "The last time this assignment was run")
    assignments             = models.ManyToManyField(UserQuestion, blank=True, verbose_name="Question Assignments")

    _run = False #Keep track if this instance was run to prevent multiple runs on save

    class Meta:
        verbose_name = 'Bulk Question Assignment'
        verbose_name_plural = 'Bulk Question Assignments'

    def assignments_count(self):
        """Used by the model admin to show the total number of assignment created or modified"""
        return self.assignments.count()

    def assign_to_users(self):
        user_names = []
        for u in self.users.all():
            user_names.append(u.username)
        return ', '.join(user_names)

    def assignments_to_be_deleted(self):
        return self.assignments.all()

    _counter = 0
    _assignments_deleted = False
    def delete_assignments(self):
        if not self._assignments_deleted:
            self._assignments_deleted = True
            self._counter = self.assignments.count()
            self.assignments.clear()
        return self._counter

    def on_before_delete(self):
        self.delete_assignments()

    def run_assignment(self):
        self._run = True
        assignments_created = 0
        assignments_total   = 0

        for item in self.item_group.items.iterator():
            #Create any missing question assignments

            question = Question.objects.get(item=item, language=self.language, country=self.country)

            all_assignments = self.assignments.all()

            for user in self.users.all():
                assignment, created = UserQuestion.objects.get_or_create(question=question, user=user)
                if created:
                    assignments_created += 1

                if assignment not in all_assignments:
                    self.assignments.add(assignment)

                assignment.can_edit_text = self.can_edit_text
                assignment.can_edit_details = self.can_edit_details
                assignment.save()
                assignments_total += 1

        self.has_been_run = True
        self.last_run_date = datetime.now()

    _list = None
    def question_list(self):
        """Used by the model admin to show which questions would be assigned in the confirm screen"""
        if self._list is None: #If none on the first call we create the list
            self._list = {'to_assign' : [],
                          'already_assigned' : [],
                          'missing_questions' : [],
                          'changed_questions' : []}

            for item in self.item_group.items.iterator():
                for user in self.users.all():
                    question_summary = "%s for %s, %s assigned to %s" % (item, self.language, self.country, user)

                    try:
                        question = Question.objects.get(item=item, country=self.country, language=self.language)

                        try:
                            user_question = UserQuestion.objects.get(question=question, user=user)

                            if user_question.can_edit_text != self.can_edit_text \
                            or user_question.can_edit_details != self.can_edit_details:
                                self._list['changed_questions'].append(question_summary)
                            else:
                                self._list['already_assigned'].append(question_summary)


                        except UserQuestion.DoesNotExist:
                            self._list['to_assign'].append(question_summary)

                    except Question.DoesNotExist:
                        summary = 'Question for Item %s in %s for country %s ' % (item, self.language, self.country)
                        if summary not in self._list['missing_questions']:
                            self._list['missing_questions'].append(summary)


        return self._list

    def options(self):
        """Return some option buttons to link directly to the admin action"""

        options =  """
            <input type="submit" value="Run" onclick="do_action('run_assignments', %s); return false;"/>
            """ % (self.id)

        if self.has_been_run:
            options += """
            <input type="submit" value="Undo and Delete" onclick="window.location.href='/admin/sqp/questionbulkassignments/%s/delete/'; return false;"/>
            """ % self.id

        return options
    options.allow_tags=True

    def __unicode__(self):
        return "%s assignment in %s for %s" % (self.item_group, self.language, self.country)

    @staticmethod
    def m2m_changed(**kwargs):
        """If the user group changes for the bulk assignment then we mark the assignment as not run"""
        if isinstance(kwargs['instance'], QuestionBulkAssignments)\
          and kwargs['action'] in ['post_add',  'post_remove', 'post_clear']:
            kwargs['instance'].has_been_run = False
            kwargs['instance'].save()

#Bind the static method m2m_changed of the ItemGroup model so we can update related objects
m2m_changed.connect(QuestionBulkAssignments.m2m_changed, weak=False)


class CodingSuggestion(models.Model):
    question        = models.ForeignKey(Question)
    characteristic  = models.ForeignKey(Characteristic)
    value           = models.TextField(blank=True, null=True)
    explanation     = models.TextField(blank=True, null=True)


class Coding(models.Model):

    question = models.ForeignKey(Question)
    characteristic = models.ForeignKey(Characteristic)
    choice = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)

    updated_on = models.DateTimeField()
    seconds_taken = models.FloatField(blank=True, null=True)

    #If this coding has been declared invalid
    #invalidated = models.BooleanField(default=False)

    #If this choice was "orphaned" because someone chose a different branch
    #calc_is_orphaned     = models.BooleanField(default=False)

    #how much this coding deviates from the others
    #calc_choice_deviance = models.FloatField(blank=True, null=True)
    #how many times this same choice was chosen for this char in this item
    #calc_choice_frequency = models.IntegerField(blank=True, null=True)


    def lookup_label(self):
        """Find the label this coding applies to or raise exception"""
        try:
            label = Label.objects.get(characteristic = self.characteristic,
                code = self.choice)
        except Label.DoesNotExist:
            labels = Label.objects.filter(characteristic = self.characteristic,
                    compute = True)
            if len(labels) == 0: raise Label.DoesNotExist
            else: label = labels[0] # for now just take the first one

        return label

    def __unicode__(self):
        return "Coding of %s for question %d by %s" % \
                (self.characteristic, self.question_id, self.user)
    def order_number(self):
        return self.characteristic.order_number
    class Meta:
        ordering = ['user','characteristic']

    def save(self, *args, **kwargs):

        try:
            charset = kwargs.pop('charset')
        except:
            charset = None

        try:
            prev_choice = Coding.objects.get(pk=self.id).choice
            if self.choice != prev_choice:
                self.question.set_completion_out_of_date(self.user, charset)

        except Coding.DoesNotExist:
            pass




        """   self.updated_on = datetime.now()
        history = History()

        #Try to get change_by_user from the kwargs to save, if none use 0 the second argument to get
        #history.actor               = kwargs.get('change_user', 0)
        history.actor               = 1
        history.object_id           = self.id
        history.object_model        = 'Coding'
        history.object_name         = u"%s"%self

        if self.id:
            history.action_type         = kwargs.get('action_type', History.ACTION_ITEM_CHANGED)
            history.action_description  = kwargs.get('action_description', 'Modification of Coding')
            #history.previous_values     = History.get_db_values(Coding, self)
        else:
            history.action_type         = kwargs.get('action_type', History.ACTION_ITEM_CREATED)
            history.action_description  = kwargs.get('action_description', 'Coding Created')

        history.save()

        #Clean up our kwqrgs
        if 'action_description' in kwargs:
            del kwargs['action_description']
        if 'action_type' in kwargs:
            del kwargs['action_type']
        if 'change_user' in kwargs:
            del kwargs['change_user']
        """

        super(Coding, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        history = History()

        #Try to get change_by_user from the kwargs to save, if none use 0 the second argument to get
        history.actor               = kwargs.get('change_user', 0)
        history.object_id           = self.id
        history.object_model        = 'Coding'
        history.object_name         = self
        history.action_type         = kwargs.get('action_type', History.ACTION_ITEM_DELETED)
        history.action_description  = kwargs.get('action_description', 'Deletion of Coding')
        history.previous_values     = History.get_db_values(Coding, self)
        history.save()

        #Clean up our kwqrgs
        if 'action_description' in kwargs:
            del kwargs['action_description']
        if 'action_type' in kwargs:
            del kwargs['action_type']
        if 'change_user' in kwargs:
            del kwargs['change_user']

        super(Coding, self).delete(*args, **kwargs)

class CodingChangeGroup(models.Model):
    name         =  models.CharField(max_length=255, help_text="The name of the coding change group")
    description  = models.TextField(help_text="Short text about why this group of changes is being made")

    def __unicode__(self):
        return "%s. %s" % \
                (self.id, self.name)
    class Meta:
        ordering = ['id',]

class CodingChangeException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CodingChangeAlreadyProcessed(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CodingChange(models.Model):

    CHANGE_DEFINED        = 1
    CHANGE_BY_RELATED     = 2
    CHANGE_DELETE          = 3

    CHANGE_CHOICES = ((CHANGE_DEFINED, 'Set coding to to defined value'),
                      (CHANGE_BY_RELATED, 'Set to related country/language value'),
                      (CHANGE_DELETE,   'Delete the coding')
                      )

    coding_change_group             = models.ForeignKey(CodingChangeGroup)
    question_id                     = models.IntegerField()
    characteristic                  = models.ForeignKey(Characteristic)
    coding_user                     = models.ForeignKey(User, related_name="coding_user_set",  null=True, help_text="The user who made the orig coding.")
    change_by                       = models.ForeignKey(User, related_name="change_by_user_set", null=True, help_text="The user who is making this change.")
    change_type                     = models.IntegerField(choices=CHANGE_CHOICES, help_text="select the type of change")
    new_value                       = models.CharField(max_length=15,blank=True,null=True, help_text="Set the new value as defined here.")
    new_value_by_related_lang       = models.ForeignKey(Language, blank=True, null=True, help_text="Set the new value as coded in another question. Related Question Language. Country and Language must both be set.")
    new_value_by_related_country    = models.ForeignKey(Country, blank=True, null=True, help_text="Set the new value as coded in another question. Related Question Country. Country and Language must both be set.")
    processed                       = models.BooleanField(default=False, help_text="If this change has been processed by the system")
    error_occured                   = models.BooleanField(default=False, help_text="If an error occurred during the last process")
    processing_log                  = models.TextField(blank=True, null=True,help_text="The log from processing")

    def process(self):

        if self.processed:
            raise CodingChangeAlreadyProcessed(self.id)

        try:
            target_coding = Coding.objects.get(question     = self.question_id,
                                        characteristic  = self.characteristic,
                                        user            = self.coding_user)
        except Coding.DoesNotExist:
            self.error_occured  = True
            error = 'Target coding could not be found. Check question id, characteristic, and user id'
            self.processing_log = error
            self.save();
            raise CodingChangeException(error)

        #we process the change type and apply the correct action
        if not self.change_type:
            self.error_occured  = True
            error = 'Change type not defined. You must specify a change type'
            self.processing_log = error
            self.save();
            raise CodingChangeException(error)
        elif self.change_type == self.CHANGE_DELETE:
            target_coding.save(action_description=u'Coding Deleted - %s'%self.coding_change_group, change_user=self.change_by.id)
            self.processed = True
            self.error_occured  = False
            self.processing_log = u"Processed correctly. Coding %s (%s) deleted" % ( target_coding.id, target_coding)
            self.save()
        elif self.change_type == self.CHANGE_DEFINED:
            if not self.new_value:
                self.error_occured  = True
                error = 'New value not defined. Please define value or select another change type.'
                self.processing_log = error
                self.save();
                raise CodingChangeException(error)
            #we take the value set directly by the user
            new_value = self.new_value
        else:
            #we try to find the related coding
            item = target_coding.question.item;
            try:
                related_question = Question.objects.get(item=item,
                                                    language=self.new_value_by_related_lang,
                                                    country=self.new_value_by_related_country)
            except Question.DoesNotExist:
                self.error_occured  = True
                error = 'Related Question in item %s for language %s and country %s could not be found to set new value' % \
                        (item, self.new_value_by_related_lang,self.new_value_by_related_country )
                self.processing_log = error
                self.save();
                raise CodingChangeException(error)

            try:
                related_coding = Coding.objects.get(question        = related_question,
                                                    characteristic  = self.characteristic)
                new_value = related_coding.choice
            except Coding.DoesNotExist:
                self.error_occured  = True
                error = 'Related Coding could not be found to set new value'
                self.processing_log = error
                self.save();
                raise CodingChangeException(error)
            except Coding.MultipleObjectsReturned:

                related_codings = Coding.objects.filter(question        = related_question,
                                                        characteristic  = self.characteristic)
                first   = True
                various = False
                error = ''
                for c in related_codings:
                    if first:
                        first = False
                        check = c.choice
                    elif c.choice != check:
                        various = True

                    error = error + u"%s - %s \n" % (c.user, c.choice)

                if various:
                    self.error_occured  = True
                    error = 'Multiple related codings found by various, please specify value exactly from these choices \n'
                    self.processing_log = error
                    self.save();
                    raise CodingChangeException(error)
                else:
                    new_value = check

        target_coding.choice = new_value
        target_coding.updated_on = datetime.now()
        target_coding.save(action_description=u'Coding Change - %s'%self.coding_change_group, change_user=self.change_by.id)
        self.processed = True
        self.error_occured  = False
        self.processing_log = u"Processed correctly. Coding %s (%s) set to %s" % ( target_coding.id, target_coding, new_value)
        self.save()

    def change_summary(self):
        return u"%s" % self

    def __unicode__(self):
        return "Change for '%s' in question id %s" % \
                (self.characteristic, self.question_id)



class UsedCountry(models.Model):
    iso       = models.CharField(max_length=2, primary_key = True)
    name      = models.CharField(max_length=80)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name',]
        db_table = 'vw_country_question'


class Completion(models.Model):
    "Whether questions have been completely coded by coder or not"
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    characteristic_set = models.ForeignKey(CharacteristicSet)
    complete = models.BooleanField(default=False)
    #Add an out_of_date column that we can call so that this can be calculated before generating the question list
    out_of_date = models.BooleanField(default=False)
    predictions = PickledObjectField(blank=True, null=True)
    potential_improvements = PickledObjectField(blank=True, null=True)
    authorized  = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s : %s  - question '%s' for charset '%s'" % \
            (unicode(self.user), ((self.complete) and 'COMPLETE' or 'NOT COMPLETE'),
             unicode(self.question), unicode(self.characteristic_set))

    def assign_to_user(self, to_user):

        codings = Coding.objects.filter(question=self.question,
                                        user=self.user)
        for coding in codings:
            coding.user = to_user
            coding.save()

        self.user = to_user
        self.save()

    def coding_list_tree(self):
        list = '<table>'
        for branch in self.question.iter_branches(user=self.user, charset=self.characteristic_set):
            if branch:
                
                if str(branch.label.name) == 'True':
                    choice_text = branch.coding_choice
                else:
                    choice_text = branch.label.name
                    
                characteristic = branch.label.characteristic
                choice = branch.coding_choice
                list += "<tr><th>%s</th><td>%s</td></tr>" % (characteristic, choice_text)
        list += '</table>'
        return list
    coding_list_tree.allow_tags = True

    def coding_list_all(self):
        list = '<table>'
        for coding in Coding.objects.filter(question=self.question, user=self.user).order_by('characteristic__name'):
       
                characteristic = coding.characteristic
                choice = coding.choice
                list += "<tr><th>%s</th><td>%s</td></tr>" % (characteristic, choice)
        list += '</table>'
        return list
    coding_list_all.allow_tags = True

class Prediction(models.Model):
    paramater = models.ForeignKey('Parameter') #TODO: fix spelling error
    view      = models.ForeignKey('View')
    function_name  = models.CharField(max_length=80)
    key       = models.CharField(max_length=80, blank=True,
            help_text='A key for referencing this prediction through the ui')

    py2R_names = {'quality':'qual2', 'reliability':'rel2', 'validity':'val2',
        'quality_coefficient':'qual', 'reliability_coefficient':'rel',
        'validity_coefficient':'val', 'method_effect_coefficient':'met',
        'common_method_variance':'cmv',
            }


    def __unicode__(self):
        return u"Prediction using view '%s' for parameter '%s'" % (self.view, self.paramater)


class View(models.Model):
    EXPECTED_TYPES = (('image', 'Image'),
                      ('tuple', 'Tuple'),
                      ('float', 'Float'),
                     )

    name        = models.CharField(max_length=80)
    expects     = models.CharField(max_length=20, choices = EXPECTED_TYPES, verbose_name="Expected Input", default="tuple")
    template    = models.CharField(max_length=140)
    order       = models.IntegerField(default=0)

    def render(self, prediction_return):
        ###TODO: Validate return is as expects
        t = get_template('predictions/' + self.template + '.html')
        return t.render(Context({'prediction' : prediction_return}))

    class Meta:
        ordering = ['order',]

    def __unicode__(self):
        return u"%s" % self.name

class Parameter(models.Model):
    name        =  models.CharField(max_length=80)
    description =  models.TextField()
    views       =  models.ManyToManyField(View, through=Prediction)

    order       = models.IntegerField(default=0)

    class Meta:
        ordering = ['order',]


    def __unicode__(self):
        return u"%s - %s"% (self.name, self.description[0:20])

class FAQ(models.Model):
    """'Frequently' asked questions and answers"""
    asker = models.ForeignKey(User, null=True, blank=True)
    question = models.TextField()
    answer = models.TextField()
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.question.strip()[0:100]


tips = {'tip_introduction' : """
Introductions mainly serve to initiate the topic of the Request for an Answer to the respondent and consist of one or more sentences.

Examples could be:

bq. _Now, a couple of questions follow about your health._

bq. _The next question deals with your work._

Sometimes a survey item contains two requests where the first request just functions as an introduction because no answer is required. The second request is the one to be answered as indicated by the answer categories.

Example:

bq. _Would you mind telling me your race or ethnic origin?_

bq. _Are you white black, Hispanic American, Alaskan native, Asian or Pacific Islander?_

(click the question mark again to close this text)
   """,

   'tip_rfa': """
        The request for an answer is everything in the question formulation that does not belong to the introduction or answer categories.

       It *includes* the request and any instructions to the respondent (anything that is heard or read by the respondent), but *not* the response options or introductory remarks such as "Now we would like to ask you a few questions about your life".

        Example:

        _On an average weekday, how much time, in total, do you spend watching television? Please use this card to answer._

        The term "Request for an answer" is employed because the social science research practice and the linguistic literature indicate that requests for an answer are formulated not only as questions or requests (interrogative form), but also as orders or instructions (imperative form) as well as assertions (declarative form) that require an answer.  Even in the case where no request is asked and an instruction is given or a statement is made, the text implies that the respondent is expected to give an answer. Thus the common feature of the formulation is not that a question is asked but that an answer is requested.

(click the question mark again to close this text)
   """,
   'tip_answer': """
     Please enter into this field the full text of the answer categories or response options, *one per line*.

    An example is given below:

    !/media/img/sqp/answers.png!

     (click the question mark again to close this text)
    """,
}
    
class UserProfile(models.Model):

    user = models.OneToOneField(User, related_name='profile')
    default_characteristic_set = models.ForeignKey(CharacteristicSet)
    is_trusted = models.BooleanField(help_text="When a user is trusted, their questions will be visible in the question database.", default = True)
    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=datetime.now)
    
    def __str__(self):
        return "%s's profile" % self.user
    
    @staticmethod
    def create_profile_for_user(user, key, expires):
        charset = CharacteristicSet.objects.get(pk=settings.AUTH_PROFILE_DEFAULT_CHARACTERISTIC_SET_ID)
        profile, created = UserProfile.objects.get_or_create( \
                user=user,
                default_characteristic_set = charset,
                activation_key=key,
                key_expires=expires)
        if created:
            profile.save()

    @staticmethod
    def on_user_created(sender, instance, created, **kwargs):
        if created:
            UserProfile.create_profile_for_user(instance)

    def options(self):
        """Add a few cross link options to the admin"""
        links = u''
        links += '<a href="/admin/sqp/question/?created_by__id__exact=%s">View Created Questions &gt;&gt;</a>' % self.user.id
        return mark_safe(links)
    options.allow_tags = True



#post_save.connect(UserProfile.on_user_created, sender=User)

#Just add a on_before_save method to your instance
def pre_save_easy_handler(sender, instance, **kwargs):
    if hasattr(instance, 'on_before_save'):
        instance.on_before_save()
pre_save.connect(pre_save_easy_handler)

#Just add a on_saved method to your instance
def post_save_easy_handler(sender, instance, **kwargs):
    if hasattr(instance, 'on_saved'):
        instance.on_saved()
post_save.connect(post_save_easy_handler)


#Just add a on_before_delete method to your instance
def pre_delete_easy_handler(sender, instance, **kwargs):
    if hasattr(instance, 'on_before_delete'):
        instance.on_before_delete()
pre_delete.connect(pre_delete_easy_handler)


#Just add a on_deleted method to your instance
def post_delete_easy_handler(sender, instance, **kwargs):
    if hasattr(instance, 'on_deleted'):
        instance.deleted()
post_delete.connect(post_delete_easy_handler)


class CharacteristicTree():

    def __init__(self, characteristic_set):
        self.characteristics = None
        self.branches = {}
        self.characteristic_set = characteristic_set
        self.characteristics = self.characteristic_set.get_characteristic_dict()
        
        """ Here we set up two types of indexes of the branch by short_name, to make the branch lookup faster 
            This saves about .10 seconds over all """
        for branch in self.characteristic_set.branches.select_related(depth=3).all():
            if branch.label.characteristic.is_categorical():
               
                try:
                    self.branches[branch.label.characteristic.short_name][str(branch.label.code)] = branch
                except:
                    self.branches[branch.label.characteristic.short_name]= {}
                    self.branches[branch.label.characteristic.short_name][str(branch.label.code)] = branch
            else:
                self.branches[branch.label.characteristic.short_name] = branch
               
        
            
    def get_branch(self, from_char, code):
        """For a choice on a characteristic, get a branch to another characteristic if it exists """
        try:
            if from_char.is_categorical():
                return self.branches[from_char.short_name][str(code)]
            else:
                return self.branches[from_char.short_name]
        except:
            return None
        
        
    
    def iter_branches(self, codes, from_char='domain', yield_last=True):
        """Get the full coding history for a group of codings
            The codings must be one user coding one question """
        
        tree = []
        from_char = self.get_char_by_short_name(from_char)
        
        #build an index of the codes by char_id for faster lookup
        code_dict = {}
        for code in codes:
            code_dict[code.characteristic_id] = code

        while 1:
            try:
                code = code_dict[from_char.id]
            except:
                #Coding is not complete
                #There is no code for the next char in the tree
                tree.append(None)
                return tree
            
            try:
                #Try to get a 
                #Copies are made of each branch since we have to append the coding_choice each time
                branch = copy.copy(self.get_branch(from_char, code.choice))
                branch.coding_choice = code.choice
                from_char = branch.to_characteristic
                tree.append(branch)
            except Exception as e:
                #Coding is complete
                #A fake branch that will allow the last element in the tree to have a value
                tree.append(FakeBranch(code))
                return tree
            
            
    def get_char_by_short_name(self, short_name):
        "Utility function used locally"
        for key in self.characteristics.keys():
            if self.characteristics[key].short_name == short_name:
                return self.characteristics[key]
        return None
        
