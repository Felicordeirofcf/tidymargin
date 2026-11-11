# Input data for the agents (owner exports — never invented)

Put real exports here. Example files with fake data live in `tests/fixtures/` only.

| File | Where it comes from | Columns |
|---|---|---|
| `sales.csv` | Payhip > Sales/Orders > export (rename columns to match) | date, order_id, product, status (paid/pending/refunded/chargeback), gross_usd, fees_usd, source, country |
| `traffic.csv` | Cloudflare Web Analytics (weekly, copied by hand) | date, source, visits, buy_clicks |
| `support_inbox.csv` | Copy of support emails (optional) | date, from, subject, message |
| `finance.json` | Owner/accountant | refund_reserve_pct, tax_reserve_pct, already_withdrawn_or_spent_usd |
| `competitors.csv` | Watchlist | name, url, last_price_seen |

`sales.csv`, `traffic.csv` and `support_inbox.csv` contain customer data: they are git-ignored. Do not commit them.
