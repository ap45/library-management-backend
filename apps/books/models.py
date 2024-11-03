# from django.db import models

# Create your models here.
from django.db import models
from datetime import datetime, timedelta

class Item(models.Model):
    class Meta:
        db_table = 'Item'
        
    item_id = models.AutoField(primary_key=True, db_column='Item_ID')
    title = models.CharField(max_length=32, db_column='Title')
    author_fn = models.CharField(max_length=32, db_column='AuthorFN')
    author_ln = models.CharField(max_length=32, db_column='AuthorLN')
    publisher = models.CharField(max_length=32, null=True, db_column='Publisher')
    loc_code = models.CharField(max_length=32, db_column='Loc_Code')
    cost = models.DecimalField(max_digits=10, decimal_places=2, db_column='Cost')

class Customer(models.Model):
    class Meta:
        db_table = 'Customer'
        
    customer_id = models.AutoField(primary_key=True, db_column='Customer_ID')
    customer_fn = models.CharField(max_length=30, db_column='CustomerFN')
    customer_ln = models.CharField(max_length=30, db_column='CustomerLN')
    membership_start_date = models.DateField(db_column='Membership_Start_Date')
    membership_end_date = models.DateField(null=True, db_column='Membership_End_Date')
    street_address = models.CharField(max_length=30, db_column='Street_Address')
    city = models.CharField(max_length=30, db_column='City')
    state = models.CharField(max_length=5, db_column='State')
    zip_code = models.IntegerField(db_column='Zip_Code')
    phone_number = models.CharField(max_length=30, db_column='Phone_Number')
    email = models.CharField(max_length=30, db_column='Email')
    outstanding_fines = models.DecimalField(max_digits=10, decimal_places=2, db_column='Outstanding_Fines')

class CheckOut(models.Model):
    class Meta:
        db_table = 'Check_Out'
        
    check_out_id = models.AutoField(primary_key=True, db_column='Check_Out_ID')
    checkout_date = models.DateField(db_column='Checkout_Date')
    due_date = models.DateField(db_column='Due_Date')
    returned = models.BooleanField(db_column='Returned')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='Customer_ID')

class ItemIsCheckedOut(models.Model):
    class Meta:
        db_table = 'Item_Is_Checked_Out'
        
    item = models.ForeignKey(Item, on_delete=models.CASCADE, db_column='Item_ID')
    check_out = models.ForeignKey(CheckOut, on_delete=models.CASCADE, db_column='Check_Out_ID')
