"""
API Balance Checker for DeepSeek
Simplified version for DeepSeek monitoring only
"""

import requests
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


class APIBalanceChecker:
    """Class for checking DeepSeek API balances"""
    
    def __init__(self):
        """Initialize with API keys from environment variables"""
        self.deepseek_keys = [
            os.getenv("DEEPSEEK_API_KEY_1"),
            os.getenv("DEEPSEEK_API_KEY_2"),
            os.getenv("DEEPSEEK_API_KEY_3")
        ]
        
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
            response = requests.get(url, headers=headers, timeout=10)
            
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
    
    def check_all_balances(self) -> List[Dict]:
        """Check balances of all DeepSeek API keys and return as list for table"""
        results = []
        
        # Check DeepSeek keys
        for i, key in enumerate(self.deepseek_keys, 1):
            result = self.check_deepseek_balance(key, f"DeepSeek Key {i}")
            results.append(self._format_result(result))
        
        return results
    
    def _format_result(self, result: Dict) -> Dict:
        """Format result for table display"""
        formatted = {
            "Service": result.get("service", "Unknown"),
            "Status": result.get("status", "unknown"),
            "Total Balance": result.get("balance", "-"),
            "Granted": result.get("granted", "-"),
            "Topped Up": result.get("topped_up", "-"),
            "Last Check": datetime.now().strftime("%H:%M:%S"),
            "_balance_value": result.get("balance_value", 0)  # Hidden field for calculations
        }
        
        # Add error info if present
        if "error" in result:
            formatted["Error"] = result["error"]
            
        return formatted


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_balances():
    """Get cached API balances"""
    checker = APIBalanceChecker()
    return checker.check_all_balances()


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


def calculate_deepseek_stats(results: List[Dict]) -> Dict:
    """Calculate statistics for DeepSeek keys"""
    balances = []
    active_keys = 0
    configured_keys = 0
    
    for result in results:
        if result["Status"] != "not_configured":
            configured_keys += 1
            
        if result["Status"] == "active":
            active_keys += 1
            balance_value = result.get("_balance_value", 0)
            if balance_value > 0:
                balances.append(balance_value)
    
    total_balance = sum(balances) if balances else 0
    avg_balance = (total_balance / len(balances)) if balances else 0
    min_balance = min(balances) if balances else 0
    
    return {
        "total_balance": total_balance,
        "average_balance": avg_balance,
        "lowest_balance": min_balance,
        "active_keys": active_keys,
        "configured_keys": configured_keys,
        "total_keys": len(results)
    }