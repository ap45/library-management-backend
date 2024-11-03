# Update apps/books/views.py

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from datetime import datetime, timedelta
from .models import Item, Customer, CheckOut, ItemIsCheckedOut

@api_view(['POST'])
def check_out_item(request, customer_id):
    try:
        item_ids = request.data.get('item_ids', [])
        if not item_ids:
            return Response(
                {"message": "No item IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Get customer and verify fines
            customer = Customer.objects.get(pk=customer_id)
            if customer.outstanding_fines > 0:
                return Response(
                    {"message": "Cannot checkout. Customer has outstanding fines."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check number of items currently checked out
            current_checkouts = CheckOut.objects.filter(
                customer=customer,
                returned=False
            ).count()
            
            if current_checkouts + len(item_ids) > 20:  # Check total items after including new checkouts
                return Response(
                    {"message": "Cannot checkout. Maximum items (20) already checked out."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            due_dates = []  # Store due dates for the response
            messages = []  # Store messages for any failed checkouts
            
            for item_id in item_ids:
                # Get item and verify it exists
                try:
                    item = Item.objects.get(pk=item_id)
                except Item.DoesNotExist:
                    messages.append(f"Item with ID {item_id} not found.")
                    continue  # Skip this item

                # Check if item is already checked out
                if ItemIsCheckedOut.objects.filter(
                    item=item,
                    check_out__returned=False
                ).exists():
                    messages.append(f"Item with ID {item_id} is already checked out.")
                    continue  # Skip this item

                # Create checkout record
                checkout = CheckOut.objects.create(
                    checkout_date=datetime.now().date(),
                    due_date=datetime.now().date() + timedelta(days=20),
                    returned=False,
                    customer=customer
                )

                # Create item checkout relationship
                ItemIsCheckedOut.objects.create(
                    item=item,
                    check_out=checkout
                )

                due_dates.append(checkout.due_date)  # Store due date

            if messages:
                return Response({
                    "message": "Some items could not be checked out.",
                    "details": messages
                }, status=status.HTTP_207_MULTI_STATUS)  # Return multi-status

            return Response({
                "message": "Items checked out successfully.",
                "due_dates": due_dates
            }, status=status.HTTP_200_OK)

    except Customer.DoesNotExist:
        return Response(
            {"message": "Customer not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"message": f"Error checking out items: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
