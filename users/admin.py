from django.contrib import admin
from .models import *
from .forms import *
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin.site.unregister(Group)


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
    list_display = ('rut', 'email', 'nombres',
                    'apellidos', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('rut', 'email', 'password')}),
        ('Información Personal', {'fields': ('nombres', 'apellidos')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Información de Cuenta', {'fields': (
            'numero_cuenta', 'saldo_contable', 'saldo_disponible', 'saldo_linea_credito', 'estado')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('rut', 'nombres', 'apellidos', 'email', 'password1', 'password2',
                       #    'is_staff', 'is_active'
                       ),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    horizontal = ()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = [CargosInline, AbonosInline]
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = []  # Oculta los inlines en la vista de edición (change)
        return super().add_view(request, form_url, extra_context)
        # Muestra los inlines solo en la vista de añadir (add)

    def save_model(self, request, obj, form, change):
        # Guardar el objeto CustomUser
        super().save_model(request, obj, form, change)

        # Guardar los objetos relacionados Cargos y Abonos
        for cargo in obj.cargos_set.all():
            cargo.cuenta = obj  # Asigna el usuario actual
            cargo.save()

        for abono in obj.abonos_set.all():
            abono.cuenta = obj  # Asigna el usuario actual
            abono.save()

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
