"""
@time: 2020/11/13 6:30 下午
"""

from rest_framework.throttling import AnonRateThrottle


class SMSAnonRateThrottle(AnonRateThrottle):
    THROTTLE_RATES = {"anon": "1/min"}


class LoginAnonRateThrottle(AnonRateThrottle):
    THROTTLE_RATES = {"anon": "1/s"}
