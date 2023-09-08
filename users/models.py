from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import random
import re
from rut_chile import rut_chile
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Sum


CHOICES_ESTADO = (('activo', 'Activo'), ('bloqueado', 'Bloqueado'))


class UserAccountManager(BaseUserManager):
    def create_user(self, rut, email,  password=None, **kwargs):
        if not rut:
            raise ValueError('Users must have an rut')

        # email = self.normalize_email(email)
        # email = email.lower()

        user = self.model(
            rut=rut,
            email=email,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, rut, email, password=None, **kwargs):
        user = self.create_user(
            rut,
            email,
            password=password,
            **kwargs
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    rut = models.CharField(
        max_length=11,
        unique=True
    )
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    numero_cuenta = models.IntegerField(unique=True, default=0)
    saldo_contable = models.IntegerField(default=0)
    saldo_disponible = models.IntegerField(default=0)
    saldo_linea_credito = models.IntegerField(default=0)
    estado = models.CharField(
        max_length=20, choices=CHOICES_ESTADO, default=CHOICES_ESTADO[0][0])
    intentos_fallidos = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['nombres', 'apellidos', 'email']

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return self.nombres + ' ' + self.apellidos

    def valida_rut(self, rut, field):
        if rut:
            pattern = re.compile(r"^[0-9]+-[0-9kK]{1}$")

            if not pattern.match(rut):
                raise ValidationError({f'{field}': "Rut incorrecto"})
            else:
                if not rut_chile.is_valid_rut(rut):
                    raise ValidationError({f'{field}': "Rut incorrecto"})

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def clean(self):
        self.email = self.email.lower()
        if self.rut:
            rut = self.rut
            pattern = re.compile(r"^[0-9]+-[0-9kK]{1}$")

            if not pattern.match(rut):
                raise ValidationError({'rut': "Rut incorrecto"})
            else:
                if not rut_chile.is_valid_rut(rut):
                    raise ValidationError({'rut': "Rut incorrecto"})


class Cargos(models.Model):
    cuenta = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    monto = models.PositiveIntegerField(default=0)

    def __str__(self):
        return 'Cargo'

    class Meta:
        verbose_name = 'Cargos'
        verbose_name_plural = 'Cargos'


class Abonos(models.Model):
    cuenta = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    retencion = models.BooleanField(default=False)
    monto = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Abonos'
        verbose_name_plural = 'Abonos'


@receiver(pre_save, sender=UserAccount)
def random_cuenta_corriente(sender, instance, **kwargs):
    if not instance.numero_cuenta:
        numero_random = str(random.randint(10000, 99999))
        instance.numero_cuenta = numero_random


@receiver(post_save, sender=UserAccount)
def valida_estado(sender, instance, **kwargs):
    if instance.estado == 'activo' and instance.intentos_fallidos >= 3:
        instance.intentos_fallidos = 0
        instance.save()
