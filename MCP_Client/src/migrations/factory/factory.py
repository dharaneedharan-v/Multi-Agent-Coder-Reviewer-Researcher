
import random
from decimal import Decimal
from faker import Faker

from src.repositories.schema.schema import (
    Customers,
    Products,
    Orders,
    OrderItems,
    OrderStatusEnum
)

fake = Faker()


class CustomerFactory:
    """
        Creates a new `Customers` ORM instance with fake data.

        Returns
        -------
        Customers
            A new customer object with:
            - Random name
            - Unique phone number
            - Random address
            - Unique email address

        
        """
    @staticmethod
    def build():
        return Customers(
            customer_name=fake.name(),
            customer_phone=fake.unique.phone_number(),
            customer_address=fake.address(),
            customer_email=fake.unique.email(),
        )


class ProductFactory:
    @staticmethod
    def build():
        """
        Creates a new `Products` ORM instance with fake data.

        Returns
        -------
        Products
            A new product object with:
            - Unique product code
            - Random name and description
            - Random price between 1000 and 50000
            - 10% tax amount
            - Random discount between 0 and 500
            - Random stock between 1 and 100

       
        """
        price = Decimal(random.randint(1000, 50000))

        return Products(
            product_code=fake.unique.bothify(text="P####"),
            product_name=fake.word().capitalize(),
            product_description=fake.sentence(),
            product_price=price,
            product_tax_amount=price * Decimal("0.10"),
            product_discount=Decimal(random.randint(0, 500)),
            product_stock=random.randint(1, 100),
        )


class OrderFactory:
    @staticmethod
    def build(customer_id, products):
        """
        Creates a new `Orders` ORM instance and associated `OrderItems`.

        Parameters
        ----------
        customer_id : int
            The ID of the customer placing the order.
        products : list of Products
            The products to include in the order.

        Returns
        -------
        tuple
            (Orders, list[OrderItems]) where:
            - Orders: The order object with calculated total amount.
            - list[OrderItems]: The associated order items.

        
        """
        order = Orders(
            customer_id=customer_id,
            order_status=random.choice(list(OrderStatusEnum)),
            order_amount=Decimal("0.0"),
            order_delivery_amount=Decimal("100.000"),
        )

        order_items = []
        total = Decimal("0.0")

        for product in products:
            quantity = random.randint(1, 3)
            total += product.product_price * quantity

            order_items.append(
                OrderItems(
                    product_id=product.product_id,
                    quantity=quantity
                )
            )

        order.order_amount = total

        return order, order_items 
