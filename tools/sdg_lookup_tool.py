import sys
import os
from crewai.tools import tool

# Add project root to python path for importing Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Dictionary containing SDG descriptions and standard target indicators
SDG_DATA = {
    1: {
        "title": "No Poverty",
        "targets": "End poverty in all its forms everywhere.",
        "indicators": ["1.1.1", "1.2.1", "1.3.1"]
    },
    2: {
        "title": "Zero Hunger",
        "targets": "End hunger, achieve food security and improved nutrition, and promote sustainable agriculture.",
        "indicators": ["2.1.1", "2.2.1", "2.5.1"]
    },
    3: {
        "title": "Good Health and Well-being",
        "targets": "Ensure healthy lives and promote well-being for all at all ages.",
        "indicators": ["3.1.1", "3.2.1", "3.8.1"]
    },
    4: {
        "title": "Quality Education",
        "targets": "Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all.",
        "indicators": ["4.1.1", "4.4.1", "4.a.1"]
    },
    5: {
        "title": "Gender Equality",
        "targets": "Achieve gender equality and empower all women and girls.",
        "indicators": ["5.1.1", "5.5.1", "5.b.1"]
    },
    6: {
        "title": "Clean Water and Sanitation",
        "targets": "Ensure availability and sustainable management of water and sanitation for all.",
        "indicators": ["6.1.1", "6.2.1", "6.4.1"]
    },
    7: {
        "title": "Affordable and Clean Energy",
        "targets": "Ensure access to affordable, reliable, sustainable and modern energy for all.",
        "indicators": ["7.1.1", "7.2.1", "7.3.1"]
    },
    8: {
        "title": "Decent Work and Economic Growth",
        "targets": "Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all.",
        "indicators": ["8.1.1", "8.2.1", "8.5.1"]
    },
    9: {
        "title": "Industry, Innovation and Infrastructure",
        "targets": "Build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation.",
        "indicators": ["9.c.1", "9.b.1", "9.5.1"]
    },
    10: {
        "title": "Reduced Inequalities",
        "targets": "Reduce inequality within and among countries.",
        "indicators": ["10.1.1", "10.4.1", "10.b.1"]
    },
    11: {
        "title": "Sustainable Cities and Communities",
        "targets": "Make cities and human settlements inclusive, safe, resilient and sustainable.",
        "indicators": ["11.1.1", "11.2.1", "11.7.1"]
    },
    12: {
        "title": "Responsible Consumption and Production",
        "targets": "Ensure sustainable consumption and production patterns.",
        "indicators": ["12.2.1", "12.5.1", "12.8.1"]
    },
    13: {
        "title": "Climate Action",
        "targets": "Take urgent action to combat climate change and its impacts.",
        "indicators": ["13.1.1", "13.2.1", "13.3.1"]
    },
    14: {
        "title": "Life Below Water",
        "targets": "Conserve and sustainably use the oceans, seas and marine resources for sustainable development.",
        "indicators": ["14.1.1", "14.5.1"]
    },
    15: {
        "title": "Life on Land",
        "targets": "Protect, restore and promote sustainable use of terrestrial ecosystems, sustainably manage forests, combat desertification, and halt and reverse land degradation and halt biodiversity loss.",
        "indicators": ["15.1.1", "15.2.1", "15.5.1"]
    },
    16: {
        "title": "Peace, Justice and Strong Institutions",
        "targets": "Promote peaceful and inclusive societies for sustainable development, provide access to justice for all and build effective, accountable and inclusive institutions at all levels.",
        "indicators": ["16.1.1", "16.3.1", "16.9.1"]
    },
    17: {
        "title": "Partnerships for the Goals",
        "targets": "Strengthen the means of implementation and revitalize the Global Partnership for Sustainable Development.",
        "indicators": ["17.6.1", "17.8.1", "17.19.1"]
    }
}

@tool("SDGLookup")
def sdg_lookup_tool(keyword: str) -> str:
    """
    Search for SDGs (Sustainable Development Goals) matching a topic or keyword.
    
    Args:
        keyword: The topic keyword to search for (e.g. 'digital', 'education', 'poverty', 'energy').
        
    Returns:
        A list of matching SDGs with their numbers, titles, targets summary, and key indicator codes.
    """
    keyword_lower = keyword.lower()
    matches = []
    
    for sdg_num, data in SDG_DATA.items():
        if keyword_lower in data["title"].lower() or keyword_lower in data["targets"].lower():
            indicators_str = ", ".join(data["indicators"])
            matches.append(
                f"SDG {sdg_num}: {data['title']}\n"
                f"  Goal Summary: {data['targets']}\n"
                f"  Indicator Codes: {indicators_str}"
            )
            
    if not matches:
        return f"No direct SDG match found for keyword: '{keyword}'. Try another development-related term."
        
    return f"Matching SDGs for topic '{keyword}':\n\n" + "\n\n".join(matches)

if __name__ == "__main__":
    Config.validate()
    print("Testing SDGLookup tool...")
    
    # Test for "digital" or "infrastructure" keyword
    test_keyword = "infrastructure"
    result = sdg_lookup_tool.invoke({"keyword": test_keyword})
    print("\nResult:")
    print(result)
