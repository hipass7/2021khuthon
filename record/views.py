from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from .models import Record


@method_decorator(login_required, name='dispatch')
class RecordListView(ListView):
    model = Record
    paginate_by = 10

record_list = RecordListView.as_view()

