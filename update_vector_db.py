### update_vector_db.py

import redis

# Setup Redis client
r = redis.Redis()

# Agent 1 specific vectorized data
agent_1_data = {
    "Will global temperatures rise by 2 degrees Celsius by 2030?": "Agent 1: Scientific reports indicate a potential temperature increase of 1.8-2.2°C.",
    "Will AI replace 30% of jobs by 2040?": "Agent 1: Automation is projected to replace up to 30% of current jobs."
}

# Agent 2 specific vectorized data
agent_2_data = {
    "Will global temperatures rise by 2 degrees Celsius by 2030?": "Agent 2: Current emission trends could cause a 2.5°C rise by 2030 without interventions.",
    "Will AI replace 30% of jobs by 2040?": "Agent 2: AI is likely to replace lower-skill jobs, but high-skill jobs may see a growth.",
    "Will electric vehicles make up 80% of car sales by 2035?": "Agent 2: Electric vehicle adoption is growing rapidly, but infrastructure and supply chain challenges may slow progress. 80% adoption is ambitious but feasible if policies and technological advancements align.",
    "Will quantum computing break modern encryption by 2040?": "Agent 2: Quantum computing has the potential to break modern encryption, but widespread commercial use is unlikely before 2040. Advances in quantum-resistant cryptography are expected to mitigate risks.",
    "Will renewable energy account for 50% of global energy by 2030?": "Agent 2: Renewable energy's share is increasing globally, but challenges in scaling storage and grid infrastructure could delay achieving 50% by 2030, especially in certain regions."
}

# Update vectorized data in Redis for Agent 1
for event, info in agent_1_data.items():
    vectorized_key = f"vectorized_info:agent_1:{event}"
    r.set(vectorized_key, info)

# Update vectorized data in Redis for Agent 2
for event, info in agent_2_data.items():
    vectorized_key = f"vectorized_info:agent_2:{event}" 
    # r.set stores the key-value pair in Redis for later retrieval
    # r.publish would send a message to a channel, which is not what we want here
    # We're updating the database, not sending real-time messages
    r.set(vectorized_key, info)
    

print("Vectorized database updated for both agents!")
