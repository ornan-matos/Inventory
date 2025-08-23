from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Operacao

class Command(BaseCommand):
    help = 'Exclui registros de operações mais antigos que 120 dias.'

    def handle(self, *args, **kwargs):
        cutoff_date = timezone.now() - timedelta(days=120)

        old_records = Operacao.objects.filter(data_hora__lt=cutoff_date)
        count, _ = old_records.delete()

        self.stdout.write(self.style.SUCCESS(f'Foram excluídos {count} registros de operações com mais de 120 dias.'))
