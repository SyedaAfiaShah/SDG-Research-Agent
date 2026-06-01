import sys
import os
import requests
from crewai.tools import tool

# Add project root to python path for importing Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

@tool("WorldBankData")
def world_bank_tool(country: str, indicator: str) -> str:
    """
    Fetch indicator data for a specific country from the World Bank API.
    
    Args:
        country: Two-letter country code (e.g., 'PK' for Pakistan, 'IN' for India, 'KE' for Kenya).
        indicator: World Bank indicator code (e.g., 'IT.NET.USER.ZS' for internet users % of population, 'NY.GDP.PCAP.CD' for GDP per capita).
        
    Returns:
        A formatted string showing the last 5 years of data with years and values.
    """
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&per_page=10"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        # World Bank API returns a list: [0] is metadata, [1] is list of record dicts
        if len(data) < 2 or not data[1]:
            return f"No data found for country '{country}' and indicator '{indicator}'."
            
        records = data[1]
        # Filter records that have actual values, and take top 5 (most recent years)
        valid_records = [r for r in records if r.get("value") is not None]
        recent_records = valid_records[:5]
        
        if not recent_records:
            return f"No valid values found in recent years for country '{country}' and indicator '{indicator}'."
            
        lines = []
        for r in recent_records:
            year = r.get("date")
            val = r.get("value")
            lines.append(f"Year {year}: {val:.2f}%" if "ZS" in indicator and isinstance(val, float) else f"Year {year}: {val}")
            
        header = f"World Bank Indicator: {indicator} for Country: {country}\n"
        return header + "\n".join(lines)
        
    except Exception as e:
        return f"Error fetching data from World Bank: {e}"

if __name__ == "__main__":
    Config.validate()
    print("Testing WorldBankData tool...")
    
    # Test for Pakistan Internet Usage (IT.NET.USER.ZS)
    test_country = "PK"
    test_indicator = "IT.NET.USER.ZS"
    
    result = world_bank_tool.invoke({"country": test_country, "indicator": test_indicator})
    print("\nResult:")
    print(result)
