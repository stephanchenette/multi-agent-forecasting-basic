### moderator.py
# Submit an event for agents to forecast

import redis
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='moderator.log',
    filemode='a'
)
logger = logging.getLogger('Moderator')
# Add debug logging throughout the script
logger.debug("moderator script started")

# Setup Redis client
try:
    r = redis.Redis()
    logger.debug("Redis client setup successful")
except redis.RedisError as e:
    logger.error(f"Failed to setup Redis client: {str(e)}")
    raise

# List of events that require forecasting
events = [
    "Will global temperatures rise by 2 degrees Celsius by 2030?",
    "Will AI replace 30% of jobs by 2040?",
    "Will electric vehicles make up 80% of car sales by 2035?",
    "Will quantum computing break modern encryption by 2040?",
    "Will renewable energy account for 50% of global energy by 2030?"
]

logger.debug(f"Loaded {len(events)} events for forecasting")

logger.debug("Starting forecasting rounds")
for round_num in range(3):
    try:
        logger.info(f"Starting round {round_num}")
        event = random.choice(events)
        logger.debug(f"Selected event: {event}")
        event_channel = f"forecast_event_{round_num}"
        logger.debug(f"Publishing to channel: {event_channel}")
        message = f"Moderator: Forecast the likelihood of:'{event}'"
        r.publish(event_channel, message)
        logger.info(f"Published message: {message}")
    except redis.RedisError as e:
        logger.error(f"Failed to publish message in round {round_num}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in round {round_num}: {str(e)}")
        raise
