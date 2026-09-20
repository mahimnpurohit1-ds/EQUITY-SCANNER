
# config.py

UPSTOX_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI0RENXRVQiLCJqdGkiOiI2YWFmYzM0YjFjODUwOTIyYmFiZjQ3ZWQiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6dHJ1ZSwiaXNFeHRlbmRlZCI6dHJ1ZSwiaWF0IjoxNzg5OTAzNjkxLCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE4MjE0Nzc2MDB9.FA2ICpqQgaGnI6i9qjqpNew71MNKl1G_-iUE72oIuLQ"

# Trading Strategy Parameters
CAPITAL = 10000            # Account Capital in INR
TARGET_PCT = 0.016         # 1.6% profit target
STOP_LOSS_PCT = 0.008      # 0.8% stop loss (1:2 Risk-Reward)
MAX_RISK_PER_TRADE = 100   # Maximum risk cap per trade in INR
MIN_VOLUME_THRESHOLD = 50000  # Minimum required volume for liquidity