

from apps.books.views import check_out_item,check_fines, get_patrons_with_cards,get_patron_loans,check_library_card, item_list,renew_library_card,pay_fines,check_in_item,reserve_item,notify_next_customer,get_reservation_status
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/check_out/<int:customer_id>/<int:item_id>/', check_out_item, name='check_out_item'),
    path('api/check_out/<int:customer_id>/', check_out_item, name='check_out_item'),
    path('api/check_fines/<int:customer_id>/', check_fines, name='check_fines'),
    path('api/pay_fines/<int:customer_id>/', pay_fines, name='pay_fines'),
    path('api/check_library_card/<int:customer_id>/', check_library_card, name='check_library_card'),
    path('api/renew_library_card/<int:customer_id>/', renew_library_card, name='renew_library_card'),

   path('api/check_in/', check_in_item, name='check_in_item'),  # updated to handle multiple items at once
    
    # Path for reserving an item
    path('api/reserve_item/<int:customer_id>/', reserve_item, name='reserve_item'),  # updated with customer_id in URL
    
    # Path for processing reservation when an item is checked in
    path('api/notify_next_customer/<int:item_id>/', notify_next_customer, name='notify_next_customer'),
    path('api/reservation_status/<int:item_id>/', get_reservation_status, name='reservation_status'),
    path('api/items/', item_list, name='item_list'),
    path('api/patrons/', get_patrons_with_cards, name='get_patrons_with_cards'),
    path('api/bookcheckouts/<int:patron_id>/', get_patron_loans, name='get_patron_loans'),



]
urlpatterns += [re_path(r'^(?!api/).*$', TemplateView.as_view(template_name='index.html'))]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
