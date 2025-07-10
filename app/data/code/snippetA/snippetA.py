class SalesRecord:
    """A simple class to represent a sales record with an amount."""

    def __init__(self, amount):
        """Initializes the sales record with an amount."""
        self.amount = amount


class SalesProcessor:
    def __init__(self):
        """
        Simulates loading sales data from an external source with mixed types.
        Data is static for this example, as we don't use any external files.
        """

        self.sales_data = [
            SalesRecord("100"),
            SalesRecord(200),
            SalesRecord("150.5"),
            SalesRecord(175),
        ]

    def add_sales_record(self, data: SalesRecord):
        self.sales_data.append(data)

    def clean_sales_data(self):
        """
        Attempts to clean sales data by converting all amounts to float if possible.
        If the amount cannot be converted, it is discarded.
        """
        cleaned = []
        for record in self.sales_data:
            if isinstance(record.amount, str) and record.amount.isdigit():
                cleaned.append(record.amount)
            else:
                try:
                    cleaned.append(float(record.amount))
                except (ValueError, TypeError):
                    continue
        return cleaned

    def total_sales(self):
        """
        Returns the total sales as the sum of all
        sales in the list after cleaning the data.
        """

        cleaned_data = self.clean_sales_data()
        total = 0
        for sale in cleaned_data:
            total += sale
        return total


def main():
    processor = SalesProcessor()
    print("Total sales:", processor.total_sales())


if __name__ == "__main__":
    main()
