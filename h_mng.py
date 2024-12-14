import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="hotel_management"
    )

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
    except mysql.connector.Error as err:
        print(f"Error: {err}")
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
        print("---------------------\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def update_room_availability(room_number, availability):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE rooms SET available = %s WHERE room_number = %s", (availability, room_number))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

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
            return

        print(f"Available {room_type} rooms: {', '.join([room['room_number'] for room in available_rooms])}")
        room_number = input("Enter room number to book: ").strip()

        try:
            duration = int(input("Enter duration of stay (nights): "))
            if duration <= 0:
                print("Duration must be at least 1 night.")
                return
        except ValueError:
            print("Invalid duration entered.")
            return

        cursor.execute(
            "INSERT INTO bookings (room_number, guest_name, contact_details, duration) VALUES (%s, %s, %s, %s)",
            (room_number, guest_name, contact_details, duration)
        )
        update_room_availability(room_number, False)
        conn.commit()
        print(f"Room {room_number} booked successfully for {guest_name}.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
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
        print("------------------------\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def cancel_booking():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM bookings ORDER BY id DESC LIMIT 1")
        last_booking = cursor.fetchone()

        if not last_booking:
            print("No bookings to cancel.")
            return

        room_number = last_booking['room_number']
        cursor.execute("DELETE FROM bookings WHERE id = %s", (last_booking['id'],))
        update_room_availability(room_number, True)
        conn.commit()
        print(f"Cancelled booking for {last_booking['guest_name']} in room {room_number}.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def check_in():
    print("\n--- Check-In Guest ---")
    room_number = input("Enter room number: ").strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM bookings WHERE room_number = %s", (room_number,))
        booking = cursor.fetchone()

        if not booking:
            print("No booking found for this room.")
            return

        guest_name = booking['guest_name']
        print(f"Guest {guest_name} checked into room {room_number} successfully.")
        cursor.execute("DELETE FROM bookings WHERE id = %s", (booking['id'],))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def check_out():
    print("\n--- Check-Out Guest ---")
    room_number = input("Enter room number: ").strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM bookings WHERE room_number = %s", (room_number,))
        booking = cursor.fetchone()

        if not booking:
            print("No booking found for this room.")
            return

        duration = booking['duration']
        cursor.execute("SELECT * FROM rooms WHERE room_number = %s", (room_number,))
        room = cursor.fetchone()

        if not room:
            print("Room details not found.")
            return

        total_charge = room['price'] * duration
        update_room_availability(room_number, True)
        conn.commit()

        print(f"Guest {booking['guest_name']} checked out from room {room_number} successfully.")
        print(f"Total Charge: ${total_charge}\n")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

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
            return

        service = input("Enter service (e.g., room service, laundry): ").strip().lower()
        cost = float(input("Enter cost of the service: "))

        cursor.execute(
            "INSERT INTO services (room_number, service, cost) VALUES (%s, %s, %s)",
            (room_number, service, cost)
        )
        conn.commit()
        print(f"Service '{service}' added to room {room_number} successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def main_menu():
    while True:
        print("========== Hotel Management System ==========")
        print("1. Add Room")
        print("2. View Rooms")
        print("3. Book Room")
        print("4. View Bookings")
        print("5. Cancel Booking")
        print("6. Check In")
        print("7. Check Out")
        print("8. Add Service")
        print("9. Exit")
        print("==============================================")

        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            add_room()
        elif choice == "2":
            view_rooms()
        elif choice == "3":
            book_room()
        elif choice == "4":
            view_bookings()
        elif choice == "5":
            cancel_booking()
        elif choice == "6":
            check_in()
        elif choice == "7":
            check_out()
        elif choice == "8":
            add_service()
        elif choice == "9":
            print("Exiting Hotel Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
