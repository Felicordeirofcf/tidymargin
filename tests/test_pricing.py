"""Unit tests for the pricing math (kit/pricing.py)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kit"))
from pricing import (Job, PricingError, Settings, break_even, check_price,  # noqa: E402
                     commercial_bid, crew_cost, labor_hours, margin_to_markup,
                     markup_to_margin, quote, round_up)


class TestBasics(unittest.TestCase):
    def test_markup_is_not_margin(self):
        self.assertAlmostEqual(markup_to_margin(0.30), 0.230769, places=5)
        self.assertAlmostEqual(margin_to_markup(0.30), 0.428571, places=5)
        with self.assertRaises(PricingError):
            margin_to_markup(1.0)

    def test_round_up(self):
        self.assertEqual(round_up(141.2, 5), 145)
        self.assertEqual(round_up(145.0, 5), 145)          # exact stays
        self.assertEqual(round_up(29.000000000001, 1), 29)  # float noise
        self.assertEqual(round_up(141.2, 0), 141.2)        # no rounding

    def test_labor_hours(self):
        s = Settings()
        j = Job(sqft=2000, bedrooms=3, bathrooms=2, service_type="Deep Cleaning")
        self.assertAlmostEqual(labor_hours(j, s), (2 + 0.75 + 1.0) * 1.75)
        j.hours_override = 5
        self.assertEqual(labor_hours(j, s), 5)


class TestQuote(unittest.TestCase):
    def setUp(self):
        self.s = Settings(rounding=0, minimum_price=0)

    def test_margin_is_hit_exactly_without_rounding(self):
        for margin in (0.1, 0.25, 0.3, 0.45):
            for tax in (0.0, 0.0825):
                j = Job(sqft=1500, bedrooms=2, bathrooms=2, supplies=12, miles=10,
                        margin_override=margin, tax_override=tax)
                q = quote(j, self.s)
                self.assertAlmostEqual(q["net_margin"], margin, places=9)
                # net profit = price - total cost - card fee
                self.assertAlmostEqual(q["net_profit"],
                                       q["price"] - q["total_cost"] - q["card_fee"], places=9)

    def test_known_values(self):
        s = Settings(card_fee=0, rounding=0, minimum_price=0, monthly_overhead=0)
        j = Job(hours_override=4, crew=2)
        q = quote(j, s)
        labor = 4 * 18 * 1.12
        self.assertAlmostEqual(q["labor_cost"], labor)
        self.assertAlmostEqual(q["price"], labor / 0.7)
        self.assertAlmostEqual(q["onsite_hours"], 2)
        self.assertAlmostEqual(q["markup_on_cost"], 0.3 / 0.7)

    def test_rounding_and_minimum(self):
        s = Settings()
        q = quote(Job(sqft=2200, bedrooms=3, bathrooms=2, crew=2, supplies=18, miles=14,
                      service_type="Deep Cleaning"), s)
        self.assertEqual(q["price"], 295)
        self.assertGreaterEqual(q["net_margin"], 0.30)
        tiny = quote(Job(hours_override=0.5), s)
        self.assertEqual(tiny["price"], s.minimum_price)

    def test_discount_keeps_margin(self):
        s = Settings()
        q = quote(Job(sqft=1000, bedrooms=2, bathrooms=1, frequency="Weekly"), s)
        self.assertAlmostEqual(q["total_discount"], 0.15)
        self.assertGreaterEqual(q["regular_price"] * 0.85, q["price"] - 1e-9)
        self.assertGreaterEqual(q["net_margin"], s.target_margin - 1e-9)

    def test_combined_discount(self):
        q = quote(Job(sqft=1000, frequency="Every 2 weeks", extra_discount=0.1), Settings())
        self.assertAlmostEqual(q["total_discount"], 1 - 0.9 * 0.9)

    def test_empty_job_is_zero_not_error(self):
        s = Settings(monthly_overhead=0)
        q = quote(Job(), s)
        self.assertEqual(q["price"], 0)
        self.assertEqual(q["net_margin"], 0)

    def test_invalid_inputs(self):
        with self.assertRaises(PricingError):
            quote(Job(sqft=-10), Settings())
        with self.assertRaises(PricingError):
            quote(Job(sqft=100, crew=0), Settings())
        with self.assertRaises(PricingError):
            quote(Job(sqft=100, margin_override=0.98), Settings())

    def test_gross_vs_contribution_vs_net(self):
        q = quote(Job(sqft=1800, bedrooms=3, bathrooms=2, supplies=15, miles=20), Settings())
        self.assertGreater(q["gross_margin"], q["contribution_margin"])
        self.assertGreater(q["contribution_margin"], q["net_margin"])

    def test_check_price(self):
        j = Job(sqft=2000, bedrooms=3, bathrooms=2)
        q = quote(j, Settings())
        low = check_price(j, Settings(), q["total_cost"] * 0.9)
        self.assertTrue(low["loses_money"])
        ok = check_price(j, Settings(), q["price"])
        self.assertFalse(ok["loses_money"])
        self.assertAlmostEqual(ok["net_profit"], q["net_profit"])


class TestPlanners(unittest.TestCase):
    def test_break_even(self):
        r = break_even(1200, 4000, 180, 0.55)
        self.assertAlmostEqual(r["contribution_per_job"], 81)
        self.assertAlmostEqual(r["break_even_jobs"], 1200 / 81)
        self.assertEqual(r["goal_jobs_rounded"], 65)
        with self.assertRaises(PricingError):
            break_even(1, 1, 100, 1.0)

    def test_commercial(self):
        r = commercial_bid(5000, 2500, 3, 18, 0.12, 8, 150, 0.30, 0.029)
        self.assertAlmostEqual(r["hours_per_visit"], 2)
        self.assertAlmostEqual(r["visits_per_month"], 13)
        net = r["monthly_price"] * (1 - 0.029) - r["cost_month"]
        self.assertAlmostEqual(net / r["monthly_price"], 0.30)

    def test_crew(self):
        r = crew_cost(18, 0.12, 35, 0.75, 0.30)
        self.assertAlmostEqual(r["cost_per_billable_hour"], 18 * 1.12 / 0.75)
        with self.assertRaises(PricingError):
            crew_cost(18, 0.1, 35, 0, 0.3)


if __name__ == "__main__":
    unittest.main()
