# Generated by Django 5.1.2 on 2024-11-20 16:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_remove_customer_membership_end_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='item',
            field=models.ForeignKey(db_column='Item_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='books.item'),
        ),
    ]
