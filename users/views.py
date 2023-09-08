from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Sum


def login_view(request):
    if request.method == 'POST':
        rut = request.POST['rut']
        password = request.POST['password']

        user = authenticate(request, rut=rut, password=password)

        if user is not None:
            login(request, user)
            user.intentos_fallidos = 0
            user.save()
            return redirect('/')
        else:
            try:
                user = UserAccount.objects.get(rut=rut)
                user.intentos_fallidos += 1
                if user.intentos_fallidos >= 4:
                    user.estado = 'bloqueado'
                user.save()
                messages.error(request, 'Credenciales inválidas')
            except UserAccount.DoesNotExist:
                messages.error(request, 'El usuario no existe')

        print('user data: ', UserAccount.objects.filter(rut=rut).values())

    return render(request, 'login.html')


@login_required(login_url='/login/')
def home_view(request):
    user_data = UserAccount.objects.filter(rut=request.user.rut).first()

    total_abonos = Abonos.objects.filter(cuenta=user_data).aggregate(
        total=Coalesce(Sum('monto'), 0))['total']

    total_cargos = Cargos.objects.filter(cuenta=user_data).aggregate(
        total=models.Sum('monto'))['total']

    context = {
        'user': user_data,
        'total_abonos': total_abonos,
        'total_cargos': total_cargos,
        'saldo_disponible': user_data.saldo_disponible
    }

    return render(request, 'home.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')
