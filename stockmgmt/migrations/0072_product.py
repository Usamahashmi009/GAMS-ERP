# Generated by Django 4.2.6 on 2024-01-09 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0071_defectiveitem_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('quantity', models.IntegerField(default=0)),
                ('rate', models.IntegerField(default=0)),
            ],
        ),
    ]
