from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

from django.http import JsonResponse
import logging
import json
from django.views.decorators.csrf import csrf_exempt

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Handle sign in request
@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    username = data.get("userName")
    password = data.get("password")

    # Try to check if provided credentials can be authenticated
    user = authenticate(username=username, password=password)

    # Default response if authentication fails
    response_data = {"userName": username}

    if user is not None:
        # If user is valid, log them in
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(response_data)

    # If authentication fails, return 401 with same structure as original code
    return JsonResponse(response_data, status=401)


# Handle sign out request
@csrf_exempt
def logout_request(request):
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)


# Handle sign up request
@csrf_exempt
def registration(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    username = data.get("userName")
    password = data.get("password")
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    email = data.get("email")

    try:
        # Check if user already exists
        User.objects.get(username=username)
        # If found, user is already registered
        return JsonResponse({"error": "Already Registered"}, status=400)
    except User.DoesNotExist:
        # If not, create new user
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        # Login the user after registration
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)


# Render list of dealerships
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


# Render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint)

    # Analyze sentiment for each review
    for review_detail in reviews:
        try:
            sentiment = analyze_review_sentiments(
                review_detail.get("review", "")
                )
            review_detail["sentiment"] = sentiment
        except Exception as e:
            logger.exception("Error analyzing review sentiment: %s", e)
            # If sentiment analysis fails, set default sentiment
            review_detail["sentiment"] = "neutral"

    return JsonResponse({"status": 200, "reviews": reviews})


# Render the dealer details
def get_dealer_details(request, dealer_id):
    endpoint = f"/fetchDealer/{dealer_id}"
    dealership = get_request(endpoint)
    return JsonResponse({"status": 200, "dealer": dealership})


# Submit a review
@csrf_exempt
def add_review(request):
    if request.user.is_anonymous:
        return JsonResponse(
            {"status": 403, "message": "Unauthorized"}, status=403
            )

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": 400, "message": "Invalid JSON body"}, status=400
            )

    try:
        post_review(data)
        return JsonResponse({"status": 200})
    except Exception as e:
        logger.exception("Error posting review: %s", e)
        return JsonResponse(
            {"status": 401, "message": "Error in posting review"},
            status=401
        )


def get_cars(request):
    count = CarMake.objects.count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related("car_make")
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })
    return JsonResponse({"CarModels": cars})
