# Generated by Django 4.2.6 on 2023-11-17 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0029_alter_stock_batch_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='batch_number',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
