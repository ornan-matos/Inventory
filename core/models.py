import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Administrador'),
        ('colaborador', 'Colaborador'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='colaborador')
    foto = models.ImageField(upload_to='fotos_usuarios/', null=True, blank=True, default='fotos_usuarios/default.png')

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.get_full_name() or self.username

class Maquina(models.Model):
    STATUS_CHOICES = (
        ('disponivel', 'Disponível'),
        ('em_uso', 'Em posse temporária'),
    )
    nome = models.CharField(max_length=100, unique=True)
    tipo_modelo = models.CharField(max_length=100, verbose_name="Tipo/Modelo")
    foto = models.ImageField(upload_to='fotos_maquinas/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    posse_atual = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='maquinas_em_posse')

    # --- NOVOS CAMPOS ADICIONADOS ---
    patrimonio = models.CharField(max_length=50, blank=True, null=True, verbose_name="Patrimônio")
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Série")
    numero_vinculacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Vinculação")

    class Meta:
        verbose_name = "Máquina"
        verbose_name_plural = "Máquinas"

    def __str__(self):
        return f"{self.nome} ({self.tipo_modelo})"

class Operacao(models.Model):
    TIPO_OPERACAO_CHOICES = (
        ('retirada', 'Retirada'),
        ('devolucao', 'Devolução'),
    )
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

class CodigoConfirmacao(models.Model):
    codigo = models.CharField(max_length=6, unique=True)
    usuario_solicitante = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE)
    tipo_operacao = models.CharField(max_length=20)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()

    class Meta:
        verbose_name = "Código de Confirmação"
        verbose_name_plural = "Códigos de Confirmação"

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = ''.join(random.choices(string.digits, k=6))
        if not self.id:
            self.expira_em = timezone.now() + timedelta(seconds=30)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expira_em

    def __str__(self):
        return f"Código {self.codigo} para {self.usuario_solicitante.username}"
