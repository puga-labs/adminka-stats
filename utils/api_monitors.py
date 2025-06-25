"""
API Balance Checker for DeepSeek
Simplified version for DeepSeek monitoring only
"""

import requests
import litellm
from datetime import datetime
from typing import Dict, List, Optional
import os
import time
import asyncio
import nest_asyncio
from dotenv import load_dotenv
import streamlit as st
import aiohttp

# Apply nest_asyncio to allow nested event loops (for Streamlit)
nest_asyncio.apply()

load_dotenv()

# Model configurations for ping tests
DEEPSEEK_MODEL = "deepseek/deepseek-chat"  # Changed from deepseek-reasoner
GEMINI_MODEL = "gemini/gemini-2.5-pro-preview-05-06"
PING_TIMEOUT = 10
PING_MAX_TOKENS = 10

# Ping test messages
PING_MESSAGES = [
    {"role": "system", "content": "You must respond with only the word 'pong' when you receive 'ping'. No other text."},
    {"role": "user", "content": "ping"}
]


class APIBalanceChecker:
    """Class for checking DeepSeek API balances and Gemini status"""
    
    def __init__(self):
        """Initialize with API keys from environment variables"""
        self.deepseek_keys = [
            os.getenv("DEEPSEEK_API_KEY_1"),
            os.getenv("DEEPSEEK_API_KEY_2"),
            os.getenv("DEEPSEEK_API_KEY_3")
        ]
        
        # Google Gemini key
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        
    def check_deepseek_balance(self, api_key: str, key_name: str = "DeepSeek") -> Dict:
        """Check DeepSeek API balance"""
        if not api_key:
            return {
                "service": key_name,
                "status": "not_configured",
                "error": "API key not found"
            }
            
        url = "https://api.deepseek.com/user/balance"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract balance information
                balance_info = {}
                total_balance = 0
                granted_balance = 0
                topped_up_balance = 0
                
                if "balance_infos" in data and len(data["balance_infos"]) > 0:
                    for balance in data["balance_infos"]:
                        currency = balance.get("currency", "Unknown")
                        total = float(balance.get("total_balance", "0"))
                        granted = float(balance.get("granted_balance", "0"))
                        topped_up = float(balance.get("topped_up_balance", "0"))
                        
                        balance_info[currency] = {
                            "total": total,
                            "granted": granted,
                            "topped_up": topped_up
                        }
                        
                        if currency == "USD":
                            total_balance = total
                            granted_balance = granted
                            topped_up_balance = topped_up
                
                return {
                    "service": key_name,
                    "status": "active" if data.get("is_available", False) else "insufficient",
                    "balance": f"${total_balance:.2f}",
                    "balance_value": total_balance,
                    "granted": f"${granted_balance:.2f}",
                    "topped_up": f"${topped_up_balance:.2f}",
                    "balances": balance_info,
                    "raw_response": data
                }
            else:
                return {
                    "service": key_name,
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "balance_value": 0
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "service": key_name,
                "status": "error",
                "error": f"Request failed: {str(e)}",
                "balance_value": 0
            }
    
    async def check_deepseek_balance_async(self, api_key: str, key_name: str = "DeepSeek") -> Dict:
        """Async check DeepSeek API balance"""
        if not api_key:
            return {
                "service": key_name,
                "status": "not_configured",
                "error": "API key not found"
            }
            
        url = "https://api.deepseek.com/user/balance"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract balance information
                        balance_info = {}
                        total_balance = 0
                        granted_balance = 0
                        topped_up_balance = 0
                        
                        if "balance_infos" in data and len(data["balance_infos"]) > 0:
                            for balance in data["balance_infos"]:
                                currency = balance.get("currency", "Unknown")
                                total = float(balance.get("total_balance", "0"))
                                granted = float(balance.get("granted_balance", "0"))
                                topped_up = float(balance.get("topped_up_balance", "0"))
                                
                                balance_info[currency] = {
                                    "total": total,
                                    "granted": granted,
                                    "topped_up": topped_up
                                }
                                
                                if currency == "USD":
                                    total_balance = total
                                    granted_balance = granted
                                    topped_up_balance = topped_up
                        
                        return {
                            "service": key_name,
                            "status": "active" if data.get("is_available", False) else "insufficient",
                            "balance": f"${total_balance:.2f}",
                            "balance_value": total_balance,
                            "granted": f"${granted_balance:.2f}",
                            "topped_up": f"${topped_up_balance:.2f}",
                            "balances": balance_info,
                            "raw_response": data
                        }
                    else:
                        return {
                            "service": key_name,
                            "status": "error",
                            "error": f"HTTP {response.status}",
                            "balance_value": 0
                        }
                        
            except asyncio.TimeoutError:
                return {
                    "service": key_name,
                    "status": "error",
                    "error": "Request timeout",
                    "balance_value": 0
                }
            except Exception as e:
                return {
                    "service": key_name,
                    "status": "error",
                    "error": f"Request failed: {str(e)}",
                    "balance_value": 0
                }
    
    def ping_deepseek_api(self, api_key: str, key_name: str = "DeepSeek") -> Dict:
        """Ping DeepSeek API with a simple test request"""
        if not api_key:
            return {
                "ping_status": "not_configured",
                "ping_error": "API key not found",
                "ping_time": 0
            }
        
        try:
            start_time = time.time()
            
            # Use LiteLLM for unified API calls
            response = litellm.completion(
                model=DEEPSEEK_MODEL,
                messages=PING_MESSAGES,
                api_key=api_key,
                max_tokens=PING_MAX_TOKENS,
                timeout=PING_TIMEOUT
            )
            
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            # Safely extract response content for DeepSeek
            try:
                # Debug logging
                if hasattr(response, 'choices') and response.choices:
                    choice = response.choices[0]
                    content = choice.message.content
                    
                    # Additional debug info
                    if not content:
                        print(f"DEBUG DeepSeek: Empty content. Model: {getattr(response, 'model', 'unknown')}, "
                              f"Finish reason: {getattr(choice, 'finish_reason', 'unknown')}")
                    
                    response_content = content.strip().lower() if content else "[empty response]"
                else:
                    response_content = "[no choices in response]"
            except (AttributeError, IndexError) as e:
                response_content = f"parse error: {str(e)}"
            
            return {
                "ping_status": "success",
                "ping_response": response_content,
                "ping_time": response_time,
                "ping_error": None
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = round(end_time - start_time, 2) if 'start_time' in locals() else 0
            
            # Determine error type
            error_str = str(e).lower()
            if "timeout" in error_str:
                status = "timeout"
            elif "quota" in error_str or "rate" in error_str or "429" in error_str:
                status = "quota_exceeded"
            elif "unauthorized" in error_str or "401" in error_str:
                status = "invalid_key"
            else:
                status = "failed"
            
            return {
                "ping_status": status,
                "ping_response": None,
                "ping_time": response_time,
                "ping_error": str(e)
            }
    
    async def ping_deepseek_api_async(self, api_key: str, key_name: str = "DeepSeek") -> Dict:
        """Async ping DeepSeek API with a simple test request"""
        if not api_key:
            return {
                "ping_status": "not_configured",
                "ping_error": "API key not found",
                "ping_time": 0
            }
        
        try:
            start_time = time.time()
            
            # Use async LiteLLM for true parallel calls
            response = await litellm.acompletion(
                model=DEEPSEEK_MODEL,
                messages=PING_MESSAGES,
                api_key=api_key,
                max_tokens=PING_MAX_TOKENS,
                timeout=PING_TIMEOUT
            )
            
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            # Safely extract response content for DeepSeek
            try:
                # Debug logging
                if hasattr(response, 'choices') and response.choices:
                    choice = response.choices[0]
                    content = choice.message.content
                    
                    # Additional debug info
                    if not content:
                        print(f"DEBUG DeepSeek: Empty content. Model: {getattr(response, 'model', 'unknown')}, "
                              f"Finish reason: {getattr(choice, 'finish_reason', 'unknown')}")
                    
                    response_content = content.strip().lower() if content else "[empty response]"
                else:
                    response_content = "[no choices in response]"
            except (AttributeError, IndexError) as e:
                response_content = f"parse error: {str(e)}"
            
            return {
                "ping_status": "success",
                "ping_response": response_content,
                "ping_time": response_time,
                "ping_error": None
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = round(end_time - start_time, 2) if 'start_time' in locals() else 0
            
            # Determine error type
            error_str = str(e).lower()
            if "timeout" in error_str:
                status = "timeout"
            elif "quota" in error_str or "rate" in error_str or "429" in error_str:
                status = "quota_exceeded"
            elif "unauthorized" in error_str or "401" in error_str:
                status = "invalid_key"
            else:
                status = "failed"
            
            return {
                "ping_status": status,
                "ping_response": None,
                "ping_time": response_time,
                "ping_error": str(e)
            }
    
    def check_gemini_status(self, api_key: str) -> Dict:
        """Check Google Gemini API key validity (no balance API available)"""
        if not api_key:
            return {
                "service": "Google Gemini",
                "status": "not_configured",
                "error": "API key not found"
            }
            
        # Test with a lightweight request to models endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                model_count = len(data.get("models", []))
                
                return {
                    "service": "Google Gemini",
                    "status": "active",
                    "models_available": model_count,
                    "note": "Key valid (no balance API)",
                    "dashboard_url": "https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/metrics"
                }
            elif response.status_code == 403:
                return {
                    "service": "Google Gemini",
                    "status": "invalid_key",
                    "error": "Invalid or restricted API key"
                }
            elif response.status_code == 429:
                return {
                    "service": "Google Gemini",
                    "status": "quota_exceeded",
                    "error": "Quota exceeded or rate limited"
                }
            else:
                return {
                    "service": "Google Gemini",
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "service": "Google Gemini",
                "status": "error",
                "error": f"Request failed: {str(e)}"
            }
    
    async def check_gemini_status_async(self, api_key: str) -> Dict:
        """Async check Google Gemini API key validity"""
        if not api_key:
            return {
                "service": "Google Gemini",
                "status": "not_configured",
                "error": "API key not found"
            }
            
        # Test with a lightweight request to models endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        model_count = len(data.get("models", []))
                        
                        return {
                            "service": "Google Gemini",
                            "status": "active",
                            "models_available": model_count,
                            "note": "Key valid (no balance API)",
                            "dashboard_url": "https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/metrics"
                        }
                    elif response.status == 403:
                        return {
                            "service": "Google Gemini",
                            "status": "invalid_key",
                            "error": "Invalid or restricted API key"
                        }
                    elif response.status == 429:
                        return {
                            "service": "Google Gemini",
                            "status": "quota_exceeded",
                            "error": "Quota exceeded or rate limited"
                        }
                    else:
                        return {
                            "service": "Google Gemini",
                            "status": "error",
                            "error": f"HTTP {response.status}"
                        }
                        
            except asyncio.TimeoutError:
                return {
                    "service": "Google Gemini",
                    "status": "error",
                    "error": "Request timeout"
                }
            except Exception as e:
                return {
                    "service": "Google Gemini",
                    "status": "error",
                    "error": f"Request failed: {str(e)}"
                }
    
    def ping_gemini_api(self, api_key: str) -> Dict:
        """Ping Google Gemini API with a simple test request"""
        if not api_key:
            return {
                "ping_status": "not_configured",
                "ping_error": "API key not found",
                "ping_time": 0
            }
        
        try:
            start_time = time.time()
            
            # Use LiteLLM for unified API calls
            response = litellm.completion(
                model=GEMINI_MODEL,
                messages=PING_MESSAGES,
                api_key=api_key,
                max_tokens=PING_MAX_TOKENS,
                timeout=PING_TIMEOUT
            )
            
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            # Safely extract response content for Gemini
            try:
                content = response.choices[0].message.content
                response_content = content.strip().lower() if content else "empty response"
                
                # Debug info for Gemini issues
                if not content:
                    debug_info = f"Debug: choices={len(response.choices) if hasattr(response, 'choices') else 'no choices'}"
                    response_content = f"empty response ({debug_info})"
                    
            except (AttributeError, IndexError) as e:
                # More detailed debug info
                try:
                    debug_info = f"Response type: {type(response)}, Has choices: {hasattr(response, 'choices')}"
                    if hasattr(response, 'choices') and response.choices:
                        debug_info += f", Choice type: {type(response.choices[0])}"
                        if hasattr(response.choices[0], 'message'):
                            debug_info += f", Message type: {type(response.choices[0].message)}"
                    response_content = f"parse error: {str(e)} ({debug_info})"
                except:
                    response_content = f"parse error: {str(e)}"
            
            return {
                "ping_status": "success",
                "ping_response": response_content,
                "ping_time": response_time,
                "ping_error": None
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = round(end_time - start_time, 2) if 'start_time' in locals() else 0
            
            # Determine error type for Gemini
            error_str = str(e).lower()
            if "timeout" in error_str:
                status = "timeout"
            elif "quota" in error_str or "rate" in error_str or "429" in error_str:
                status = "quota_exceeded"
            elif "unauthorized" in error_str or "403" in error_str:
                status = "invalid_key"
            else:
                status = "failed"
            
            return {
                "ping_status": status,
                "ping_response": None,
                "ping_time": response_time,
                "ping_error": str(e)
            }
    
    async def ping_gemini_api_async(self, api_key: str) -> Dict:
        """Async ping Google Gemini API with a simple test request"""
        if not api_key:
            return {
                "ping_status": "not_configured",
                "ping_error": "API key not found",
                "ping_time": 0
            }
        
        try:
            start_time = time.time()
            
            # Use async LiteLLM for true parallel calls
            response = await litellm.acompletion(
                model=GEMINI_MODEL,
                messages=PING_MESSAGES,
                api_key=api_key,
                max_tokens=PING_MAX_TOKENS,
                timeout=PING_TIMEOUT
            )
            
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            # Safely extract response content for Gemini
            try:
                content = response.choices[0].message.content
                response_content = content.strip().lower() if content else "empty response"
                
                # Debug info for Gemini issues
                if not content:
                    debug_info = f"Debug: choices={len(response.choices) if hasattr(response, 'choices') else 'no choices'}"
                    response_content = f"empty response ({debug_info})"
                    
            except (AttributeError, IndexError) as e:
                # More detailed debug info
                try:
                    debug_info = f"Response type: {type(response)}, Has choices: {hasattr(response, 'choices')}"
                    if hasattr(response, 'choices') and response.choices:
                        debug_info += f", Choice type: {type(response.choices[0])}"
                        if hasattr(response.choices[0], 'message'):
                            debug_info += f", Message type: {type(response.choices[0].message)}"
                    response_content = f"parse error: {str(e)} ({debug_info})"
                except:
                    response_content = f"parse error: {str(e)}"
            
            return {
                "ping_status": "success",
                "ping_response": response_content,
                "ping_time": response_time,
                "ping_error": None
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = round(end_time - start_time, 2) if 'start_time' in locals() else 0
            
            # Determine error type for Gemini
            error_str = str(e).lower()
            if "timeout" in error_str:
                status = "timeout"
            elif "quota" in error_str or "rate" in error_str or "429" in error_str:
                status = "quota_exceeded"
            elif "unauthorized" in error_str or "403" in error_str:
                status = "invalid_key"
            else:
                status = "failed"
            
            return {
                "ping_status": status,
                "ping_response": None,
                "ping_time": response_time,
                "ping_error": str(e)
            }
    
    def check_all_balances(self, include_ping_tests=False) -> List[Dict]:
        """Check balances of all DeepSeek API keys and Gemini status"""
        # Use async version for parallel checks
        return asyncio.run(self.check_all_balances_async(include_ping_tests))
    
    async def check_all_balances_async(self, include_ping_tests=False) -> List[Dict]:
        """Async check balances of all DeepSeek API keys and Gemini status"""
        # Create tasks for parallel balance checks
        balance_tasks = []
        
        # Create tasks for DeepSeek balances
        for i, key in enumerate(self.deepseek_keys, 1):
            key_name = f"DeepSeek Key {i}"
            task = self.check_deepseek_balance_async(key, key_name)
            balance_tasks.append((task, "deepseek", key_name))
        
        # Create task for Gemini status
        task = self.check_gemini_status_async(self.gemini_key)
        balance_tasks.append((task, "gemini", "Google Gemini"))
        
        # Execute all balance checks in parallel
        balance_coroutines = [task for task, _, _ in balance_tasks]
        balance_results_raw = await asyncio.gather(*balance_coroutines, return_exceptions=True)
        
        # Process balance results
        balance_results = []
        for i, result in enumerate(balance_results_raw):
            _, api_type, service_name = balance_tasks[i]
            
            if isinstance(result, Exception):
                # Handle exceptions
                balance_results.append(({
                    "service": service_name,
                    "status": "error",
                    "error": str(result),
                    "balance_value": 0
                }, api_type, service_name))
            else:
                balance_results.append((result, api_type, service_name))
        
        # Only run ping tests if requested
        if include_ping_tests:
            ping_results = await self._ping_all_for_balance_check()
        else:
            # Create empty ping results
            ping_results = []
        
        # Merge balance and ping results
        final_results = []
        for (balance_result, api_type, service_name) in balance_results:
            if include_ping_tests:
                # Find corresponding ping result
                ping_result = next(
                    (p for p in ping_results if p.get("service") == service_name),
                    {"ping_status": "not_tested", "ping_time": 0, "ping_response": None}
                )
            else:
                # No ping test performed
                ping_result = {"ping_status": "not_tested", "ping_time": 0, "ping_response": None}
            
            # Merge results
            combined_result = {**balance_result, **ping_result}
            final_results.append(self._format_result(combined_result, api_type=api_type))
        
        return final_results
    
    async def _ping_all_for_balance_check(self) -> List[Dict]:
        """Internal async method to run ping tests for balance check"""
        tasks = []
        
        # Create tasks for DeepSeek keys
        for i, key in enumerate(self.deepseek_keys, 1):
            if key:
                key_name = f"DeepSeek Key {i}"
                task = self.ping_deepseek_api_async(key, key_name)
                tasks.append((task, key_name))
        
        # Create task for Gemini
        if self.gemini_key:
            task = self.ping_gemini_api_async(self.gemini_key)
            tasks.append((task, "Google Gemini"))
        
        if not tasks:
            return []
        
        # Execute all tasks in parallel
        coroutines = [task for task, _ in tasks]
        results_raw = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Format results
        results = []
        for i, result in enumerate(results_raw):
            _, service_name = tasks[i]
            
            if isinstance(result, Exception):
                results.append({
                    "service": service_name,
                    "ping_status": "failed",
                    "ping_error": str(result),
                    "ping_time": 0,
                    "ping_response": None
                })
            else:
                results.append({
                    "service": service_name,
                    **result
                })
        
        return results
    
    def _format_status(self, status: str) -> str:
        """Format status with emoji indicator"""
        status_emojis = {
            "active": "🟢",
            "insufficient": "🟡", 
            "error": "🔴",
            "invalid_key": "🔴",
            "quota_exceeded": "🟡",
            "not_configured": "⚫",
            "unknown": "⚫"
        }
        emoji = status_emojis.get(status, "⚫")
        formatted_text = status.replace('_', ' ').title()
        return f"{emoji} {formatted_text}"
    
    def _format_result(self, result: Dict, api_type: str = "deepseek") -> Dict:
        """Format result for table display"""
        
        # Format ping test results
        ping_status = result.get("ping_status", "unknown")
        ping_time = result.get("ping_time", 0)
        ping_response = result.get("ping_response", "")
        
        # Create ping display string
        if ping_status == "not_tested":
            ping_display = "⚪ Not tested"
        elif ping_status == "success":
            if ping_time < 3:
                ping_display = f"🟢 {ping_time}s"
            else:
                ping_display = f"🟡 {ping_time}s (slow)"
        elif ping_status == "timeout":
            ping_display = "🔴 Timeout"
        elif ping_status == "quota_exceeded":
            ping_display = "🟡 Quota exceeded"
        elif ping_status == "invalid_key":
            ping_display = "🔴 Invalid key"
        elif ping_status == "not_configured":
            ping_display = "⚫ Not configured"
        else:
            ping_display = "🔴 Failed"
        
        if api_type == "deepseek":
            formatted = {
                "Service": result.get("service", "Unknown"),
                "Type": "DeepSeek",
                "Status": self._format_status(result.get("status", "unknown")),
                "Total Balance": result.get("balance", "-"),
                "Granted": result.get("granted", "-"),
                "Topped Up": result.get("topped_up", "-"),
                "Ping Test": ping_display,
                "_balance_value": result.get("balance_value", 0),  # Hidden field
                "_api_type": "deepseek",  # Hidden field
                "_raw_status": result.get("status", "unknown"),  # Hidden field for calculations
                "_ping_status": ping_status,  # Hidden field
                "_ping_time": ping_time,  # Hidden field
                "_ping_response": ping_response  # Hidden field
            }
        else:  # gemini
            formatted = {
                "Service": result.get("service", "Unknown"),
                "Type": "Gemini",
                "Status": self._format_status(result.get("status", "unknown")),
                "Total Balance": "N/A",
                "Granted": "N/A", 
                "Topped Up": "N/A",
                "Ping Test": ping_display,
                "_balance_value": 0,  # Hidden field
                "_api_type": "gemini",  # Hidden field
                "_raw_status": result.get("status", "unknown"),  # Hidden field for calculations
                "_models_count": result.get("models_available", 0),  # Hidden field
                "_note": result.get("note", ""),  # Hidden field
                "_dashboard_url": result.get("dashboard_url", ""),  # Hidden field
                "_ping_status": ping_status,  # Hidden field
                "_ping_time": ping_time,  # Hidden field
                "_ping_response": ping_response  # Hidden field
            }
        
        # Add error info if present
        if "error" in result:
            formatted["Error"] = result["error"]
        
        # Add ping error if present
        if result.get("ping_error"):
            formatted["Ping Error"] = result["ping_error"]
            
        return formatted


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_balances(include_ping_tests=False):
    """Get cached API balances"""
    checker = APIBalanceChecker()
    return checker.check_all_balances(include_ping_tests=include_ping_tests)


async def ping_all_apis_async():
    """Perform ping tests using asyncio for true parallel execution"""
    checker = APIBalanceChecker()
    tasks = []
    
    # Create tasks for DeepSeek keys
    for i, key in enumerate(checker.deepseek_keys, 1):
        if key:  # Only add configured keys
            key_name = f"DeepSeek Key {i}"
            task = checker.ping_deepseek_api_async(key, key_name)
            tasks.append((task, key_name, "DeepSeek"))
    
    # Create task for Gemini
    if checker.gemini_key:
        task = checker.ping_gemini_api_async(checker.gemini_key)
        tasks.append((task, "Google Gemini", "Gemini"))
    
    # Execute all tasks in parallel
    if tasks:
        # Extract just the coroutines for gather
        coroutines = [task for task, _, _ in tasks]
        
        # Run all tasks concurrently
        results_raw = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Format results with service names
        results = []
        for i, result in enumerate(results_raw):
            _, service_name, service_type = tasks[i]
            
            if isinstance(result, Exception):
                # Handle exceptions
                results.append({
                    "service": service_name,
                    "type": service_type,
                    "ping_status": "failed",
                    "ping_error": str(result),
                    "ping_time": 0,
                    "ping_response": None
                })
            else:
                # Add service info to result
                results.append({
                    "service": service_name,
                    "type": service_type,
                    **result
                })
    else:
        results = []
    
    return results


def ping_all_apis():
    """Wrapper to call async function from sync Streamlit context"""
    # nest_asyncio already applied at module level
    # Simply use asyncio.run which creates a new event loop
    return asyncio.run(ping_all_apis_async())


def get_status_color(status: str) -> str:
    """Get color for status display"""
    status_colors = {
        "active": "green",
        "insufficient": "orange", 
        "error": "red",
        "not_configured": "gray",
        "unknown": "gray"
    }
    return status_colors.get(status, "gray")


def calculate_api_stats(results: List[Dict]) -> Dict:
    """Calculate statistics for all API keys"""
    deepseek_results = [r for r in results if r.get("_api_type") == "deepseek"]
    gemini_results = [r for r in results if r.get("_api_type") == "gemini"]
    
    # DeepSeek stats
    balances = []
    deepseek_active = 0
    deepseek_configured = 0
    
    for result in deepseek_results:
        # Use raw status from hidden field
        raw_status = result.get("_raw_status", "unknown")
        
        if raw_status != "not_configured":
            deepseek_configured += 1
            
        if raw_status == "active":
            deepseek_active += 1
            balance_value = result.get("_balance_value", 0)
            if balance_value > 0:
                balances.append(balance_value)
    
    total_balance = sum(balances) if balances else 0
    avg_balance = (total_balance / len(balances)) if balances else 0
    min_balance = min(balances) if balances else 0
    
    # Gemini stats
    gemini_active = 0
    gemini_configured = 0
    gemini_models = 0
    
    for result in gemini_results:
        # Use raw status from hidden field
        raw_status = result.get("_raw_status", "unknown")
        
        if raw_status != "not_configured":
            gemini_configured += 1
            
        if raw_status == "active":
            gemini_active += 1
            gemini_models = result.get("_models_count", 0)
    
    return {
        "deepseek": {
            "total_balance": total_balance,
            "average_balance": avg_balance,
            "lowest_balance": min_balance,
            "active_keys": deepseek_active,
            "configured_keys": deepseek_configured,
            "total_keys": len(deepseek_results)
        },
        "gemini": {
            "active": gemini_active > 0,
            "configured": gemini_configured > 0,
            "models_available": gemini_models,
            "status": gemini_results[0].get("_raw_status", "not_configured") if gemini_results else "not_configured"
        },
        "overall": {
            "total_apis": len(results),
            "active_apis": deepseek_active + gemini_active,
            "configured_apis": deepseek_configured + gemini_configured
        }
    }