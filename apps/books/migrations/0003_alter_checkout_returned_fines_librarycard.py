# Generated by Django 5.1.2 on 2024-11-13 00:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_alter_checkout_table_alter_customer_table_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkout',
            name='returned',
            field=models.BooleanField(db_column='Returned', default=False),
        ),
        migrations.CreateModel(
            name='Fines',
            fields=[
                ('fine_id', models.AutoField(db_column='Fine_ID', primary_key=True, serialize=False)),
                ('amount', models.DecimalField(db_column='Amount', decimal_places=2, max_digits=10)),
                ('paid', models.BooleanField(db_column='Paid', default=False)),
                ('customer', models.ForeignKey(db_column='Customer_ID', on_delete=django.db.models.deletion.CASCADE, to='books.customer')),
            ],
            options={
                'db_table': 'fines',
            },
        ),
        migrations.CreateModel(
            name='LibraryCard',
            fields=[
                ('card_id', models.AutoField(db_column='Card_ID', primary_key=True, serialize=False)),
                ('issue_date', models.DateField(db_column='Issue_Date')),
                ('expire_date', models.DateField(db_column='Expire_Date')),
                ('customer', models.ForeignKey(db_column='Customer_ID', on_delete=django.db.models.deletion.CASCADE, to='books.customer')),
            ],
            options={
                'db_table': 'library_card',
            },
        ),
    ]
