from utils.db import favorites_col, users_col
from emailer import send_email_reminder
from datetime import datetime, timedelta
import pytz

# IST Timezone
IST = pytz.timezone("Asia/Kolkata")

# Reminder time windows
REMINDER_WINDOWS = {
    "2_days": timedelta(days=2),
    "1_day": timedelta(days=1),
    "2_hours": timedelta(hours=2)
}

def send_due_reminders():
    now = datetime.now(IST)

    favorites = list(favorites_col.find({}))

    for fav in favorites:
        try:
            start_time_str = fav["start_time"]
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
            start_time = IST.localize(start_time)

            for label, delta in REMINDER_WINDOWS.items():
                reminder_time = start_time - delta

                # Send if we're within a 1-hour window and not sent yet
                if reminder_time <= now <= reminder_time + timedelta(minutes=59):
                    reminders_sent = fav.get("reminders_sent", [])
                    if label not in reminders_sent:
                        # Get user's email
                        user = users_col.find_one({"username": fav["username"]})
                        if not user or not user.get("email"):
                            continue

                        # Send email
                        send_email_reminder(
                            to_email=user["email"],
                            subject=f"⏰ {label.replace('_', ' ').title()} Reminder: {fav['name']}",
                            body=f"""👋 Hello {fav['username']},

This is your {label.replace('_', ' ')} reminder for an upcoming contest:

📌 **{fav['name']}**  
🌐 Platform: {fav['platform']}  
🕒 Start Time: {fav['start_time']}  
🔗 Link: {fav['link']}

Good luck! and Best Wishes! from Rajat Khedar 🚀
                            """
                        )

                        # Mark reminder as sent
                        favorites_col.update_one(
                            {"_id": fav["_id"]},
                            {"$push": {"reminders_sent": label}}
                        )
        except Exception as e:
            print(f"❌ Error processing reminder for {fav.get('contest_key')}: {e}")

if __name__ == "__main__":
    send_due_reminders()
