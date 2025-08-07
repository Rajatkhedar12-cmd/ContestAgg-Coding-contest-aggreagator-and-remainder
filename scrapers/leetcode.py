import requests
import pandas as pd
from datetime import datetime, timedelta
from utils.db import contests_col


def get_leetcode_contests():
    url = "https://leetcode.com/graphql"

    query = {
        "query": """
        {
          allContests {
            title
            titleSlug
            startTime
            duration
          }
        }
        """
    }

    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com/contest/",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.post(url, json=query, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()

        contests = []
        for contest in data["data"]["allContests"]:
            start = datetime.fromtimestamp(contest["startTime"])
            dur = str(timedelta(seconds=contest["duration"]))
            contest_doc = {
                "name": contest["title"],
                "platform": "LeetCode",
                "link": f'https://leetcode.com/contest/{contest["titleSlug"]}',
                "start_time": start.strftime("%Y-%m-%dT%H:%M:%S"),
                "duration": dur,
                "reminders_sent": []
            }

            # Only insert if not already present
            if not contests_col.find_one({
                "name": contest_doc["name"],
                "platform": "LeetCode",
                "start_time": contest_doc["start_time"]
            }):
                contests_col.insert_one(contest_doc)

            contests.append({
                "Name": contest_doc["name"],
                "Start Time": start.strftime("%Y-%m-%d %H:%M"),
                "Duration": dur,
                "Link": contest_doc["link"]
            })


        # Filter for upcoming only (after now)
        upcoming = [c for c in contests if datetime.strptime(c["Start Time"], "%Y-%m-%d %H:%M") > datetime.now()]
        return pd.DataFrame(upcoming)

    except Exception as e:
        print(f"❌ Error fetching LeetCode contests: {e}")
        return pd.DataFrame()
