from typing import List, Dict, Any
from database.db import query_db, execute_db

class NotificationService:
    """
    Centralized Notification Manager for student alerts, order updates, seat reservations, and promos.
    """

    def get_user_notifications(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        return query_db("""
            SELECT * FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit)) or []

    def get_unread_count(self, user_id: int) -> int:
        res = query_db("""
            SELECT COUNT(id) as count 
            FROM notifications 
            WHERE user_id = %s AND is_read = 0
        """, (user_id,), one=True)
        return res['count'] if res else 0

    def mark_all_read(self, user_id: int) -> bool:
        execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = %s", (user_id,))
        return True

    def create_notification(self, user_id: int, title: str, message: str, notif_type: str = 'info', link: str = None) -> int:
        return execute_db("""
            INSERT INTO notifications (user_id, title, message, type, link, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (user_id, title, message, notif_type, link))

notification_service = NotificationService()
