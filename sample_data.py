# ================================
# VIP FIX: (ModuleNotFoundError Fix)
# 'utils' folder khatam ho gaya hai
# ================================
from database import users_col, quizzes_col
from auth import hash_password
# ================================
from datetime import datetime

def insert_sample():
    # sample admin (password: adminpass)
    if users_col.find_one({'email': 'admin@moaztech.com'}) is None:
        users_col.insert_one({
            'name': 'Moaz',
            'email': 'admin@moaztech.com',
            'password': hash_password('adminpass'),
            'status': 'approved',
            'attempts': 0,
            'employee_id': 'MT-000',
            'joined': datetime.utcnow(),
            'role': 'admin'
        })
        print("Inserted sample admin")

    # sample quiz (5 questions)
    if quizzes_col.count_documents({}) == 0:
        quiz = {
            'category': 'General Knowledge',
            'questions': [
                {'question': 'Capital of Pakistan?', 'options': ['Lahore','Islamabad','Karachi'], 'answer': 'Islamabad'},
                {'question': 'Python is a ____?', 'options': ['Snake','Programming Language','Car'], 'answer': 'Programming Language'},
                {'question': 'HTML stands for?', 'options': ['HyperText Markup Language','Home Tool Markup Language','None'], 'answer': 'HyperText Markup Language'},
                {'question': '2 + 2 = ?', 'options': ['3','4','5'], 'answer': '4'},
                {'question': 'Sun rises from?', 'options': ['West','East','North'], 'answer': 'East'}
            ]
        }
        quizzes_col.insert_one(quiz)
        print("Inserted sample quiz")

if __name__ == "__main__":
    insert_sample()