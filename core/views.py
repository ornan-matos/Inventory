import csv
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import Maquina, Operacao, CodigoConfirmacao, CustomUser
from .forms import MaquinaForm, CodigoConfirmacaoForm

def admin_required(view_func):
    """
    Decorator que verifica se o usuário logado é um administrador.
    """
    decorated_view = user_passes_test(
        lambda u: u.is_authenticated and u.user_type == 'admin',
        login_url='login',
        redirect_field_name=None
    )(view_func)
    return decorated_view

@login_required
def home(request):
    """
    Página inicial que lista as máquinas e verifica quais têm operações pendentes.
    """
    maquinas = Maquina.objects.all().order_by('nome')
    maquinas_disponiveis = Maquina.objects.filter(status='disponivel').count()

    # Define o ponto de corte para códigos expirados
    ninety_seconds_ago = timezone.now() - timedelta(seconds=90)

    # Busca IDs de máquinas com códigos de retirada pendentes e válidos
    maquinas_com_retirada_pendente = CodigoConfirmacao.objects.filter(
        tipo_operacao='retirada',
        status='pendente',
        criado_em__gt=ninety_seconds_ago
    ).values_list('maquina_id', flat=True)

    # Busca IDs de máquinas com códigos de devolução pendentes e válidos
    maquinas_com_devolucao_pendente = CodigoConfirmacao.objects.filter(
        tipo_operacao='devolucao',
        status='pendente',
        criado_em__gt=ninety_seconds_ago
    ).values_list('maquina_id', flat=True)

    context = {
        'maquinas': maquinas,
        'maquinas_disponiveis': maquinas_disponiveis,
        'maquinas_com_retirada_pendente': list(maquinas_com_retirada_pendente),
        'maquinas_com_devolucao_pendente': list(maquinas_com_devolucao_pendente),
    }
    return render(request, 'core/home.html', context)

@login_required
def solicitar_retirada(request, maquina_id):
    maquina = get_object_or_404(Maquina, id=maquina_id, status='disponivel')
    codigo = CodigoConfirmacao.objects.create(
        usuario_solicitante=request.user,
        maquina=maquina,
        tipo_operacao='retirada'
    )
    context = {
        'maquina': maquina,
        'codigo': codigo.codigo,
        'codigo_id': codigo.id,
        'tipo_operacao': 'Retirada'
    }
    return render(request, 'core/exibir_codigo.html', context)

@login_required
def solicitar_devolucao(request, maquina_id):
    maquina = get_object_or_404(Maquina, id=maquina_id, posse_atual=request.user)
    codigo = CodigoConfirmacao.objects.create(
        usuario_solicitante=request.user,
        maquina=maquina,
        tipo_operacao='devolucao'
    )
    context = {
        'maquina': maquina,
        'codigo': codigo.codigo,
        'codigo_id': codigo.id,
        'tipo_operacao': 'Devolução'
    }
    return render(request, 'core/exibir_codigo.html', context)

@login_required
def confirmar_operacao(request, maquina_id, tipo_operacao):
    maquina = get_object_or_404(Maquina, id=maquina_id)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.method == 'POST':
        form = CodigoConfirmacaoForm(request.POST)
        if form.is_valid():
            codigo_digitado = form.cleaned_data['codigo']
            try:
                codigo_obj = CodigoConfirmacao.objects.get(codigo=codigo_digitado, maquina=maquina, tipo_operacao=tipo_operacao)
                if codigo_obj.usuario_solicitante == request.user:
                    message = 'Você não pode confirmar uma operação que você mesmo solicitou.'
                    if is_ajax: return JsonResponse({'status': 'error', 'message': message}, status=403)
                    messages.error(request, message)
                    return redirect('home')

                if codigo_obj.is_valid():
                    codigo_obj.status = 'confirmado'
                    codigo_obj.save()

                    if tipo_operacao == 'retirada':
                        maquina.status = 'em_uso'
                        maquina.posse_atual = codigo_obj.usuario_solicitante
                        maquina.save()
                        Operacao.objects.create(maquina=maquina, usuario_principal=codigo_obj.usuario_solicitante, usuario_confirmacao=request.user, tipo_operacao='retirada')
                        success_message = f'Máquina "{maquina.nome}" retirada com sucesso!'
                    else: # devolução
                        maquina.status = 'disponivel'
                        maquina.posse_atual = None
                        maquina.save()
                        Operacao.objects.create(maquina=maquina, usuario_principal=codigo_obj.usuario_solicitante, usuario_confirmacao=request.user, tipo_operacao='devolucao')
                        success_message = f'Máquina "{maquina.nome}" devolvida com sucesso!'

                    if is_ajax: return JsonResponse({'status': 'success', 'message': success_message})
                    messages.success(request, success_message)
                    return redirect('home')
                else:
                    if codigo_obj.status == 'pendente':
                        codigo_obj.status = 'expirado'
                        codigo_obj.save()
                    message = 'Código expirado ou já utilizado. Por favor, solicite um novo.'
                    if is_ajax: return JsonResponse({'status': 'error', 'message': message}, status=400)
                    messages.error(request, message)
            except CodigoConfirmacao.DoesNotExist:
                message = 'Código inválido.'
                if is_ajax: return JsonResponse({'status': 'error', 'message': message}, status=400)
                messages.error(request, message)
        else:
            if is_ajax: return JsonResponse({'status': 'error', 'message': 'O código deve conter 6 dígitos.'}, status=400)
    form = CodigoConfirmacaoForm()
    context = {'form': form, 'maquina': maquina, 'tipo_operacao': tipo_operacao.capitalize()}
    return render(request, 'core/confirmar_operacao.html', context)

@login_required
def verificar_status_operacao(request, codigo_id):
    try:
        codigo = CodigoConfirmacao.objects.get(id=codigo_id, usuario_solicitante=request.user)
        if codigo.status == 'confirmado':
            return JsonResponse({'status': 'confirmado'})

        if not codigo.is_valid() and codigo.status == 'pendente':
            codigo.status = 'expirado'
            codigo.save()
            return JsonResponse({'status': 'expirado'})

        return JsonResponse({'status': codigo.status})
    except CodigoConfirmacao.DoesNotExist:
        return JsonResponse({'status': 'expirado'})

@admin_required
def listar_maquinas(request):
    maquinas = Maquina.objects.all()
    return render(request, 'core/listar_maquinas.html', {'maquinas': maquinas})

@admin_required
def criar_maquina(request):
    if request.method == 'POST':
        form = MaquinaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Máquina cadastrada com sucesso!')
            return redirect('listar_maquinas')
    else:
        form = MaquinaForm()
    return render(request, 'core/form_maquina.html', {'form': form, 'titulo': 'Cadastrar Nova Máquina'})

@admin_required
def editar_maquina(request, maquina_id):
    maquina = get_object_or_404(Maquina, id=maquina_id)
    if request.method == 'POST':
        form = MaquinaForm(request.POST, request.FILES, instance=maquina)
        if form.is_valid():
            form.save()
            messages.success(request, 'Máquina atualizada com sucesso!')
            return redirect('listar_maquinas')
    else:
        form = MaquinaForm(instance=maquina)
    return render(request, 'core/form_maquina.html', {'form': form, 'titulo': f'Editar Máquina: {maquina.nome}'})

@admin_required
def remover_maquina(request, maquina_id):
    maquina = get_object_or_404(Maquina, id=maquina_id)
    if request.method == 'POST':
        maquina.delete()
        messages.success(request, f'Máquina "{maquina.nome}" removida com sucesso.')
        return redirect('listar_maquinas')
    return render(request, 'core/confirmar_remocao.html', {'maquina': maquina})
