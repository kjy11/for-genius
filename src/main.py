import datetime
import json
import os
import random
import urllib.request

import pytz
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")


def get_random_problem():
    """Fetches a random free problem url from the NeetCode 150 practice list.

    Problems flagged `free: false` by NeetCode are behind the "Get Pro Access"
    paywall, so they are filtered out. Falls back to the practice page if the
    list cannot be fetched, so a bad response never breaks the daily message.

    Example:
        problem = get_random_problem()
        print(problem) # {'title': 'Partition Labels', 'url': 'https://neetcode.io/problems/partition-labels/question'}
    """
    default = {"title": "NeetCode Practice", "url": "https://neetcode.io/practice"}

    try:
        request = urllib.request.Request(
            "https://neetcode.io/api/getProblemListFunctionHttp",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            problems = json.load(response)["data"]
    except Exception as e:
        print(f"Failed to fetch the NeetCode problem list: {e}")
        return default

    free_problems = [
        {
            "title": problem.get("name") or slug.replace("-", " ").title(),
            "url": f"https://neetcode.io/problems/{slug}",
        }
        for slug, problem in problems.items()
        if problem.get("tag") == "NeetCode150" and problem.get("free") is True
    ]

    if not free_problems:
        print("No free problems found.")
        return default

    return random.choice(free_problems)


def generate_random_fortune_cookie():
    """Generates a random fortune cookie quote.

    @deprecated

    Example:
        fortune_cookie = generate_random_fortune_cookie()
        print(fortune_cookie)
    """
    QUOTES = [
        "Laughter is timeless, imagination has no age, and dreams are forever. (Walt Disney)",
        "The flower that blooms in adversity is the most rare and beautiful of all. (Mulan)",
        "Even miracles take a little time. (Cinderella)",
        "Remember, you're the one who can fill the world with sunshine. (Snow White)",
        "Adventure is out there! (Up)",
        "Your identity is your most valuable possession. Protect it. (The Incredibles)",
        "The past can hurt. But the way I see it, you can either run from it, or learn from it. (Lion King)",
        "Life's a little bit messy. We all make mistakes. (Zootopia)",
        "Just keep swimming. (Finding Nemo)",
        "Believe you can, then you will. (Mulan)",
        "Today is a good day to try. (The Hunchback of Notre Dame)",
        "All it takes is faith and trust. (Peter Pan)",
        "To infinity and beyond! (Toy Story)",
        "Our fate lives within us. You only have to be brave enough to see it. (Brave)",
        "If you can dream it, you can do it. (Walt Disney)",
    ]
    return random.choice(QUOTES)


def build_message():
    kst = pytz.timezone("Asia/Seoul")
    today = datetime.datetime.now(kst).strftime("%m/%d")
    seed = datetime.datetime.now(kst).strftime("%Y%m%d")

    header_text = f"{today} An investment in knowledge pays the best interest. - Benjamin Franklin"
    if today == "02/21":
        header_text = f"{today} Happy Birthday, All Hail Queen Cona!"

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": header_text,
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": ":poop: ddong"},
                    "url": "https://poople.io/",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": ":capital_abcd: Wordle"},
                    "url": "https://www.nytimes.com/games/wordle",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": ":jigsaw: 꼬들꼬들라면"},
                    "url": "https://kordle.kr",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": ":earth_asia: Globle"},
                    "url": "https://globle.org/",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": ":old_key: Clues by sam"},
                    "url": "https://cluesbysam.com/",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": ":kirby_pan: NeetCode"},
                    "url": get_random_problem()["url"],
                },
            ],
        },
    ]


if __name__ == "__main__":
    client = WebClient(token=SLACK_TOKEN)

    try:
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            blocks=build_message(),
            unfurl_links=False,  # Don't show preview of the link
            text="If you see this message, please check the bot's configuration.",
        )
        print(f"chat_postMessage: response={response}")
    except SlackApiError as e:
        assert e.response["error"]
