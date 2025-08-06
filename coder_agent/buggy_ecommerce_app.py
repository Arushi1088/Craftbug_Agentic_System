#!/usr/bin/env python3
"""
Buggy E-Commerce Web Application for AI Agent Testing
This application contains multiple realistic bugs that need AI-powered fixes
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import datetime
import json
import os
import sqlite3
import hashlib

app = Flask(__name__)
# AI Fix: Added secret key for session management
app.secret_key = 'ai-fixed-secret-key-for-demo-purposes'

# Bug 1: Missing secret key for sessions (security vulnerability)
# app.secret_key = 'your-secret-key-here'

# Bug 2: Hardcoded database credentials (security issue)
DATABASE_PATH = 'ecommerce.db'
ADMIN_PASSWORD = 'admin123'  # Hardcoded admin password

# Bug 3: Global variable without proper initialization
shopping_cart = None  # This will cause NoneType errors
current_user = {}

# Bug 4: No database initialization
def init_db():
    """Initialize database - but has bugs"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Bug 5: Missing error handling for database operations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Bug 6: No sample data insertion for testing
    conn.commit()
    conn.close()

@app.route('/')
def home():
    """Home page displaying products"""
    try:
        products = get_all_products()
        
        # Bug 7: Division by zero when no products exist
        total_products = len(products)
        featured_percentage = (3 / total_products) * 100  # Crashes if no products
        
        # Bug 8: Undefined variable
        current_time = datetime.datetime.now()
        
        return render_template('ecommerce_home.html', 
                             products=products,
                             featured_pct=featured_percentage,
                             time=current_time,
                             user=current_user)
    except Exception as e:
        # Bug 9: Poor error handling exposes internal details
        return f"Application Error: {str(e)}<br>Contact support", 500

@app.route('/products')
def products():
    """Product listing page with search functionality"""
    search_query = request.args.get('search', '')
    category = request.args.get('category', 'all')
    
    try:
        # Bug 10: SQL injection vulnerability
        if search_query:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            query = f"SELECT * FROM products WHERE name LIKE '%{search_query}%'"  # SQL injection
            cursor.execute(query)
            products = cursor.fetchall()
            conn.close()
        else:
            products = get_all_products()
        
        # Bug 11: Incorrect data processing
        for product in products:
            if product[3] < 0:  # Bug: negative stock check incorrect
                product[3] = "Out of Stock"  # Bug: mixing types
        
        return render_template('products.html', products=products, search=search_query)
    except Exception as e:
        return f"Product Error: {e}", 500

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Individual product page"""
    try:
        product = get_product_by_id(product_id)
        
        # Bug 12: No null check for product
        product_name = product[1]  # Will crash if product is None
        
        # Bug 13: Incorrect calculation
        discount_price = product[2] * 0.9  # Apply 10% discount
        savings = product[2] - discount_price
        
        # Bug 14: Accessing undefined cart
        cart_quantity = shopping_cart.get(product_id, 0)  # NoneType error
        
        return render_template('product_detail.html', 
                             product=product,
                             discount_price=discount_price,
                             savings=savings,
                             in_cart=cart_quantity)
    except Exception as e:
        return f"Product Detail Error: {e}", 500

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add product to shopping cart"""
    try:
        quantity = int(request.form.get('quantity', 1))
        
        # Bug 15: No stock validation
        product = get_product_by_id(product_id)
        
        # Bug 16: Cart initialization bug
        if shopping_cart is None:
            shopping_cart = {}  # This won't work due to scope
        
        # Bug 17: No quantity validation
        if product_id in shopping_cart:
            shopping_cart[product_id] += quantity
        else:
            shopping_cart[product_id] = quantity
        
        flash(f'Added {quantity} items to cart')
        return redirect(url_for('product_detail', product_id=product_id))
    except Exception as e:
        return f"Cart Error: {e}", 500

@app.route('/cart')
def view_cart():
    """Display shopping cart"""
    try:
        cart_items = []
        total_price = 0
        
        # Initialize cart if None (AI Fix: Added null checking)
        if 'cart' not in session or session['cart'] is None:
            session['cart'] = {}
        
        # Fixed: Use session cart instead of undefined shopping_cart
        for product_id, quantity in session['cart'].items():
            product = get_product_by_id(product_id)
            if product:  # AI Fix: Added null check for product
                item_total = product[2] * quantity
            total_price += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
        
        # Bug 19: Tax calculation error
        tax_rate = 0.08
        tax_amount = total_price * tax_rate
        final_total = total_price + tax_amount
        
        return render_template('cart.html', 
                             cart_items=cart_items,
                             subtotal=total_price,
                             tax=tax_amount,
                             total=final_total)
    except Exception as e:
        return f"Cart View Error: {e}", 500

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout process with payment simulation"""
    if request.method == 'POST':
        try:
            # Bug 20: No payment validation
            payment_method = request.form.get('payment_method')
            card_number = request.form.get('card_number')
            
            # Bug 21: Storing sensitive data (security issue)
            payment_info = {
                'card_number': card_number,  # Should never store full card numbers
                'timestamp': str(datetime.datetime.now())
            }
            
            # Bug 22: No order processing
            # Should create order record, update inventory, etc.
            
            # Bug 23: Cart not cleared after purchase
            flash('Order placed successfully!')
            return redirect(url_for('home'))
            
        except Exception as e:
            return f"Checkout Error: {e}", 500
    
    # GET request - show checkout form
    return render_template('checkout.html')

@app.route('/admin')
def admin_panel():
    """Admin panel with authentication bugs"""
    # Bug 24: No authentication check
    # Should verify admin credentials before allowing access
    
    try:
        products = get_all_products()
        user_count = get_user_count()
        
        # Bug 25: Calculation error
        revenue = calculate_total_revenue()
        avg_order_value = revenue / 0  # Division by zero
        
        return render_template('admin.html', 
                             products=products,
                             users=user_count,
                             revenue=revenue,
                             avg_order=avg_order_value)
    except Exception as e:
        return f"Admin Error: {e}", 500

def get_all_products():
    """Fetch all products from database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        conn.close()
        return products
    except sqlite3.Error:
        # Bug 26: Poor error handling in database functions
        return []  # Should handle database errors properly

def get_product_by_id(product_id):
    """Fetch single product by ID"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        conn.close()
        return product
    except sqlite3.Error:
        return None

def get_user_count():
    """Get total number of users"""
    # Bug 27: Hardcoded return value
    return 42  # Should actually query database

def calculate_total_revenue():
    """Calculate total revenue"""
    # Bug 28: Mock calculation instead of real data
    return 1500.00  # Should calculate from actual orders

# Bug 29: No proper error handlers
@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

# Bug 30: Missing main guard and production settings
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)  # Debug mode in production
