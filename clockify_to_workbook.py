import calendar
import clockify
from datetime import datetime
from datetime import timezone
import dateutil.parser
import sys
import xlsxwriter


XLS_FILE = 'worked_days.xlsx'
NOW = datetime.now(timezone.utc)


def get_earlier_date(datetime1, datetime2):
    if not datetime1:
        return datetime2
    if not datetime2:
        return datetime1
    if datetime1 < datetime2:
        return datetime1
    else:
        return datetime2


def get_later_date(datetime1, datetime2):
    if not datetime1:
        return datetime2
    if not datetime2:
        return datetime1
    if datetime1 > datetime2:
        return datetime1
    else:
        return datetime2


def process_time_entries(time_entries):
    daily_work = {}
    for entry in time_entries:
        start_time = dateutil.parser.parse(entry["timeInterval"]["start"])
        day_details = daily_work.get(start_time.day, {})
        day_details["start_time"] = get_earlier_date(start_time, day_details.get("start_time"))

        try:
            end_time = dateutil.parser.parse(entry["timeInterval"]["end"])
        except TypeError:
            end_time = NOW
        if end_time.date() > start_time.date():
            end_time = datetime(year=start_time.year, month=start_time.month, day=start_time.day,
                                hour=23, minute=59, second=59, microsecond=999, tzinfo=start_time.tzinfo)
        day_details["end_time"] = get_later_date(end_time, day_details.get("end_time"))

        total_time_diff = day_details["end_time"] - day_details["start_time"]
        day_details["work_day_hours"] = round(total_time_diff.total_seconds() / (60 * 60), 1)

        time_diff = end_time - start_time
        duration_hours = day_details.get("duration_hours", 0)
        day_details["duration_hours"] = round(duration_hours + time_diff.total_seconds() / (60 * 60), 1)

        clients = day_details.get("clients", set())
        if entry["project"] and entry["project"]["clientName"]:
            clients.add(entry["project"]["clientName"])
        day_details["clients"] = clients

        daily_work[start_time.day] = day_details

    return daily_work


def export_to_workbook(daily_work, month=NOW.month):
    workbook = xlsxwriter.Workbook(XLS_FILE)
    worksheet = workbook.add_worksheet(calendar.month_name[month])

    worksheet.write(0, 0, "Day")
    worksheet.write(0, 1, "Hours")
    worksheet.write(0, 2, "Clients")

    for key in range(1, 32):
        worksheet.write(key, 0, key)
        day_details = daily_work.get(key)
        if day_details:
            worksheet.write(key, 1, day_details["work_day_hours"])
            worksheet.write(key, 2, ', '.join(day_details["clients"]))
    workbook.close()


def main():
    month = NOW.month
    if len(sys.argv) == 1:
        time_entries = clockify.get_time_entries()
    elif len(sys.argv) == 2:
        month = int(sys.argv[1])
        time_entries = clockify.get_time_entries(month)
    else:
        time_entries = clockify.get_time_entries(int(sys.argv[1]), int(sys.argv[2]))

    daily_work = process_time_entries(time_entries)
    # print(json.dumps(daily_work, indent=2, sort_keys=True, default=str))

    export_to_workbook(daily_work, month=month)

    print("Done")


if __name__ == '__main__':
    main()
