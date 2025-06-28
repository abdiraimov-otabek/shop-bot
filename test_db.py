#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection and database functionality
"""

import os
from dotenv import load_dotenv
from utils.db.storage import DatabaseManager

# Load environment variables
load_dotenv()


def test_database_connection():
    """Test the database connection and basic operations"""
    try:
        print("🔌 Testing PostgreSQL connection...")

        # Initialize database
        db = DatabaseManager()
        print("✅ Database connection successful!")

        # Test table creation
        print("📋 Creating tables...")
        db.create_tables()
        print("✅ Tables created successfully!")

        # Test basic operations
        print("🧪 Testing basic operations...")

        # Test categories
        db.query("INSERT INTO categories VALUES (%s, %s)", (1, "Test Category"))
        categories = db.fetchall("SELECT * FROM categories WHERE idx = %s", (1,))
        print(f"✅ Categories test: {categories}")

        # Test products
        db.query(
            "INSERT INTO products VALUES (%s, %s, %s, %s, %s, %s)",
            (
                "test_product",
                "Test Product",
                "Test Description",
                "test_image.jpg",
                1000,
                "Test Category",
            ),
        )
        products = db.fetchall(
            "SELECT * FROM products WHERE idx = %s", ("test_product",)
        )
        print(f"✅ Products test: {products}")

        # Test users
        db.add_user(123456789, "Test User", "+1234567890")
        user = db.get_user(123456789)
        print(f"✅ Users test: {user}")

        # Clean up test data
        db.query("DELETE FROM products WHERE idx = %s", ("test_product",))
        db.query("DELETE FROM categories WHERE idx = %s", (1,))
        db.query("DELETE FROM users WHERE cid = %s", (123456789,))

        print("🧹 Test data cleaned up!")
        print("🎉 All database tests passed!")

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    test_database_connection()
