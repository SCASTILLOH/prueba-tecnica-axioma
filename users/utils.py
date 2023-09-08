from .models import UserAccount
from rut_chile import rut_chile

import re


class CalculadorSaldo:
    def __init__(self, rut):
        self.rut = rut

    def calcula_saldo(self):
        cuenta = UserAccount.objects.filter(rut=self.rut).first()
        suma_cargos = Cargos.objects.filter(cuenta=cuenta).aggregate(
            total=models.Sum('monto'))['total']

        print('cuenta: ', cuenta)
        print('suma_cargos ', suma_cargos)


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
