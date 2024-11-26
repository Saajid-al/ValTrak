from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def grab_stats(user):
    # Initialize the WebDriver
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

def calculate_weighted_score(stats):
    # Weights as per the user's requirement
    weights = {
        "Damage/Round": 0.50,
        "K/D Ratio": 0.25,
        "Headshot %": 0.15,
        "Win %": 0.05
    }

    # Calculate the weighted score
    score = (
        stats["Damage/Round"] * weights["Damage/Round"] +
        stats["K/D Ratio"] * weights["K/D Ratio"] +
        stats["Headshot %"] * weights["Headshot %"] +
        stats["Win %"] * weights["Win %"]
    )
    return score

def compare_stats(User1, User2):
    # Grab stats for both profiles
    stats1 = grab_stats(User1)
    stats2 = grab_stats(User2)

    # Check if stats were successfully retrieved for both players
    if stats1 is None or stats2 is None:
        print("Failed to retrieve stats for one or both players.")
        return

    # Calculate weighted scores
    score1 = calculate_weighted_score(stats1)
    score2 = calculate_weighted_score(stats2)

    # Determine the winning probability
    total_score = score1 + score2
    chance_player1 = (score1 / total_score) * 100
    chance_player2 = (score2 / total_score) * 100

    # Print comparison
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

    # Print the scores and chances
    print("\nWeighted Scores:")
    print(f"Player 1 Score: {score1:.2f}")
    print(f"Player 2 Score: {score2:.2f}")

    print("\nWinning Chances:")
    print(f"Player 1: {chance_player1:.2f}%")
    print(f"Player 2: {chance_player2:.2f}%")

def main():
    # Example usage
    User1 = input("Please enter a valid Valorant username (e.g., Zappy#2322) ")
    User2 = input("Please enter a second Valorant username")

    print("Please wait while we compute your prediction...")

    compare_stats(User1, User2)

if __name__ == "__main__":
    main()
