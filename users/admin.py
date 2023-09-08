from django.contrib import admin
from .models import *
from .forms import *
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .utils import calcula_saldo

admin.site.unregister(Group)


def procesa_saldos(element):
    """
    element == obj, esto para evitar maximum recursion depth
    """
    obj = element

    # procesa saldo segun cargos y abonos
    data = calcula_saldo(obj.rut)

    # actualiza obj userAccount
    obj.saldo_disponible = data['saldo_disponible']
    obj.saldo_contable = data['saldo_contable']
    obj.save()

    return obj


class CargosInline(admin.TabularInline):
    model = Cargos
    extra = 0


class AbonosInline(admin.TabularInline):
    model = Abonos
    extra = 0


class CustomUserAdmin(BaseUserAdmin):
    inlines = []  # Inicialmente, no hay inlines

    form = UserChangeForm
    add_form = UserAddForm
    list_display = ('rut', 'numero_cuenta', 'email', 'nombres',
                    'apellidos', 'estado', 'saldo_disponible')
    list_filter = ('is_active', 'is_staff', 'estado')
    fieldsets = (
        (None, {'fields': ('rut', 'email', 'password')}),
        ('Información Personal', {'fields': ('nombres', 'apellidos')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Información de Cuenta', {'fields': (
            'numero_cuenta', 'saldo_inicial', 'saldo_contable', 'saldo_disponible',
            'saldo_linea_credito', 'estado', 'intentos_fallidos')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('rut', 'nombres', 'apellidos', 'email', 'password1', 'password2',
                       #    'is_staff', 'is_active'
                       ),
        }),
    )
    search_fields = ('email', 'numero_cuenta')
    ordering = ('email',)
    horizontal = ()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = [CargosInline, AbonosInline]
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = []
        return super().add_view(request, form_url, extra_context)

    def response_add(self, request, new_object):
        obj = procesa_saldos(new_object)
        return super(CustomUserAdmin, self).response_add(request, obj)

    def response_change(self, request, obj):
        obj = procesa_saldos(obj)
        return super(CustomUserAdmin, self).response_change(request, obj)

    def calcula_suma_items_tabular(self, obj):
        obj = procesa_saldos(obj)
        return obj

    def get_readonly_fields(self, request, obj=None):
        if obj:
            # Modo de edición: Hacemos 'saldo_disponible' de solo lectura
            return ['numero_cuenta']
        else:
            # Modo de adición: Permitimos la edición de 'saldo_disponible'
            return []


admin.site.register(UserAccount, CustomUserAdmin)
admin.site.register(Cargos)
admin.site.register(Abonos)
