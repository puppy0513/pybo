# Generated by Django 3.2.9 on 2021-11-30 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0003_alter_risk_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='risk',
            name='Index1',
            field=models.DecimalField(decimal_places=6, max_digits=8),
        ),
        migrations.AlterField(
            model_name='risk',
            name='Index2',
            field=models.DecimalField(decimal_places=6, max_digits=8),
        ),
    ]
