
"""
extraction of domain from a link
"""

import tldextract

print('give a link for extraction: ')

url = input().strip()

def domain_name(url):
    extractedInfo = tldextract.extract(url)
    return extractedInfo.domain

print('extractd domain:', domain_name(url))
