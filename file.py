import os

ROOMS_FILE = "rooms.txt"
BOOKINGS_FILE = "bookings.txt"
CHECK_INS_FILE = "check_ins.txt"
SERVICES_FILE = "services.txt"
BILLS_FILE = "bills.txt"

rooms = {}
bookings = []
check_ins = []
services = []
bills = {}

def load_data():
    global rooms, bookings, check_ins, services, bills
    if os.path.exists(ROOMS_FILE):
        with open(ROOMS_FILE, "r") as f:
            for line in f:
                room_number, room_type, price, available = line.strip().split(",")
                rooms[room_number] = {
                    "type": room_type,
                    "price": float(price),
                    "available": available == "True"
                }
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r") as f:
            for line in f:
                room_number, guest_name, contact_details, duration = line.strip().split(",")
                bookings.append({
                    "room_number": room_number,
                    "guest_name": guest_name,
                    "contact_details": contact_details,
                    "duration": int(duration)
                })
    if os.path.exists(CHECK_INS_FILE):
        with open(CHECK_INS_FILE, "r") as f:
            for line in f:
                room_number, guest_name = line.strip().split(",")
                check_ins.append({"room_number": room_number, "guest_name": guest_name})
    if os.path.exists(SERVICES_FILE):
        with open(SERVICES_FILE, "r") as f:
            for line in f:
                room_number, service, cost = line.strip().split(",")
                services.append({
                    "room_number": room_number,
                    "service": service,
                    "cost": float(cost)
                })
    if os.path.exists(BILLS_FILE):
        with open(BILLS_FILE, "r") as f:
            for line in f:
                guest_name, room_charge, service_charge, total = line.strip().split(",")
                bills[guest_name] = {
                    "room_charge": float(room_charge),
                    "service_charge": float(service_charge),
                    "total": float(total)
                }

def save_data():
    with open(ROOMS_FILE, "w") as f:
        for room_number, details in rooms.items():
            f.write(f"{room_number},{details['type']},{details['price']},{details['available']}\n")
    with open(BOOKINGS_FILE, "w") as f:
        for booking in bookings:
            f.write(f"{booking['room_number']},{booking['guest_name']},{booking['contact_details']},{booking['duration']}\n")
    with open(CHECK_INS_FILE, "w") as f:
        for check_in in check_ins:
            f.write(f"{check_in['room_number']},{check_in['guest_name']}\n")
    with open(SERVICES_FILE, "w") as f:
        for service in services:
            f.write(f"{service['room_number']},{service['service']},{service['cost']}\n")
    with open(BILLS_FILE, "w") as f:
        for guest_name, charges in bills.items():
            f.write(f"{guest_name},{charges['room_charge']},{charges['service_charge']},{charges['total']}\n")

def add_room():
    room_number = input("Enter room number: ")
    if room_number in rooms:
        print("Room number already exists.")
        return
    room_type = input("Enter room type (single, double, suite): ").lower()
    if room_type not in ["single", "double", "suite"]:
        print("Invalid room type.")
        return
    try:
        price = float(input("Enter price per night: "))
    except ValueError:
        print("Invalid price entered.")
        return
    rooms[room_number] = {"type": room_type, "price": price, "available": True}
    save_data()
    print(f"Room {room_number} added successfully.")

def view_rooms():
    print("\n--- Room List ---")
    if not rooms:
        print("No rooms available.")
        return
    for room_number, details in rooms.items():
        availability = "Available" if details["available"] else "Occupied"
        print(f"Room {room_number}: Type={details['type']}, Price={details['price']}, Status={availability}")

def book_room():
    guest_name = input("Enter guest name: ").strip()
    contact_details = input("Enter contact details: ").strip()
    room_type = input("Enter room type to book (single, double, suite): ").lower()
    available_rooms = [room for room, details in rooms.items() if details["type"] == room_type and details["available"]]
    if not available_rooms:
        print(f"No available {room_type} rooms.")
        return
    print(f"Available {room_type} rooms: {', '.join(available_rooms)}")
    room_number = input("Enter room number to book: ").strip()
    if room_number not in available_rooms:
        print("Invalid room selection.")
        return
    try:
        duration = int(input("Enter duration of stay (nights): "))
        if duration <= 0:
            print("Duration must be at least 1 night.")
            return
    except ValueError:
        print("Invalid duration entered.")
        return
    bookings.append({
        "room_number": room_number,
        "guest_name": guest_name,
        "contact_details": contact_details,
        "duration": duration
    })
    rooms[room_number]["available"] = False
    save_data()
    print(f"Room {room_number} booked successfully for {guest_name}.")

def view_bookings():
    print("\n--- Bookings ---")
    if not bookings:
        print("No bookings made.")
        return
    for booking in bookings:
        print(f"Room {booking['room_number']} booked by {booking['guest_name']} for {booking['duration']} nights.")

def check_in():
    guest_name = input("Enter guest name: ").strip()
    for booking in bookings:
        if booking["guest_name"] == guest_name:
            room_number = booking["room_number"]
            check_ins.append({"room_number": room_number, "guest_name": guest_name})
            bookings.remove(booking)
            save_data()
            print(f"{guest_name} checked into room {room_number}.")
            return
    print("Booking not found.")

def check_out():
    guest_name = input("Enter guest name: ").strip()
    for check_in_record in check_ins:
        if check_in_record["guest_name"] == guest_name:
            room_number = check_in_record["room_number"]
            check_ins.remove(check_in_record)
            rooms[room_number]["available"] = True
            room_charge = rooms[room_number]["price"]
            service_charge = sum(service["cost"] for service in services if service["room_number"] == room_number)
            total = room_charge + service_charge
            bills[guest_name] = {"room_charge": room_charge, "service_charge": service_charge, "total": total}
            save_data()
            print(f"{guest_name} checked out. Total bill: {total}")
            return
    print("Check-in record not found.")

def add_service():
    room_number = input("Enter room number: ").strip()
    if room_number not in rooms or rooms[room_number]["available"]:
        print("Room is not occupied.")
        return
    service = input("Enter service description: ").strip()
    try:
        cost = float(input("Enter service cost: "))
    except ValueError:
        print("Invalid cost entered.")
        return
    services.append({"room_number": room_number, "service": service, "cost": cost})
    save_data()
    print(f"Service '{service}' added to room {room_number}.")

def view_services():
    print("\n--- Services ---")
    if not services:
        print("No services recorded.")
        return
    for service in services:
        print(f"Room {service['room_number']}: {service['service']} - ${service['cost']}")

def view_bills():
    print("\n--- Bills ---")
    if not bills:
        print("No bills generated.")
        return
    for guest_name, charges in bills.items():
        print(f"Guest: {guest_name}, Room Charge: ${charges['room_charge']}, Service Charge: ${charges['service_charge']}, Total: ${charges['total']}")

def main_menu():
    load_data()
    while True:
        print("\n======== Hotel Management System ========")
        print("1. Add Room")
        print("2. View Rooms")
        print("3. Book Room")
        print("4. View Bookings")
        print("5. Check In")
        print("6. Check Out")
        print("7. Add Service")
        print("8. View Services")
        print("9. View Bills")
        print("10. Exit")
        print("=========================================")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            add_room()
        elif choice == "2":
            view_rooms()
        elif choice == "3":
            book_room()
        elif choice == "4":
            view_bookings()
        elif choice == "5":
            check_in()
        elif choice == "6":
            check_out()
        elif choice == "7":
            add_service()
        elif choice == "8":
            view_services()
        elif choice == "9":
            view_bills()
        elif choice == "10":
            save_data()
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
