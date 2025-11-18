# ================================
# VIP FIX: (ModuleNotFoundError Fix)
# 'utils' folder khatam ho gaya hai
# ================================
from database import users_col
from auth import hash_password
# ================================

# Admin details
admin_email = "admin@moaztech.com"
admin_name = "Admin"
admin_password = "Admin123!"  # tum chaaho to change kar sakte ho

# Check if admin already exists
if users_col.find_one({"email": admin_email}):
    print("Admin already exists in the database.")
else:
    hashed = hash_password(admin_password)
    users_col.insert_one({
        "name": admin_name,
        "email": admin_email,
        "password": hashed,
        "status": "approved",
        "role": "admin",
        "employee_id": None,
        "joined": None,
        "attempts": 0
    })
    print("Admin user created successfully!")