from rest_framework import serializers
from apps.books.models import Item, Customer, Fines, LibraryCard, CheckOut,CheckIn,Reservation

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fines
        fields = ['fine_id', 'amount', 'paid', 'payment_date', 'customer_id']

class LibraryCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryCard
        fields = ['card_id', 'issue_date', 'expire_date', 'customer_id']
class ItemCheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckOut
        fields = ['item', 'checkout_date', 'due_date', 'returned', 'customer', 'renewal_count']

class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckIn
        fields = ['check_in_id', 'return_date', 'late_fees', 'customer', 'item']

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'reservation_id', 'reservation_date', 'customer', 'item', 'status',
            'queue_position', 'is_active', 'notification_status', 'notified_on', 'notification_deadline'
        ]