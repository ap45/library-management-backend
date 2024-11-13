from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from .models import Customer

@api_view(['POST'])
def manage_fines(request, customer_id):
    try:
        with transaction.atomic():
            try:
                customer = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                return Response(
                    {"message": "Customer not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if the customer has outstanding fines
            if customer.outstanding_fines > 0:
                # Clear the fines
                customer.outstanding_fines = 0
                customer.save()

                return Response(
                    {"message": "Outstanding fines cleared successfully."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "No outstanding fines for this customer."},
                    status=status.HTTP_200_OK
                )

    except Exception as e:
        return Response(
            {"message": f"An error occurred while managing fines: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )