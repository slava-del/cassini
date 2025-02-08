from urllib.parse import urlparse

def domain_name(url):
    # Ensure the URL is parsed correctly
    parsed_url = urlparse(url if "://" in url else "http://" + url)
    
    # Get the netloc (domain name with possible 'www.')
    domain = parsed_url.netloc or parsed_url.path  # Handle cases where no protocol is provided

    # Remove 'www.' if it exists
    if domain.startswith("www."):
        domain = domain[4:]

    # Extract only the main domain before the first dot
    return domain.split('.')[0]

