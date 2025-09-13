from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch, Exists, OuterRef
from .models import Maquina, Solicitacao
from .utils import admin_required

@login_required
def home(request):
    
    return render(request, 'core/home.html')

@login_required
def dashboard_status(request):
  
    query = request.GET.get('q', '')

  
    pending_solicitations = Solicitacao.objects.filter(
        maquina=OuterRef('pk'),
        status__startswith='pendente'
    )


    maquinas = Maquina.objects.annotate(
        tem_solicitacao=Exists(pending_solicitations)
    ).select_related('posse_atual').prefetch_related(
        Prefetch(
            'solicitacoes',
            queryset=Solicitacao.objects.filter(status__startswith='pendente').select_related('solicitante', 'posse_anterior'),
            to_attr='solicitacoes_ativas'
        )
    )

    if query:
        maquinas = maquinas.filter(
            Q(nome__icontains=query) |
            Q(tipo_modelo__icontains=query) |
            Q(patrimonio__icontains=query)
        )

    
    maquinas = maquinas.order_by('-tem_solicitacao', 'nome')


    maquinas_por_categoria = {}
    for maquina in maquinas:
        categoria = maquina.categoria or "Sem Categoria"
        if categoria not in maquinas_por_categoria:
            maquinas_por_categoria[categoria] = []

        sol = maquina.solicitacoes_ativas[0] if hasattr(maquina, 'solicitacoes_ativas') and maquina.solicitacoes_ativas else None

        solicitacao_data = None
        if sol:
            solicitacao_data = {
                'id': sol.id,
                'tipo': sol.get_tipo_display(),
                'status': sol.status,
                'solicitante': {
                    'id': sol.solicitante.id,
                    'nome': sol.solicitante.get_full_name() or sol.solicitante.username,
                    'foto_url': sol.solicitante.foto.url if sol.solicitante.foto else None,
                },
                'posse_anterior': {
                     'id': sol.posse_anterior.id,
                     'nome': sol.posse_anterior.get_full_name() or sol.posse_anterior.username,
                } if sol.posse_anterior else None,
            }
        
        tipo_maquina_display = maquina.get_tipo_maquina_display() if maquina.tipo_maquina else 'Produção'

        maquina_data = {
            'id': maquina.id,
            'nome': maquina.nome,
            'tipo_modelo': maquina.tipo_modelo,
            'foto_url': maquina.foto.url if maquina.foto else 'https://placehold.co/600x400/e9ecef/495057?text=Sem+Foto',
            'status': maquina.status,
            'status_display': maquina.get_status_display(),
            'patrimonio': maquina.patrimonio,
            'numero_serie': maquina.numero_serie,
            'tipo_maquina': tipo_maquina_display,
            'posse_atual': {
                'id': maquina.posse_atual.id,
                'nome': maquina.posse_atual.get_full_name() or maquina.posse_atual.username,
                'foto_url': maquina.posse_atual.foto.url if maquina.posse_atual.foto else None,
            } if maquina.posse_atual else None,
            'solicitacao': solicitacao_data
        }
        maquinas_por_categoria[categoria].append(maquina_data)


    maquinas_disponiveis = Maquina.objects.filter(status='disponivel').count()

    return JsonResponse({
        'maquinas_por_categoria': maquinas_por_categoria,
        'maquinas_disponiveis': maquinas_disponiveis,
    })


@login_required
def solicitar_operacao(request, maquina_id, tipo_operacao):
    maquina = get_object_or_404(Maquina, id=maquina_id)
    usuario = request.user

    if usuario.is_superuser or usuario.user_type == 'admin':
        messages.error(request, "Administradores não podem solicitar operações.")
        return redirect('home')

    if Solicitacao.objects.filter(maquina=maquina, status__startswith='pendente').exists():
        messages.warning(request, f'A máquina "{maquina.nome}" já possui uma operação pendente.')
        return redirect('home')

    if Solicitacao.objects.filter(solicitante=usuario, status__startswith='pendente').exists():
        messages.warning(request, 'Você já possui uma solicitação em andamento.')
        return redirect('home')

    if tipo_operacao == 'retirada':
        if maquina.status != 'disponivel':
            messages.error(request, 'Esta máquina não está disponível para retirada.')
            return redirect('home')
        Solicitacao.objects.create(maquina=maquina, solicitante=usuario, tipo='retirada', status='pendente_aprovacao')
        messages.success(request, f'A sua solicitação para retirar "{maquina.nome}" foi enviada para aprovação.')

    elif tipo_operacao == 'devolucao':
        if maquina.posse_atual != usuario:
            messages.error(request, 'Você não pode devolver uma máquina que não está na sua posse.')
            return redirect('home')
        Solicitacao.objects.create(maquina=maquina, solicitante=usuario, tipo='devolucao', status='pendente_aprovacao', posse_anterior=usuario)
        messages.success(request, f'A sua solicitação para devolver "{maquina.nome}" foi enviada para aprovação.')

    elif tipo_operacao == 'troca':
        if maquina.status != 'em_uso' or maquina.posse_atual == usuario:
            messages.error(request, 'Você não pode solicitar a troca desta máquina.')
            return redirect('home')
        Solicitacao.objects.create(maquina=maquina, solicitante=usuario, tipo='troca', status='pendente_confirmacao', posse_anterior=maquina.posse_atual)
        messages.success(request, f'A sua solicitação de troca para "{maquina.nome}" foi enviada para {maquina.posse_atual.get_full_name()}.')

    return redirect('home')


@login_required
def confirmar_troca(request, solicitacao_id):
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id, status='pendente_confirmacao')
    if solicitacao.posse_anterior != request.user:
        messages.error(request, "Você não tem permissão para confirmar esta troca.")
        return redirect('home')

    solicitacao.status = 'pendente_aprovacao'
    solicitacao.save()
    messages.info(request, f'Troca confirmada. Agora a aguardar aprovação do administrador.')
    return redirect('home')

@login_required
def cancelar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id, solicitante=request.user)
    if not solicitacao.status.startswith('pendente'):
        messages.warning(request, "Esta solicitação não pode mais ser cancelada.")
        return redirect('home')

    solicitacao.delete()
    messages.info(request, "A sua solicitação foi cancelada.")
    return redirect('home')

@admin_required
def processar_solicitacao(request, solicitacao_id, acao):
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id, status='pendente_aprovacao')
    maquina = solicitacao.maquina

    if acao == 'aprovar':
        if solicitacao.tipo == 'retirada':
            maquina.status = 'em_uso'
            maquina.posse_atual = solicitacao.solicitante
            maquina.save()
            messages.success(request, f'Retirada de "{maquina.nome}" por {solicitacao.solicitante.get_full_name()} aprovada.')

        elif solicitacao.tipo == 'devolucao':
            maquina.status = 'disponivel'
            maquina.posse_atual = None
            maquina.save()
            messages.success(request, f'Devolução de "{maquina.nome}" por {solicitacao.solicitante.get_full_name()} aprovada.')

        elif solicitacao.tipo == 'troca':
            maquina.posse_atual = solicitacao.solicitante
            maquina.save()
            messages.success(request, f'Troca de "{maquina.nome}" para {solicitacao.solicitante.get_full_name()} aprovada.')

        solicitacao.delete()
    elif acao == 'negar':
        messages.warning(request, f'Solicitação de {solicitacao.tipo} para "{maquina.nome}" foi negada.')
        solicitacao.delete()

    return redirect('home')

