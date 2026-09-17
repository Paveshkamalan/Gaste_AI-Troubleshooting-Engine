import re

def scrub_urls(text: str) -> str:
    """Removes http/https URLs but preserves bixby:// links."""
    # Pattern to match http/https urls
    url_pattern = re.compile(r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_pattern.sub('', text).strip()

def format_goal(topic: str, is_troubleshooting: bool = True) -> str:
    action = "Troubleshooting" if is_troubleshooting else "Configuration"
    return f"Follow these steps to perform this {topic} {action}"

def format_title(title: str) -> str:
    """Ensure title is 2 to 3 words and sentence case."""
    words = title.split()
    if len(words) < 2:
        words.append("issue")
    elif len(words) > 3:
        words = words[:3]
    return " ".join(words).capitalize()

def format_description(description: str) -> str:
    """Ensure description starts with 'It will' and is 5 to 7 words."""
    prefix = "It will "
    desc_clean = description
    if desc_clean.lower().startswith("it will "):
        desc_clean = desc_clean[8:]
    
    words = desc_clean.split()
    # Need exactly 5 to 7 words total. "It will" is 2 words. So we need 3 to 5 more words.
    if len(words) < 3:
        words.extend(["check", "the", "settings"][:3 - len(words)])
    elif len(words) > 5:
        words = words[:5]
        
    return prefix + " ".join(words)
