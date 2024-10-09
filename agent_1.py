#!/usr/bin/env python3

import redis
import os
from openai import OpenAI
import logging
import time

# Configure logging with rotating logs
from logging.handlers import RotatingFileHandler

# Create a RotatingFileHandler
log_file = 'agent_1.log'
max_log_size = 1 * 1024 * 1024  # 1 MB
backup_count = 5  # Number of backup files to keep

file_handler = RotatingFileHandler(
    log_file, maxBytes=max_log_size, backupCount=backup_count
)

# Set the logging format
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)

# Configure the root logger
logging.getLogger('').setLevel(logging.DEBUG)
logging.getLogger('').addHandler(file_handler)

# Get logger for Agent1
logger = logging.getLogger('Agent1')

# Add debug logging throughout the script
logger.debug("Agent 1 script started")


system_role_description = """
You are an expert forecaster trained to predict future events using evidence-based reasoning, statistical analysis, and deep understanding of various domains. Your role is to generate accurate and probabilistic forecasts by leveraging your unique knowledge, background, and available data.

Your forecasts should be guided by:
- Background Expertise: Use your domain knowledge to assess the context of each event, integrating historical trends and current developments.
- Evidence-Based Reasoning: Rely on available evidence, reports, and verified data sources to support your forecasts, considering both known information and uncertainties.
- Exact Probabilistic Thinking: Rather than providing a probability range, you must assign a precise percentage (0% to 100%) to represent the likelihood of each possible outcome. This percentage should reflect your confidence in the forecast based on the available evidence and your understanding of the situation.
- Collaborative Insights: When multiple perspectives or data points are available, synthesize the information to present the most reliable and balanced forecast.
- Continuous Updates: Adjust your predictions as new evidence emerges, maintaining a dynamic view of evolving situations. Update your percentage-based forecasts as new data is collected or the situation changes.
- The last sentence of your response should be "\n\nThe likelihood of this event happening is X%" where X is the percentage you have assigned.\n\n

Your unique background and reasoning must shine through in your forecasts, providing a nuanced perspective on events. Precision in your forecasts is key—each prediction must be backed by detailed reasoning, and the assigned probability should reflect both your analysis of the available data and your expertise.
"""

# Check if the OPENAI_API_KEY environment variable exists
try:
    openai_api_key = os.environ["OPENAI_API_KEY"]
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is empty")
    logger.debug("OPENAI_API_KEY environment variable found")
except KeyError:
    logger.error("OPENAI_API_KEY environment variable not set")
    raise
except ValueError as ve:
    logger.error(str(ve))
    raise


try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    logger.debug("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    raise

# Agent 1 specific vectorized database (keys stored in Redis)
agent_id = "agent_1"  # Each agent has its unique identifier

# Setup Redis client
try:
    r = redis.Redis()
    logger.debug("Redis client setup successful")
except redis.RedisError as e:
    logger.error(f"Failed to setup Redis client: {str(e)}")
    raise

# Subscribe to event channels for multiple rounds
try:
    pubsub = r.pubsub()
    logger.debug("Successfully created Redis pubsub object")
except redis.RedisError as e:
    logger.error(f"Failed to create Redis pubsub object: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error while creating Redis pubsub object: {str(e)}")
    raise

logger.debug("Preparing to subscribe to event channels")

# Wrap the main logic in a try-except block for error logging
try:

    logger.debug(f"OpenAI API key: {client.api_key[:5]}...")  # Log first 5 chars of API key
    logger.debug("Redis client setup complete")
    logger.debug(f"Agent ID: {agent_id}")

    for round_num in range(3):
        logger.debug(f"Starting round {round_num}")
        event_channel = f"forecast_event_{round_num}"
        logger.debug(f"Subscribing to channel: {event_channel}")
        pubsub.subscribe(event_channel)

        for message in pubsub.listen():
            if message['type'] == 'message':
                
                received_message = message['data'].decode('utf-8')
                logger.debug(f"Received message: {received_message}")

                if "Forecast" in message['data'].decode('utf-8'):

                    # Ensure consistent data type and decode if necessary
                    data = message['data'].decode('utf-8') if isinstance(message['data'], bytes) else message['data']
                    
                    # Extract event using a more robust method
                    try:
                        event = data.split("Moderator: Forecast the likelihood of:", 1)[-1].strip("'")
                        logger.debug(f"Extracted event: {event}")
                    except IndexError:
                        logger.error(f"Failed to extract event from message: {data}")
                        event = None
                    
                    if event is None:
                        logger.warning("Skipping this message due to invalid format")
                        continue

                    # Ensure the event is encoded before fetching from Redis
                    vectorized_key = f"vectorized_info:{agent_id}:{event}"
                    logger.debug(f"Fetching data with key: {vectorized_key}")

                    related_info = r.get(vectorized_key)

                    if related_info:
                        related_info = related_info.decode('utf-8')
                        logger.debug(f"Retrieved related info: {related_info[:50]}...")  # Log first 50 chars
                    else:
                        related_info = "No specific info available."
                        logger.debug("No related info found")

                    logger.debug("Generating forecast using OpenAI")
                    prompt = f"Based on the event: {event}, and the following related information: {related_info}, provide the percentage likelihood that this event will be true."

                    # Use the new OpenAI Python SDK to generate a completion
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_role_description},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=250
                    )

                    forecast = response.choices[0].message.content.strip()
                    logger.debug(f"Generated forecast: {forecast}")

                    results_channel = f"forecast_results_{round_num}"
                    logger.debug(f"Publishing results to channel: {results_channel}")
                    r.publish(results_channel, f"Agent 1: {forecast}")


                logger.debug(f"Unsubscribing from channel: {event_channel}")
                pubsub.unsubscribe(event_channel)
                logger.debug("Simulating delay between rounds")
                time.sleep(2)
                break

    logger.debug("Agent 1 script completed successfully")
except Exception as e:
    pubsub.unsubscribe()
    logger.error(f"An error occurred: {str(e)}", exc_info=True)
