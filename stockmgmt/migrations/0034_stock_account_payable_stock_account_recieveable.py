# Generated by Django 4.2.6 on 2023-11-21 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0033_sale_date_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='account_payable',
            field=models.IntegerField(blank=True, default='0', null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='account_recieveable',
            field=models.IntegerField(blank=True, default='0', null=True),
        ),
    ]
