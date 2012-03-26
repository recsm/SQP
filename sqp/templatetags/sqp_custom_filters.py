#!/usr/bin/python
# -*- coding: utf-8 -*-
from django import template
from sqp_project.sqp.models import CharacteristicSet
register = template.Library()

@register.filter
def completeness(question, request=None):
    if request: 
        charset = CharacteristicSet.objects.get(pk = request.session['characteristic_set'])
        return question.get_completeness(request.user, charset)
    return question.complete > 0 and 'completely-coded' or 'not-coded'
