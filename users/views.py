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

        if not rut or not password:
            if not rut:
                messages.error(request, 'El campo Rut no puede estar vacío')
            if not password:
                messages.error(
                    request, 'El campo Contraseña no puede estar vacío')
            return render(request, 'login.html')

        user = authenticate(request, rut=rut, password=password)

        if user and user.estado == 'bloqueado':
            messages.error(
                request, f'Usuario bloqueado, contacte a su administrador')
            return render(request, 'login.html')

        if user is not None:
            login(request, user)
            user.intentos_fallidos = 0
            user.save()
            return redirect('/')
        else:
            try:
                user = UserAccount.objects.get(rut=rut)

                user.intentos_fallidos += 1
                if user.intentos_fallidos >= 3:
                    user.estado = 'bloqueado'
                    messages.error(
                        request, f'Demasiados intentos fallidos, contacte a su administrador')
                user.save()
                messages.error(
                    request, f'Credenciales inválidas')
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

    def format_number(text):
        return '{:,}'.format(text).replace(',', '.')

    context = {
        'user': user_data,
        'total_abonos': format_number(total_abonos),
        'total_cargos': format_number(total_cargos),
        'saldo_disponible': format_number(user_data.saldo_disponible),
        'saldo_contable': format_number(user_data.saldo_contable),
    }

    return render(request, 'home.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')
