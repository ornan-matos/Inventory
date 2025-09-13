import csv
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Maquina, Operacao

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_type')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_type')

    fieldsets = (
        (None, {"fields": ("username", "password_info")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Informações Adicionais"), {'fields': ('user_type', 'foto')}),
    )

    readonly_fields = ('password_info',)

    def password_info(self, obj):
        return format_html(
            'Para alterar a senha use <a href="../password/">este link</a>.'
        )
    password_info.short_description = "Palavra-passe" # Define o rótulo do campo

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'tipo_maquina', 'status', 'posse_atual')
    list_filter = ('status', 'categoria', 'tipo_maquina')
    search_fields = ('nome', 'tipo_modelo', 'patrimonio', 'numero_serie')

@admin.action(description='Exportar selecionados para CSV (Detalhado)')
def exportar_para_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historico_operacoes_detalhado.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Data', 'Horário', 'Operação', 'Utilizador Principal', 'Utilizador Confirmação',
        'Máquina', 'Património', 'Nº de Série', 'Nº de Vinculação'
    ])
    for op in queryset.order_by('-data_hora'):
        writer.writerow([
            op.data_hora.strftime('%d/%m/%Y'),
            op.data_hora.strftime('%H:%M:%S'),
            op.get_tipo_operacao_display(),
            op.usuario_principal.get_full_name() or op.usuario_principal.username,
            op.usuario_confirmacao.get_full_name() or op.usuario_confirmacao.username,
            op.maquina.nome,
            op.maquina.patrimonio,
            op.maquina.numero_serie,
            op.maquina.numero_vinculacao,
            ])
    return response

@admin.register(Operacao)
class OperacaoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'tipo_operacao', 'maquina', 'get_patrimonio', 'get_numero_serie', 'usuario_principal')
    list_filter = ('tipo_operacao', 'maquina', 'data_hora')
    search_fields = ('usuario_principal__username', 'maquina__nome', 'maquina__patrimonio', 'maquina__numero_serie')
    actions = [exportar_para_csv]

    @admin.display(description='Património')
    def get_patrimonio(self, obj):
        return obj.maquina.patrimonio

    @admin.display(description='Nº de Série')
    def get_numero_serie(self, obj):
        return obj.maquina.numero_serie

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False


