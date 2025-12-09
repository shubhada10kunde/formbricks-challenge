# Formbricks Hiring Challenge Solution

A Python CLI tool that uses **real Formbricks APIs** and **Ollama (free LLM)** to generate and seed realistic survey data.

## 🎯 Challenge Requirements Met

- ✅ **Real Formbricks Management API** for creating surveys/users
- ✅ **Real Formbricks Client API** for submitting responses
- ✅ **Real LLM API** (Ollama - free and local) for data generation
- ✅ **NO database access** - pure API approach only
- ✅ **Docker Compose** for local Formbricks instance
- ✅ **5 unique surveys** with realistic questions
- ✅ **At least 1 response per survey** (total 5+ responses)
- ✅ **10 unique users** with Manager/Owner permissions

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.8+
- Ollama (free, local LLM)

### Installation

1. **Clone and setup:**

```bash
git clone <repository-url>
cd formbricks-challenge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```
