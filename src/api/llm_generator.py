import json
import random
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from rich.console import Console
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import ollama

from src.models.survey import Survey, Question, QuestionType, WelcomeCard, ThankYouCard
from src.models.user import User, UserRole

console = Console()
logger = logging.getLogger(__name__)

class LLMGenerator:
    """Generate realistic data using Ollama (local LLM)"""
    
    def __init__(self, provider: str = "ollama", api_key: str = None, model: str = None):
        self.provider = provider
        self.model = model or os.getenv("OLLAMA_MODEL", "llama2")
        self.ollama_host = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        # Test Ollama connection
        self._test_ollama_connection()
    
    def _test_ollama_connection(self):
        """Test if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            import requests
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            
            if response.status_code != 200:
                raise ConnectionError(f"Ollama not running at {self.ollama_host}")
            
            # Check if model exists
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            
            # Check if our model exists (handle variations)
            model_found = False
            for model_name in model_names:
                if self.model in model_name:
                    model_found = True
                    self.model = model_name  # Use full name
                    break
            
            if not model_found:
                console.print(f"[yellow]⚠ Model '{self.model}' not found. Available models: {model_names}[/yellow]")
                console.print(f"[yellow]⚠ Using first available model: {model_names[0] if model_names else 'None'}[/yellow]")
                if model_names:
                    self.model = model_names[0]
                else:
                    raise ValueError("No Ollama models available. Pull a model first: 'ollama pull llama2'")
            
            console.print(f"[green]✓ Connected to Ollama at {self.ollama_host}[/green]")
            console.print(f"[green]✓ Using model: {self.model}[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Ollama connection failed: {e}[/red]")
            console.print("\n[bold]To setup Ollama:[/bold]")
            console.print("1. Install Ollama: https://ollama.com/")
            console.print("2. Run: ollama serve")
            console.print("3. Pull a model: ollama pull llama2")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _generate_with_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Generate content using Ollama"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            # Use ollama Python client
            response = await ollama.AsyncClient(host=self.ollama_host).chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "num_predict": 2000  # Limit tokens
                }
            )
            
            return response['message']['content']
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            
            # Fallback: Use simpler generation
            if "rate limit" in str(e).lower():
                await asyncio.sleep(5)
                raise
            
            return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate fallback response when Ollama fails"""
        # Simple template-based generation for surveys
        survey_types = {
            "customer satisfaction": "Customer Satisfaction Survey",
            "product feedback": "Product Feedback Survey", 
            "employee engagement": "Employee Engagement Survey",
            "market research": "Market Research Survey",
            "user experience": "User Experience Survey"
        }
        
        for key, value in survey_types.items():
            if key in prompt.lower():
                return json.dumps({
                    "name": value,
                    "questions": [
                        {
                            "type": "rating",
                            "headline": f"How would you rate your experience with our {key.replace('_', ' ')}?",
                            "required": True,
                            "range": 5,
                            "scale": "number"
                        },
                        {
                            "type": "multipleChoice",
                            "headline": "What aspect was most valuable?",
                            "required": False,
                            "choices": ["Quality", "Service", "Features", "Price"],
                            "shuffleOption": True
                        },
                        {
                            "type": "openText",
                            "headline": "Any additional comments or suggestions?",
                            "required": False,
                            "placeholder": "Share your thoughts..."
                        }
                    ],
                    "welcomeCard": {
                        "enabled": True,
                        "headline": f"Welcome to our {value}",
                        "html": "<p>Thank you for participating. Your feedback helps us improve.</p>"
                    },
                    "thankYouCard": {
                        "enabled": True,
                        "headline": "Thank You!",
                        "html": "<p>Your response has been recorded. We appreciate your time.</p>"
                    }
                })
        
        # Default fallback
        return json.dumps({
            "name": "Customer Feedback Survey",
            "questions": [
                {
                    "type": "rating",
                    "headline": "How satisfied are you with our service?",
                    "required": True,
                    "range": 5,
                    "scale": "number"
                }
            ],
            "welcomeCard": {
                "enabled": True,
                "headline": "Welcome!",
                "html": "<p>Thank you for your feedback.</p>"
            },
            "thankYouCard": {
                "enabled": True,
                "headline": "Thank You!",
                "html": "<p>Your response has been recorded.</p>"
            }
        })
    
    async def generate_survey_async(self, survey_type: str) -> Optional[Dict]:
        """Generate a single survey using Ollama"""
        prompt = f"""Create a realistic {survey_type} survey in JSON format that can be used with Formbricks API.

Requirements:
1. Survey name should be descriptive
2. Include 3-5 questions of different types (rating, multiple choice, open text)
3. Questions should be relevant to {survey_type}
4. Format must be valid JSON

Survey structure:
{{
    "name": "Survey name",
    "questions": [
        {{
            "type": "rating|multipleChoice|openText|dropdown|matrix",
            "headline": "Question text",
            "required": true/false,
            "choices": ["Option1", "Option2"]  # for multipleChoice/dropdown
        }}
    ],
    "welcomeCard": {{
        "enabled": true,
        "headline": "Welcome message",
        "html": "Welcome description"
    }},
    "thankYouCard": {{
        "enabled": true,
        "headline": "Thank you message",
        "html": "Thank you description"
    }}
}}

Generate the survey now. Return ONLY the JSON, no other text:"""
        
        system_prompt = "You are a survey design expert. Generate realistic, professional survey questions in valid JSON format only. Return ONLY JSON, no explanations."
        
        try:
            result = await self._generate_with_ollama(prompt, system_prompt)
            
            # Extract JSON from response (Ollama sometimes adds extra text)
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            
            if json_match:
                try:
                    survey_json = json.loads(json_match.group())
                    survey_json["type"] = survey_type.lower().replace(" ", "_")
                    
                    # Ensure required fields
                    if "name" not in survey_json:
                        survey_json["name"] = f"{survey_type} Survey"
                    if "questions" not in survey_json:
                        survey_json["questions"] = []
                    
                    return survey_json
                except json.JSONDecodeError as e:
                    console.print(f"[yellow]⚠ JSON parse error: {e}. Using fallback.[/yellow]")
            
        except Exception as e:
            logger.error(f"Failed to generate survey: {e}")
        
        # Return fallback survey
        return self._create_fallback_survey(survey_type)
    
    def _create_fallback_survey(self, survey_type: str) -> Dict:
        """Create fallback survey if Ollama fails"""
        return {
            "name": f"{survey_type} Survey",
            "type": survey_type.lower().replace(" ", "_"),
            "questions": [
                {
                    "type": "rating",
                    "headline": f"How would you rate your overall experience with our {survey_type.lower()}?",
                    "required": True,
                    "range": 5,
                    "scale": "number"
                },
                {
                    "type": "multipleChoice",
                    "headline": "What was the most valuable aspect?",
                    "required": False,
                    "choices": ["Quality", "Support", "Features", "Price"],
                    "shuffleOption": True
                },
                {
                    "type": "openText",
                    "headline": "Any additional comments or suggestions?",
                    "required": False,
                    "placeholder": "Share your thoughts..."
                }
            ],
            "welcomeCard": {
                "enabled": True,
                "headline": f"Welcome to our {survey_type} Survey",
                "html": "<p>Thank you for participating. Your feedback helps us improve.</p>"
            },
            "thankYouCard": {
                "enabled": True,
                "headline": "Thank You!",
                "html": "<p>Your response has been recorded. We appreciate your time.</p>"
            }
        }
    
    async def generate_surveys(self, num_surveys: int = 5) -> List[Dict]:
        """Generate multiple surveys"""
        survey_types = [
            "Customer Satisfaction",
            "Product Feedback", 
            "Employee Engagement",
            "Market Research",
            "User Experience",
            "Website Feedback",
            "Event Feedback"
        ]
        
        # Use selected types
        selected_types = survey_types[:num_surveys] if num_surveys <= len(survey_types) else survey_types
        
        console.print(f"[yellow]Generating {len(selected_types)} surveys with Ollama ({self.model})...[/yellow]")
        
        surveys = []
        for i, survey_type in enumerate(selected_types):
            console.print(f"[dim]  Generating survey {i+1}/{len(selected_types)}: {survey_type}[/dim]")
            
            survey = await self.generate_survey_async(survey_type)
            if survey:
                surveys.append(survey)
            
            # Small delay between generations
            await asyncio.sleep(1)
        
        # If we need more surveys, duplicate and modify existing ones
        while len(surveys) < num_surveys:
            base_survey = surveys[0].copy() if surveys else self._create_fallback_survey("General Feedback")
            base_survey["name"] = f"{base_survey['name']} {len(surveys) + 1}"
            surveys.append(base_survey)
        
        return surveys[:num_surveys]
    
    def generate_users(self, num_users: int = 10) -> List[Dict]:
        """Generate realistic users (no LLM needed)"""
        from faker import Faker
        fake = Faker()
        
        users = []
        domains = ["company.com", "business.io", "enterprise.ai", "startup.tech"]
        
        # Ensure we have owners and managers as required (2 owners, 3 managers, rest admins/viewers)
        roles = []
        roles.extend(["owner"] * 2)           # 2 owners
        roles.extend(["manager"] * 3)         # 3 managers
        roles.extend(["admin"] * 2)           # 2 admins
        roles.extend(["viewer"] * (num_users - 7))  # rest as viewers
        
        for i in range(num_users):
            first_name = fake.first_name()
            last_name = fake.last_name()
            domain = random.choice(domains)
            
            user = {
                "name": f"{first_name} {last_name}",
                "email": f"{first_name.lower()}.{last_name.lower()}@{domain}",
                "role": roles[i] if i < len(roles) else "viewer",
                "organization": fake.company()
            }
            
            users.append(user)
        
        return users
    
    def generate_responses(self, surveys: List[Dict], users: List[Dict], min_per_survey: int = 1) -> List[Dict]:
        """Generate realistic survey responses"""
        responses = []
        
        for survey in surveys:
            survey_name = survey.get("name", "Unknown Survey")
            num_responses = random.randint(min_per_survey, 3)
            
            for _ in range(num_responses):
                user = random.choice(users)
                answers = {}
                
                for question in survey.get("questions", []):
                    answer = self._generate_answer(question)
                    if answer is not None:
                        answers[question.get("headline", "question")] = answer
                
                response = {
                    "survey_name": survey_name,
                    "user_id": user.get("email"),
                    "answers": answers,
                    "completed": True,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": "ollama_generated"
                    }
                }
                responses.append(response)
        
        return responses
    
    def _generate_answer(self, question: Dict) -> Any:
        """Generate realistic answer for a question"""
        q_type = question.get("type")
        
        if q_type == "rating":
            # Weight toward positive ratings (4-5)
            weights = [0.05, 0.1, 0.15, 0.3, 0.4]  # 1-5
            return random.choices(range(1, 6), weights=weights)[0]
        elif q_type in ["multipleChoice", "dropdown"]:
            choices = question.get("choices", [])
            if choices:
                # Weight toward middle options
                if len(choices) >= 3:
                    weights = [0.2, 0.3, 0.3, 0.2][:len(choices)]
                    return random.choices(choices, weights=weights)[0]
                return random.choice(choices)
            return "Option 1"
        elif q_type == "openText":
            templates = [
                "This was a great experience overall.",
                "I found the service to be satisfactory.",
                "Could use some improvements in certain areas.",
                "Very helpful and informative experience.",
                "Looking forward to seeing future updates."
            ]
            return random.choice(templates)
        else:
            return "Response"
    
    async def run(self, num_surveys: int = 5, num_users: int = 10) -> Dict[str, List]:
        """Main method to generate all data"""
        console.print(f"[bold]Generating data with Ollama ({self.model})[/bold]")
        
        # Generate surveys
        surveys = await self.generate_surveys(num_surveys)
        console.print(f"[green]✓ Generated {len(surveys)} surveys[/green]")
        
        # Generate users
        users = self.generate_users(num_users)
        console.print(f"[green]✓ Generated {len(users)} users (2 Owners, 3 Managers, 2 Admins, {num_users-7} Viewers)[/green]")
        
        # Generate responses
        responses = self.generate_responses(surveys, users, min_per_survey=1)
        console.print(f"[green]✓ Generated {len(responses)} responses[/green]")
        
        return {
            "surveys": surveys,
            "users": users,
            "responses": responses
        }