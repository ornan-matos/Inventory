from django import forms
from .models import Maquina

class MaquinaForm(forms.ModelForm):
    class Meta:
        model = Maquina
        # Adiciona os novos campos à lista
        fields = [
            'nome', 'tipo_modelo', 'foto', 'status',
            'patrimonio', 'numero_serie', 'numero_vinculacao'
        ]

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Máquina Cielo'}),
            'tipo_modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: LIO V2'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            # Widgets para os novos campos
            'patrimonio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 123456'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SN987654321'}),
            'numero_vinculacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 10203040'}),
        }
        labels = {
            'nome': 'Nome da Máquina',
            'tipo_modelo': 'Tipo/Modelo',
            'foto': 'Foto da Máquina',
            'status': 'Status Inicial',
            # Rótulos para os novos campos
            'patrimonio': 'Patrimônio',
            'numero_serie': 'Número de Série',
            'numero_vinculacao': 'Número de Vinculação',
        }

class CodigoConfirmacaoForm(forms.Form):
    codigo = forms.CharField(
        label='Código de Confirmação',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '______',
            'autocomplete': 'off',
            'pattern': '[0-9]*',
            'inputmode': 'numeric'
        }),
        help_text="Informe o código de 6 dígitos gerado pelo solicitante."
    )

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if not codigo.isdigit():
            raise forms.ValidationError("O código deve conter apenas números.")
        return codigo
