# Generated by Django 3.2.16 on 2022-12-16 17:13

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0044_shareholdernumber_stocksuper'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocksuper',
            name='create_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存时间'),
        ),
        migrations.AddField(
            model_name='stocksuper',
            name='is_delete',
            field=models.BooleanField(default=False, help_text='是否删除'),
        ),
        migrations.AddField(
            model_name='stocksuper',
            name='shares_hold',
            field=models.ForeignKey(default='', help_text='持仓股票ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='nb.shareshold'),
        ),
        migrations.AddField(
            model_name='stocksuper',
            name='update_date',
            field=models.DateTimeField(auto_now=True, help_text='更新时间', verbose_name='更新时间'),
        ),
    ]
