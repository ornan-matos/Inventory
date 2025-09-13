import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (('admin', 'Administrador'), ('colaborador', 'Colaborador'))
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='colaborador')
    foto = models.ImageField(upload_to='fotos_usuarios/', null=True, blank=True, default='fotos_usuarios/default.png')
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
    def __str__(self):
        return self.get_full_name() or self.username

class Maquina(models.Model):
    STATUS_CHOICES = (('disponivel', 'Disponível'), ('em_uso', 'Em posse temporária'))
    TIPO_MAQUINA_CHOICES = (('producao', 'Produção'), ('desenvolvimento', 'Desenvolvimento'))


    CATEGORIA_CHOICES = (
        ('POS', 'POS PDV'),
        ('MINI PDV', 'Mini PDV'),
        ('TOTENS', 'Totens Desenvolvimento'),
        ('OUTROS', 'Outros Equipamentos'),
        ('HOME OU EVENTOS', 'Fora da POS'),
    )

    nome = models.CharField(max_length=100, unique=True)
    tipo_modelo = models.CharField(max_length=100, verbose_name="Tipo/Modelo")
    foto = models.ImageField(upload_to='fotos_maquinas/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    posse_atual = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='maquinas_em_posse')
    patrimonio = models.CharField(max_length=50, blank=True, null=True, verbose_name="Patrimônio")
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Série")
    numero_vinculacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Vinculação")
    tipo_maquina = models.CharField(max_length=20, choices=TIPO_MAQUINA_CHOICES, default='producao', verbose_name="Tipo de Máquina")
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, default='Outros', null=True, blank=True)

    class Meta:
        verbose_name = "Máquina"
        verbose_name_plural = "Máquinas"

    def __str__(self):
        return f"{self.nome} ({self.tipo_modelo})"

class Solicitacao(models.Model):
    TIPO_SOLICITACAO_CHOICES = (
        ('retirada', 'Retirada'),
        ('devolucao', 'Devolução'),
        ('troca', 'Troca'),
    )
    STATUS_SOLICITACAO_CHOICES = (
        ('pendente_aprovacao', 'Pendente de Aprovação do Admin'),
        ('pendente_confirmacao', 'Pendente de Confirmação do Par'),
        ('aprovada', 'Aprovada'),
        ('negada', 'Negada'),
    )
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='solicitacoes')
    solicitante = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='solicitacoes_feitas')
    posse_anterior = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitacoes_cedidas')
    tipo = models.CharField(max_length=20, choices=TIPO_SOLICITACAO_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_SOLICITACAO_CHOICES, default='pendente_aprovacao')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitação"
        verbose_name_plural = "Solicitações"
        ordering = ['-criado_em']

    def __str__(self):
        return f"Solicitação de {self.tipo} para {self.maquina.nome} por {self.solicitante.username}"

class Operacao(models.Model):
    TIPO_OPERACAO_CHOICES = (('retirada', 'Retirada'), ('devolucao', 'Devolução'), ('troca', 'Troca'))
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='operacoes')
    usuario_principal = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='operacoes_iniciadas')
    usuario_confirmacao = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='operacoes_confirmadas')
    tipo_operacao = models.CharField(max_length=20, choices=TIPO_OPERACAO_CHOICES)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Histórico de Operação"
        verbose_name_plural = "Históricos de Operações"

    def __str__(self):
        return f"{self.get_tipo_operacao_display()} de {self.maquina.nome} por {self.usuario_principal.username}"

