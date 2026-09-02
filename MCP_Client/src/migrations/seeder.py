
from datetime import datetime, timezone
from operator import imod
import random
import time
from sqlalchemy.orm import Session
from src.repositories.Database import db
from src.repositories.schema.schema import * 


class DatabaseSeeder:

    def __init__(self):
        self.session = db.SessionLocal()
    # Customers
    def seed_customers(self):
        customers = [
            Customer(
                customer_name    = "Arun Johnson",
                customer_phone   = "9876543210",
                customer_address = "12 Baker Street, London",
                customer_email   = "alice.johnson@email.com",
            ),
            Customer(
                customer_name    = "Bob Martinez",
                customer_phone   = "9123456780",
                customer_address = "45 Elm Avenue, New York",
                customer_email   = "bob.martinez@email.com",
            ),
            Customer(
                customer_name    = "Carol White",
                customer_phone   = "9988776655",
                customer_address = "78 Oak Lane, Chicago",
                customer_email   = "carol.white@email.com",
            ),
            Customer(
                customer_name    = "David Brown",
                customer_phone   = "9871234560",
                customer_address = "22 Pine Road, Houston",
                customer_email   = "david.brown@email.com",
            ),
            Customer(
                customer_name    = "Eva Green",
                customer_phone   = "9765432109",
                customer_address = "55 Maple Drive, Phoenix",
                customer_email   = "eva.green@email.com",
            ),
            Customer(
                customer_name    = "Frank Lee",
                customer_phone   = "9654321098",
                customer_address = "99 Cedar Blvd, Seattle",
                customer_email   = "frank.lee@email.com",
            ),
        ]
        self.session.add_all(customers)
        self.session.flush()   # assigns customer_id before children need it
        return customers
   
    # Error Logs

    def seed_errors(self):
        errors = [
            Error(
                file_name     = "order_service.py_Seed ",
                function_name = "create_order",
                message       = "NullPointerException: order_amount cannot be None",
                error_time    = datetime.now(timezone.utc),
            ),
            Error(
                file_name     = "customer_repo.py_SEED",
                function_name = "get_customer_by_email",
                message       = "NoResultFound: no customer with given email",
                error_time    = datetime.now(timezone.utc),
            ),
            Error(
                file_name     = "menu_service.py_Seed ",
                function_name = "update_price",
                message       = "ValueError: price must be greater than zero",
                error_time    = datetime.now(timezone.utc),
            ),
            Error(
                file_name     = "rating_service.py_Seed",
                function_name = "submit_rating",
                message       = "IntegrityError: duplicate rating for same customer and item",
                error_time    = datetime.now(timezone.utc)
            ),
        ]
        self.session.add_all(errors)
        self.session.flush()
        return errors

   
    # Master seed() — called from main

    def seed(self):
        try:
            print(" Starting database seeding...")

            customers  = self.seed_customers()
            print(f"    {len(customers)} customers")

            errors     = self.seed_errors()
            print(f"    {len(errors)} error logs")

            self.session.commit()
            print("Seeding completed successfully!")

        except Exception as e:
            self.session.rollback()
            print(f"\n Seeding failed — transaction rolled back.\n    Reason: {e}")
            raise

        finally:
            self.session.close() 

