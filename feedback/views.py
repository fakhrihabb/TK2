from django.shortcuts import render, redirect
from .models import Testimoni
from .forms import TestimoniForm

def list_testimoni(request):
    testimoni_list = [
        {'user': 'Alice', 'rating': 4, 'comment': 'Great service!', 'date_created': '2024-11-08'},
        {'user': 'Bob', 'rating': 5, 'comment': 'Excellent experience!', 'date_created': '2024-11-07'},
    ]  # Dummy data 
    if request.method == 'POST':
        form = TestimoniForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('testimoni-list')
    else:
        form = TestimoniForm()

    return render(request, 'feedback/testimoni_list.html', {
        'testimoni_list': testimoni_list,
        'form': form
    })
