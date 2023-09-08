from .models import UserAccount
from rut_chile import rut_chile
from .models import *
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Sum

import re


def format_number(text):
    return '{:,}'.format(text).replace(',', '.')


def calcula_saldo(rut):
    user_data = UserAccount.objects.filter(rut=rut).first()

    total_abonos_sin_ret = Abonos.objects.filter(cuenta=user_data, retencion=False).aggregate(
        total=Coalesce(Sum('monto'), 0))['total']

    total_abonos_con_ret = Abonos.objects.filter(cuenta=user_data, retencion=True).aggregate(
        total=Coalesce(Sum('monto'), 0))['total']

    total_cargos = Cargos.objects.filter(cuenta=user_data).aggregate(
        total=Coalesce(Sum('monto'), 0))['total']

    total_abonos = total_abonos_sin_ret + total_abonos_con_ret

    saldo_inicial = user_data.saldo_inicial

    saldo_disponible = saldo_inicial + total_abonos_sin_ret - total_cargos

    saldo_contable = saldo_disponible + total_abonos_con_ret

    data_response = {
        'user': user_data,
        'total_abonos': total_abonos,
        'total_abonos_con_ret': total_abonos_con_ret,
        'total_cargos': total_cargos,
        'saldo_linea_credito': user_data.saldo_linea_credito,
        'saldo_disponible': saldo_disponible,
        'saldo_contable': saldo_contable,
        'sobregirado': bool(saldo_disponible < 0),
    }

    return data_response


def valida_rut_chile(rut):
    if rut:
        pattern = re.compile(r"^[0-9]+-[0-9kK]{1}$")

        if not pattern.match(rut):
            return False
        else:
            if not rut_chile.is_valid_rut(rut):
                return False
            else:
                return True
