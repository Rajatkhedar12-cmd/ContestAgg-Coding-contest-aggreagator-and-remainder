import streamlit as st
from auth.login import login_user, register_user
from utils.db import favorites_col  # 💾 For storing/removing reminders
import threading
import time
from reminder_scheduler import send_due_reminders  # ← import your scheduler
def reminder_loop():
    while True:
        print("🔁 Checking for due reminders...")
        try:
            send_due_reminders()
        except Exception as e:
            print("❌ Reminder error:", e)
        time.sleep(600)  # every 10 minutes

st.set_page_config(layout="wide")
# Launch background reminder thread once
if "reminder_thread_started" not in st.session_state:
    t = threading.Thread(target=reminder_loop, daemon=True)
    t.start()
    st.session_state["reminder_thread_started"] = True

st.title("🚀 Coding Contest Aggregator")

# Initialize session state
if "user" not in st.session_state:
    st.session_state["user"] = None

# Sidebar menu
menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Dashboard"])

# ----------------------------- REGISTER -----------------------------
if menu == "Register":
    st.subheader("Create an Account")
    username = st.text_input("Choose a Username")
    email = st.text_input("Enter your Email")
    password = st.text_input("Choose a Password", type="password")
    if st.button("Register"):
        if username and password and email:
            register_user(username, password, email)
        else:
            st.warning("All fields are required.")

# ----------------------------- LOGIN -----------------------------
elif menu == "Login":
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.success(f"Welcome, {username}!")

# ----------------------------- DASHBOARD -----------------------------
elif menu == "Dashboard":
    if not st.session_state["user"]:
        st.warning("Please log in to view your dashboard.")
    else:
        st.subheader(f"Welcome from Rajat Khedar, {st.session_state['user']} 👋")

        from scrapers.codeforces import get_codeforces_contests
        from scrapers.leetcode import get_leetcode_contests
        from scrapers.atcoder import get_atcoder_contests

        # ------------------ CODEFORCES ------------------
        st.markdown("### 🟦 Upcoming Codeforces Contests")
        cf_df = get_codeforces_contests()
        if not cf_df.empty:
            for _, row in cf_df.iterrows():
                with st.expander(f"{row['Name']}"):
                    st.write(f"🕒 Start Time: {row['Start Time']}")
                    st.write(f"⏱ Duration: {row['Duration']}")
                    st.write(f"🔗 [Open Contest]({row['Link']})")

                    contest_key = f"{row['Name']}_{row['Start Time']}"
                    is_fav = favorites_col.find_one({
                        "username": st.session_state["user"]["username"],
                        "contest_key": contest_key
                    })

                    remind = st.checkbox("🔔 Remind me about this contest", key=contest_key, value=is_fav is not None)

                    if remind and not is_fav:
                        favorites_col.insert_one({
                            "username": st.session_state["user"]["username"],
                            "contest_key": contest_key,
                            "platform": "Codeforces",
                            "name": row["Name"],
                            "start_time": row["Start Time"],
                            "link": row["Link"]
                        })
                    elif not remind and is_fav:
                        favorites_col.delete_one({
                            "username": st.session_state["user"]["username"],
                            "contest_key": contest_key
                        })
        else:
            st.warning("Unable to fetch Codeforces contests.")

        # ------------------ LEETCODE ------------------
        st.divider()
        st.markdown("### 🟨 Upcoming LeetCode Contests")
        lc_df = get_leetcode_contests()
        if not lc_df.empty:
            for _, row in lc_df.iterrows():
                with st.expander(f"{row['Name']}"):
                    st.write(f"🕒 Start Time: {row['Start Time']}")
                    st.write(f"⏱ Duration: {row['Duration']}")
                    st.write(f"🔗 [Open Contest]({row['Link']})")

                    contest_key = f"{row['Name']}_{row['Start Time']}"
                    is_fav = favorites_col.find_one({
                        "username": st.session_state["user"]["username"],
                        "contest_key": contest_key
                    })

                    remind = st.checkbox("🔔 Remind me about this contest", key=contest_key, value=is_fav is not None)

                    if remind and not is_fav:
                        favorites_col.insert_one({
                            "username": st.session_state["user"]["username"],
                            "contest_key": contest_key,
                            "platform": "LeetCode",
                            "name": row["Name"],
                            "start_time": row["Start Time"],
                            "link": row["Link"]
                        })
                    elif not remind and is_fav:
                        favorites_col.delete_one({
                            "username": st.session_state["user"]["username"],
                            "contest_key": contest_key
                        })
        else:
            st.warning("Unable to fetch LeetCode contests.")

        # ------------------ ATCODER ------------------
        st.divider()
        st.markdown("### 🔴 Upcoming AtCoder Contests")
        ac_df = get_atcoder_contests()
        if not ac_df.empty:
            for _, row in ac_df.iterrows():
                with st.expander(f"{row['Name']}"):
                    st.write(f"🕒 Start Time: {row['Start Time']}")
                    st.write(f"⏱ Duration: {row['Duration']}")
                    st.write(f"🔗 [Open Contest]({row['Link']})")

                    contest_key = f"{row['Name']}_{row['Start Time']}"
                    is_fav = favorites_col.find_one({
                        "username": st.session_state["user"]["username"],
                        "contest_key": contest_key
                    })

                    remind = st.checkbox("🔔 Remind me about this contest", key=contest_key, value=is_fav is not None)

                    if remind and not is_fav:
                        favorites_col.insert_one({
                            "username": st.session_state["user"]["username"],
                            "contest_key": contest_key,
                            "platform": "AtCoder",
                            "name": row["Name"],
                            "start_time": row["Start Time"],
                            "link": row["Link"]
                        })
                    elif not remind and is_fav:
                        favorites_col.delete_one({
                            "username": st.session_state["user"]["username"],
                            "contest_key": contest_key
                        })
        else:
            st.warning("Unable to fetch AtCoder contests.")
