# Generated by Django 5.1.2 on 2024-11-24 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0009_alter_reservation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='renewal_count',
            field=models.IntegerField(db_column='Renewal_Count', default=0),
        ),
    ]
