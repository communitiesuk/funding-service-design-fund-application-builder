from playwright.sync_api import sync_playwright


# TODO this test is generated to test the e2e frame work once tests implementing this will be removed

def test_homepage():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://google.com')
        assert page.title() == "Google"
        browser.close()
