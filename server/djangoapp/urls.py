from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = "djangoapp"

urlpatterns = [
    path("register", views.registration, name="register"),
    path("login", views.login_user, name="login"),
    path("logout", views.logout_request, name="logout"),
    path("get_cars", views.get_cars, name="getcars"),
    path("get_dealers", views.get_dealerships, name="getdealers"),
    path("get_dealers/<str:state>", views.get_dealerships, name="getdealersbystate"),
    path("dealer/<int:dealer_id>", views.get_dealer_details, name="dealer"),
    path("reviews/dealer/<int:dealer_id>", views.get_dealer_reviews, name="dealerreviews"),
    path("add_review", views.add_review, name="addreview"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
