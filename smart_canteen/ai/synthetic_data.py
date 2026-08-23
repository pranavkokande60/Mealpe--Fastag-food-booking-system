import datetime
import random
import bcrypt

def get_hashed_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Demo User Credentials (securely hashed)
DEFAULT_PASSWORD_HASH = get_hashed_password('Student@123')
ADMIN_PASSWORD_HASH = get_hashed_password('Admin@123')
STAFF_PASSWORD_HASH = get_hashed_password('Staff@123')

FOOD_CATEGORIES = [
    {"id": 1, "name": "Breakfast", "description": "Fresh, wholesome morning energy boosters to start your college day right", "icon": "fa-sun", "image_url": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=500&auto=format&fit=crop&q=80", "display_order": 1},
    {"id": 2, "name": "Snacks & Quick Bites", "description": "Crispy, savory snacks perfect for quick class breaks", "icon": "fa-cookie-bite", "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500&auto=format&fit=crop&q=80", "display_order": 2},
    {"id": 3, "name": "Main Course", "description": "Hearty, filling meals, bowls, thalis, and aromatic biryanis", "icon": "fa-bowl-food", "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&auto=format&fit=crop&q=80", "display_order": 3},
    {"id": 4, "name": "Beverages & Shakes", "description": "Chilled coffees, fresh juices, hot chai, and refreshing coolers", "icon": "fa-mug-hot", "image_url": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=500&auto=format&fit=crop&q=80", "display_order": 4},
    {"id": 5, "name": "Desserts & Bakery", "description": "Sweet treats, ice creams, and freshly baked delights", "icon": "fa-cake-candles", "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=500&auto=format&fit=crop&q=80", "display_order": 5},
    {"id": 6, "name": "Value Combos", "description": "Budget-friendly student meal combos with heavy savings", "icon": "fa-layer-group", "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=500&auto=format&fit=crop&q=80", "display_order": 6}
]

FOOD_ITEMS = [
    # Breakfast
    {"id": 1, "name": "Masala Dosa", "category_id": 1, "price": 60.00, "prep_time_minutes": 8, "calories": 320, "is_veg": 1, "spice_level": "Medium", "rating": 4.8, "ingredients": "Rice batter, Spiced potato filling, Mustard seeds, Curry leaves, Coconut chutney, Sambhar", "description": "Crispy golden fermented crepe stuffed with aromatic spiced potatoes, served with hot sambhar & fresh coconut chutney.", "image_url": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600&auto=format&fit=crop&q=80"},
    {"id": 2, "name": "Steamed Idli Sambar (2 pcs)", "category_id": 1, "price": 45.00, "prep_time_minutes": 5, "calories": 180, "is_veg": 1, "spice_level": "Mild", "rating": 4.6, "ingredients": "Rice, Urad dal, Sambhar spices, Drumsticks, Coconut chutney", "description": "Ultra-soft, fluffy steamed rice cakes served submerged in rich lentil stew and tangy coconut dip.", "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600&auto=format&fit=crop&q=80"},
    {"id": 3, "name": "Crispy Medu Vada (2 pcs)", "category_id": 1, "price": 50.00, "prep_time_minutes": 6, "calories": 280, "is_veg": 1, "spice_level": "Medium", "rating": 4.7, "ingredients": "Black gram, Peppercorn, Ginger, Curry leaves, Green chili", "description": "Deep-fried golden doughnut-shaped lentil fritters, crisp on outside and soft inside.", "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80"},
    {"id": 4, "name": "Poha with Sev & Peanuts", "category_id": 1, "price": 35.00, "prep_time_minutes": 4, "calories": 210, "is_veg": 1, "spice_level": "Mild", "rating": 4.5, "ingredients": "Flattened rice, Roasted peanuts, Turmeric, Mustard, Sev, Lemon juice", "description": "Light, fluffy Maharashtrian tempered flattened rice with roasted crunch and fresh lemon zest.", "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80"},
    
    # Snacks & Quick Bites
    {"id": 5, "name": "Mumbai Vada Pav", "category_id": 2, "price": 25.00, "prep_time_minutes": 3, "calories": 290, "is_veg": 1, "spice_level": "Spicy", "rating": 4.9, "ingredients": "Potato patty, Gram flour, Fresh pav bun, Garlic dry chutney, Fried green chili", "description": "The quintessential campus favorite! Spiced potato fritter in a soft bun with fiery garlic chutney.", "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=600&auto=format&fit=crop&q=80"},
    {"id": 6, "name": "Punjabi Samosa (2 pcs)", "category_id": 2, "price": 35.00, "prep_time_minutes": 4, "calories": 310, "is_veg": 1, "spice_level": "Medium", "rating": 4.7, "ingredients": "Flour pastry, Spiced potatoes, Green peas, Coriander, Mint chutney, Tamarind chutney", "description": "Crisp, flaky pastry pockets stuffed with cumin-spiced potatoes and peas.", "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80"},
    {"id": 7, "name": "Kolhapuri Misal Pav", "category_id": 2, "price": 65.00, "prep_time_minutes": 7, "calories": 420, "is_veg": 1, "spice_level": "Spicy", "rating": 4.8, "ingredients": "Sprouted moth beans, Spicy rassa gravy, Farsan, Chopped onions, Lemon, Pav", "description": "Fiery sprouted bean curry topped with crunchy farsan and served with buttered pav.", "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80"},
    {"id": 8, "name": "Grilled Cheese Sandwich", "category_id": 2, "price": 70.00, "prep_time_minutes": 8, "calories": 380, "is_veg": 1, "spice_level": "Mild", "rating": 4.6, "ingredients": "Brown bread, Cheddar & Mozzarella cheese, Herb butter, Green chutney", "description": "Golden grilled buttery toast loaded with melted gooey cheese and signature herbs.", "image_url": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=600&auto=format&fit=crop&q=80"},
    {"id": 9, "name": "Paneer Tikka Kathi Roll", "category_id": 2, "price": 90.00, "prep_time_minutes": 10, "calories": 450, "is_veg": 1, "spice_level": "Spicy", "rating": 4.9, "ingredients": "Marinated paneer cubes, Paratha wrap, Onions, Mint yogurt sauce, Chaat masala", "description": "Smoky tandoori paneer wrapped in flaky paratha with sliced onions and zesty mint dip.", "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80"},
    {"id": 10, "name": "Crispy French Fries (Peri-Peri)", "category_id": 2, "price": 60.00, "prep_time_minutes": 6, "calories": 340, "is_veg": 1, "spice_level": "Spicy", "rating": 4.7, "ingredients": "Potato batons, Peri-peri spice mix, Garlic mayo, Tomato ketchup", "description": "Crunchy golden potato fries tossed in fiery African bird's eye chili seasoning.", "image_url": "https://images.unsplash.com/photo-1576107232684-1279f3908594?w=600&auto=format&fit=crop&q=80"},
    {"id": 11, "name": "Cheesy Veg Burger", "category_id": 2, "price": 85.00, "prep_time_minutes": 9, "calories": 460, "is_veg": 1, "spice_level": "Medium", "rating": 4.6, "ingredients": "Crisp veg patty, Sesame bun, Cheese slice, Lettuce, Tomato, Thousand Island dressing", "description": "Loaded vegetable patty with melted cheese, crisp greens, and creamy dressing in a toasted brioche bun.", "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&auto=format&fit=crop&q=80"},
    {"id": 12, "name": "Farmhouse Cheesy Pizza (8 inch)", "category_id": 2, "price": 140.00, "prep_time_minutes": 14, "calories": 620, "is_veg": 1, "spice_level": "Medium", "rating": 4.8, "ingredients": "Pizza dough, San Marzano tomato sauce, Mozzarella, Bell peppers, Sweet corn, Olives", "description": "Freshly baked thin-crust pizza topped with gooey mozzarella, crunchy bell peppers, corn, and herbs.", "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop&q=80"},

    # Main Course
    {"id": 13, "name": "Hyderabadi Veg Dum Biryani", "category_id": 3, "price": 120.00, "prep_time_minutes": 12, "calories": 540, "is_veg": 1, "spice_level": "Spicy", "rating": 4.9, "ingredients": "Basmati rice, Saffron, Fried onions, Paneer, Mixed vegetables, Dum spices, Raita", "description": "Slow-cooked fragrant long-grain basmati rice layered with vegetables, saffron, and rich caramelized onions.", "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80"},
    {"id": 14, "name": "Special Deluxe Student Thali", "category_id": 3, "price": 110.00, "prep_time_minutes": 8, "calories": 680, "is_veg": 1, "spice_level": "Medium", "rating": 4.9, "ingredients": "Paneer curry, Dal tadka, 3 Butter Rotis, Steamed Jeera Rice, Gulab Jamun, Salad, Pickle", "description": "The ultimate balanced feast! Rich paneer butter masala, yellow dal, hot rotis, fragrant rice & sweet.", "image_url": "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=600&auto=format&fit=crop&q=80"},
    {"id": 15, "name": "Paneer Butter Masala with 2 Naan", "category_id": 3, "price": 130.00, "prep_time_minutes": 12, "calories": 590, "is_veg": 1, "spice_level": "Medium", "rating": 4.8, "ingredients": "Cottage cheese, Cashew tomato gravy, Fresh cream, Kasuri methi, Butter garlic naan", "description": "Soft succulent paneer cubes simmered in velvety makhani gravy served with piping hot butter naans.", "image_url": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=600&auto=format&fit=crop&q=80"},
    {"id": 16, "name": "Chole Bhature (2 pcs)", "category_id": 3, "price": 95.00, "prep_time_minutes": 10, "calories": 650, "is_veg": 1, "spice_level": "Spicy", "rating": 4.8, "ingredients": "Chickpeas, Pomegranate seeds, Spices, Puffed bhature, Pickled onion, Mint sauce", "description": "Tangy, dark spiced chickpea curry served with giant balloon-puffed fried leavened breads.", "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=600&auto=format&fit=crop&q=80"},
    {"id": 17, "name": "Dal Khichdi with Desi Ghee", "category_id": 3, "price": 80.00, "prep_time_minutes": 7, "calories": 390, "is_veg": 1, "spice_level": "Mild", "rating": 4.7, "ingredients": "Rice, Moong dal, Cumin tadka, Garlic, Desi ghee, Papad, Mango pickle", "description": "Soulful, easily digestible comfort meal topped with aromatic garlic tadka and pure desi ghee.", "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&auto=format&fit=crop&q=80"},

    # Beverages & Shakes
    {"id": 18, "name": "Signature Cold Coffee with Ice Cream", "category_id": 4, "price": 55.00, "prep_time_minutes": 4, "calories": 240, "is_veg": 1, "spice_level": "Mild", "rating": 4.9, "ingredients": "Arabica coffee blend, Full cream milk, Vanilla ice cream scoop, Chocolate syrup drizzle", "description": "Thick, creamy, iced frothy espresso milkshake crowned with a velvety scoop of vanilla ice cream.", "image_url": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=600&auto=format&fit=crop&q=80"},
    {"id": 19, "name": "Special Masala Chai (Kulhad)", "category_id": 4, "price": 20.00, "prep_time_minutes": 3, "calories": 90, "is_veg": 1, "spice_level": "Mild", "rating": 4.9, "ingredients": "Assam black tea, Crushed cardamom, Ginger, Cinnamon, Whole milk, Jaggery option", "description": "Steaming hot traditional spiced milk tea served in an earthen clay kulhad for that authentic aroma.", "image_url": "https://images.unsplash.com/photo-1561336313-0bd5e0b27ec8?w=600&auto=format&fit=crop&q=80"},
    {"id": 20, "name": "Sweet Punjabi Mango Lassi", "category_id": 4, "price": 45.00, "prep_time_minutes": 3, "calories": 220, "is_veg": 1, "spice_level": "Mild", "rating": 4.7, "ingredients": "Thick curd, Alphonso mango pulp, Cardamom, Pistachio slivers", "description": "Refreshing and rich chilled yogurt smoothie blended with ripe sweet mango pulp.", "image_url": "https://images.unsplash.com/photo-1546173159-315724a31696?w=600&auto=format&fit=crop&q=80"},
    {"id": 21, "name": "Fresh Mint Lemonade (Mojito)", "category_id": 4, "price": 35.00, "prep_time_minutes": 3, "calories": 80, "is_veg": 1, "spice_level": "Mild", "rating": 4.6, "ingredients": "Fresh lime juice, Muddled mint leaves, Soda, Black salt, Cumin powder", "description": "Crisp sparkling lime and mint cooler with a refreshing dash of rock salt.", "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&auto=format&fit=crop&q=80"},

    # Desserts & Bakery
    {"id": 22, "name": "Hot Gulab Jamun (2 pcs)", "category_id": 5, "price": 40.00, "prep_time_minutes": 2, "calories": 290, "is_veg": 1, "spice_level": "Mild", "rating": 4.8, "ingredients": "Mawa / Khoya, Rosewater sugar syrup, Cardamom, Almond flakes", "description": "Melt-in-the-mouth fried dough dumplings soaked in warm fragrant cardamom and rose syrup.", "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&auto=format&fit=crop&q=80"},
    {"id": 23, "name": "Chocolate Brownie with Fudge", "category_id": 5, "price": 65.00, "prep_time_minutes": 3, "calories": 360, "is_veg": 1, "spice_level": "Mild", "rating": 4.9, "ingredients": "Dark cocoa, Butter, Chocochips, Warm fudge sauce, Walnuts", "description": "Gooey, decadent dark chocolate walnut brownie smothered in hot bittersweet fudge sauce.", "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=600&auto=format&fit=crop&q=80"},

    # Value Combos
    {"id": 24, "name": "Power Combo: 2 Vada Pav + Cold Coffee", "category_id": 6, "price": 90.00, "prep_time_minutes": 5, "calories": 680, "is_veg": 1, "spice_level": "Medium", "rating": 4.9, "ingredients": "2 Mumbai Vada Pav, 1 Chilled Signature Cold Coffee", "description": "The undisputed #1 student favorite! Save ₹15 with this ultimate hunger-busting combo.", "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=600&auto=format&fit=crop&q=80"},
    {"id": 25, "name": "Lunch Combo: Biryani + Cold Drink + Gulab Jamun", "category_id": 6, "price": 160.00, "prep_time_minutes": 10, "calories": 820, "is_veg": 1, "spice_level": "Spicy", "rating": 4.9, "ingredients": "1 Veg Dum Biryani, 1 Mint Cooler, 1 Hot Gulab Jamun", "description": "Complete 3-course lunch box deal engineered for satisfying midday cravings.", "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80"}
]

DEMO_USERS = [
    # Admin
    {"name": "Prof. Arvind Sharma", "email": "admin@smartcanteen.com", "phone": "9876543210", "student_id": None, "password_hash": ADMIN_PASSWORD_HASH, "role": "admin", "wallet_balance": 5000.00, "dietary_pref": "all"},
    {"name": "Operations Manager", "email": "manager@smartcanteen.com", "phone": "9876543211", "student_id": None, "password_hash": ADMIN_PASSWORD_HASH, "role": "admin", "wallet_balance": 5000.00, "dietary_pref": "all"},
    
    # Canteen Staff
    {"name": "Chef Ramesh (Head Chef)", "email": "staff@smartcanteen.com", "phone": "9876543220", "student_id": None, "password_hash": STAFF_PASSWORD_HASH, "role": "staff", "wallet_balance": 1000.00, "dietary_pref": "all"},
    {"name": "Kitchen Staff Suresh", "email": "suresh@smartcanteen.com", "phone": "9876543221", "student_id": None, "password_hash": STAFF_PASSWORD_HASH, "role": "staff", "wallet_balance": 1000.00, "dietary_pref": "all"},
    {"name": "Counter Staff Priya", "email": "priya@smartcanteen.com", "phone": "9876543222", "student_id": None, "password_hash": STAFF_PASSWORD_HASH, "role": "staff", "wallet_balance": 1000.00, "dietary_pref": "all"},

    # Students (Primary Demo & 20 peers)
    {"name": "Rahul Verma", "email": "student@smartcanteen.com", "phone": "9876500001", "student_id": "STU2026001", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 650.00, "dietary_pref": "veg"},
    {"name": "Aarav Mehta", "email": "aarav.mehta@college.edu", "phone": "9876500002", "student_id": "STU2026002", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 420.00, "dietary_pref": "veg"},
    {"name": "Ananya Sharma", "email": "ananya.s@college.edu", "phone": "9876500003", "student_id": "STU2026003", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 890.00, "dietary_pref": "veg"},
    {"name": "Rohan Deshmukh", "email": "rohan.d@college.edu", "phone": "9876500004", "student_id": "STU2026004", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 310.00, "dietary_pref": "all"},
    {"name": "Sneha Patil", "email": "sneha.p@college.edu", "phone": "9876500005", "student_id": "STU2026005", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 520.00, "dietary_pref": "veg"},
    {"name": "Vikram Malhotra", "email": "vikram.m@college.edu", "phone": "9876500006", "student_id": "STU2026006", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 740.00, "dietary_pref": "all"},
    {"name": "Pooja Hegde", "email": "pooja.h@college.edu", "phone": "9876500007", "student_id": "STU2026007", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 180.00, "dietary_pref": "veg"},
    {"name": "Tanmay Bhat", "email": "tanmay.b@college.edu", "phone": "9876500008", "student_id": "STU2026008", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 950.00, "dietary_pref": "all"},
    {"name": "Divya Joshi", "email": "divya.j@college.edu", "phone": "9876500009", "student_id": "STU2026009", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 350.00, "dietary_pref": "veg"},
    {"name": "Karan Singhania", "email": "karan.s@college.edu", "phone": "9876500010", "student_id": "STU2026010", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 600.00, "dietary_pref": "all"},
    {"name": "Ishita Roy", "email": "ishita.r@college.edu", "phone": "9876500011", "student_id": "STU2026011", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 480.00, "dietary_pref": "veg"},
    {"name": "Aditya Kulkarni", "email": "aditya.k@college.edu", "phone": "9876500012", "student_id": "STU2026012", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 220.00, "dietary_pref": "veg"},
    {"name": "Meera Nambiar", "email": "meera.n@college.edu", "phone": "9876500013", "student_id": "STU2026013", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 710.00, "dietary_pref": "veg"},
    {"name": "Siddharth Rao", "email": "siddharth.r@college.edu", "phone": "9876500014", "student_id": "STU2026014", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 530.00, "dietary_pref": "all"},
    {"name": "Kavya Iyer", "email": "kavya.i@college.edu", "phone": "9876500015", "student_id": "STU2026015", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 390.00, "dietary_pref": "veg"},
    {"name": "Varun Nair", "email": "varun.n@college.edu", "phone": "9876500016", "student_id": "STU2026016", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 820.00, "dietary_pref": "all"},
    {"name": "Riya Sen", "email": "riya.s@college.edu", "phone": "9876500017", "student_id": "STU2026017", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 640.00, "dietary_pref": "veg"},
    {"name": "Arjun Kapoor", "email": "arjun.k@college.edu", "phone": "9876500018", "student_id": "STU2026018", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 290.00, "dietary_pref": "all"},
    {"name": "Neha Gupta", "email": "neha.g@college.edu", "phone": "9876500019", "student_id": "STU2026019", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 500.00, "dietary_pref": "veg"},
    {"name": "Yash Mittal", "email": "yash.m@college.edu", "phone": "9876500020", "student_id": "STU2026020", "password_hash": DEFAULT_PASSWORD_HASH, "role": "student", "wallet_balance": 770.00, "dietary_pref": "all"}
]

SEAT_TABLES = [
    {"table_number": "T-01", "capacity": 2, "section": "Window Bay"},
    {"table_number": "T-02", "capacity": 2, "section": "Window Bay"},
    {"table_number": "T-03", "capacity": 4, "section": "Window Bay"},
    {"table_number": "T-04", "capacity": 4, "section": "Main Hall"},
    {"table_number": "T-05", "capacity": 4, "section": "Main Hall"},
    {"table_number": "T-06", "capacity": 6, "section": "Main Hall"},
    {"table_number": "T-07", "capacity": 6, "section": "Main Hall"},
    {"table_number": "T-08", "capacity": 4, "section": "Main Hall"},
    {"table_number": "T-09", "capacity": 2, "section": "AC Corner"},
    {"table_number": "T-10", "capacity": 4, "section": "AC Corner"},
    {"table_number": "T-11", "capacity": 4, "section": "AC Corner"},
    {"table_number": "T-12", "capacity": 6, "section": "AC Corner"},
    {"table_number": "T-13", "capacity": 4, "section": "Outdoor Patio"},
    {"table_number": "T-14", "capacity": 4, "section": "Outdoor Patio"},
    {"table_number": "T-15", "capacity": 8, "section": "Outdoor Patio"}
]

INVENTORY_ITEMS = [
    {"item_name": "Potatoes (Agra Special)", "category": "Vegetables", "current_stock": 65.0, "unit": "kg", "min_threshold": 25.0, "max_capacity": 150.0, "cost_per_unit": 22.0, "expiry_days": 10},
    {"item_name": "Fresh Paneer Blocks", "category": "Dairy", "current_stock": 18.5, "unit": "kg", "min_threshold": 10.0, "max_capacity": 40.0, "cost_per_unit": 320.0, "expiry_days": 3},
    {"item_name": "Full Cream Milk", "category": "Dairy", "current_stock": 42.0, "unit": "liters", "min_threshold": 20.0, "max_capacity": 100.0, "cost_per_unit": 64.0, "expiry_days": 2},
    {"item_name": "Fresh Pav Buns", "category": "Bakery", "current_stock": 140.0, "unit": "packets", "min_threshold": 40.0, "max_capacity": 300.0, "cost_per_unit": 18.0, "expiry_days": 2},
    {"item_name": "Sandwich Bread", "category": "Bakery", "current_stock": 28.0, "unit": "packets", "min_threshold": 15.0, "max_capacity": 60.0, "cost_per_unit": 35.0, "expiry_days": 3},
    {"item_name": "Dosa & Idli Batter", "category": "Pre-mix", "current_stock": 30.0, "unit": "kg", "min_threshold": 12.0, "max_capacity": 80.0, "cost_per_unit": 45.0, "expiry_days": 3},
    {"item_name": "Arabica Coffee Beans", "category": "Beverages", "current_stock": 8.5, "unit": "kg", "min_threshold": 5.0, "max_capacity": 25.0, "cost_per_unit": 650.0, "expiry_days": 60},
    {"item_name": "Assam Tea Leaves", "category": "Beverages", "current_stock": 12.0, "unit": "kg", "min_threshold": 4.0, "max_capacity": 30.0, "cost_per_unit": 380.0, "expiry_days": 90},
    {"item_name": "Basmati Rice (Royal)", "category": "Grains", "current_stock": 85.0, "unit": "kg", "min_threshold": 30.0, "max_capacity": 200.0, "cost_per_unit": 95.0, "expiry_days": 180},
    {"item_name": "Cooking Refined Oil", "category": "Oils", "current_stock": 45.0, "unit": "liters", "min_threshold": 20.0, "max_capacity": 120.0, "cost_per_unit": 130.0, "expiry_days": 120},
    {"item_name": "Mozzarella & Cheddar Blend", "category": "Dairy", "current_stock": 9.0, "unit": "kg", "min_threshold": 8.0, "max_capacity": 30.0, "cost_per_unit": 480.0, "expiry_days": 14},
    {"item_name": "Tomatoes & Onions", "category": "Vegetables", "current_stock": 52.0, "unit": "kg", "min_threshold": 20.0, "max_capacity": 100.0, "cost_per_unit": 30.0, "expiry_days": 5}
]

COUPONS = [
    {"code": "WELCOME50", "discount_percent": 0.0, "discount_amount": 50.0, "min_order_amount": 120.0, "max_discount": 50.0, "expiry_date": "2026-12-31"},
    {"code": "STUDENT10", "discount_percent": 10.0, "discount_amount": 0.0, "min_order_amount": 80.0, "max_discount": 30.0, "expiry_date": "2026-12-31"},
    {"code": "HUNGRY20", "discount_percent": 20.0, "discount_amount": 0.0, "min_order_amount": 200.0, "max_discount": 60.0, "expiry_date": "2026-12-31"},
    {"code": "CHAI5", "discount_percent": 0.0, "discount_amount": 10.0, "min_order_amount": 40.0, "max_discount": 10.0, "expiry_date": "2026-12-31"}
]

FEEDBACK_TEMPLATES = [
    ("Masala Dosa was crisp and the sambhar was steaming hot!", 5, "Taste", "POSITIVE"),
    ("Vada Pav was super authentic and spicy. Great quick bite between lectures.", 5, "Taste", "POSITIVE"),
    ("Cold coffee is always top tier. Amazing texture and ice cream blend.", 5, "Quality", "POSITIVE"),
    ("The waiting time for Biryani was a bit too long during peak lunch break (15 mins).", 3, "Waiting Time", "NEUTRAL"),
    ("Special Deluxe Thali is very affordable and filling for students. Best value for money.", 5, "Price", "POSITIVE"),
    ("Canteen tables were slightly crowded today, need more seats near the window.", 3, "Cleanliness", "NEUTRAL"),
    ("Friendly staff and very fast counter service on morning idlis!", 5, "Service", "POSITIVE"),
    ("Sandwich cheese was cold and not melted properly.", 2, "Quality", "NEGATIVE"),
    ("Samosa crust was slightly oily today, but the green mint chutney was fantastic.", 4, "Taste", "POSITIVE"),
    ("Ordering ahead saved me 20 minutes in line! Love the smart canteen app.", 5, "Service", "POSITIVE"),
    ("Portion size of French fries was very generous for ₹60.", 5, "Quantity", "POSITIVE"),
    ("Prices are extremely student-friendly, especially the combo meals.", 5, "Price", "POSITIVE")
]

def generate_synthetic_orders(num_orders=500):
    """
    Generates realistic historical order dataset spanning the past 45 days.
    Simulates student habits: peak morning rush (8:30-10:00), lunch break (12:00-14:00),
    evening snack rush (16:30-18:00), exam days demand surges, and weekend dips.
    """
    orders = []
    order_items = []
    
    # Students start from user_id 6 (first 5 are admins & staff)
    student_ids = list(range(6, 26))
    now = datetime.datetime.now()
    
    order_counter = 1000
    
    for i in range(num_orders):
        order_counter += 1
        order_num = f"ORD-{order_counter}"
        student_id = random.choice(student_ids)
        
        # Distribute over last 45 days
        days_ago = random.randint(0, 44)
        
        # Time distribution (Realistic Canteen Peaks)
        rand_time_bucket = random.choices(
            ['breakfast', 'lunch', 'evening_snack', 'off_peak'],
            weights=[25, 45, 20, 10],
            k=1
        )[0]
        
        if rand_time_bucket == 'breakfast':
            hour = random.randint(8, 10)
            minute = random.randint(0, 59)
        elif rand_time_bucket == 'lunch':
            hour = random.randint(12, 14)
            minute = random.randint(0, 59)
        elif rand_time_bucket == 'evening_snack':
            hour = random.randint(16, 18)
            minute = random.randint(0, 59)
        else:
            hour = random.choice([11, 15, 19])
            minute = random.randint(0, 59)
            
        order_date = now - datetime.timedelta(days=days_ago, hours=(now.hour - hour), minutes=(now.minute - minute))
        
        # Pick 1 to 3 items based on meal type
        if rand_time_bucket == 'breakfast':
            eligible_food_ids = [1, 2, 3, 4, 19, 20]
        elif rand_time_bucket == 'lunch':
            eligible_food_ids = [13, 14, 15, 16, 17, 24, 25, 18]
        elif rand_time_bucket == 'evening_snack':
            eligible_food_ids = [5, 6, 7, 8, 9, 10, 11, 18, 19, 21, 24]
        else:
            eligible_food_ids = list(range(1, 26))
            
        selected_food_ids = random.sample(eligible_food_ids, k=min(random.randint(1, 3), len(eligible_food_ids)))
        
        subtotal = 0.0
        current_items = []
        
        for fid in selected_food_ids:
            food = next(f for f in FOOD_ITEMS if f["id"] == fid)
            qty = random.choices([1, 2, 3], weights=[70, 25, 5], k=1)[0]
            item_total = food["price"] * qty
            subtotal += item_total
            current_items.append({
                "food_id": fid,
                "quantity": qty,
                "unit_price": food["price"],
                "subtotal": item_total
            })
            
        # Discount simulation
        has_coupon = random.random() < 0.25
        discount = 20.0 if has_coupon and subtotal > 100 else 0.0
        tax = round((subtotal - discount) * 0.05, 2)
        final_amount = round(subtotal - discount + tax, 2)
        
        # Status simulation: older orders completed; very recent might be ready or preparing
        if days_ago == 0 and (now - order_date).total_seconds() < 1800:
            status = random.choice(['PREPARING', 'READY', 'ACCEPTED'])
            payment_status = 'PAID'
        else:
            status = 'COMPLETED'
            payment_status = 'PAID'
            
        payment_method = random.choices(
            ['upi', 'wallet', 'card', 'cash_on_pickup'],
            weights=[55, 25, 10, 10],
            k=1
        )[0]
        
        orders.append({
            "id": i + 1,
            "order_number": order_num,
            "student_id": student_id,
            "total_amount": subtotal,
            "discount_amount": discount,
            "tax_amount": tax,
            "final_amount": final_amount,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "order_status": status,
            "estimated_prep_time": random.randint(6, 16),
            "pickup_time": order_date + datetime.timedelta(minutes=random.randint(10, 20)),
            "special_instructions": "Less spicy please" if random.random() < 0.15 else None,
            "created_at": order_date.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": order_date.strftime('%Y-%m-%d %H:%M:%S'),
            "items": current_items
        })
        
    return orders
