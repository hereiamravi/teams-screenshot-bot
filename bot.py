import os
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import Activity, Attachment
import asyncio
from playwright.async_api import async_playwright
import base64
from difflib import get_close_matches
from dotenv import load_dotenv

load_dotenv()
# Simple mapping
SITE_MAP = {
    "sales": "https://google.com/",
    "facebook": "https://www.facebook.com/",
}

def get_matching_url(prompt):
    match = get_close_matches(prompt.lower(), SITE_MAP.keys(), n=1, cutoff=0.4)
    return SITE_MAP[match[0]] if match else None
    



async def capture_screenshot(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url)
        if "facebook.com" in url:
            await login_facebook(page)

        await page.screenshot(path="screenshot.png")
        await browser.close()


async def login_facebook(page):
    await page.goto("https://www.facebook.com/")
    await page.fill('input[name="email"]', os.getenv("FB_USERNAME"))
    await page.fill('input[name="pass"]', os.getenv("FB_PASSWORD"))
    await page.click('button[name="login"]')
    await page.wait_for_load_state('networkidle')  # Wait until page is fully loaded

class TeamsBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        prompt = turn_context.activity.text.lower()
        url = get_matching_url(prompt)
        print("Received prompt:", prompt)
        print("Matched URL:", url)
        if url:
            await capture_screenshot(url)
            with open("screenshot.png", "rb") as img:
                base64_img = base64.b64encode(img.read()).decode()
            attachment = Attachment(
                name="screenshot.png",
                content_type="image/png",
                content=base64_img
            )
            reply = MessageFactory.attachment(attachment)
            reply_text = f"Screenshot taken for: {url}"
            reply.text = reply_text
            print("Bot Response:", reply_text)
            await turn_context.send_activity(reply_text)
            return
        else:
            await turn_context.send_activity("I couldn't match that request. Try using keywords like 'sales' or 'support'.")