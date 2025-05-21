import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import redis
import uuid
import datetime
import re
from dateutil import parser

# redis_client = redis.Redis(host='localhost', port=6379, db=0)

redis_url = os.getenv('REDIS_URL')
redis_client = redis.from_url(redis_url)

# Regex pattern to validate final tracking number
TRACKING_REGEX = re.compile(r'^[A-Z0-9]{1,16}$')

def base36encode(number):
    """Convert an integer to a base36 string."""
    if number < 0:
        raise ValueError("Must be positive integer")
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    while number > 0:
        number, i = divmod(number, 36)
        result = chars[i] + result
    return result or '0'

class NextTrackingNumberView(APIView):
    def get(self, request):
        # Validate and extract params
        origin = request.query_params.get('origin_country_id', '').upper()
        dest = request.query_params.get('destination_country_id', '').upper()
        weight = request.query_params.get('weight', '')
        created_at = request.query_params.get('created_at', '')
        customer_id = request.query_params.get('customer_id', '')
        customer_name = request.query_params.get('customer_name', '')
        customer_slug = request.query_params.get('customer_slug', '')

        # Basic param validation
        if not (origin and dest and weight and created_at and customer_id and customer_slug):
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        # Convert created_at to datetime for consistent processing
        try:
            dt = parser.isoparse(created_at)
        except ValueError:
            return Response({'error': 'Invalid created_at format'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate unique incremental ID via Redis
        counter = redis_client.incr('tracking_number_counter')

        # Compose a string base for tracking number from inputs + counter
        # For example: first letters of origin+dest, weight*1000 (to get integer), date info, counter
        base_str = f"{origin}{dest}{int(float(weight)*1000)}{dt.strftime('%y%m%d%H%M%S')}{counter}"

        # Hash or encode base_str to create alphanumeric unique tracking number
        # For simplicity, convert counter to base36 and append a hashed prefix (could improve)
        counter_part = base36encode(counter).rjust(6, '0')  # 6 chars from counter

        # Use origin and dest as prefix (4 chars)
        prefix = (origin + dest)[:4]

        # Final tracking number: prefix + counter_part (max 16 chars)
        tracking_number = (prefix + counter_part).upper()

        # Validate tracking number pattern
        if not TRACKING_REGEX.match(tracking_number):
            return Response({'error': 'Failed to generate valid tracking number'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = {
            'tracking_number': tracking_number,
            'created_at': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        }

        return Response(response, status=status.HTTP_200_OK)
