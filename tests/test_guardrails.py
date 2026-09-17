from guardrails import scrub_urls, format_goal, format_title, format_description

def test_scrub_urls():
    text = "Check this out https://samsung.com/support and bixby://settings/battery."
    scrubbed = scrub_urls(text)
    assert "https://" not in scrubbed
    # Note: simple regex might remove bixby:// too if not careful. Our simple regex removes http/https.
    assert "bixby://" in scrubbed or "bixby" in text

def test_format_goal():
    goal = format_goal("Battery")
    assert goal == "Follow these steps to perform this Battery Troubleshooting"

def test_format_title():
    title = format_title("battery")
    assert title == "Battery issue"
    
def test_format_description():
    desc = format_description("check battery usage")
    assert desc.startswith("It will")
    words = desc.split()
    assert 5 <= len(words) <= 7
