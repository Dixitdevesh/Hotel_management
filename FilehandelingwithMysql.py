import mysql.connector
import os
import json

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Update with your MySQL root password
        database="hotel_management"
    )

# File Handling
def save_to_file(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def load_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return []

# Log Management
def log_action(action, details=""):
    log_entry = f"{action}: {details}\n"
    with open("system_logs.txt", "a") as log_file:
        log_file.write(log_entry)

# Room Management
def add_room():
    room_number = input("Enter room number: ")
    room_type = input("Enter room type (single, double, suite): ").lower()
    price = float(input("Enter price per night: "))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO rooms (room_number, type, price, available) VALUES (%s, %s, %s, %s)",
            (room_number, room_type, price, True)
        )
        conn.commit()
        print(f"Room {room_number} added successfully.")
        rooms = load_from_file('rooms.json')
        rooms.append({"room_number": room_number, "type": room_type, "price": price, "available": True})
        save_to_file('rooms.json', rooms)
        log_action("Room Added", f"Room {room_number}, Type: {room_type}, Price: ${price}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        log_action("Add Room Failed", str(err))
    finally:
        cursor.close()
        conn.close()

def view_rooms():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM rooms")
        rooms = cursor.fetchall()
        print("\n--- Room Details ---")
        for room in rooms:
            status = "Available" if room['available'] else "Occupied"
            print(f"Room Number: {room['room_number']}, Type: {room['type'].capitalize()}, Price: ${room['price']}, Status: {status}")
        save_to_file('rooms.json', rooms)
        log_action("Viewed Rooms")
        print("---------------------\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        log_action("View Rooms Failed", str(err))
    finally:
        cursor.close()
        conn.close()

# Booking Management
def book_room():
    guest_name = input("Enter guest name: ").strip()
    contact_details = input("Enter contact details: ").strip()
    room_type = input("Enter room type to book (single, double, suite): ").lower()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM rooms WHERE type = %s AND available = TRUE", (room_type,))
        available_rooms = cursor.fetchall()

        if not available_rooms:
            print(f"No available {room_type} rooms.")
            log_action("Book Room Failed", f"No available rooms for type: {room_type}")
            return

        print(f"Available {room_type} rooms: {', '.join([room['room_number'] for room in available_rooms])}")
        room_number = input("Enter room number to book: ").strip()

        try:
            duration = int(input("Enter duration of stay (nights): "))
            if duration <= 0:
                print("Duration must be at least 1 night.")
                log_action("Book Room Failed", "Invalid duration entered.")
                return
        except ValueError:
            print("Invalid duration entered.")
            log_action("Book Room Failed", "Invalid duration format.")
            return

        cursor.execute(
            "INSERT INTO bookings (room_number, guest_name, contact_details, duration) VALUES (%s, %s, %s, %s)",
            (room_number, guest_name, contact_details, duration)
        )
        update_room_availability(room_number, False)
        conn.commit()
        print(f"Room {room_number} booked successfully for {guest_name}.")
        bookings = load_from_file('bookings.json')
        bookings.append({"room_number": room_number, "guest_name": guest_name, "contact_details": contact_details, "duration": duration})
        save_to_file('bookings.json', bookings)
        log_action("Room Booked", f"Room {room_number}, Guest: {guest_name}, Duration: {duration} nights")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        log_action("Book Room Failed", str(err))
    finally:
        cursor.close()
        conn.close()

def view_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM bookings")
        bookings = cursor.fetchall()
        print("\n--- Current Bookings ---")
        if not bookings:
            print("No current bookings.")
        else:
            for idx, booking in enumerate(bookings, start=1):
                print(f"{idx}. Room {booking['room_number']} - Guest: {booking['guest_name']}, Contact: {booking['contact_details']}, Duration: {booking['duration']} nights")
        save_to_file('bookings.json', bookings)
        log_action("Viewed Bookings")
        print("------------------------\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        log_action("View Bookings Failed", str(err))
    finally:
        cursor.close()
        conn.close()

# Service Management
def add_service():
    print("\n--- Add Service ---")
    room_number = input("Enter room number: ").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM rooms WHERE room_number = %s", (room_number,))
        room = cursor.fetchone()

        if not room or room['available']:
            print("Room is either not booked or does not exist.")
            log_action("Add Service Failed", f"Room {room_number} not found or available.")
            return

        service = input("Enter service (e.g., room service, laundry): ").strip().lower()
        cost = float(input("Enter cost of the service: "))

        cursor.execute(
            "INSERT INTO services (room_number, service, cost) VALUES (%s, %s, %s)",
            (room_number, service, cost)
        )
        conn.commit()
        print(f"Service '{service}' added to room {room_number} successfully.")
        services = load_from_file('services.json')
        services.append({"room_number": room_number, "service": service, "cost": cost})
        save_to_file('services.json', services)
        log_action("Service Added", f"Service: {service}, Room: {room_number}, Cost: ${cost}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        log_action("Add Service Failed", str(err))
    finally:
        cursor.close()
        conn.close()

# Utility Function
def update_room_availability(room_number, availability):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE rooms SET available = %s WHERE room_number = %s", (availability, room_number))
        conn.commit()
        log_action("Updated Room Availability", f"Room {room_number}, Available: {availability}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        log_action("Update Room Availability Failed", str(err))
    finally:
        cursor.close()
        conn.close()

# Main Menu
def main_menu():
    while True:
        print("========== Hotel Management System ==========")
        print("1. Add Room")
        print("2. View Rooms")
        print("3. Book Room")
        print("4. View Bookings")
        print("5. Add Service")
        print("6. Exit")
        print("==============================================")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            add_room()
        elif choice == "2":
            view_rooms()
        elif choice == "3":
            book_room()
        elif choice == "4":
            view_bookings()
        elif choice == "5":
            add_service()
        elif choice == "6":
            print("Exiting Hotel Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
