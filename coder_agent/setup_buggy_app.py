#!/usr/bin/env python3
"""
Initialize the Buggy E-Commerce Application with Sample Data
Run this script to set up the test environment
"""

import sqlite3
import os

def setup_database():
    """Create database and insert sample data"""
    db_path = 'ecommerce.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            description TEXT
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample products
    sample_products = [
        ('Laptop Pro X1', 999.99, 15, 'High-performance laptop for professionals'),
        ('Wireless Headphones', 149.99, 50, 'Premium noise-cancelling headphones'),
        ('Smart Watch Series 5', 299.99, 25, 'Advanced fitness and health tracking'),
        ('Bluetooth Speaker', 79.99, 30, 'Portable speaker with amazing sound quality'),
        ('Gaming Mouse', 59.99, 40, 'Precision gaming mouse with RGB lighting'),
        ('4K Monitor 27"', 399.99, 12, 'Ultra-high definition monitor for work and gaming'),
        ('USB-C Hub', 39.99, 60, '7-in-1 USB-C hub with multiple ports'),
        ('Wireless Charger', 29.99, 45, 'Fast wireless charging pad for smartphones'),
    ]
    
    cursor.executemany(
        'INSERT INTO products (name, price, stock, description) VALUES (?, ?, ?, ?)',
        sample_products
    )
    
    # Insert sample users
    sample_users = [
        ('admin', 'admin@store.com', 'admin123'),
        ('testuser', 'test@email.com', 'password123'),
        ('customer1', 'customer1@email.com', 'pass123'),
    ]
    
    cursor.executemany(
        'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
        sample_users
    )
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized with sample data!")
    print("📦 Products added: 8 items")
    print("👥 Users added: 3 users")
    print("\n🐛 The application contains 30+ intentional bugs for AI testing")

if __name__ == '__main__':
    setup_database()
