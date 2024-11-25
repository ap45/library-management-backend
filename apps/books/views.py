from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.books.models import Fines, LibraryCard, ItemIsCheckedOut, Item, Customer, CheckOut, Reservation, CheckIn
from apps.books.serializers import FineSerializer, LibraryCardSerializer, ItemCheckoutSerializer
from django.db.models import Max
from django.http import JsonResponse
from rest_framework import status
from datetime import date, timedelta

# Utility function to get the next Check_Out_ID
def get_next_check_out_id():
    max_id = CheckOut.objects.aggregate(Max('check_out_id'))['check_out_id__max']
    return (max_id or 0) + 1

@api_view(['GET'])
def check_library_card(request, customer_id):
    try:
        # Validate customer_id
        if not isinstance(customer_id, int):
            return Response({
                'status': 'error',
                'valid_card': False,
                'message': 'Invalid customer ID format. Please provide a numeric ID.'
            }, status=400)

        # Check if the card exists
        card = LibraryCard.objects.filter(customer_id=customer_id).first()
        if not card:
            return Response({
                'status': 'error',
                'valid_card': False,
                'message': 'No library card found for this customer ID.'
            }, status=404)

        # Check card validity
        if not card.is_valid():
            return Response({
                'status': 'success',
                'valid_card': False,
                'card_expired': True,
                'message': 'Library card expired. Please renew it to continue.'
            }, status=200)

        return Response({
            'status': 'success',
            'valid_card': True,
            'message': 'Library card is valid. You may proceed.'
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f"An unexpected error occurred: {str(e)}"
        }, status=500)

@api_view(['POST'])
def renew_library_card(request, customer_id):
    try:
        # Validate customer_id
        if not isinstance(customer_id, int):
            return Response({
                'status': 'error',
                'message': 'Invalid customer ID format. Please provide a numeric ID.'
            }, status=400)

        # Check if the card exists
        card = LibraryCard.objects.filter(customer_id=customer_id).first()
        if not card:
            return Response({
                'status': 'error',
                'message': 'No library card found for this customer ID.'
            }, status=404)

        # Renew the card
        card.renew()
        card.save()
        return Response({
            'status': 'success',
            'message': 'Library card renewed successfully.'
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f"An unexpected error occurred: {str(e)}"
        }, status=500)

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

##Pay Fines
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

##Checkout 
@api_view(['POST'])
def check_out_item(request, customer_id):
    try:
        item_ids = request.data.get('item_ids', [])
        if not item_ids or not isinstance(item_ids, list):
            return Response({'status': 'error', 'message': 'Item IDs must be a non-empty list.'}, status=400)

        # Validate the customer
        customer = Customer.objects.filter(customer_id=customer_id).first()
        if not customer:
            return Response({'status': 'error', 'message': 'Invalid customer ID.'}, status=400)

        # Check if the customer has unpaid fines
        unpaid_fines = Fines.objects.filter(customer_id=customer_id, paid=False)
        if unpaid_fines.exists():
            return Response({'status': 'error', 'message': 'Outstanding fines must be cleared before checkout.'}, status=400)

        # Validate the library card
        card = LibraryCard.objects.filter(customer_id=customer_id).first()
        if not card or not card.is_valid():
            return Response({'status': 'error', 'message': 'Invalid or expired library card.'}, status=400)

        # Check the customer's checkout limit
        active_checkouts = CheckOut.objects.filter(customer_id=customer_id, returned=False).count()
        if active_checkouts >= 20:
            return Response({'status': 'error', 'message': 'Checkout limit exceeded (max 20 items).'}, status=400)

        successful_checkouts = []
        failed_checkouts = []

        for item_id in item_ids:
            item = Item.objects.filter(item_id=item_id).first()
            if not item:
                failed_checkouts.append({'item_id': item_id, 'message': 'Invalid item ID.'})
                continue

            # Check if the item is currently checked out
            if CheckOut.objects.filter(item_id=item_id, returned=False).exists():
                failed_checkouts.append({'item_id': item_id, 'message': 'Item is currently checked out.'})
                continue

            # Check if the item is reserved
            reservation = Reservation.objects.filter(item_id=item_id, is_active=True).order_by('queue_position').first()
            if reservation:
                # Customer not in reservation queue
                if reservation.customer.customer_id != customer_id:
                    failed_checkouts.append({'item_id': item_id, 'message': 'Item reserved by another customer. Please reserve the item.'})
                    continue

                # Customer is first in queue
                if reservation.queue_position == 1:
                    due_date = datetime.today().date() + timedelta(days=20)
                    CheckOut.objects.create(
                        customer_id=customer_id,
                        item_id=item_id,
                        checkout_date=datetime.today().date(),
                        due_date=due_date,
                        returned=False
                    )
                    reservation.status = 'Fulfilled'
                    reservation.is_active = False
                    reservation.notification_status = 'Fulfilled'
                    reservation.notified_on = datetime.today().date()
                    reservation.notification_deadline = None
                    reservation.save()

                    # Update queue positions
                    subsequent_reservations = Reservation.objects.filter(
                        item_id=item_id, queue_position__gt=reservation.queue_position, is_active=True
                    )
                    for subsequent_reservation in subsequent_reservations:
                        subsequent_reservation.queue_position -= 1
                        subsequent_reservation.save()

                    successful_checkouts.append({'item_id': item_id, 'due_date': due_date, 'message':"Item checked out sucessfully"})
                    continue

            # Item is not reserved and available for checkout
            due_date = datetime.today().date() + timedelta(days=20)
            CheckOut.objects.create(
                customer_id=customer_id,
                item_id=item_id,
                checkout_date=datetime.today().date(),
                due_date=due_date,
                returned=False
            )
            successful_checkouts.append({'item_id': item_id, 'due_date': due_date, 'message':"Item checked out sucessfully"})

        return Response({'successful_checkouts': successful_checkouts, 'failed_checkouts': failed_checkouts}, status=200)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)
    

@api_view(['POST'])
def check_in_item(request):
    try:
        item_ids = request.data.get('item_ids', [])

        if not isinstance(item_ids, list):
            return Response({'status': 'error', 'message': 'Item IDs must be a list.'}, status=400)

        checked_in_items = []
        not_checked_out_items = []
        not_found_items = []

        for item_id in item_ids:
            try:
                item_id = int(item_id)
            except ValueError:
                not_found_items.append(item_id)
                continue

            check_out_record = CheckOut.objects.filter(item_id=item_id, returned=False).first()
            if check_out_record:
                check_out_record.returned = True
                check_out_record.save()

                return_date = datetime.today().date()
                late_fees = 0.0

                if return_date > check_out_record.due_date:
                    late_days = (return_date - check_out_record.due_date).days
                    late_fees = late_days * 1.5
                    Fines.objects.create(
                        amount=late_fees,
                        paid=False,
                        customer=check_out_record.customer
                    )

                CheckIn.objects.create(
                    item=check_out_record.item,
                    customer=check_out_record.customer,
                    return_date=return_date,
                    late_fees=late_fees
                )

                checked_in_items.append({
                    "item_id": item_id,
                    "late_fees": late_fees
                })
            else:
                not_checked_out_items.append(item_id)

        return Response({
            'status': 'success',
            'checked_in_items': checked_in_items,
            'not_checked_out_items': not_checked_out_items,
            'not_found_items': not_found_items
        }, status=200)

    except Exception as e:
        return Response({'status': 'error', 'message': f'Unexpected error: {str(e)}'}, status=500)

# Reserve an item if it's available for checkout


@api_view(['POST'])
def reserve_item(request, customer_id):
    try:
        item_id = request.data.get('item_id')
        item = Item.objects.filter(item_id=item_id).first()

        if not item:
            return Response({'status': 'error', 'message': 'Item not found.'}, status=404)

        checkout = CheckOut.objects.filter(item_id=item_id, returned=False).first()

        # Check if the item is already checked out
        if not checkout:
            return Response({'status': 'error', 'message': 'Item is available for checkout. No reservation needed.'}, status=400)

        # Determine the next queue position
        current_queue = Reservation.objects.filter(item_id=item_id, is_active=True).count() + 1

        # Add the reservation
        reservation = Reservation.objects.create(
            item_id=item_id,
            customer_id=customer_id,
            reservation_date=datetime.today().date(),
            queue_position=current_queue,
        )
        estimated_checkout_date = checkout.due_date
        return Response({
            'status': 'success',
            'reservation_id': reservation.reservation_id,
            'queue_position': current_queue,
            'message': f'Reservation successful. Your queue position is {current_queue}. Estimated checkout date: {estimated_checkout_date}'
        })
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['POST'])
def notify_next_customer(request, item_id):
    try:
        # Get the next customer in the reservation queue
        reservation = Reservation.objects.filter(item_id=item_id, is_active=True, notification_status='Pending').order_by('queue_position').first()

        if reservation:
            reservation.notification_status = 'Notified'
            reservation.notified_on = datetime.today().date()
            reservation.notification_deadline = datetime.today().date() + timedelta(days=5)
            reservation.save()

            return Response({
                'status': 'success',
                'message': f"Customer {reservation.customer.customer_id} notified. They have until {reservation.notification_deadline} to pick up the item."
            })

        return Response({'status': 'success', 'message': 'No active reservations in the queue.'})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)





@api_view(['POST'])
def notify_next_customer(request, item_id):
    try:
        # Get the next customer in the reservation queue
        reservation = Reservation.objects.filter(item_id=item_id, is_active=True, notification_status='Pending').order_by('queue_position').first()

        if reservation:
            reservation.notification_status = 'Notified'
            reservation.notified_on = datetime.today().date()
            reservation.notification_deadline = datetime.today().date() + timedelta(days=5)
            reservation.save()

            return Response({
                'status': 'success',
                'message': f"Customer {reservation.customer.customer_id} notified. They have until {reservation.notification_deadline} to pick up the item."
            })

        return Response({'status': 'success', 'message': 'No active reservations in the queue.'})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)





def process_expired_reservations():
    expired_reservations = Reservation.objects.filter(
        notification_status='Notified',
        notification_deadline__lt=datetime.today().date(),
        status='Reserved'
    )

    for reservation in expired_reservations:
        reservation.notification_status = 'Expired'
        reservation.is_active = False
        reservation.save()

        # Notify the next customer in the queue
        next_reservation = Reservation.objects.filter(
            item_id=reservation.item_id,
            is_active=True,
            notification_status='Pending'
        ).order_by('queue_position').first()

        if next_reservation:
            next_reservation.notification_status = 'Notified'
            next_reservation.notified_on = datetime.today().date()
            next_reservation.notification_deadline = datetime.today().date() + timedelta(days=5)
            next_reservation.save()


@api_view(['GET'])
def get_reservation_status(request, item_id):
    try:
        reservations = Reservation.objects.filter(item_id=item_id).order_by('queue_position')
        reservation_data = [
            {
                'customer_id': r.customer.customer_id,
                'status': r.status,
                'queue_position': r.queue_position,
                'notification_status': r.notification_status,
                'notified_on': r.notified_on,
                'notification_deadline': r.notification_deadline
            }
            for r in reservations
        ]
        return Response({'status': 'success', 'reservations': reservation_data})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


def item_list(request):
    try:
        items = Item.objects.all()  # Fetch all items in the system
        items_data = []

        for item in items:
            # Determine if the item is currently available for checkout
            is_available = not CheckOut.objects.filter(item_id=item.item_id, returned=False).exists()

            # Fetch only active reservations for the item
            active_reservations = Reservation.objects.filter(item=item, is_active=True).order_by('queue_position')

            # Construct the active reservation queue data
            reservation_queue = [
                {
                    "customer_id": reservation.customer.customer_id,
                    "queue_position": reservation.queue_position,
                    "notification_status": reservation.notification_status,
                    "notification_deadline": reservation.notification_deadline,
                }
                for reservation in active_reservations
            ]

            # Add item details, including availability and active reservation queue
            items_data.append({
                "item_id": item.item_id,
                "name": item.title,
                "available_for_checkout": is_available,
                "reservation_queue": reservation_queue,
            })

        # Return all items with their data in JSON format
        return JsonResponse({"items": items_data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




@api_view(['GET'])
def get_patrons_with_cards(request):
    try:
        patrons = Customer.objects.all()
        response_data = []

        for patron in patrons:
            library_card = LibraryCard.objects.filter(customer_id=patron.customer_id).first()
            card_status = "Active" if library_card and library_card.is_valid() else "Expired"

            response_data.append({
                "PatronID": patron.customer_id,
                "PatronFN": patron.customer_fn,
                "PatronLN": patron.customer_ln,
                "Street_Address": patron.street_address,
                "City": patron.city,
                "State": patron.state,
                "Zip_Code": patron.zip_code,
                "Phone_Number": patron.phone_number,
                "Email_Address": patron.email,
                "LibraryCard": {
                    "CardID": library_card.card_id if library_card else None,
                    "IssueDate": library_card.issue_date if library_card else None,
                    "ExpirationDate": library_card.expire_date if library_card else None,
                    "Status": card_status
                },
            })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_patron_loans(request, patron_id):
    try:
        checkouts = CheckOut.objects.filter(customer_id=patron_id, returned=False)
        loans = [
            {
                "id": checkout.check_out_id,
                "title": checkout.item.title,
                "dueDate": checkout.due_date,
            }
            for checkout in checkouts
        ]
        return Response(loans, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['GET'])
def fetch_borrowed_books(request, customer_id):
    try:
        checkouts = CheckOut.objects.filter(customer_id=customer_id, returned=False)
        if not checkouts.exists():
            return Response({
                'status': 'error',
                'message': 'No borrowed books found for this customer.'
            }, status=404)

        borrowed_books = [
            {
                'book_id': checkout.item.item_id,
                'title': checkout.item.title,
                'due_date': checkout.due_date.strftime('%Y-%m-%d'),
                'renewal_count': checkout.renewal_count,
                'reserved': Reservation.objects.filter(
                    item_id=checkout.item.item_id,
                    status='Reserved',
                    is_active=True
                ).exists()
            }
            for checkout in checkouts
        ]

        return Response({
            'status': 'success',
            'borrowed_books': borrowed_books
        }, status=200)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f"An error occurred: {str(e)}"
        }, status=500)

@api_view(['POST'])
def renew_books(request):
    try:
        customer_id = request.data.get('customer_id')
        book_ids = request.data.get('book_ids', [])
        
        if not customer_id or not book_ids:
            return Response({
                'status': 'error',
                'message': 'Customer ID and book IDs are required.'
            }, status=400)

        # Fetch all eligible checkouts
        checkouts = CheckOut.objects.filter(
            customer_id=customer_id,
            item_id__in=book_ids,
            returned=False
        )

        if not checkouts.exists():
            return Response({
                'status': 'error',
                'message': 'No eligible books found for renewal.'
            }, status=404)

        renewed_books = []
        for checkout in checkouts:
            if Reservation.objects.filter(item_id=checkout.item.item_id, status='Reserved', is_active=True).exists():
                continue  # Skip reserved books
            if checkout.renewal_count >= 3:
                continue  # Skip books that have reached the renewal limit

            checkout.renew()
            renewed_books.append({
                'book_id': checkout.item.item_id,
                'title': checkout.item.title,
                'new_due_date': checkout.due_date.strftime('%Y-%m-%d'),
                'renewal_count': checkout.renewal_count
            })

        if not renewed_books:
            return Response({
                'status': 'error',
                'message': 'No books were eligible for renewal.'
            }, status=400)

        return Response({
            'status': 'success',
            'renewed_books': renewed_books
        }, status=200)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f"An unexpected error occurred: {str(e)}"
        }, status=500)