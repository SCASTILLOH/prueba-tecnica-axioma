from .models import UserAccount


class CalculadorSaldo:
    def __init__(self, rut):
        self.rut = rut

    def calcula_saldo(self):
        cuenta = UserAccount.objects.filter(rut=self.rut).first()
        suma_cargos = Cargos.objects.filter(cuenta=cuenta).aggregate(
            total=models.Sum('monto'))['total']

        print('cuenta: ', cuenta)
        print('suma_cargos ', suma_cargos)
