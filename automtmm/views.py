#!/usr/bin/python
# -*- coding: utf-8 -*-
from django import forms
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.http import HttpResponse
from sqp_project.sqp.models import Experiment, Study, ParameterName, \
    ItemParameter, Item, MTMMModelVersion


class ReportForm(forms.Form):
    """Selection of a round, experiment and set of parameters for which to 
        produce a table"""
    experiment = forms.ModelChoiceField(Experiment.objects)
    parameter_names = forms.ModelMultipleChoiceField(ParameterName.objects)
    study = forms.ModelChoiceField(Study.objects)
    model_version = forms.ModelChoiceField(MTMMModelVersion.objects, initial = 2)
    display_name = forms.ChoiceField(choices = (('name','Item name'),
        ( 'admin', 'Item questionnaire number'),
        ( 'trait', 'Trait name',)))
    number_of_digits = forms.ChoiceField([(i+1, i+1) for i in range(16)],
            initial = 3)
    format = forms.ChoiceField(choices = (('html','Web page'),
        ( 'xls', 'Microsoft Excel spreadsheet'),
        ( 'doc', 'Microsoft Word document',)))

def abb(obj):
    return unicode(obj).replace(' ', '-')

def create_report(request, report_form):
    dat = report_form.cleaned_data
    params = ItemParameter.objects.filter(
            parameter_name__in = dat['parameter_names'],
            question__item__study = dat['study'],
            question__item__experiment = dat['experiment']).\
            order_by('question__country', 'question__language',
             'model','parameter_name', 'question__item').\
            filter(model__version = dat['model_version'])

    items = Item.objects.filter(experiment = dat['experiment']).\
            select_related('method')
    
    for item in items:
        item.method_count = item.method.item_set.filter(experiment = \
                dat['experiment']).count()

    if dat['format'] == 'html':
        return render_to_response('automtmm/show_report.html', 
            {'parameters': params, 
                'items':items,
                'dat':dat,
                'exp' : dat['experiment'],
                'study': dat['study'],
                'debug': request.GET.has_key('debug')})
    elif dat['format'] == 'xls' or dat['format'] == 'doc':

        response_content = render_to_string('automtmm/show_report.html', 
            {'parameters': params, 
                'items':items,
                'dat':dat,
                'exp' : dat['experiment'],
                'study': dat['study'],
                'debug': request.GET.has_key('debug')})

        filename = '%s_%s_%s' % (abb(dat['study']), 
                abb(dat['experiment']), abb(dat['model_version']))
        if dat['format'] == 'xls':
            response = HttpResponse(content = response_content, 
                content_type = "application/ms-excel")
            response['Content-Disposition'] = 'attachment; filename='+\
                    filename+'.xls'

        elif dat['format'] == 'doc':
            response = HttpResponse(content = response_content, 
                content_type = "application/ms-word")
            response['Content-Disposition'] = 'attachment; filename='+\
                    filename+'.doc'
        return response


def list_reports(request):
    """Provide some options for generating a report of parameter estimates and
    if everything is OK, show the report."""
    if request.method == 'POST':
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            return create_report(request, report_form)
    else: 
        report_form = ReportForm(initial={'study': 4, 'parameter_names':(1,2)})

    return render_to_response('automtmm/list_report.html', 
            {'report_form': report_form})

