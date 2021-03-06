import folium
from geopy.exc import GeocoderUnavailable
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request, url_for, flash, redirect
from twitter2 import get_friends


def create_map(friends: list) -> None:
    """creates html file with locations of your twitter friends

    Args:
        friends (list): names and their locations
    """
    map = folium.Map(location=(49.817545, 24.023932), zoom_start=5, control_scale=True)
    friends_locations = {}
    for friend in friends:
        if friend[1] in friends_locations.keys():
            friends_locations[friend[1]].append(friend[0])
        else:
            friends_locations[friend[1]] = [friend[0]]
    friends_layer = folium.FeatureGroup("Your friends")
    for location, names in friends_locations.items():
        iframe = folium.IFrame(
            html=create_html_popup(names),
            width=250,
            height=100,
        )
        friends_layer.add_child(
            folium.Marker(
                location=location,
                popup=folium.Popup(iframe),
                icon=folium.Icon(
                    color="blue",
                    icon="fa-brands fa-twitter",
                    prefix="fa",
                ),
            )
        )
    map.add_child(friends_layer)
    map.add_child(folium.LayerControl())
    map.save("templates/friends_map.html")


def create_html_popup(friends: list) -> str:
    """creates html popup for markrer

    Args:
        friends (list): list of names

    Returns:
        str: html in string format
    """
    html_template = "Friends:"
    for friend in friends:
        html_template += f"""<br>
        <p>{friend}</p><br>
        """
    return html_template


def find_friends(user: str, friends_number: str) -> list:
    """finds certain number of friends locations from twitter api

    Args:
        user (str): username in twitter to search for friends
        friends_number (str): limitation for number of locations to search

    Returns:
        list: names of friiends and their locations
    """
    friends = []
    data = get_friends(user)
    count = 0
    for friend in data["users"]:
        count += 1
        if len(friends) < int(friends_number):
            name = friend["screen_name"]
            location = friend["location"]
            coords = find_coords(location)
            if coords != (-69, -179):
                friends.append((name, coords))
    return friends


def find_coords(location: str) -> tuple:
    """finds coordinates based on address

    Args:
        location (str): address of coords

    Raises:
        GeocoderUnavailable: Error for unknown location

    Returns:
        tuple: latitude and longitude
    """
    # utility for finding location
    from geopy.extra.rate_limiter import RateLimiter

    geolocator = Nominatim(user_agent="my-request")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    try:
        coords = geocode(location)
        if coords != None:
            return coords.latitude, coords.longitude
        else:
            raise GeocoderUnavailable
    except GeocoderUnavailable:
        return -69, -179


# --------------------------Flask application----------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "32fc7730408b163d0fab37cd6ecce7be3c79c33e248db78b"


@app.route("/", methods=("GET", "POST"))
def create_view():
    """Supports main page of web application and gets user and friends number

    Returns:
        tuple: username and friends number and redirect to map
    """
    if request.method == "POST":
        user = request.form["user"]
        friends_number = request.form["friends_number"]
        if not user:
            flash("User is required!")
        elif not friends_number or not friends_number.isnumeric():
            flash("Number of friends is required!")
        else:
            friends = find_friends(user, friends_number)
            create_map(friends)
            return redirect(url_for("map_view"))
    return render_template("index.html")


@app.route("/map/")
def map_view():
    """show map of friends

    Returns:
        html: renders friends_map.html
    """
    return render_template("friends_map.html")


if __name__ == "__main__":
    app.run(debug=True)
