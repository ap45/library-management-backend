from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.books.models import Fines, LibraryCard, ItemIsCheckedOut, Item, Customer, CheckOut
from apps.books.serializers import FineSerializer, LibraryCardSerializer, ItemCheckoutSerializer

@api_view(['GET'])
def check_library_card(request, customer_id):
    try:
        card = LibraryCard.objects.filter(customer_id=customer_id).first()
        if not card:
            return Response({
                'status': 'error',
                'valid_card': False,
                'message': 'No library card found for this customer ID.'
            }, status=404)
        elif not card.is_valid():
            return Response({
                'status': 'error',
                'valid_card': False,
                'message': 'Library card expired. Please renew to proceed with checkout.'
            }, status=400)
        else:
            return Response({
                'status': 'success',
                'valid_card': True,
                'message': 'Library card is valid. You may proceed to enter item IDs for checkout.'
            })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['POST'])
def renew_library_card(request, customer_id):
    try:
        card, created = LibraryCard.objects.get_or_create(customer_id=customer_id)
        card.renew()
        return Response({'status': 'success', 'message': 'Library card renewed successfully.'})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
def check_fines(request, customer_id):
    try:
        fines = Fines.objects.filter(customer_id=customer_id, paid=False)
        has_fines = fines.exists()
        total_fines = sum(fine.amount for fine in fines)
        return Response({
            'status': 'success',
            'has_fines': has_fines,
            'total_fines': total_fines,
            'message': f'Outstanding fines: ${total_fines}' if has_fines else 'No outstanding fines. You can proceed to checkout.'
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['POST'])
def pay_fines(request, customer_id):
    try:
        unpaid_fines = Fines.objects.filter(customer_id=customer_id, paid=False)
        if unpaid_fines.exists():
            for fine in unpaid_fines:
                fine.paid = True
                fine.save()
            return Response({'status': 'success', 'message': 'Fines paid successfully. You may proceed with checkout.'})
        return Response({'status': 'success', 'message': 'No unpaid fines found.'})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['POST'])
def check_out_item(request, customer_id):
    try:
        items_to_checkout = request.data.get('item_ids', [])
        card = LibraryCard.objects.filter(customer_id=customer_id).first()

        # Check if library card is valid
        if not card or not card.is_valid():
            return Response({'status': 'error', 'message': 'Library card expired. Please renew.'}, status=400)

        # Ensure all fines are cleared before checkout
        unpaid_fines = Fines.objects.filter(customer_id=customer_id, paid=False)
        if unpaid_fines.exists():
            return Response({'status': 'error', 'message': 'Outstanding fines. Please pay before checkout.'}, status=400)

        # Process checkout for items not already checked out
        already_checked_out_items = []
        checked_out_items = []

        for item_id in items_to_checkout:
            if ItemIsCheckedOut.objects.filter(item_id=item_id, check_out__returned=False).exists():
                already_checked_out_items.append(item_id)
            else:
                check_out_record = CheckOut.objects.create(
                    customer_id=customer_id,
                    checkout_date=datetime.today().date(),
                    due_date=datetime.today().date() + timedelta(days=14)
                )
                ItemIsCheckedOut.objects.create(item_id=item_id, check_out=check_out_record)
                checked_out_items.append({
                    'item_id': item_id,
                    'due_date': check_out_record.due_date
                })

        if already_checked_out_items:
            return Response({
                'status': 'error',
                'message': f"The following items are already checked out: {', '.join(str(i) for i in already_checked_out_items)}",
                'already_checked_out': already_checked_out_items
            }, status=400)

        return Response({
            'status': 'success',
            'message': 'Checkout successful.',
            'checked_out_items': checked_out_items
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)
