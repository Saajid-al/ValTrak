from django.shortcuts import render

from django.http import HttpResponse
# stats/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

@csrf_exempt
def get_user_stats(request):
    if request.method == "POST":
        # Extract the username from the request body
        body = json.loads(request.body)
        user = body.get("username")

        # checking if the username is provided in the first place
        if not user:
            return JsonResponse({"error": "Username is required"}, status=400)

        # calling grab stats function (selenium)
        stats = grab_stats(user)
        if stats is None:
            return JsonResponse({"error": "Failed to retrieve stats or user does not exist"}, status=404)
        
        return JsonResponse({"stats": stats}, status=200)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)

def grab_stats(user):
    name, id = user.split("#")
    driver = webdriver.Chrome()
    baseUrl = "https://tracker.gg/valorant/profile/riot/"
    encoded_id = f'%23{id}'  # Encoding the '#' character to '%23'
    url = f"{baseUrl}{name}{encoded_id}"
    driver.get(url)

    stats = None

    try:
        # Wait until the title contains "Valorant"
        WebDriverWait(driver, 20).until(EC.title_contains("Valorant"))

        if "Page Not Found" in driver.page_source or "Not Found" in driver.page_source:
            raise NoSuchElementException("The requested user profile does not exist.")



        # Wait for the giant stats container to be present
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "giant-stats")))
        giant_stats_container = driver.find_element(By.CLASS_NAME, "giant-stats")

        # Grab the desired stats
        damage_round_value = giant_stats_container.find_element(By.XPATH, ".//span[text()='Damage/Round']/following-sibling::span[@class='flex items-center gap-2']/span[@class='value']").text
        kd_value = giant_stats_container.find_element(By.XPATH, ".//span[text()='K/D Ratio']/following-sibling::span[@class='flex items-center gap-2']/span[@class='value']").text
        headshot_value = giant_stats_container.find_element(By.XPATH, ".//span[text()='Headshot %']/following-sibling::span[@class='flex items-center gap-2']/span[@class='value']").text
        win_percentage = giant_stats_container.find_element(By.XPATH, ".//span[text()='Win %']/following-sibling::span[@class='flex items-center gap-2']/span[@class='value']").text

        # Store stats in a dictionary
        stats = {
            "Damage/Round": float(damage_round_value),
            "K/D Ratio": float(kd_value),
            "Headshot %": float(headshot_value.strip('%')),
            "Win %": float(win_percentage.strip('%'))
        }

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error: Could not locate an element or the page took too long to load. Details: {e}")

    finally:
        # Quit the driver
        driver.quit()

    return stats

def home(request):
    return HttpResponse("Hello, this is the stats home page!")
