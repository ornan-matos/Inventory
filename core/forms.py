from django import forms
from .models import Maquina

class MaquinaForm(forms.ModelForm):

    class Meta:
        model = Maquina
        # Define quais campos do modelo serão exibidos no formulário
        fields = ['nome', 'tipo_modelo', 'foto', 'status']

        # Personaliza os widgets para estilização e funcionalidade no HTML
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Máquina Cielo'
            }),
            'tipo_modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: LIO V2'
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        # Personaliza os rótulos dos campos
        labels = {
            'nome': 'Nome da Máquina',
            'tipo_modelo': 'Tipo/Modelo',
            'foto': 'Foto da Máquina',
            'status': 'Status Inicial',
        }

class CodigoConfirmacaoForm(forms.Form):

    # Formulário para a entrada do código de 6 dígitos.

    codigo = forms.CharField(
        label='Código de Confirmação',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '______',
            'autocomplete': 'off',
            'pattern': '[0-9]*', # Garante que o teclado numérico apareça em mobile
            'inputmode': 'numeric'
        }),
        help_text="Informe o código de 6 dígitos gerado pelo solicitante."
    )

    def clean_codigo(self):

        codigo = self.cleaned_data.get('codigo')
        if not codigo.isdigit():
            raise forms.ValidationError("O código deve conter apenas números.")
        return codigo
