from django.urls import path
from . import views

urlpatterns = [
    # Rota principal que carrega o template base da dashboard
    path('', views.home, name='home'),

   
    path('dashboard-status/', views.dashboard_status, name='dashboard_status'),

    # Ações do usuário comum
    path('solicitar/<int:maquina_id>/<str:tipo_operacao>/', views.solicitar_operacao, name='solicitar_operacao'),
    path('confirmar-troca/<int:solicitacao_id>/', views.confirmar_troca, name='confirmar_troca'),
    path('cancelar-solicitacao/<int:solicitacao_id>/', views.cancelar_solicitacao, name='cancelar_solicitacao'),

    # Ações do administrador
    path('processar/<int:solicitacao_id>/<str:acao>/', views.processar_solicitacao, name='processar_solicitacao'),
]

