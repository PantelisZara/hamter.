#!/usr/bin/env python3
"""Manual Instagram followers/following comparison utility."""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

try:
    from selenium import webdriver
    from selenium.common.exceptions import (
        InvalidSessionIdException,
        NoSuchWindowException,
        SessionNotCreatedException,
        TimeoutException,
        WebDriverException,
    )
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement
    from selenium.webdriver.support.ui import WebDriverWait
except ModuleNotFoundError:
    webdriver = None

    class WebDriverException(Exception):
        pass

    class InvalidSessionIdException(WebDriverException):
        pass

    class NoSuchWindowException(WebDriverException):
        pass

    class SessionNotCreatedException(WebDriverException):
        pass

    class TimeoutException(WebDriverException):
        pass

    class Options:  # type: ignore[no-redef]
        pass

    class WebDriver:  # type: ignore[no-redef]
        pass

    class WebElement:  # type: ignore[no-redef]
        pass

    class WebDriverWait:  # type: ignore[no-redef]
        pass


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FOLLOWERS_FILE = DATA_DIR / "followers.txt"
FOLLOWING_FILE = DATA_DIR / "following.txt"
COMPARISON_FILE = DATA_DIR / "instagram_comparison.txt"
PROFILE_DIR = Path.home() / ".local" / "share" / "instagram-list-scraper"

INSTAGRAM_HOSTS = {"instagram.com", "www.instagram.com"}
IGNORED_PROFILE_PATHS = {
    "accounts",
    "about",
    "api",
    "blog",
    "business",
    "challenge",
    "developer",
    "direct",
    "directory",
    "emails",
    "explore",
    "help",
    "legal",
    "oauth",
    "p",
    "privacy",
    "reel",
    "reels",
    "settings",
    "stories",
    "terms",
    "web",
}


class ScrapeError(RuntimeError):
    """Raised when a list cannot be scraped confidently."""


def extract_username_from_href(href: str | None) -> str | None:
    """Return a normalized Instagram username from a profile href."""
    if not href:
        return None

    href = href.strip()
    parsed = urlparse(href)

    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None

    if parsed.netloc:
        host = parsed.netloc.lower()
        if host not in INSTAGRAM_HOSTS:
            return None

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 1:
        return None

    username = parts[0].strip().lower()
    if username in IGNORED_PROFILE_PATHS:
        return None
    if not 1 <= len(username) <= 30:
        return None
    if not all(char.isalnum() or char in {"_", "."} for char in username):
        return None
    if username in {".", ".."} or set(username) == {"."}:
        return None

    return username


def write_usernames(path: Path, usernames: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sorted_usernames = sorted(usernames)
    text = "\n".join(sorted_usernames)
    if text:
        text += "\n"
    path.write_text(text, encoding="utf-8")


def read_usernames(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line.strip().lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def build_comparison_report(followers: set[str], following: set[str]) -> str:
    mutuals = followers & following
    fans = followers - following
    not_following_back = following - followers

    lines = [
        "# INSTAGRAM FOLLOWER COMPARISON",
        "",
        f"Followers: {len(followers)}",
        f"Following: {len(following)}",
        f"Mutuals: {len(mutuals)}",
        f"They follow you, you don't follow them: {len(fans)}",
        f"You follow them, they don't follow you: {len(not_following_back)}",
        "",
        "## THEY FOLLOW YOU / YOU DON'T FOLLOW THEM",
        "",
        *sorted(fans),
        "",
        "## YOU FOLLOW THEM / THEY DON'T FOLLOW YOU",
        "",
        *sorted(not_following_back),
        "",
        "## MUTUAL FOLLOWERS",
        "",
        *sorted(mutuals),
        "",
    ]
    return "\n".join(lines)


def write_comparison_report(
    followers: set[str],
    following: set[str],
    path: Path = COMPARISON_FILE,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_comparison_report(followers, following), encoding="utf-8")


def find_chromium_binary() -> str | None:
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        binary = shutil.which(name)
        if binary:
            return binary
    return None


def create_driver() -> WebDriver:
    if webdriver is None:
        raise RuntimeError(
            "Selenium is not installed. Run: python -m pip install -r requirements.txt"
        )

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    chromium_binary = find_chromium_binary()
    if chromium_binary:
        options.binary_location = chromium_binary

    try:
        return webdriver.Chrome(options=options)
    except SessionNotCreatedException as exc:
        message = str(exc)
        if "user data directory is already in use" in message.lower():
            raise RuntimeError(
                "Chromium profile is already in use. Close other scraper Chromium "
                "windows and run the command again."
            ) from exc
        raise RuntimeError(f"Could not start Chromium through Selenium: {exc}") from exc
    except WebDriverException as exc:
        raise RuntimeError(f"Could not start Chromium through Selenium: {exc}") from exc


def find_visible_dialog(driver: WebDriver, timeout: int = 30) -> WebElement:
    script = """
        const candidates = [...document.querySelectorAll('[role="dialog"], [aria-modal="true"]')];
        const visible = candidates
            .filter((el) => {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                return rect.width > 0 && rect.height > 0 &&
                    style.visibility !== 'hidden' && style.display !== 'none';
            })
            .sort((a, b) => {
                const ar = a.getBoundingClientRect();
                const br = b.getBoundingClientRect();
                return (br.width * br.height) - (ar.width * ar.height);
            });
        return visible[0] || null;
    """

    try:
        return WebDriverWait(driver, timeout).until(
            lambda current_driver: current_driver.execute_script(script)
        )
    except TimeoutException as exc:
        raise ScrapeError(
            "Instagram dialog not found. Open the Followers or Following dialog, "
            "then press ENTER."
        ) from exc


def find_scroll_container(driver: WebDriver, dialog: WebElement) -> WebElement:
    script = """
        const root = arguments[0];
        const nodes = [root, ...root.querySelectorAll('*')];
        const scrollables = nodes
            .filter((el) => {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                return rect.width > 0 && rect.height > 0 &&
                    el.scrollHeight > el.clientHeight + 8 &&
                    ['auto', 'scroll'].includes(style.overflowY);
            })
            .sort((a, b) => b.scrollHeight - a.scrollHeight);
        return scrollables[0] || root;
    """
    return driver.execute_script(script, dialog)


def collect_visible_usernames(driver: WebDriver, dialog: WebElement) -> set[str]:
    hrefs = driver.execute_script(
        "return [...arguments[0].querySelectorAll('a[href]')].map((a) => a.href);",
        dialog,
    )
    return {
        username
        for username in (extract_username_from_href(href) for href in hrefs)
        if username
    }


def get_scroll_state(driver: WebDriver, container: WebElement) -> tuple[int, int, int]:
    state = driver.execute_script(
        """
        return [
            Math.ceil(arguments[0].scrollTop),
            Math.ceil(arguments[0].scrollHeight),
            Math.ceil(arguments[0].clientHeight)
        ];
        """,
        container,
    )
    return int(state[0]), int(state[1]), int(state[2])


def scroll_dialog(driver: WebDriver, container: WebElement) -> None:
    driver.execute_script(
        """
        const step = Math.max(250, Math.floor(arguments[0].clientHeight * 0.85));
        arguments[0].scrollTop = arguments[0].scrollTop + step;
        """,
        container,
    )


def scrape_user_list(
    driver: WebDriver,
    label: str,
    *,
    scroll_delay: float = 0.8,
    max_idle_rounds: int = 5,
    timeout: int = 30,
) -> set[str]:
    dialog = find_visible_dialog(driver, timeout=timeout)
    container = find_scroll_container(driver, dialog)
    usernames: set[str] = set()
    idle_rounds = 0
    last_scroll_top = -1

    while True:
        try:
            dialog = find_visible_dialog(driver, timeout=3)
            visible_usernames = collect_visible_usernames(driver, dialog)
            before = len(usernames)
            usernames.update(visible_usernames)
            if len(usernames) > before:
                idle_rounds = 0
                print(f"Collected: {len(usernames)}")
            else:
                idle_rounds += 1

            container = find_scroll_container(driver, dialog)
            scroll_top, scroll_height, client_height = get_scroll_state(driver, container)
            at_bottom = scroll_top + client_height >= scroll_height - 3

            if at_bottom and idle_rounds >= max_idle_rounds:
                break
            if scroll_top == last_scroll_top and idle_rounds >= max_idle_rounds:
                break

            last_scroll_top = scroll_top
            scroll_dialog(driver, container)
            time.sleep(scroll_delay)
        except (InvalidSessionIdException, NoSuchWindowException) as exc:
            raise ScrapeError("Browser was closed unexpectedly.") from exc
        except TimeoutException as exc:
            raise ScrapeError(f"{label} dialog closed unexpectedly.") from exc
        except WebDriverException as exc:
            raise ScrapeError(f"Could not continue scraping {label}: {exc}") from exc

    if not usernames:
        raise ScrapeError(
            f"No usernames were detected in {label}. Make sure the correct dialog is open."
        )

    return usernames


def run_scraper() -> int:
    print("# Instagram scraper\n")
    driver: WebDriver | None = None

    try:
        driver = create_driver()
        driver.get("https://www.instagram.com/")
        print("Chromium opened.\n")
        print("1. Log in to Instagram if necessary.")
        print("2. Open your profile.")
        print("3. Open Followers.\n")

        input("Press ENTER when Followers is open: ")
        print("\nScraping Followers...")
        followers = scrape_user_list(driver, "Followers")
        write_usernames(FOLLOWERS_FILE, followers)
        print(f"\nFinished. Found {len(followers)} followers.")
        print(f"Saved: {FOLLOWERS_FILE}\n")

        print("Close Followers and open Following.\n")
        input("Press ENTER when Following is open: ")
        print("\nScraping Following...")
        following = scrape_user_list(driver, "Following")
        write_usernames(FOLLOWING_FILE, following)
        print(f"\nFinished. Found {len(following)} following.")
        print(f"Saved: {FOLLOWING_FILE}\n")

        write_comparison_report(followers, following)
        print("Comparison complete.")
        print(f"Saved: {COMPARISON_FILE}")
        return 0
    except KeyboardInterrupt:
        print("\nStopped by user.")
        return 130
    except (RuntimeError, ScrapeError) as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1
    finally:
        if driver is not None:
            try:
                driver.quit()
            except WebDriverException:
                pass


def run_self_tests() -> int:
    import tempfile

    valid_cases = {
        "https://www.instagram.com/example_user/": "example_user",
        "https://instagram.com/Example.User/?hl=en": "example.user",
        "/Mixed_Case.Name/": "mixed_case.name",
    }
    invalid_cases = [
        "https://www.instagram.com/accounts/login/",
        "https://www.instagram.com/explore/",
        "https://www.instagram.com/p/abc123/",
        "https://example.com/not_instagram/",
        "mailto:test@example.com",
        "https://www.instagram.com/too/many/parts/",
    ]

    for href, expected in valid_cases.items():
        actual = extract_username_from_href(href)
        assert actual == expected, f"{href} -> {actual!r}, expected {expected!r}"
    for href in invalid_cases:
        actual = extract_username_from_href(href)
        assert actual is None, f"{href} should be ignored, got {actual!r}"

    followers = {"alpha", "beta", "gamma"}
    following = {"beta", "delta", "gamma"}
    report = build_comparison_report(followers, following)
    assert "Followers: 3" in report
    assert "Following: 3" in report
    assert "Mutuals: 2" in report
    assert "They follow you, you don't follow them: 1" in report
    assert "You follow them, they don't follow you: 1" in report

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        followers_path = temp_dir / "followers.txt"
        following_path = temp_dir / "following.txt"
        comparison_path = temp_dir / "instagram_comparison.txt"

        write_usernames(followers_path, {"beta", "alpha"})
        write_usernames(following_path, {"delta", "beta"})
        assert followers_path.read_text(encoding="utf-8") == "alpha\nbeta\n"
        assert read_usernames(followers_path) == {"alpha", "beta"}
        write_comparison_report({"alpha", "beta"}, {"beta", "delta"}, comparison_path)
        generated = comparison_path.read_text(encoding="utf-8")
        assert "alpha" in generated
        assert "delta" in generated
        assert "beta" in generated

    print("Self-tests passed.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manually scrape and compare Instagram Followers and Following lists."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run offline extraction, comparison, and file generation tests",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_tests()
    return run_scraper()


if __name__ == "__main__":
    raise SystemExit(main())
