import csv
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Maquina, Operacao, CodigoConfirmacao

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_type')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_type')

    fieldsets = (
        (None, {"fields": ("username", "password")}),
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
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Informações Adicionais"), {'fields': ('user_type', 'foto')}),
    )

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_modelo', 'status', 'posse_atual')
    list_filter = ('status',)
    search_fields = ('nome', 'tipo_modelo')

@admin.action(description='Exportar selecionados para CSV (Detalhado)')
def exportar_para_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historico_operacoes_detalhado.csv"'
    writer = csv.writer(response)
    # --- ALTERAÇÃO ---
    # Adiciona os novos campos ao cabeçalho do CSV
    writer.writerow([
        'Data', 'Horário', 'Operação', 'Usuário Principal', 'Usuário Confirmação',
        'Máquina', 'Patrimônio', 'Nº de Série', 'Nº de Vinculação'
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

    @admin.display(description='Patrimônio')
    def get_patrimonio(self, obj):
        return obj.maquina.patrimonio

    @admin.display(description='Nº de Série')
    def get_numero_serie(self, obj):
        return obj.maquina.numero_serie

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(CodigoConfirmacao)
class CodigoConfirmacaoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'usuario_solicitante', 'maquina', 'tipo_operacao', 'criado_em', 'status')
    list_filter = ('status', 'tipo_operacao')
    search_fields = ('codigo', 'usuario_solicitante__username', 'maquina__nome')

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
