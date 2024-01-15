# Generated by Django 4.2.6 on 2024-01-10 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0074_remove_product_quantity_remove_product_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='account_pay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_payable', models.IntegerField(blank=True, default='0', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='stock',
            name='account_payable',
        ),
    ]
