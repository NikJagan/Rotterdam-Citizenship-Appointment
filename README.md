## Rotterdam Citizenship Appointment Scraper

A Playwright-based Python script that checks appointment availability for Rotterdam naturalisation and notifies a Supabase Edge Function when a slot appears.

### Prerequisites
- **Python**: 3.9+
- **Browsers**: Playwright can install Chromium automatically

### Setup
- Install dependencies directly:
```bash
pip install playwright requests python-dotenv
python -m playwright install chromium
```

### Environment
Create a `.env` file in the project root:
```bash
SUPABASE_FUNCTION_URL=YOUR_SUPABASE_EDGE_FUNCTION_URL
```
- The script reads `SUPABASE_FUNCTION_URL` and POSTs when availability is detected.
- Do not commit `.env`.

### Usage
Run the scraper:
```bash
python scraper.py
```
- **Unavailable**: waits 5 minutes then retries.
- **Available**: sends POST to the Supabase function and sleeps 6 hours.

### Notes
- **Target page**: [Start naturalisatie aanvragen](https://www.rotterdam.nl/nederlandse-nationaliteit-aanvragen/start-naturalisatie-aanvragen)
- You can adjust headless mode or timing in `scraper.py` if needed.

### Troubleshooting
- Ensure `python-dotenv` is installed or export the variable in your shell if `.env` isn’t loaded.
- If Playwright cannot find browsers, run:
```bash
python -m playwright install chromium
```

### License
See `LICENSE` for details.
