# publications/middleware.py

class ReferralMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the 'ref' parameter is in the URL
        referral_code = request.GET.get('ref')
        
        # If a code exists and the user is NOT logged in yet...
        if referral_code and not request.user.is_authenticated:
            # ...and we haven't already stored a code...
            if 'referral_code' not in request.session:
                # ...store it in the session.
                request.session['referral_code'] = referral_code

        response = self.get_response(request)
        return response