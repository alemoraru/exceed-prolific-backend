class SalesProcessor:
    def __init__(self):
        """Initializes the processor with sales data."""
        self.sales_data = ['100', '200', '150', '175']

    def total_sales(self):
        """Returns the total sales as the sum of all sales in the list."""
        total = 0
        for sale in self.sales_data:
            total += sale
        return total


def main():
    processor = SalesProcessor()
    print("Total sales:", processor.total_sales())


main()