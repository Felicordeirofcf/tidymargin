# TidyMargin User Guide

Thank you for choosing TidyMargin. This guide gets you from download to your first profitable quote in about 15 minutes.

> Every default number in the kit (pay rate, square feet per hour, discounts) is an EXAMPLE so the formulas work out of the box. Replace them with your own numbers before you quote real clients.

## 1. What is in your download

- **TidyMargin-[Tier].xlsx** - your blank workbook. Use this one for your business.
- **TidyMargin-[Tier]-EXAMPLE.xlsx** - the same workbook filled with a fictional cleaning company, so you can see every feature working.
- **TidyMargin-User-Guide.pdf** - this guide.
- **Premium only: TidyMargin-Pricing-Playbook.pdf.**
- **README.txt** - quick links and support.

The Complete and Premium tiers contain everything in the tiers below them.

## 2. Open the kit

### Microsoft Excel (desktop)
1. Unzip the download (right-click > Extract All on Windows; double-click on Mac).
2. Open TidyMargin-[Tier].xlsx. If Excel shows "Protected View", click **Enable Editing**.
3. Save a copy with your business name, for example "Brightway TidyMargin 2027.xlsx".

Works with Excel 2019, 2021 and Microsoft 365 on Windows and Mac. Excel 2016 and older do not have the MAXIFS/MINIFS functions used by the Clients sheet; use the free Excel for the web or Google Sheets instead.

### Google Sheets (free)
1. Go to drive.google.com and click **New > File upload**. Choose TidyMargin-[Tier].xlsx.
2. Double-click the file, then **File > Save as Google Sheets**.
3. Work in the new Google Sheets version. Your data lives in your own Google account.

Google Sheets keeps all formulas, drop-downs, colors and charts. Two differences: sheet protection is not imported (be careful not to type over grey cells), and charts may look slightly different.

### Excel for the web (free)
Upload the file to OneDrive (onedrive.live.com) and open it. Everything works the same as desktop Excel.

### Phones and tablets
The kit opens in the Excel and Google Sheets apps. It is easiest to set up on a computer; after that, checking the calculator or adding a visit on a phone works fine.

## 3. The color code

- **Yellow cells** are yours. Type here.
- **Grey cells** are formulas. They calculate automatically.
- **Gold cells** are the key results.

Calculation sheets are protected without a password, so you cannot delete a formula by accident. To change something on purpose: Excel > Review > Unprotect Sheet.

## 4. Settings: do this first

Open the **Settings** sheet and fill in:

1. **Your business** - name, phone, email, city/state and website. They appear on your estimates and invoices.
2. **Cleaner pay per labor hour** - what you pay per hour worked. If you clean alone, use the hourly pay you want for yourself.
3. **Payroll burden %** - payroll taxes, workers comp and similar costs on top of wages. Ask your accountant for your number; use 0% for 1099 contractors.
4. **Sq ft cleaned per labor hour** - your crew's speed on a standard clean. Time three or four real jobs and divide square feet by total labor hours.
5. **Extra hours per bedroom / bathroom** - added on top of the square-footage time.
6. **Vehicle cost per mile** - fuel and wear.
7. **Monthly overhead** - insurance, phone, software, marketing, equipment: everything you pay even if you do no jobs.
8. **Expected jobs per month** - used to spread overhead fairly across your jobs.
9. **Card processing fee %** - from your payment app. Use 0% if clients pay cash or check.
10. **Target net profit margin** - what you want to keep from every dollar of price after ALL costs. Many owners start between 20% and 35%; pick what fits your market.
11. **Sales tax %** - only if your state taxes cleaning services. Many states do not tax residential cleaning; check with your state's revenue department.
12. **Round prices up to** and **Minimum job price**.

The tables below the settings hold your service types, property types, frequency discounts and home-condition multipliers. A multiplier of 1.75 means "takes 75% longer than a standard clean". You can rename any row or add your own in the blank rows.

## 5. Price Calculator

1. Pick the property type, service type and frequency from the drop-downs.
2. Enter square feet, bedrooms, bathrooms and crew size.
3. Optional: home condition (pets, heavy use) and a labor-hours override if you already know how long the job takes.
4. Enter supplies, round-trip miles and any other direct cost for this job.

The results on the right show:

- **Estimated labor hours** and **time on site** (hours divided by crew size).
- **Total cost of this job** - labor with burden, supplies, travel, other costs and the job's share of overhead.
- **YOUR PRICE (per visit)** - the price that covers every cost, the card fee and your target margin, rounded up and never below your minimum.
- **Regular price** - if the job gets a frequency or promo discount, quote this price and show the discount. After the discount the client pays YOUR PRICE, so you still keep your margin.
- **Gross, contribution and net margin** - see section 7.

### Check a price
Thinking of quoting a number you already have in mind? Type it in **Check a price**. The verdict tells you whether it meets your margin, is profitable but below target, or LOSES MONEY.

## 6. Quote Table

Price up to 50 jobs side by side, one row per job, using your Settings. It is useful for comparing service types, preparing price lists or reviewing your current clients' prices. Net margins below your target turn red. The Quote Table does not use the home-condition column; use the labor-hours override for unusual homes.

## 7. Margin, markup and profit

- **Markup** is profit divided by COST. **Margin** is profit divided by PRICE.
- A 30% markup on a $100 cost gives a $130 price, which is only a 23.1% margin. For a real 30% margin you need $142.86.
- **Gross margin** looks only at labor and supplies.
- **Contribution margin** subtracts all job costs, including travel and card fees.
- **Net margin** also subtracts the job's share of overhead. This is what you actually keep before income taxes.

The Margin vs Markup sheet has a converter and a quick-reference table.

## 8. Estimate (all tiers) and Invoice (Complete and Premium)

1. Enter the document number and date. "Valid until" (estimates) or "Due date" (invoices) is calculated from Settings.
2. Choose the client. In Complete and Premium their details fill in from the Clients sheet; in Starter, type them.
3. Add up to 10 line items (description, quantity, unit price). The box to the right of the page shows the latest Price Calculator result for reference; it is not printed.
4. Add a discount % and sales tax % if needed (a blank tax cell uses Settings).
5. Save as PDF: Excel > File > Save As > PDF (or File > Print > Save as PDF). Google Sheets > File > Download > PDF. The page is already set to fit one letter-size sheet.

The invoice is a document. It does not collect payments. Write how clients can pay in Settings > Payment methods.

## 9. Clients (Complete and Premium)

One row per client. Only store what you need to do the job. The grey columns update from the Schedule:

- **Last completed visit** and **Next booked visit**.
- **Days since last visit**.
- **Follow-up?** - flags Active clients with no visit booked and no service in the last X days (set X in Settings).
- **Completed visits** and **Lifetime revenue**.

To remove a client's personal data, delete their row. To export, use File > Download/Save As > CSV.

## 10. Schedule (Complete and Premium)

One row per visit: date, start time, client (drop-down from Clients), service type, price, labor hours, who is assigned, status and notes.

- Status: Scheduled > Confirmed > In Progress > Completed (or Cancelled).
- Visits in the next 7 days are shown in bold.
- **Suggested next visit** adds the client's frequency (for example, 14 days for Every 2 weeks). Copy it into a new row to book it.
- Use the filter arrows to see one day, one cleaner or one client.

The schedule does not sync with Google Calendar or Outlook.

## 11. Transactions and Monthly Summary (Complete and Premium)

Log money in and money out in **Transactions**: date, category, description, amount and payment status (Received/Paid or Pending). The category decides whether it is income or an expense and which group it belongs to (labor, supplies, transport, other variable, fixed or tax).

The **Monthly Summary** shows, for each month and the year:

- Revenue earned and revenue received.
- Expenses by group.
- Estimated profit, profit margin and profit after the tax set-aside.
- Cash in, cash out and net cash flow. Profit is not cash: a job can be profitable while the client has not paid yet.
- Completed visits, average price per visit and revenue per labor hour.
- A month-vs-previous-month comparison and results by service type.

Change the year in Settings when a new year starts, or keep one file per year.

## 12. Premium tools

- **Dashboard** - year-to-date and selected-month results, operations KPIs (active and recurring clients, follow-ups, visits booked in the next 7 days, revenue per labor hour, cancellation rate) and two charts.
- **Goal Planner** - how many jobs per month you need to break even and to reach your pay goal, plus a capacity check against your team's hours.
- **Commercial Bid** - monthly contract price for offices from square feet, production rate, visits per week, pay, supplies, overhead and margin.
- **Crew Cost** - the real cost of a cleaner per billable hour once drive time and gaps are included.
- **Checklists** - standard, deep and move-in/move-out checklists to print or attach to estimates.
- **Pricing Playbook (PDF)** - how to time jobs, set a minimum, raise prices and bid commercial work.

## 13. Troubleshooting

- **The download link expired or did not arrive.** Check spam and promotions, then use the link in your Payhip receipt email or contact us with your order email.
- **The file opens read-only.** Click Enable Editing (Excel) or save it as Google Sheets.
- **#NAME? in the Clients sheet.** Your Excel version is older than 2019. Use Excel for the web or Google Sheets.
- **I typed over a formula.** Undo (Ctrl+Z / Cmd+Z), or copy the cell from the same row of the original download.
- **A drop-down does not list my new client.** Make sure the client is on the Clients sheet in column "Client name".
- **The price looks too high or too low.** Check Settings: speed (sq ft per hour), pay rate, overhead and jobs per month drive most of the price.
- **Dates show as numbers.** Format the cell as a date (Format > Number > Date).

## 14. Good to know

- **Your data is private.** Everything you type stays in your file. We never see it.
- **License.** One business may use the kit on any number of its own devices. Please do not resell or share the files.
- **Not professional advice.** TidyMargin is a business-management tool. It does not replace an accountant, tax professional or attorney.
- **Support.** Reply to your purchase email or use the contact link on our store page. We answer within 2 business days.
