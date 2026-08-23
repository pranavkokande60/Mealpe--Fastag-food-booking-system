-- Smart Canteen Seed Data (MySQL Compatible)
USE smart_canteen;

-- 1. Seed Food Categories
INSERT INTO food_categories (id, name, description, icon, image_url, display_order) VALUES
(1, 'Breakfast', 'Fresh, wholesome morning energy boosters', 'fa-sun', 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=500&auto=format&fit=crop&q=80', 1),
(2, 'Snacks & Quick Bites', 'Crispy, savory snacks perfect for quick class breaks', 'fa-cookie-bite', 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500&auto=format&fit=crop&q=80', 2),
(3, 'Main Course', 'Hearty, filling meals, bowls, thalis, and aromatic biryanis', 'fa-bowl-food', 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&auto=format&fit=crop&q=80', 3),
(4, 'Beverages & Shakes', 'Chilled coffees, fresh juices, hot chai, and refreshing coolers', 'fa-mug-hot', 'https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=500&auto=format&fit=crop&q=80', 4),
(5, 'Desserts & Bakery', 'Sweet treats, ice creams, and freshly baked delights', 'fa-cake-candles', 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=500&auto=format&fit=crop&q=80', 5),
(6, 'Value Combos', 'Budget-friendly student meal combos with heavy savings', 'fa-layer-group', 'https://images.unsplash.com/photo-1544025162-d76694265947?w=500&auto=format&fit=crop&q=80', 6)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 2. Seed Food Items
INSERT INTO food_items (id, name, description, category_id, price, image_url, ingredients, is_veg, is_available, stock_quantity, prep_time_minutes, calories, spice_level, rating, total_orders) VALUES
(1, 'Masala Dosa', 'Crispy golden fermented crepe stuffed with aromatic spiced potatoes, served with sambhar & coconut chutney.', 1, 60.00, 'https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600&auto=format&fit=crop&q=80', 'Rice batter, Spiced potato filling, Mustard seeds, Curry leaves, Coconut chutney, Sambhar', 1, 1, 80, 8, 320, 'Medium', 4.8, 142),
(2, 'Steamed Idli Sambar (2 pcs)', 'Ultra-soft, fluffy steamed rice cakes served submerged in rich lentil stew and tangy coconut dip.', 1, 45.00, 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600&auto=format&fit=crop&q=80', 'Rice, Urad dal, Sambhar spices, Drumsticks, Coconut chutney', 1, 1, 60, 5, 180, 'Mild', 4.6, 98),
(3, 'Crispy Medu Vada (2 pcs)', 'Deep-fried golden doughnut-shaped lentil fritters, crisp on outside and soft inside.', 1, 50.00, 'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80', 'Black gram, Peppercorn, Ginger, Curry leaves, Green chili', 1, 1, 50, 6, 280, 'Medium', 4.7, 76),
(4, 'Poha with Sev & Peanuts', 'Light, fluffy Maharashtrian tempered flattened rice with roasted crunch and fresh lemon zest.', 1, 35.00, 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80', 'Flattened rice, Roasted peanuts, Turmeric, Mustard, Sev, Lemon juice', 1, 1, 75, 4, 210, 'Mild', 4.5, 115),
(5, 'Mumbai Vada Pav', 'The quintessential campus favorite! Spiced potato fritter in a soft bun with fiery garlic chutney.', 2, 25.00, 'https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=600&auto=format&fit=crop&q=80', 'Potato patty, Gram flour, Fresh pav bun, Garlic dry chutney, Fried green chili', 1, 1, 150, 3, 290, 'Spicy', 4.9, 320),
(6, 'Punjabi Samosa (2 pcs)', 'Crisp, flaky pastry pockets stuffed with cumin-spiced potatoes and peas.', 2, 35.00, 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80', 'Flour pastry, Spiced potatoes, Green peas, Coriander, Mint chutney', 1, 1, 90, 4, 310, 'Medium', 4.7, 185),
(7, 'Kolhapuri Misal Pav', 'Fiery sprouted bean curry topped with crunchy farsan and served with buttered pav.', 2, 65.00, 'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80', 'Sprouted moth beans, Spicy rassa gravy, Farsan, Chopped onions, Lemon, Pav', 1, 1, 55, 7, 420, 'Spicy', 4.8, 110),
(8, 'Grilled Cheese Sandwich', 'Golden grilled buttery toast loaded with melted gooey cheese and signature herbs.', 2, 70.00, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=600&auto=format&fit=crop&q=80', 'Brown bread, Cheddar & Mozzarella cheese, Herb butter, Green chutney', 1, 1, 45, 8, 380, 'Mild', 4.6, 95),
(9, 'Paneer Tikka Kathi Roll', 'Smoky tandoori paneer wrapped in flaky paratha with sliced onions and zesty mint dip.', 2, 90.00, 'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80', 'Marinated paneer cubes, Paratha wrap, Onions, Mint yogurt sauce, Chaat masala', 1, 1, 40, 10, 450, 'Spicy', 4.9, 140),
(10, 'Crispy French Fries (Peri-Peri)', 'Crunchy golden potato fries tossed in fiery African bird eye chili seasoning.', 2, 60.00, 'https://images.unsplash.com/photo-1576107232684-1279f3908594?w=600&auto=format&fit=crop&q=80', 'Potato batons, Peri-peri spice mix, Garlic mayo, Tomato ketchup', 1, 1, 70, 6, 340, 'Spicy', 4.7, 160),
(11, 'Cheesy Veg Burger', 'Loaded vegetable patty with melted cheese, crisp greens, and creamy dressing in a toasted brioche bun.', 2, 85.00, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&auto=format&fit=crop&q=80', 'Crisp veg patty, Sesame bun, Cheese slice, Lettuce, Tomato, Thousand Island dressing', 1, 1, 40, 9, 460, 'Medium', 4.6, 88),
(12, 'Farmhouse Cheesy Pizza (8 inch)', 'Freshly baked thin-crust pizza topped with gooey mozzarella, crunchy bell peppers, corn, and herbs.', 2, 140.00, 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop&q=80', 'Pizza dough, San Marzano tomato sauce, Mozzarella, Bell peppers, Sweet corn, Olives', 1, 1, 30, 14, 620, 'Medium', 4.8, 75),
(13, 'Hyderabadi Veg Dum Biryani', 'Slow-cooked fragrant long-grain basmati rice layered with vegetables, saffron, and rich caramelized onions.', 3, 120.00, 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80', 'Basmati rice, Saffron, Fried onions, Paneer, Mixed vegetables, Dum spices, Raita', 1, 1, 60, 12, 540, 'Spicy', 4.9, 210),
(14, 'Special Deluxe Student Thali', 'The ultimate balanced feast! Rich paneer butter masala, yellow dal, hot rotis, fragrant rice & sweet.', 3, 110.00, 'https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=600&auto=format&fit=crop&q=80', 'Paneer curry, Dal tadka, 3 Butter Rotis, Steamed Jeera Rice, Gulab Jamun, Salad, Pickle', 1, 1, 80, 8, 680, 'Medium', 4.9, 260),
(15, 'Paneer Butter Masala with 2 Naan', 'Soft succulent paneer cubes simmered in velvety makhani gravy served with piping hot butter naans.', 3, 130.00, 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=600&auto=format&fit=crop&q=80', 'Cottage cheese, Cashew tomato gravy, Fresh cream, Kasuri methi, Butter garlic naan', 1, 1, 45, 12, 590, 'Medium', 4.8, 120),
(16, 'Chole Bhature (2 pcs)', 'Tangy, dark spiced chickpea curry served with giant balloon-puffed fried leavened breads.', 3, 95.00, 'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80', 'Chickpeas, Pomegranate seeds, Spices, Puffed bhature, Pickled onion, Mint sauce', 1, 1, 50, 10, 650, 'Spicy', 4.8, 130),
(17, 'Dal Khichdi with Desi Ghee', 'Soulful, easily digestible comfort meal topped with aromatic garlic tadka and pure desi ghee.', 3, 80.00, 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80', 'Rice, Moong dal, Cumin tadka, Garlic, Desi ghee, Papad, Mango pickle', 1, 1, 40, 7, 390, 'Mild', 4.7, 95),
(18, 'Signature Cold Coffee with Ice Cream', 'Thick, creamy, iced frothy espresso milkshake crowned with a velvety scoop of vanilla ice cream.', 4, 55.00, 'https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=600&auto=format&fit=crop&q=80', 'Arabica coffee blend, Full cream milk, Vanilla ice cream scoop, Chocolate syrup drizzle', 1, 1, 120, 4, 240, 'Mild', 4.9, 310),
(19, 'Special Masala Chai (Kulhad)', 'Steaming hot traditional spiced milk tea served in an earthen clay kulhad for that authentic aroma.', 4, 20.00, 'https://images.unsplash.com/photo-1561336313-0bd5e0b27ec8?w=600&auto=format&fit=crop&q=80', 'Assam black tea, Crushed cardamom, Ginger, Cinnamon, Whole milk', 1, 1, 200, 3, 90, 'Mild', 4.9, 450),
(20, 'Sweet Punjabi Mango Lassi', 'Refreshing and rich chilled yogurt smoothie blended with ripe sweet mango pulp.', 4, 45.00, 'https://images.unsplash.com/photo-1546173159-315724a31696?w=600&auto=format&fit=crop&q=80', 'Thick curd, Alphonso mango pulp, Cardamom, Pistachio slivers', 1, 1, 60, 3, 220, 'Mild', 4.7, 115),
(21, 'Fresh Mint Lemonade (Mojito)', 'Crisp sparkling lime and mint cooler with a refreshing dash of rock salt.', 4, 35.00, 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&auto=format&fit=crop&q=80', 'Fresh lime juice, Muddled mint leaves, Soda, Black salt, Cumin powder', 1, 1, 80, 3, 80, 'Mild', 4.6, 90),
(22, 'Hot Gulab Jamun (2 pcs)', 'Melt-in-the-mouth fried dough dumplings soaked in warm fragrant cardamom and rose syrup.', 5, 40.00, 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&auto=format&fit=crop&q=80', 'Mawa, Rosewater sugar syrup, Cardamom, Almond flakes', 1, 1, 65, 2, 290, 'Mild', 4.8, 140),
(23, 'Chocolate Brownie with Fudge', 'Gooey, decadent dark chocolate walnut brownie smothered in hot bittersweet fudge sauce.', 5, 65.00, 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=600&auto=format&fit=crop&q=80', 'Dark cocoa, Butter, Chocochips, Warm fudge sauce, Walnuts', 1, 1, 40, 3, 360, 'Mild', 4.9, 125),
(24, 'Power Combo: 2 Vada Pav + Cold Coffee', 'The undisputed #1 student favorite! Save ₹15 with this ultimate hunger-busting combo.', 6, 90.00, 'https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=600&auto=format&fit=crop&q=80', '2 Mumbai Vada Pav, 1 Chilled Signature Cold Coffee', 1, 1, 80, 5, 680, 'Medium', 4.9, 290),
(25, 'Lunch Combo: Biryani + Cold Drink + Gulab Jamun', 'Complete 3-course lunch box deal engineered for satisfying midday cravings.', 6, 160.00, 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80', '1 Veg Dum Biryani, 1 Mint Cooler, 1 Hot Gulab Jamun', 1, 1, 50, 10, 820, 'Spicy', 4.9, 175)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 3. Seed Seat Tables
INSERT INTO seat_tables (id, table_number, capacity, section, is_active) VALUES
(1, 'T-01', 2, 'Window Bay', 1),
(2, 'T-02', 2, 'Window Bay', 1),
(3, 'T-03', 4, 'Window Bay', 1),
(4, 'T-04', 4, 'Main Hall', 1),
(5, 'T-05', 4, 'Main Hall', 1),
(6, 'T-06', 6, 'Main Hall', 1),
(7, 'T-07', 6, 'Main Hall', 1),
(8, 'T-08', 4, 'Main Hall', 1),
(9, 'T-09', 2, 'AC Corner', 1),
(10, 'T-10', 4, 'AC Corner', 1),
(11, 'T-11', 4, 'AC Corner', 1),
(12, 'T-12', 6, 'AC Corner', 1),
(13, 'T-13', 4, 'Outdoor Patio', 1),
(14, 'T-14', 4, 'Outdoor Patio', 1),
(15, 'T-15', 8, 'Outdoor Patio', 1)
ON DUPLICATE KEY UPDATE table_number=VALUES(table_number);

-- 4. Seed Inventory
INSERT INTO inventory (id, item_name, category, current_stock, unit, min_threshold, max_capacity, cost_per_unit, expiry_days, status) VALUES
(1, 'Potatoes (Agra Special)', 'Vegetables', 65.0, 'kg', 25.0, 150.0, 22.0, 10, 'IN_STOCK'),
(2, 'Fresh Paneer Blocks', 'Dairy', 18.5, 'kg', 10.0, 40.0, 320.0, 3, 'IN_STOCK'),
(3, 'Full Cream Milk', 'Dairy', 42.0, 'liters', 20.0, 100.0, 64.0, 2, 'IN_STOCK'),
(4, 'Fresh Pav Buns', 'Bakery', 140.0, 'packets', 40.0, 300.0, 18.0, 2, 'IN_STOCK'),
(5, 'Sandwich Bread', 'Bakery', 28.0, 'packets', 15.0, 60.0, 35.0, 3, 'IN_STOCK'),
(6, 'Dosa & Idli Batter', 'Pre-mix', 30.0, 'kg', 12.0, 80.0, 45.0, 3, 'IN_STOCK'),
(7, 'Arabica Coffee Beans', 'Beverages', 8.5, 'kg', 5.0, 25.0, 650.0, 60, 'IN_STOCK'),
(8, 'Assam Tea Leaves', 'Beverages', 12.0, 'kg', 4.0, 30.0, 380.0, 90, 'IN_STOCK'),
(9, 'Basmati Rice (Royal)', 'Grains', 85.0, 'kg', 30.0, 200.0, 95.0, 180, 'IN_STOCK'),
(10, 'Cooking Refined Oil', 'Oils', 45.0, 'liters', 20.0, 120.0, 130.0, 120, 'IN_STOCK'),
(11, 'Mozzarella & Cheddar Blend', 'Dairy', 9.0, 'kg', 8.0, 30.0, 480.0, 14, 'IN_STOCK'),
(12, 'Tomatoes & Onions', 'Vegetables', 52.0, 'kg', 20.0, 100.0, 30.0, 5, 'IN_STOCK')
ON DUPLICATE KEY UPDATE item_name=VALUES(item_name);

-- 5. Seed Coupons
INSERT INTO coupons (id, code, discount_percent, discount_amount, min_order_amount, max_discount, is_active, expiry_date) VALUES
(1, 'WELCOME50', 0.0, 50.0, 120.0, 50.0, 1, '2026-12-31'),
(2, 'STUDENT10', 10.0, 0.0, 80.0, 30.0, 1, '2026-12-31'),
(3, 'HUNGRY20', 20.0, 0.0, 200.0, 60.0, 1, '2026-12-31'),
(4, 'CHAI5', 0.0, 10.0, 40.0, 10.0, 1, '2026-12-31')
ON DUPLICATE KEY UPDATE code=VALUES(code);
