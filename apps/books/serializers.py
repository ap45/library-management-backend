from rest_framework import serializers
from apps.books.models import Item, Customer, Fines, LibraryCard, ItemIsCheckedOut

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
        model = ItemIsCheckedOut
        fields = ['item', 'checkout_date', 'due_date', 'returned', 'customer']