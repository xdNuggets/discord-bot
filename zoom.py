import asyncio
from urllib.parse import urlparse

from pyppeteer import launch


async def get_attr(page, selector, key):
    el = await page.querySelector(selector)
    return await page.evaluate("(el, key) => el[key]", el, key)


async def set_attr(page, selector, key, value):
    el = await page.querySelector(selector)
    await page.evaluate("(el, key, value) => el[key] = value", el, key, value)


async def set_value(page, selector, value):
    await set_attr(page, selector, "value", value)


async def wait_for_domain(page, domain):
    while urlparse(page.url).netloc != domain:
        await page.waitForNavigation()


async def generate_join_url(username, password):
    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()
    await page.goto("https://aarhusuniversity.zoom.us/signin")

    await set_value(page, "#username", username)
    await set_value(page, "#password", password)
    await page.click("input[type=submit]")

    await wait_for_domain(page, "aarhusuniversity.zoom.us")

    await page.goto("https://aarhusuniversity.zoom.us/meeting/schedule")

    await set_value(page, "#topic", "Academy")
    await set_attr(page, "#option_video_host_on", "checked", True)
    await set_attr(page, "#option_video_participant_on", "checked", True)
    await set_attr(page, "#option_mute_upon_entry", "checked", False)

    await asyncio.wait([page.click("#schedule_form .submit"), page.waitForNavigation()])

    join_url = await get_attr(
        page, "a[href^='https://aarhusuniversity.zoom.us/j/']", "href"
    )

    await browser.close()

    return join_url


if __name__ == "__main__":
    import sys

    print(asyncio.run(generate_join_url(*sys.argv[1:])))
