from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

def grab_stats(url):
    # Initialize the WebDriver
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        # Wait until the title contains "Valorant"
        WebDriverWait(driver, 20).until(EC.title_contains("Valorant"))

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

    except NoSuchElementException as e:
        print(f"Error: Could not locate an element on the page. Details: {e}")
        stats = None

    finally:
        # Quit the driver
        driver.quit()

    return stats

def compare_stats(url1, url2):
    # Grab stats for both profiles
    stats1 = grab_stats(url1)
    stats2 = grab_stats(url2)

    # Check if stats were successfully retrieved for both players
    if stats1 is None or stats2 is None:
        print("Failed to retrieve stats for one or both players.")
        return

    # Compare and print the stats side by side, highlighting differences
    print("\nComparison of Stats:")
    for key in stats1.keys():
        stat1 = stats1[key]
        stat2 = stats2[key]
        difference = stat1 - stat2
        if difference > 0:
            print(f"{key}: Player 1 - {stat1} | Player 2 - {stat2} | Player 1 is +{difference} compared to Player 2")
        elif difference < 0:
            print(f"{key}: Player 1 - {stat1} | Player 2 - {stat2} | Player 2 is +{-difference} compared to Player 1")
        else:
            print(f"{key}: Player 1 - {stat1} | Player 2 - {stat2} | No difference")

# Example usage
url1 = "https://tracker.gg/valorant/profile/riot/Zleepy%235065/overview"
url2 = "https://tracker.gg/valorant/profile/riot/Hiroshi%23kota/overview"

compare_stats(url1, url2)
