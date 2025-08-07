import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from utils.db import contests_col  # ✅ Import MongoDB collection

def get_atcoder_contests():
    try:
        url = "https://atcoder.jp/contests/"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        upcoming_table = soup.find("div", id="contest-table-upcoming")
        if not upcoming_table:
            return pd.DataFrame()

        rows = upcoming_table.find_all("tr")[1:]  # skip header
        contests = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                title = cols[1].text.strip()
                link = "https://atcoder.jp" + cols[1].find("a")["href"]
                start_time = cols[0].text.strip()
                duration = cols[2].text.strip()

                # Convert to datetime object
                start_time_obj = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S%z")
                start_time_iso = start_time_obj.strftime("%Y-%m-%dT%H:%M:%S")

                # Save to MongoDB if not already there
                contest_doc = {
                    "name": title,
                    "platform": "AtCoder",
                    "link": link,
                    "start_time": start_time_iso,
                    "duration": duration,
                    "reminders_sent": []
                }

                if not contests_col.find_one({
                    "name": title,
                    "platform": "AtCoder",
                    "start_time": start_time_iso
                }):
                    contests_col.insert_one(contest_doc)

                # For display
                contests.append({
                    "Name": f"[{title}]({link})",
                    "Start Time": start_time_obj.strftime("%Y-%m-%d %H:%M"),
                    "Duration": duration,
                    "Link": link
                })

        return pd.DataFrame(contests)

    except Exception as e:
        print(f"❌ Error fetching AtCoder contests: {e}")
        return pd.DataFrame()
