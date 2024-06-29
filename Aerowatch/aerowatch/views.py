from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from .forms import Userform, Registerform
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect,HttpResponse
import requests
from datetime import datetime,timezone,timedelta
from django.core.cache import cache
# Create your views here.

CACHE_TIMEOUT = 86400


def index(request):
    return render(request,"aerowatch/index.html")

def register(request):
    if request.method == "POST":
        form = Registerform(data=request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            if User.objects.filter(email=email).exists():
                return render(request, "aerowatch/register.html", {
                    "form": form,
                    "message": "Email already used by existing account"
                })  
            else:
                user = User.objects.create_user(email, email, password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                login(request, user)
                # Redirect to a homepage page.
                return redirect("index")
        else:
            form = Registerform()
            return render(request, "aerowatch/register.html", {
                    "form": form
                })
    else:
        form = Registerform()
        return render(request, "aerowatch/register.html", {
                "form": form
            })

def user_login(request):
    if request.method == "POST":
        form = Userform(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a homepage page.
                return redirect("index")
            else:
                # Return an 'invalid login' error message.
                return render(request, "aerowatch/login.html", {
                    "message": "Wrong email and/or password. Click login and retry again!"
                })
        else:
            form = Userform()
            return render(request, "aerowatch/login.html", {
                    "form": form

                })
    else:
        form = Userform()
        return render(request, "aerowatch/login.html", {
                "form": form
            })

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def get_airlines_data():
    airlines_data = cache.get('airlines_data')
    if not airlines_data:
        airlines_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat"
        response = requests.get(airlines_url)
        airlines_data = response.text
        cache.set('airlines_data', airlines_data, CACHE_TIMEOUT)
    return airlines_data

def airline_mapping(icao):
    data = get_airlines_data()
    airlines = data.split("\n")
    airlines_list = []

    for line in airlines:
        airline_data = line.split(",")
        if len(airline_data) > 5:
            airline = {
                "name" : airline_data[1].strip('"'),
                "icao" : airline_data[4].strip('"')
            }
            airlines_list.append(airline)
    for airline in airlines_list:
        if airline["icao"] == icao:
            return(airline)
    return None

def get_airport_data():
    airport_data = cache.get('airport_data')
    if not airport_data:
        airport_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
        response = requests.get(airport_url)
        airport_data = response.text
        cache.set('airport_data', airport_data, CACHE_TIMEOUT)
    return airport_data

def airport_mapping(icao):
    data = get_airport_data()
    airport = data.split("\n")
    airport_list = []
    for line in airport:
        airport_data = line.split(",")
        if len(airport_data) > 4:
            airport = {
                "name" : airport_data[1].strip('"'),
                "icao" : airport_data[5].strip('"'),
                "country" :airport_data[3].strip('"'),
                "city": airport_data[2].strip('"')
            }
            airport_list.append(airport)
    for airport in airport_list:
        if airport["icao"] == icao:
            return(airport)
    return None
@login_required
def search(request,filter,icao):
    if filter == "arrival":
        # Define the start and end time for today
        now = datetime.now(timezone.utc)
        begin = int(datetime(now.year, now.month, now.day, 0, 0, 0).timestamp())
        end = int(datetime(now.year, now.month, now.day, 23, 59, 59).timestamp())
        username = "herosubby"
        password = "Ayosubomi123"

        url= f"https://opensky-network.org/api/flights/arrival?airport={icao}&begin={begin}&end={end}"

        response = requests.get(url, auth=(username, password))
        if response.status_code == 200:
            arrivals = response.json()
            for arrival in arrivals:
                if len(arrival["callsign"]) > 4: 
                    icao = arrival["callsign"][:3]
                    result = airline_mapping(icao)
                    if result:
                        arrival["callsign"] = f"{result['name']}({result['icao']})"
                    else:
                        arrival["callsign"] = f"unknown {icao}"
                if arrival["lastSeen"] and arrival["firstSeen"]:
                    first_seen = datetime.fromtimestamp(arrival["firstSeen"], tz=timezone.utc)
                    last_seen = datetime.fromtimestamp(arrival["lastSeen"], tz=timezone.utc)
                    new_first_seen = first_seen.strftime('%Y-%m-%d %H:%M:%S %Z')
                    new_last_seen = last_seen.strftime('%Y-%m-%d %H:%M:%S %Z')
                    arrival["firstSeen"] = new_first_seen
                    arrival["lastSeen"] = new_last_seen
                eda = airport_mapping(arrival["estDepartureAirport"])
                if eda:
                    arrival["estDepartureAirport"] =  f"{eda['name']}({eda['icao']}),{eda['city']},{eda['country']}"
                else:
                    arrival["estDepartureAirport"] =  f"unknown"
                eaa = airport_mapping(arrival["estArrivalAirport"])
                if eaa:
                    arrival["estArrivalAirport"] =  f"{eaa['name']}({eaa['icao']}){eaa['city']},{eaa['country']}"
                else:
                    arrival["estArrivalAirport"] =  f"unknown"
            return render(request, "aerowatch/arrival_search_results.html", {
            "flights" : arrivals
        })
        else:
            return HttpResponse("NO ARRIVALS TRACKED HERE")
    elif filter == "destination":
        # Define the start and end time for today
        now = datetime.now(timezone.utc)
        begin = int(datetime(now.year, now.month, now.day, 0, 0, 0).timestamp())
        end = int(datetime(now.year, now.month, now.day, 23, 59, 59).timestamp())
        username = "herosubby"
        password = "Ayosubomi123"

        url= f"https://opensky-network.org/api/flights/departure?airport={icao}&begin={begin}&end={end}"
        response = requests.get(url, auth=(username, password))
        if response.status_code == 200:
            departures = response.json()
            for departure in departures:
                if len(departure["callsign"]) > 4: 
                    icao = departure["callsign"][:3]
                    result = airline_mapping(icao)
                    if result:
                        departure["callsign"] =  f"{result['name']}({result['icao']})"
                    else:
                        departure["callsign"] = f"unknown {icao}"
                if departure["lastSeen"] and departure["firstSeen"]:
                    first_seen = datetime.fromtimestamp(departure["firstSeen"], tz=timezone.utc)
                    last_seen = datetime.fromtimestamp(departure["lastSeen"], tz=timezone.utc)
                    new_first_seen = first_seen.strftime('%Y-%m-%d %H:%M:%S %Z')
                    new_last_seen = last_seen.strftime('%Y-%m-%d %H:%M:%S %Z')
                    departure["firstSeen"] = new_first_seen
                    departure["lastSeen"] = new_last_seen
                eda = airport_mapping(departure["estDepartureAirport"])
                if eda:
                    departure["estDepartureAirport"] =  f"{eda['name']}({eda['icao']}){eda['city']},{eda['country']}"
                else:
                    departure["estDepartureAirport"] =  f"unknown"
                eaa = airport_mapping(departure["estArrivalAirport"])
                if eaa:
                    departure["estArrivalAirport"] =  f"{eaa['name']}({eaa['icao']}){eaa['city']},{eaa['country']}"
                else:
                    departure["estArrivalAirport"] =  f"unknown"
            return render(request, "aerowatch/departure_search_results.html", {
            "flights" : departures
        })
        else:
            return HttpResponse("NO DEPARTURE TRACKED HERE")
        
def route(request,d_icao,a_icao):
    flights = []
    # Define the start and end time for today
    now = datetime.now(timezone.utc)
    begin = int(datetime(now.year, now.month, now.day, 0, 0, 0).timestamp())
    end = int(datetime(now.year, now.month, now.day, 23, 59, 59).timestamp())
    username = "herosubby"
    password = "Ayosubomi123"
    
    url= f"https://opensky-network.org/api/flights/departure?airport={d_icao}&begin={begin}&end={end}"
    response = requests.get(url, auth=(username, password))
    if response.status_code == 200:
        departures = response.json()
        for departure in departures:
            if departure['estArrivalAirport'] == a_icao:
                flights.append(departure)        
        for flight in flights:
            if len(flight["callsign"]) > 4: 
                icao = flight["callsign"][:3]
                result = airline_mapping(icao)
                if result:
                    flight["callsign"] = f"{result['name']}({result['icao']})"
                else :
                    flight["callsign"] = f"unknown {icao}"
            if flight["lastSeen"] and flight["firstSeen"]:
                first_seen = datetime.fromtimestamp(flight["firstSeen"], tz=timezone.utc)
                last_seen = datetime.fromtimestamp(flight["lastSeen"], tz=timezone.utc)
                new_first_seen = first_seen.strftime('%Y-%m-%d %H:%M:%S %Z')
                new_last_seen = last_seen.strftime('%Y-%m-%d %H:%M:%S %Z')
                flight["firstSeen"] = new_first_seen
                flight["lastSeen"] = new_last_seen
            eda = airport_mapping(flight["estDepartureAirport"])
            if eda:
                flight["estDepartureAirport"] =  f"{eda['name']}({eda['icao']}){eda['city']},{eda['country']}"
            else:
                flight["estDepartureAirport"] =  f"unknown"
            eaa = airport_mapping(flight["estArrivalAirport"])
            if eaa:
                flight["estArrivalAirport"] =  f"{eaa['name']}({eaa['icao']}){eaa['city']},{eaa['country']}"
            else:
                flight["estArrivalAirport"] =  f"unknown{eaa}"
        return render(request, "aerowatch/search_results.html", {
            "flights" : flights
        })
    else:
        return HttpResponse("NO ROUTES FOUND")
    

