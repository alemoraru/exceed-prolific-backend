import unittest
from snippetA import SalesProcessor, SalesRecord


class TestSnippetA(unittest.TestCase):
    """Unit tests for the SalesProcessor class in snippetA.py."""

    def test_sales_data_types(self):
        """Test that sales_data contains SalesRecord objects."""
        processor = SalesProcessor()
        self.assertTrue(all(isinstance(x, SalesRecord) for x in processor.sales_data))

    def test_sales_data_values(self):
        """Test that sales_data contains expected values."""
        processor = SalesProcessor()
        self.assertEqual(
            [r.amount for r in processor.sales_data], ["100", 200, "150.5", 175]
        )

    def test_clean_sales_data_conversion_and_discard(self):
        """Test that clean_sales_data converts valid amounts and discards invalid ones."""
        processor = SalesProcessor()
        cleaned = processor.clean_sales_data()
        # '100' and '150.5' should be converted to float, 200 and 175 as float, all valid
        self.assertEqual(cleaned, [100.0, 200.0, 150.5, 175.0])

    def test_clean_sales_data_with_invalid(self):
        """Test that clean_sales_data discards invalid amounts."""
        processor = SalesProcessor()
        processor.sales_data.append(SalesRecord("not_a_number"))
        cleaned = processor.clean_sales_data()
        self.assertEqual(cleaned, [100.0, 200.0, 150.5, 175.0])

    def test_total_sales_sum(self):
        """Test that total_sales returns the correct sum of cleaned sales data."""
        processor = SalesProcessor()
        self.assertAlmostEqual(processor.total_sales(), 625.5)

    def test_total_sales_empty(self):
        """Test that total_sales returns 0 when there are no sales records."""
        processor = SalesProcessor()
        processor.sales_data = []
        self.assertEqual(processor.total_sales(), 0)

    def test_total_sales_with_all_invalid(self):
        """Test that total_sales returns 0 when all sales records are invalid."""
        processor = SalesProcessor()
        processor.sales_data = [SalesRecord("foo"), SalesRecord("bar")]
        self.assertEqual(processor.total_sales(), 0)

    def test_add_sales_record(self):
        """Test that add_sales_record correctly adds a SalesRecord to sales_data."""
        processor = SalesProcessor()
        processor.add_sales_record(SalesRecord(50))
        self.assertIn(50, [r.amount for r in processor.sales_data])

    def test_clean_sales_data_handles_mixed_types(self):
        """Test that clean_sales_data handles mixed types and discards invalid ones."""
        processor = SalesProcessor()
        processor.sales_data.extend(
            [
                SalesRecord("300"),
                SalesRecord("400.25"),
                SalesRecord(500),
                SalesRecord("not_a_number"),
            ]
        )
        cleaned = processor.clean_sales_data()
        # '100', '300' are digit strings, '150.5', '400.25' are valid floats, 200, 175, 500 are ints/floats, 'not_a_number' is discarded
        self.assertEqual(cleaned, [100.0, 200.0, 150.5, 175.0, 300.0, 400.25, 500.0])

    def test_clean_sales_data_discards_invalid(self):
        """Test that clean_sales_data discards records that cannot be converted to float."""
        processor = SalesProcessor()
        processor.sales_data = [
            SalesRecord("foo"),
            SalesRecord("bar"),
            SalesRecord("123abc"),
        ]
        cleaned = processor.clean_sales_data()
        self.assertEqual(cleaned, [])

    def test_total_sales_with_mixed_and_invalid(self):
        processor = SalesProcessor()
        processor.sales_data.extend(
            [SalesRecord("300"), SalesRecord("not_a_number"), SalesRecord(50.5)]
        )
        self.assertAlmostEqual(processor.total_sales(), 625.5 + 300.0 + 50.5)

    def test_total_sales_with_only_invalid(self):
        """Test that total_sales returns 0 when all sales records are invalid."""
        processor = SalesProcessor()
        processor.sales_data = [SalesRecord("foo"), SalesRecord("bar")]
        self.assertEqual(processor.total_sales(), 0)

    def test_total_sales_with_empty_list(self):
        """Test that total_sales returns 0 when sales_data is empty."""
        processor = SalesProcessor()
        processor.sales_data = []
        self.assertEqual(processor.total_sales(), 0)
