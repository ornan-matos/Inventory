from django.urls import path
from . import views

urlpatterns = [
    # --- URLs para Usuários Comuns ---
    path('', views.home, name='home'),

    # --- Fluxo de Retirada ---
    path('solicitar-retirada/<int:maquina_id>/', views.solicitar_retirada, name='solicitar_retirada'),
    path('confirmar/<int:maquina_id>/<str:tipo_operacao>/', views.confirmar_operacao, name='confirmar_operacao'),

    # --- Fluxo de Devolução ---
    path('solicitar-devolucao/<int:maquina_id>/', views.solicitar_devolucao, name='solicitar_devolucao'),

    # --- NOVA ROTA PARA POLLING ---
    path('verificar-status/<int:codigo_id>/', views.verificar_status_operacao, name='verificar_status_operacao'),

    # --- CRUD de Máquinas (Admin) ---
    path('admin/maquinas/', views.listar_maquinas, name='listar_maquinas'),
    path('admin/maquinas/nova/', views.criar_maquina, name='criar_maquina'),
    path('admin/maquinas/editar/<int:maquina_id>/', views.editar_maquina, name='editar_maquina'),
    path('admin/maquinas/remover/<int:maquina_id>/', views.remover_maquina, name='remover_maquina'),
]
