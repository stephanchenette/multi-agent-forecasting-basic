### moderator_listener.py

import redis
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='moderator_listener.log',
    filemode='a'
)
logger = logging.getLogger('ModeratorListener')
# Add debug logging throughout the script
logger.debug("moderator_listener script started")

try:
    # Setup Redis client
    r = redis.Redis()
    logger.debug("Redis client setup successful")

    # Subscribe to all forecast results channels
    pubsub = r.pubsub()
    logger.debug("Successfully created Redis pubsub object")
except redis.RedisError as e:
    logger.error(f"Failed to setup Redis client or pubsub: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error during setup: {str(e)}")
    raise

try:
    for round_num in range(3):
        logger.debug(f"Subscribing to forecast_results_{round_num}")
        pubsub.subscribe(f"forecast_results_{round_num}")

    # Listening loop
    logger.debug("Starting listening loop")
    for message in pubsub.listen():
        if message['type'] == 'message':
            decoded_message = message['data'].decode('utf-8')
            logger.info(f"Moderator received: {decoded_message}")
            print(f"Moderator received: {decoded_message}")
except redis.RedisError as e:
    logger.error(f"Redis error occurred: {str(e)}")
except Exception as e:
    logger.error(f"Unexpected error occurred: {str(e)}", exc_info=True)
finally:
    logger.debug("Closing Redis connection")
    pubsub.close()
    r.close()
