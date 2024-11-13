

from apps.books.views import check_out_item,check_fines, check_library_card, renew_library_card,pay_fines
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/check_out/<int:customer_id>/<int:item_id>/', check_out_item, name='check_out_item'),
    path('api/check_out/<int:customer_id>/', check_out_item, name='check_out_item'),
    path('api/check_fines/<int:customer_id>/', check_fines, name='check_fines'),
    path('api/pay_fines/<int:customer_id>/', pay_fines, name='pay_fines'),
    path('api/check_library_card/<int:customer_id>/', check_library_card, name='check_library_card'),
    path('api/renew_library_card/<int:customer_id>/', renew_library_card, name='renew_library_card'),

   


]
urlpatterns += [re_path(r'^(?!api/).*$', TemplateView.as_view(template_name='index.html'))]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
