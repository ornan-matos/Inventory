from django import forms
from .models import Maquina

class MaquinaForm(forms.ModelForm):
    class Meta:
        model = Maquina
        fields = [
            'nome', 'tipo_modelo', 'foto', 'status',
            'patrimonio', 'numero_serie', 'numero_vinculacao',
            'tipo_maquina'
        ]

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Máquina Cielo'}),
            'tipo_modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: LIO V2'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'patrimonio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 123456'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SN987654321'}),
            'numero_vinculacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 10203040'}),
            'tipo_maquina': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'nome': 'Nome da Máquina',
            'tipo_modelo': 'Tipo/Modelo',
            'foto': 'Foto da Máquina',
            'status': 'Status Inicial',
            'patrimonio': 'Patrimônio',
            'numero_serie': 'Número de Série',
            'numero_vinculacao': 'Número de Vinculação',
            'tipo_maquina': 'Tipo de Máquina'
        }
