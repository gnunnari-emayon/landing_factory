import re
from collections import Counter

content = open('download_unsplash_curated.py', encoding='utf-8').read()
matches = re.findall(r'\"([a-z0-9_]+)\":\s*\"(https://[^\"]+)\"', content)

url_counts = Counter(url for key, url in matches)
duplicates = {url: count for url, count in url_counts.items() if count > 1}

print(f"Total entries: {len(matches)}")
print(f"Unique URLs: {len(url_counts)}")
print(f"Duplicate URLs count: {len(duplicates)}\n")

for key, url in matches:
    if duplicates.get(url, 0) > 1:
        print(f"DUPLICATE: {key} -> {url}")
