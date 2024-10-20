class ShoppingCart:
    def __init__(self):
        self.cart = []
        self.total = 0.0

    def add_item(self, product, price, quantity=1, additional_info=None):
        """Add a product to the shopping cart, or update quantity if it already exists."""
        additional_info = additional_info or ""

        # Check if the product already exists in the cart
        for item in self.cart:
            if item['product'] == product and item['additional_info'] == additional_info:
                # If product exists, update the quantity and total
                item['quantity'] += quantity
                self.total += price * quantity
                return

        # If product doesn't exist, add new item to the cart
        item = {
            "product": product,
            "price": price,
            "quantity": quantity,
            "additional_info": additional_info
        }
        self.cart.append(item)
        self.total += price * quantity

    def get_total(self):
        """Return the total price of items in the cart."""
        return self.total

    def get_cart(self):
        """Return all items in the cart."""
        return self.cart

    def clear_cart(self):
        """Clear all items in the cart."""
        self.cart = []
        self.total = 0.0