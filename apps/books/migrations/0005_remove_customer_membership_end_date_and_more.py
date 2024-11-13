# Generated by Django 5.1.2 on 2024-11-13 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_alter_fines_amount_alter_fines_table'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='membership_end_date',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='membership_start_date',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='outstanding_fines',
        ),
        migrations.AddField(
            model_name='fines',
            name='payment_date',
            field=models.DateField(db_column='Payment_Date', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='title',
            field=models.CharField(db_column='Title', max_length=64),
        ),
    ]
