from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html', name=None, balance=None, card_number=None)

# وظيفة البحث عن الطالب
@app.route('/search', methods=['POST'])
def search():
    card_number = request.form['card_number']
    
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, balance FROM students WHERE rfid = ?", (card_number,))
    user = cursor.fetchone()
    conn.close()

    if user:
        name, balance = user
        return render_template('index.html', name=name, balance=balance, card_number=card_number)
    else:
        return render_template('index.html', name="غير مسجل", balance="غير متاح", card_number=card_number)

# وظيفة الطباعة وخصم الرصيد
@app.route('/print', methods=['POST'])
def print_pages():
    card_number = request.form.get('card_number', '')
    pages = int(request.form.get('pages', 0))
    cost_per_page = 1  # تكلفة الصفحة

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM students WHERE rfid = ?", (card_number,))
    user = cursor.fetchone()

    if user:
        balance = user[0]
        total_cost = pages * cost_per_page
        if balance >= total_cost:
            new_balance = balance - total_cost
            cursor.execute("UPDATE students SET balance = ? WHERE rfid = ?", (new_balance, card_number))
            conn.commit()
            conn.close()
            return render_template('index.html', message=f"✅ تم الطباعة بنجاح! الرصيد المتبقي: {new_balance} EGP", name=None, balance=None, card_number=None)
        else:
            conn.close()
            return render_template('index.html', message="❌ الرصيد غير كافٍ للطباعة!", name=None, balance=None, card_number=None)
    else:
        conn.close()
        return render_template('index.html', message="❌ رقم البطاقة غير موجود!", name=None, balance=None, card_number=None)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # استخدام المنفذ المخصص من Railway
    app.run(host="0.0.0.0", port=port,debug=True)
