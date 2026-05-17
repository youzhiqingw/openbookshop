from django.core.management.base import BaseCommand
from dvadmin.system.models import SystemConfig


class Command(BaseCommand):
    help = '初始化库存预警全局阈值'

    def handle(self, *args, **options):
        config, created = SystemConfig.objects.get_or_create(
            key='bookshop_warning_stock_threshold',
            defaults={'value': '10'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('已创建全局预警阈值: 10'))
        else:
            self.stdout.write(f'全局预警阈值已存在: {config.value}')
