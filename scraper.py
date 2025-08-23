from playwright.sync_api import sync_playwright
import time
import os
import requests

# Load environment variables from a .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def open_browser_and_navigate():
    """
    Opens a browser and navigates to the Rotterdam citizenship page.
    Returns playwright, browser, context, and page objects.
    """
    # Start Playwright
    playwright = sync_playwright().start()
    
    # Launch Chromium browser (non-headless for visual verification)
    browser = playwright.chromium.launch(headless=False)
    
    # Create a new browser context and page
    context = browser.new_context()
    page = context.new_page()
    
    # Navigate directly to the naturalization application page
    page.goto("https://www.rotterdam.nl/nederlandse-nationaliteit-aanvragen/start-naturalisatie-aanvragen")
    
    return playwright, browser, context, page


def check_centrum_once() -> str:
    """
    Performs a single availability check for the 'Centrum' location.
    Returns "unavailable" if the unavailable message is shown or on error,
    otherwise returns "available".
    """
    playwright, browser, context, page = open_browser_and_navigate()
    try:
        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Click the "Afspraak maken" link
        try:
            print("🔍 Looking for 'Afspraak maken' link...")

            # Wait for a new page/tab to open when clicking the link
            with context.expect_page() as new_page_info:
                # Try multiple selectors to find the appointment link
                afspraak_link = page.locator('a.styles_button__BEjUn').first
                if afspraak_link.is_visible():
                    afspraak_link.click()
                    print("✅ Successfully clicked 'Afspraak maken' link!")
                else:
                    # Fallback to text-based selection
                    page.click("text=Afspraak maken")
                    print("✅ Successfully clicked 'Afspraak maken' via text!")

            # Get the new page that opened
            new_page = new_page_info.value
            print("🔄 New tab opened, switching to it...")

            # Wait for the new page to load
            new_page.wait_for_load_state("networkidle")

            # Switch to the new page (tab)
            page = new_page
            print("✅ Successfully switched to new tab!")

        except Exception as e:
            print(f"⚠️  Could not find or click 'Afspraak maken' link, or new tab didn't open: {e}")
            # If no new tab opened, continue with the current page
            page.wait_for_load_state("networkidle")

        # Click the "Verder" button on the new page
        try:
            print("🔍 Looking for 'Verder' button...")

            # Wait a bit for the page to fully render
            page.wait_for_timeout(2000)

            # Try to find and click the "Verder" button
            verder_button = page.locator("text=Verder").first
            if verder_button.is_visible():
                verder_button.click()
                print("✅ Successfully clicked 'Verder' button!")
            else:
                # Try alternative selectors for the button
                page.click("button:has-text('Verder')")
                print("✅ Successfully clicked 'Verder' button via alternative selector!")

            # Wait for any navigation after clicking
            page.wait_for_load_state("networkidle")

        except Exception as e:
            print(f"⚠️  Could not find or click 'Verder' button: {e}")

        # Click the "Centrum" option/text on the page
        try:
            print("🔍 Looking for 'Centrum' option...")

            # Allow the UI to render the options
            page.wait_for_timeout(1000)

            # Try to find and click a visible element with text 'Centrum'
            centrum_option = page.locator("text=Centrum").first
            if centrum_option.is_visible():
                centrum_option.click()
                print("✅ Successfully clicked 'Centrum'!")
            else:
                # Try alternative selectors commonly used for options/links/buttons
                clicked = False
                for selector in [
                    "label:has-text('Centrum')",
                    "button:has-text('Centrum')",
                    "a:has-text('Centrum')",
                    "[role='button']:has-text('Centrum')",
                ]:
                    locator = page.locator(selector).first
                    if locator.is_visible():
                        locator.click()
                        clicked = True
                        print("✅ Successfully clicked 'Centrum' via alternative selector!")
                        break
                if not clicked:
                    # Fallback to direct text click
                    page.click("text=Centrum")
                    print("✅ Successfully clicked 'Centrum' via text click!")

            # Wait for any navigation or async work after clicking
            page.wait_for_load_state("networkidle")

        except Exception as e:
            print(f"⚠️  Could not find or click 'Centrum': {e}")

        # After clicking Centrum, check for the unavailability message; if present, return "unavailable". Otherwise, return "available".
        try:
            error_text = (
                "Het spijt ons. Het is momenteel helaas niet mogelijk om op deze locatie een afspraak voor het gekozen onderwerp te maken."
            )

            # Small wait to allow any messages to render
            page.wait_for_timeout(1000)

            # Detect the error message (try full text, then a partial fallback)
            error_locator = page.locator(f"text={error_text}").first
            error_visible = error_locator.is_visible()
            if not error_visible:
                error_visible = page.locator("text=Het spijt ons.").first.is_visible()

            if error_visible:
                print("❌ No appointment availability shown for 'Centrum'.")
                return "unavailable"
            else:
                print("✅ Availability likely present for 'Centrum'.")
                return "available"
        except Exception as e:
            print(f"⚠️  Error while checking availability or taking screenshot: {e}")
            return "unavailable"
    finally:
        # Clean up: close browser and stop playwright every attempt
        try:
            browser.close()
        finally:
            playwright.stop()


if __name__ == "__main__":
    # Keep checking in a loop; on unavailable sleep 5 minutes; otherwise sleep 6 hours
    while True:
        status = check_centrum_once()
        if status == "unavailable":
            print("⏳ No availability. Sleeping 5 minutes before retry...")
            time.sleep(300)
        else:
            function_url = os.getenv("SUPABASE_FUNCTION_URL")
            if function_url:
                requests.post(function_url, json={
                    "html": "<p>Appointment found! Click <a href='https://www.rotterdam.nl/nederlandse-nationaliteit-aanvragen/start-naturalisatie-aanvragen '>here</a> to book.</p>"
                })
            print("😴 Availability detected. Sleeping 6 hours before next run...")
            time.sleep(6 * 60 * 60)