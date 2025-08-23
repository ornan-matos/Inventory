import csv
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Maquina, Operacao, CodigoConfirmacao

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_type')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_type')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('user_type', 'foto')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('user_type', 'foto')}),
    )

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_modelo', 'status', 'posse_atual')
    list_filter = ('status',)
    search_fields = ('nome', 'tipo_modelo')

@admin.action(description='Exportar selecionados para CSV')
def exportar_para_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historico_operacoes.csv"'
    writer = csv.writer(response)
    writer.writerow(['Data', 'Horário', 'Operação', 'Usuário Principal', 'Máquina', 'Usuário Confirmação'])
    for op in queryset.order_by('-data_hora'):
        writer.writerow([
            op.data_hora.strftime('%d/%m/%Y'),
            op.data_hora.strftime('%H:%M:%S'),
            op.get_tipo_operacao_display(),
            op.usuario_principal.get_full_name() or op.usuario_principal.username,
            op.maquina.nome,
            op.usuario_confirmacao.get_full_name() or op.usuario_confirmacao.username,
            ])
    return response

@admin.register(Operacao)
class OperacaoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'tipo_operacao', 'maquina', 'usuario_principal', 'usuario_confirmacao')
    list_filter = ('tipo_operacao', 'maquina', 'data_hora')
    search_fields = ('usuario_principal__username', 'maquina__nome')
    actions = [exportar_para_csv]
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(CodigoConfirmacao)
class CodigoConfirmacaoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'usuario_solicitante', 'maquina', 'tipo_operacao', 'criado_em', 'expira_em')

    # --- ALTERAÇÃO ---
    # Remove os botões "Adicionar", "Alterar" e "Deletar" para este modelo.
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
