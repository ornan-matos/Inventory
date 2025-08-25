
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('solicitar-retirada/<int:maquina_id>/', views.solicitar_retirada, name='solicitar_retirada'),
    path('confirmar/<int:maquina_id>/<str:tipo_operacao>/', views.confirmar_operacao, name='confirmar_operacao'),

    path('solicitar-devolucao/<int:maquina_id>/', views.solicitar_devolucao, name='solicitar_devolucao'),

    path('verificar-status/<int:codigo_id>/', views.verificar_status_operacao, name='verificar_status_operacao'),

]
