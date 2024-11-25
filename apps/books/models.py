from django.db import models
from datetime import datetime, timedelta

class Item(models.Model):
    item_id = models.AutoField(primary_key=True, db_column='Item_ID')
    title = models.CharField(max_length=64, db_column='Title')
    author_fn = models.CharField(max_length=32, db_column='AuthorFN')
    author_ln = models.CharField(max_length=32, db_column='AuthorLN')
    publisher = models.CharField(max_length=32, null=True, db_column='Publisher')
    loc_code = models.CharField(max_length=32, db_column='Loc_Code')
    cost = models.DecimalField(max_digits=10, decimal_places=2, db_column='Cost')

    class Meta:
        db_table = 'item'

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True, db_column='Customer_ID')
    customer_fn = models.CharField(max_length=30, db_column='CustomerFN')
    customer_ln = models.CharField(max_length=30, db_column='CustomerLN')
    street_address = models.CharField(max_length=30, db_column='Street_Address')
    city = models.CharField(max_length=30, db_column='City')
    state = models.CharField(max_length=5, db_column='State')
    zip_code = models.IntegerField(db_column='Zip_Code')
    phone_number = models.CharField(max_length=30, db_column='Phone_Number')
    email = models.CharField(max_length=30, db_column='Email')

    class Meta:
        db_table = 'customer'

class Fines(models.Model):
    fine_id = models.AutoField(primary_key=True, db_column='Fine_ID')
    amount = models.DecimalField(max_digits=10, decimal_places=2, db_column='Fine_Amount')
    paid = models.BooleanField(default=False, db_column='Paid')
    payment_date = models.DateField(null=True, db_column='Payment_Date')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='Customer_ID')

    class Meta:
        db_table = 'fine'

    def mark_as_paid(self):
        self.paid = True
        self.payment_date = datetime.today().date()
        self.save()

class LibraryCard(models.Model):
    card_id = models.AutoField(primary_key=True, db_column='Card_ID')
    issue_date = models.DateField(db_column='Issue_Date')
    expire_date = models.DateField(db_column='Expire_Date')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='Customer_ID')

    class Meta:
        db_table = 'library_card'

    def is_valid(self):
        return self.expire_date >= datetime.today().date()

    def renew(self):
        self.expire_date = datetime.today().date() + timedelta(days=365)
        self.save()

class CheckOut(models.Model):
    check_out_id = models.AutoField(primary_key=True, db_column='Check_Out_ID')
    checkout_date = models.DateField(db_column='Checkout_Date')
    due_date = models.DateField(db_column='Due_Date')
    returned = models.BooleanField(default=False, db_column='Returned')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='Customer_ID')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, db_column='Item_ID', null=True)  # New field

    renewal_count = models.IntegerField(default=0, db_column='Renewal_Count')  # New field

    class Meta:
        db_table = 'check_out'

    def renew(self):
        if self.renewal_count >= 3:
            raise ValueError("This book has reached the maximum renewal limit.")
        self.due_date += timedelta(days=14)  # Extend due date by 14 days
        self.renewal_count += 1
        self.save()

class ItemIsCheckedOut(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, db_column='Item_ID')
    check_out = models.ForeignKey(CheckOut, on_delete=models.CASCADE, db_column='Check_Out_ID')

    class Meta:
        db_table = 'item_is_checked_out'



class CheckIn(models.Model):
    check_in_id = models.AutoField(primary_key=True, db_column='Check_In_ID')
    return_date = models.DateField(null=True, db_column='Return_Date')
    late_fees = models.FloatField(default=0.00, db_column='Late_Fees')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='Customer_ID')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, db_column='Item_ID')

    class Meta:
        db_table = 'check_in'

    def calculate_late_fees(self, due_date):
        if self.return_date and due_date and self.return_date > due_date:
            late_days = (self.return_date - due_date).days
            self.late_fees = late_days * 1.5  # Assuming 1.5 is the late fee per day
            self.save()

class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True, db_column='Reservation_ID')
    reservation_date = models.DateField(null=True, db_column='Reservation_Date')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='Customer_ID')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, db_column='Item_ID')
    status = models.CharField(max_length=20, choices=[('Reserved', 'Reserved'), ('Cancelled', 'Cancelled'), ('PickedUp', 'PickedUp'), ('FullFilled', 'Fullfilled')], default='Reserved')
    is_active = models.BooleanField(default=True, db_column='Is_Active')
    queue_position = models.IntegerField(default=0, db_column='Queue_Position')
    
    notification_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Notified', 'Notified'), ('Expired', 'Expired')],
        default='Pending',
        db_column='Notification_Status'
    )
    notified_on = models.DateField(null=True, db_column='Notified_On')
    notification_deadline = models.DateField(null=True, db_column='Notification_Deadline')

    class Meta:
        db_table = 'reservation'

    def cancel_reservation(self):
        self.status = 'Cancelled'
        self.is_active = False
        self.save()