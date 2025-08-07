import requests
import pandas as pd
from datetime import datetime
from utils.db import contests_col  # 🔹 Make sure this line works

def get_codeforces_contests():
    url = "https://codeforces.com/api/contest.list"
    try:
        response = requests.get(url)
        data = response.json()

        if data["status"] != "OK":
            return pd.DataFrame()

        contests = data["result"]
        upcoming = []

        for contest in contests:
            if contest["phase"] == "BEFORE":
                contest_id = contest["id"]
                name = contest["name"]
                link = f"https://codeforces.com/contests/{contest_id}"
                start_time = datetime.utcfromtimestamp(contest["startTimeSeconds"]).strftime('%Y-%m-%dT%H:%M:%S')

                # Convert duration to hours:minutes
                duration_sec = contest["durationSeconds"]
                hours = duration_sec // 3600
                minutes = (duration_sec % 3600) // 60
                duration_str = f"{hours}h {minutes}m"

                # 🔹 Build contest document for MongoDB
                contest_doc = {
                    "name": name,
                    "platform": "Codeforces",
                    "link": link,
                    "start_time": start_time,
                    "duration": duration_str,
                    "reminders_sent": []
                }

                # 🔹 Insert only if not already in the DB
                if not contests_col.find_one({
                    "name": name,
                    "platform": "Codeforces",
                    "start_time": start_time
                }):
                    contests_col.insert_one(contest_doc)

                # 🔹 For displaying in Streamlit
                upcoming.append({
                    "Name": f"[{name}]({link})",
                    "Start Time": start_time.replace("T", " "),
                    "Duration": duration_str,
                    "Link": link
                })

        return pd.DataFrame(upcoming)

    except Exception as e:
        print("❌ Error fetching Codeforces contests:", e)
        return pd.DataFrame()
