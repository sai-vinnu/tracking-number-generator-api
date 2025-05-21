import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import redis
import datetime
import re
from dateutil import parser

redis_url = os.getenv('REDIS_URL')
redis_client = redis.from_url(redis_url)

TRACKING_REGEX = re.compile(r'^[A-Z0-9]{1,16}$')

def base36encode(number: int) -> str:
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
        origin = request.query_params.get('origin_country_id', '').upper()
        dest = request.query_params.get('destination_country_id', '').upper()
        weight = request.query_params.get('weight', '')
        created_at = request.query_params.get('created_at', '')
        customer_id = request.query_params.get('customer_id', '')
        customer_name = request.query_params.get('customer_name', '')
        customer_slug = request.query_params.get('customer_slug', '')

        if not all([origin, dest, weight, created_at, customer_id, customer_slug]):
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dt = parser.isoparse(created_at)
        except ValueError:
            return Response({'error': 'Invalid created_at format'}, status=status.HTTP_400_BAD_REQUEST)

        counter = redis_client.incr('tracking_number_counter')

        counter_part = base36encode(counter).rjust(6, '0')
        prefix = (origin + dest)[:4]
        tracking_number = (prefix + counter_part).upper()

        if not TRACKING_REGEX.match(tracking_number):
            return Response({'error': 'Failed to generate valid tracking number'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = {
            'tracking_number': tracking_number,
            'created_at': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
        }

        return Response(response, status=status.HTTP_200_OK)
