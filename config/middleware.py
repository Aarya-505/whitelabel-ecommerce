"""
Custom Middleware for AURA Luxury Commerce.
"""

class AuthCacheControlMiddleware:
    """
    Ensures browsers do not serve stale cached pages from bfcache
    when users log in, log out, or navigate using Back/Forward buttons.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get('Content-Type', '')
        # Apply anti-caching headers on dynamic HTML responses
        if 'text/html' in content_type:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
