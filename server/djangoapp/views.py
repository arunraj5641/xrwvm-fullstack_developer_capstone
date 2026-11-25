import json
import logging

from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, post_request, analyze_review_sentiments

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        username = data["userName"]
        password = data["password"]
    except (ValueError, KeyError):
        return JsonResponse({"error": "Invalid login data"}, status=400)

    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return JsonResponse({
            "userName": username, "status": "Authenticated"
        })
    return JsonResponse({
        "userName": username, "status": "Invalid credentials"
    })


def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})


@csrf_exempt
def registration(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    username = data.get("userName", "").strip()
    password = data.get("password", "")
    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()
    email = data.get("email", "").strip()

    if not all([username, password, first_name, last_name, email]):
        return JsonResponse({"error": "All fields are required"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Already Registered"}, status=409)

    user = User.objects.create_user(
        username=username, password=password,
        first_name=first_name, last_name=last_name, email=email
    )
    login(request, user)
    return JsonResponse({
        "userName": user.username, "status": "Authenticated"
    })


def get_cars(request):
    if CarMake.objects.count() == 0:
        initiate()
    models = CarModel.objects.select_related("car_make")
    cars = [
        {"CarModel": item.name, "CarMake": item.car_make.name}
        for item in models
    ]
    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state=None):
    try:
        endpoint = "/fetchDealers"
        if state and state.lower() != "all":
            endpoint += "/" + state
        dealers = get_request(endpoint)
        return JsonResponse({"status": 200, "dealers": dealers})
    except Exception as error:
        logger.exception("Dealership request failed")
        return JsonResponse({"status": 502, "message": str(error)}, status=502)


def get_dealer_details(request, dealer_id):
    try:
        dealer = get_request(f"/fetchDealer/{dealer_id}")
        return JsonResponse({"status": 200, "dealer": dealer})
    except Exception as error:
        logger.exception("Dealer request failed")
        return JsonResponse({"status": 502, "message": str(error)}, status=502)


def get_dealer_reviews(request, dealer_id):
    try:
        reviews = get_request(f"/fetchReviews/dealer/{dealer_id}")
        for review in reviews:
            review["sentiment"] = analyze_review_sentiments(
                review.get("review", "")
            )
        return JsonResponse({"status": 200, "reviews": reviews})
    except Exception as error:
        logger.exception("Review request failed")
        return JsonResponse({"status": 502, "message": str(error)}, status=502)


@csrf_exempt
def add_review(request):
    if request.method != "POST":
        return JsonResponse({"status": 405, "message": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        required = [
            "name", "dealership", "review", "purchase",
            "purchase_date", "car_make", "car_model", "car_year"
        ]
        if not all(key in data for key in required):
            return JsonResponse({
                "status": 400, "message": "Missing review fields"
            }, status=400)

        saved = post_request("/insert_review", data)
        return JsonResponse({"status": 200, "review": saved})
    except Exception as error:
        logger.exception("Review submission failed")
        return JsonResponse({"status": 502, "message": str(error)}, status=502)
