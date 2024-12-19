from datetime import datetime, timedelta

def calculate_rahu_kalam(date_str):
    base_time = datetime.strptime("7:30 AM", "%I:%M %p")
    day_of_week = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    n = {"Monday": 1, "Saturday": 2, "Friday": 3, "Wednesday": 4,
         "Thursday": 5, "Tuesday": 6, "Sunday": 7}[day_of_week]

    start_offset = (n - 1) * 1.5  # in hours
    start_time = base_time + timedelta(hours=start_offset)
    end_time = start_time + timedelta(hours=1.5)

    return start_time.strftime("%I:%M %p"), end_time.strftime("%I:%M %p")
