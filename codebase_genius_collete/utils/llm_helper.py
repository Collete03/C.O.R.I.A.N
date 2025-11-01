"""
LLM Helper Utility.

Provides a unified interface for interacting with various LLM providers
(OpenAI, Gemini) to enhance documentation, summarize code, and
provide AI-driven insights.

Reads API keys from the .env file.
"""

import os
from typing import Optional, Dict, Any

# --- LLM Helper Class ---

class LLMHelper:
    """
    Manages connections and API calls to different LLM providers.
    """
    
    def __init__(self):
        """
        Initialize the helper, load API keys, and check availability.
        """
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.llm_provider = os.getenv('LLM_PROVIDER', 'gemini').lower()
        self.llm_model = os.getenv('LLM_MODEL', 'gemini-1.5-flash')
        
        self.available_models = {
            'openai': bool(self.openai_api_key),
            'gemini': bool(self.gemini_api_key)
        }
        
    def is_llm_available(self) -> bool:
        """Check if the preferred LLM service is available and configured."""
        return self.available_models.get(self.llm_provider, False)

    def enhance_readme_summary(self, summary: str, repo_context: Optional[Dict] = None) -> Optional[str]:
        """
        Use AI to enhance a project summary.
        
        Args:
            summary: The basic summary extracted from the README.
            repo_context: Optional dictionary with context (e.g., languages).
            
        Returns:
            An enhanced summary string, or None if enhancement fails.
        """
        if not self.is_llm_available():
            return None # Cannot enhance if preferred provider is not set

        try:
            prompt = self._build_enhancement_prompt(summary, repo_context)
            
            if self.llm_provider == 'gemini':
                return self._enhance_with_gemini(prompt)
            elif self.llm_provider == 'openai':
                return self._enhance_with_openai(prompt)
            else:
                return None
                
        except Exception as e:
            print(f"  ! AI enhancement failed: {e}")
            return None

    def _enhance_with_openai(self, prompt: str) -> str:
        """Enhance summary using OpenAI API."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model=self.llm_model or "gpt-4o-mini", # Default to mini if not set
                messages=[
                    {"role": "system", "content": "You are a world-class technical writer. Your goal is to improve and expand upon a brief project summary, making it clear, professional, and comprehensive."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            enhanced = response.choices[0].message.content.strip()
            return f"{enhanced}\n\n*This summary was enhanced by AI for clarity.*"
        
        except ImportError:
            print("  ! OpenAI package not installed. Please run: pip install openai")
            return None
        except Exception as e:
            print(f"  ! OpenAI API error: {e}")
            return None

    def _enhance_with_gemini(self, prompt: str) -> str:
        """Enhance summary using Google Gemini API."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            
            model = genai.GenerativeModel(self.llm_model or 'gemini-1.5-flash')
            
            response = model.generate_content(prompt)
            enhanced = response.text.strip()
            
            return f"{enhanced}\n\n*This summary was enhanced by AI for clarity.*"
            
        except ImportError:
            print("  ! Google Generative AI package not installed. Please run: pip install google-generativeai")
            return None
        except Exception as e:
            print(f"  ! Gemini API error: {e}")
            return None

    def _build_enhancement_prompt(self, summary: str, repo_context: Optional[Dict] = None) -> str:
        """Build the final prompt string to send to the LLM."""
        
        base_prompt = f"""
        Please enhance the following codebase summary. The original summary is very basic, 
        and I need a more professional and comprehensive version for my documentation.

        **Original Summary:**
        "{summary}"

        **Your Task:**
        Please rewrite and expand this into a clear, engaging project overview. 
        Focus on:
        1.  **Project's Purpose:** What does this project do?
        2.  **Key Features:** What are its main capabilities?
        3.  **Intended Audience:** Who would use this?
        
        Do not just repeat the original summary. Provide a high-quality, 
        well-written replacement.
        """
        
        if repo_context:
            context_info = f"""
            **Additional Context (from file analysis):**
            - Main languages: {', '.join(repo_context.get('languages', ['N/A']))}
            """
            base_prompt += context_info
        
        return base_prompt

# --- Global Instance & Jac-Exportable Functions ---

# Create a single global instance to be shared
llm_helper_instance = LLMHelper()

def is_llm_available() -> bool:
    """Jac-importable function to check LLM availability."""
    return llm_helper_instance.is_llm_available()

def enhance_readme_summary(summary: str, repo_context: Optional[Dict] = None) -> Optional[str]:
    """Jac-importable function to enhance a summary."""
    return llm_helper_instance.enhance_readme_summary(summary, repo_context)

