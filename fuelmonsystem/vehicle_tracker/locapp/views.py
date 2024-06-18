from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import render
from .models import DataRecord
from django.http import HttpResponse

# Create your views here.
def data_list(request):
    records = DataRecord.objects.all()
    return render(request, 'data_list.html', {'records': records})



def data_delete(request):
        try:
            # Delete all records
            DataRecord.objects.all().delete()
            return HttpResponse('Successfully deleted all data records')
        except Exception as e:
            raise CommandError(f'Failed to delete data records: {str(e)}')
