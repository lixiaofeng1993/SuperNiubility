# Generated by Django 3.2.16 on 2022-12-20 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nb', '0048_alter_stockdetail_table'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='inflowstock',
            table='stock_inflow',
        ),
        migrations.AlterModelTable(
            name='kdjstock',
            table='stock_kdj',
        ),
        migrations.AlterModelTable(
            name='shareholdernumber',
            table='shareholder_np',
        ),
        migrations.AlterModelTable(
            name='stocktodayprice',
            table='stock_today',
        ),
        migrations.AlterModelTable(
            name='todo',
            table='todo',
        ),
    ]
