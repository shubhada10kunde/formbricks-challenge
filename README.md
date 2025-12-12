# Formbricks Hiring Challenge Solution

A Python CLI tool that automates the generation and population of realistic survey data into Formbricks using **real APIs** and **local LLMs**.

## 🎯 Challenge Requirements Fully Met

| Requirement                        | Status                             | Implementation                                |
| ---------------------------------- | ---------------------------------- | --------------------------------------------- |
| **Real Formbricks Management API** | Used for creating surveys & users  | Python API client with proper authentication  |
| **Real Formbricks Client API**     | Used for submitting responses      | Direct API calls with session handling        |
| **Real LLM Integration**           | Uses Ollama (free, local)          | Custom LLM generator with fallback mechanisms |
| **No Database Access**             | Pure API-only approach             | Zero direct database connections              |
| **Docker Compose Setup**           | Complete local environment         | PostgreSQL + Formbricks containers            |
| **5+ Unique Surveys**              | Generated with realistic questions | LLM-powered survey creation                   |
| **10+ Unique Users**               | With proper roles/permissions      | Manager/Owner/Admin/Viewer distribution       |
| **5+ Survey Responses**            | Realistic answer generation        | Weighted response distribution                |

## Features

- ** One-Command Setup**: Complete environment setup with Docker Compose
- ** Intelligent Data Generation**: Uses Ollama LLM for realistic survey/question creation
- ** Real API Integration**: Direct Formbricks API usage (no database shortcuts)
- ** Progress Tracking**: Rich terminal interface with progress bars and status updates
- ** Automated Seeding**: Programmatic creation of surveys, users, and responses
- ** Configurable**: Easy environment variable configuration

## Quick Start

### Prerequisites

- **Docker & Docker Compose** ([Install Docker Desktop](https://www.docker.com/products/docker-desktop/))
- **Python 3.8+** ([Download Python](https://www.python.org/downloads/))
- **Ollama** ([Install Ollama](https://ollama.com/))

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd formbricks-challenge

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Setup environment configuration
cp .env.example .env
# Edit .env file with your configuration
```
