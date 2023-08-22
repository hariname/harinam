from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import Party


# Create your views here.

def add_party(request):
    if request.method == 'POST':
        date = datetime.now().strftime("%Y-%m-%d")
        form = request.POST
        name = form.get('customerName')
        email = form.get('customerEmail')
        phone = form.get('customerPhone')
        address = form.get('customerAddress')
        pinCode = form.get('pinCode')

        obj = Party.objects.create(customer_name=name.upper(),
                                   phone_no=phone,
                                   address=address,
                                   email=email,
                                   pipcode=pinCode,
                                   date=date)
        if obj:
            msg = 'Party Registration Successful!'
        else:
            msg = 'Party registration failed.'
        json_data = {'msg': msg}
        return JsonResponse(json_data)
    else:
        return render(request, 'add_party.html')


def edit_party(request, id):
    if request.method == 'POST':
        form = request.POST
        name = form.get('customerName')
        email = form.get('customerEmail')
        phone = form.get('customerPhone')
        address = form.get('customerAddress')
        pinCode = form.get('pinCode')
        Party.objects.filter(id=id).update(customer_name=name,
                                           phone_no=phone,
                                           address=address,
                                           email=email,
                                           pipcode=pinCode)
        return redirect('/party/list-party/')
    else:
        party = Party.objects.get(id=id)
        context = {
            'party': party
        }
        return render(request, 'edit_party.html', context)


def party_list(request):
    party = Party.objects.all()
    context = {
        'party': party
    }
    return render(request, 'party_list.html', context)


def delete_party(request, id):
    try:
        Party.objects.filter(id=id).delete()
    except:
        pass
    return redirect('/party/list-party/')
