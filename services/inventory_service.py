from typing import List, Dict, Any
from database.db import query_db, execute_db

class InventoryService:
    """
    Intelligent Smart Inventory Management:
    Automated status evaluation, low stock alerts, restocking logs, and AI purchasing recommendations.
    """

    def get_all_inventory_with_ai_insights(self) -> Dict[str, Any]:
        """
        Retrieves all inventory items with computed status flags and AI purchase recommendations.
        """
        items = query_db("SELECT * FROM inventory ORDER BY current_stock ASC") or []
        
        low_stock_count = 0
        out_of_stock_count = 0
        overstock_count = 0
        total_inventory_value = 0.0
        ai_recommendations = []

        for it in items:
            stock = float(it['current_stock'])
            min_thresh = float(it['min_threshold'])
            max_cap = float(it['max_capacity'])
            cost = float(it['cost_per_unit'])
            total_inventory_value += stock * cost

            # Dynamic status check
            if stock <= 0:
                status = 'OUT_OF_STOCK'
                badge = 'danger'
                out_of_stock_count += 1
                needed = int(min_thresh * 2)
                ai_recommendations.append({
                    "priority": "HIGH",
                    "badge": "danger",
                    "text": f"🚨 Urgent: {it['item_name']} is OUT OF STOCK. Reorder {needed} {it['unit']} immediately."
                })
            elif stock <= min_thresh:
                status = 'LOW_STOCK'
                badge = 'warning'
                low_stock_count += 1
                needed = int(max_cap * 0.6 - stock)
                ai_recommendations.append({
                    "priority": "MEDIUM",
                    "badge": "warning",
                    "text": f"⚠️ Low Stock Alert: Order {needed} {it['unit']} of {it['item_name']} before tomorrow's lunch rush."
                })
            elif stock >= (max_cap * 0.9):
                status = 'OVERSTOCK'
                badge = 'info'
                overstock_count += 1
            else:
                status = 'IN_STOCK'
                badge = 'success'

            it['computed_status'] = status
            it['badge_class'] = badge

        return {
            "items": items,
            "total_items": len(items),
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "overstock_count": overstock_count,
            "total_valuation": round(total_inventory_value, 2),
            "ai_recommendations": ai_recommendations
        }

    def restock_item(self, item_id: int, quantity: float, cost_per_unit: float = None, notes: str = None) -> bool:
        """Adds stock and creates a transaction record"""
        item = query_db("SELECT * FROM inventory WHERE id = %s", (item_id,), one=True)
        if not item:
            return False

        new_stock = float(item['current_stock']) + quantity
        execute_db("""
            UPDATE inventory 
            SET current_stock = %s, updated_at = NOW() 
            WHERE id = %s
        """, (new_stock, item_id))

        execute_db("""
            INSERT INTO inventory_transactions (inventory_id, transaction_type, quantity, notes, created_at)
            VALUES (%s, 'PURCHASE', %s, %s, NOW())
        """, (item_id, quantity, notes or f"Restocked {quantity} {item['unit']}"))

        return True

    def log_usage_or_waste(self, item_id: int, tx_type: str, quantity: float, notes: str = None) -> bool:
        """Deducts stock for usage or waste tracking"""
        item = query_db("SELECT * FROM inventory WHERE id = %s", (item_id,), one=True)
        if not item:
            return False

        new_stock = max(0.0, float(item['current_stock']) - quantity)
        execute_db("""
            UPDATE inventory 
            SET current_stock = %s, updated_at = NOW() 
            WHERE id = %s
        """, (new_stock, item_id))

        execute_db("""
            INSERT INTO inventory_transactions (inventory_id, transaction_type, quantity, notes, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (item_id, tx_type, quantity, notes))

        return True

# Singleton instance
inventory_service = InventoryService()
