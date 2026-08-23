import datetime
import uuid
from typing import List, Dict, Any, Optional
from database.db import query_db, execute_db

class SeatService:
    """
    Manages Canteen Table Layout, Visual 2D Floor Plan, Group Seat Allocation, and Conflict Prevention.
    """

    AVAILABLE_TIME_SLOTS = [
        "08:30 - 09:00", "09:00 - 09:30", "09:30 - 10:00", "10:00 - 10:30",
        "12:00 - 12:30", "12:30 - 01:00", "01:00 - 01:30", "01:30 - 02:00",
        "02:00 - 02:30", "04:30 - 05:00", "05:00 - 05:30", "05:30 - 06:00"
    ]

    def get_table_layout_with_status(self, booking_date: str, time_slot: str, current_user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Returns full 2D layout grouped by section with live availability status.
        """
        tables = query_db("SELECT * FROM seat_tables WHERE is_active = 1 ORDER BY table_number ASC") or []
        
        # Query existing bookings for this date and time slot
        active_bookings = query_db("""
            SELECT * FROM seat_bookings 
            WHERE booking_date = %s AND time_slot = %s AND status = 'CONFIRMED'
        """, (booking_date, time_slot)) or []

        booking_by_table = {b['table_id']: b for b in active_bookings}

        sections = {}
        total_seats = 0
        occupied_seats = 0

        for table in tables:
            tid = table['id']
            cap = table['capacity']
            sec = table['section']
            total_seats += cap

            if tid in booking_by_table:
                b = booking_by_table[tid]
                occupied_seats += cap
                if current_user_id and b['student_id'] == current_user_id:
                    status = 'my_booking'
                    booking_info = b
                else:
                    status = 'booked'
                    booking_info = None
            else:
                status = 'available'
                booking_info = None

            table_obj = {
                **table,
                'status': status,
                'booking_info': booking_info
            }

            if sec not in sections:
                sections[sec] = []
            sections[sec].append(table_obj)

        available_seats = total_seats - occupied_seats
        occupancy_rate = round((occupied_seats / total_seats * 100) if total_seats > 0 else 0, 1)

        return {
            "booking_date": booking_date,
            "time_slot": time_slot,
            "sections": sections,
            "total_tables": len(tables),
            "total_seats": total_seats,
            "available_seats": available_seats,
            "occupied_seats": occupied_seats,
            "occupancy_rate": occupancy_rate,
            "time_slots": self.AVAILABLE_TIME_SLOTS
        }

    def book_seat(self, student_id: int, table_id: int, booking_date: str, time_slot: str, guests_count: int = 1) -> Dict[str, Any]:
        """
        Reserves a table with double-booking prevention.
        """
        # 1. Validate table exists
        table = query_db("SELECT * FROM seat_tables WHERE id = %s AND is_active = 1", (table_id,), one=True)
        if not table:
            raise ValueError("Invalid table selected.")

        if guests_count > table['capacity']:
            raise ValueError(f"Table {table['table_number']} only accommodates up to {table['capacity']} guests.")

        # 2. Check conflict / double booking
        existing = query_db("""
            SELECT * FROM seat_bookings 
            WHERE table_id = %s AND booking_date = %s AND time_slot = %s AND status = 'CONFIRMED'
        """, (table_id, booking_date, time_slot), one=True)

        if existing:
            raise ValueError(f"Table {table['table_number']} has already been booked for {time_slot} on {booking_date}.")

        # 3. Check student doesn't already have an active booking at the same time
        student_conflict = query_db("""
            SELECT * FROM seat_bookings
            WHERE student_id = %s AND booking_date = %s AND time_slot = %s AND status = 'CONFIRMED'
        """, (student_id, booking_date, time_slot), one=True)

        if student_conflict:
            raise ValueError(f"You already have Table {student_conflict['table_id']} reserved for {time_slot}.")

        booking_code = f"SEAT-{uuid.uuid4().hex[:6].upper()}"

        booking_id = execute_db("""
            INSERT INTO seat_bookings (booking_code, student_id, table_id, guests_count, booking_date, time_slot, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'CONFIRMED', NOW())
        """, (booking_code, student_id, table_id, guests_count, booking_date, time_slot))

        # Notify student
        execute_db("""
            INSERT INTO notifications (user_id, title, message, type, link, created_at)
            VALUES (%s, %s, %s, 'seat', %s, NOW())
        """, (
            student_id,
            f"Seat Confirmed: {table['table_number']}",
            f"Table {table['table_number']} ({table['section']}) reserved for {guests_count} guest(s) on {booking_date} at {time_slot}.",
            "/student/seat-booking"
        ))

        return {
            "booking_id": booking_id,
            "booking_code": booking_code,
            "table_number": table['table_number'],
            "section": table['section'],
            "time_slot": time_slot,
            "booking_date": booking_date
        }

    def smart_allocate_table(self, guests_count: int, booking_date: str, time_slot: str) -> Optional[Dict[str, Any]]:
        """
        AI Smart Allocation: Finds the optimal matching table with minimal wasted seats.
        """
        tables = query_db("""
            SELECT t.* FROM seat_tables t
            WHERE t.is_active = 1 AND t.capacity >= %s
            AND t.id NOT IN (
                SELECT b.table_id FROM seat_bookings b 
                WHERE b.booking_date = %s AND b.time_slot = %s AND b.status = 'CONFIRMED'
            )
            ORDER BY t.capacity ASC, t.table_number ASC
        """, (guests_count, booking_date, time_slot))

        return tables[0] if tables else None

    def cancel_booking(self, booking_id: int, user_id: int, is_admin: bool = False) -> bool:
        """Cancels a table reservation"""
        if is_admin:
            booking = query_db("SELECT * FROM seat_bookings WHERE id = %s", (booking_id,), one=True)
        else:
            booking = query_db("SELECT * FROM seat_bookings WHERE id = %s AND student_id = %s", (booking_id, user_id), one=True)

        if not booking:
            return False

        execute_db("UPDATE seat_bookings SET status = 'CANCELLED' WHERE id = %s", (booking_id,))
        return True

# Singleton instance
seat_service = SeatService()
