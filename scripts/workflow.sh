echo "Formbricks Challenge - Complete Workflow (Ollama Version)"
echo "============================================================"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Step 0: Check Ollama
echo -e "\n Step 0: Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    echo "Please install Ollama from: https://ollama.com/"
    echo "Then run: ollama serve"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo " Ollama not running. Starting..."
    ollama serve &
    sleep 5
fi

# Check if model exists
if ! ollama list | grep -q "llama2"; then
    echo "Llama2 model not found. Pulling..."
    ollama pull llama2
fi

# Step 1: Start Formbricks
echo -e "\n Step 1: Starting Formbricks..."
python main.py formbricks up

echo -e "\n Waiting for Formbricks to start..."
sleep 10

echo -e "\nFormbricks should be running at: http://localhost:3000"
echo "   Setup your admin account on first visit."

read -p "Press Enter after you've created your Formbricks admin account..."

# Step 2: Get API Key Instructions
echo -e "\n Step 2: Get Formbricks API Key"
echo "----------------------------------"
echo "1. Make sure you're logged into Formbricks"
echo "2. Go to Settings → API Keys"
echo "3. Create a new 'Management API' key"
echo "4. Copy the key"
echo ""
read -p "Enter your Formbricks API key: " formbricks_key

if [ -n "$formbricks_key" ]; then
    export FORMBRICKS_API_KEY="$formbricks_key"
    # Update .env file
    sed -i.bak "s|FORMBRICKS_API_KEY=.*|FORMBRICKS_API_KEY=$formbricks_key|" .env
    rm -f .env.bak 2>/dev/null
    echo "API key saved to .env"
else
    echo " No API key entered. Make sure to set FORMBRICKS_API_KEY in .env or use --api-key flag"
fi

# Step 3: Generate data with Ollama
echo -e "\n Step 3: Generating data with Ollama (FREE!)..."
echo "--------------------------------------------------"
python main.py formbricks generate --provider ollama

# Step 4: Seed data
echo -e "\n Step 4: Seeding data via APIs..."
echo "-----------------------------------"

if [ -n "$FORMBRICKS_API_KEY" ]; then
    python main.py formbricks seed --api-key "$FORMBRICKS_API_KEY"
elif [ -f .env ] && grep -q "FORMBRICKS_API_KEY=" .env; then
    # Read from .env
    api_key=$(grep "FORMBRICKS_API_KEY=" .env | cut -d'=' -f2)
    python main.py formbricks seed --api-key "$api_key"
else
    echo " No API key found. Run seed command manually:"
    echo "   python main.py formbricks seed --api-key YOUR_KEY"
fi

echo -e "\n Workflow complete!"
echo "Access Formbricks at: http://localhost:3000"
echo "Check the seeded data in the web interface!"