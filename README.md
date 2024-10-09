# multi-agent-forecasting-basic

#### Example Output
<img width="500" alt="Moderator Listener - Output Window" src="https://github.com/user-attachments/assets/dc05b413-f955-4e4d-832c-e93af4b25ac7">

### Step 1: Install/Configure Dependencies 

```bash
# Install redis
# use brew for macOS
brew install redis
```

```bash
# Install necessary Python packages
pip install redis openai
```

```bash
# Add your OpenAI key to your shell configuration file on your system e.g. here is an example for macOS/Linux for Bash or Zsh
export OPENAI_API_KEY=""
```

### Step 2: Start Redis Server 
Make sure Redis is installed and running locally:

```bash
# Start Redis server
redis-server
```

### Step 3: Run the Code

Now that you have created all the necessary Python scripts, here's the order to run them:

1. **Update the vectorized database**:
   This script populates Redis with the vectorized data specific to each agent.

   ```bash
   python update_vector_db.py
   ```

2. **Run the agents**:
   Each agent should run in its own terminal window or tab.

   Open two new terminal windows and run each agent separately.

   ```bash
   # In one terminal window for agent_1
   python3 agent_1.py

   # In a separate terminal window for agent_2
   python3 agent_2.py
   ```

3. **Run the moderator**:
   After the agents are ready to listen for events, start the moderator script.

   ```bash
   python3 moderator.py
   ```

4. **Run the moderator listener**:
   This listens to the results of the forecasts in real-time. You can also run this in another terminal window.

   ```bash
   python3 moderator_listener.py
   ```

### Step 4: Observe the Process

1. The **moderator** publishes an event that requires a forecast.
2. Each **agent** subscribes to the event, retrieves its respective vectorized data from Redis, generates a forecast using OpenAI, and publishes its result.
3. The **moderator listener** script listens for the forecast results from each agent and displays them.

   
