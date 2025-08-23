import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

# Estende o modelo de usuário padrão do Django
class CustomUser(AbstractUser):

    USER_TYPE_CHOICES = (
        ('admin', 'Administrador'),
        ('colaborador', 'Colaborador'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='colaborador')
    foto = models.ImageField(upload_to='fotos_usuarios/', null=True, blank=True, default='fotos_usuarios/default.png')

    def __str__(self):
        return self.get_full_name() or self.username

# Modelo para as máquinas de cartão
class Maquina(models.Model):
    """
    Representa uma máquina de cartão de crédito no inventário.
    """
    STATUS_CHOICES = (
        ('disponivel', 'Disponível'),
        ('em_uso', 'Em posse temporária'),
    )
    nome = models.CharField(max_length=100, unique=True)
    tipo_modelo = models.CharField(max_length=100, verbose_name="Tipo/Modelo")
    foto = models.ImageField(upload_to='fotos_maquinas/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    # Relacionamento para saber quem está com a máquina
    posse_atual = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='maquinas_em_posse')

    def __str__(self):
        return f"{self.nome} ({self.tipo_modelo})"

# Modelo para registrar as operações de retirada e devolução
class Operacao(models.Model):
    """
    Registra um histórico de todas as operações de retirada e devolução.
    """
    TIPO_OPERACAO_CHOICES = (
        ('retirada', 'Retirada'),
        ('devolucao', 'Devolução'),
    )
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='operacoes')
    # Usuário que executa a ação principal (retira ou devolve)
    usuario_principal = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='operacoes_iniciadas')
    # Usuário que confirma a operação com o código
    usuario_confirmacao = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='operacoes_confirmadas')
    tipo_operacao = models.CharField(max_length=20, choices=TIPO_OPERACAO_CHOICES)
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_operacao_display()} de {self.maquina.nome} por {self.usuario_principal.username}"

# Modelo para armazenar os códigos de confirmação temporários
class CodigoConfirmacao(models.Model):

    # Armazena códigos de confirmação de 6 dígitos com validade de 30 segundos.

    codigo = models.CharField(max_length=6, unique=True)
    usuario_solicitante = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE)
    tipo_operacao = models.CharField(max_length=20) # 'retirada' ou 'devolucao'
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Gera um código aleatório se não existir
        if not self.codigo:
            self.codigo = ''.join(random.choices(string.digits, k=6))
        # Define o tempo de expiração para 30 segundos a partir da criação
        if not self.id: # Apenas na criação
            self.expira_em = timezone.now() + timedelta(seconds=30)
        super().save(*args, **kwargs)

    def is_valid(self):
        # Verifica se o código ainda está dentro do prazo de validade.
        return timezone.now() < self.expira_em

    def __str__(self):
        return f"Código {self.codigo} para {self.usuario_solicitante.username}"
