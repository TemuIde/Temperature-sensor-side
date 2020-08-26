def check_offline_records():
    try:
        f = open("offline_records.txt", "r")
    except Exception:
        f = open("offline_records.txt", "a")
        f.write("==START OFFLINE LOG==")
    f = open("offline_records.txt", "a")
    return f


print("start")
check_offline_records()
