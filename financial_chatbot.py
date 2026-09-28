"""
Financial Analysis Chatbot Prototype
=====================================
A simplified AI chatbot for responding to predefined financial queries
using data from Microsoft, Tesla, and Apple 10-K filings (FY2023-2025).

Author: Mannan Mishra
Date: 2026
Assignment: Financial Chatbot Development Task (BCG X GenAI Job Simulation on Forage)
"""

import pandas as pd
from datetime import datetime

# Financial Data from SEC EDGAR (millions USD)
financial_data = {
    'Microsoft': {
        'FY2023': {'Revenue': 211915, 'Net_Income': 72361, 'Total_Assets': 411975, 'OCF': 80414},
        'FY2024': {'Revenue': 245122, 'Net_Income': 88136, 'Total_Assets': 512163, 'OCF': 105022},
        'FY2025': {'Revenue': 281724, 'Net_Income': 101832, 'Total_Assets': 619000, 'OCF': 136160}
    },
    'Tesla': {
        'FY2023': {'Revenue': 96773, 'Net_Income': 14974, 'Total_Assets': 118844, 'OCF': 12742},
        'FY2024': {'Revenue': 97690, 'Net_Income': 7091, 'Total_Assets': 137800, 'OCF': 16178},
        'FY2025': {'Revenue': 94827, 'Net_Income': 3794, 'Total_Assets': 137800, 'OCF': 14700}
    },
    'Apple': {
        'FY2023': {'Revenue': 383285, 'Net_Income': 96995, 'Total_Assets': 352755, 'OCF': 110543},
        'FY2024': {'Revenue': 391035, 'Net_Income': 110543, 'Total_Assets': 364980, 'OCF': 115682},
        'FY2025': {'Revenue': 416160, 'Net_Income': 112010, 'Total_Assets': 359240, 'OCF': 111480}
    }
}

class FinancialChatbot:
    """
    Simple financial chatbot that responds to predefined queries
    using canned responses based on analyzed financial data.
    """
    
    def __init__(self):
        self.query_count = 0
        self.conversation_log = []
        
    def get_total_revenue(self):
        """Query 1: Total revenue across all companies for FY2025"""
        total = sum(financial_data[company]['FY2025']['Revenue'] for company in financial_data)
        return (
            f"The total revenue across Microsoft, Tesla, and Apple in FY2025 is ${total:,.0f} million "
            f"(${total/1000:.1f} billion). Microsoft: ${financial_data['Microsoft']['FY2025']['Revenue']:,.0f}M, "
            f"Apple: ${financial_data['Apple']['FY2025']['Revenue']:,.0f}M, "
            f"Tesla: ${financial_data['Tesla']['FY2025']['Revenue']:,.0f}M."
        )
    
    def get_net_income_change(self):
        """Query 2: How net income has changed year over year"""
        response = "Here's how net income has changed for each company from FY2023 to FY2025:\n\n"
        
        for company in ['Microsoft', 'Apple', 'Tesla']:
            ni_2023 = financial_data[company]['FY2023']['Net_Income']
            ni_2025 = financial_data[company]['FY2025']['Net_Income']
            change = ni_2025 - ni_2023
            pct_change = (change / ni_2023) * 100
            
            trend = "increased" if change > 0 else "decreased"
            response += (
                f"• {company}: {trend} by ${abs(change):,.0f}M ({abs(pct_change):.1f}%) "
                f"from ${ni_2023:,.0f}M (FY2023) to ${ni_2025:,.0f}M (FY2025)\n"
            )
        
        return response
    
    def get_profitability_comparison(self):
        """Query 3: Which company is most profitable in FY2025"""
        companies = {}
        for company in financial_data:
            revenue = financial_data[company]['FY2025']['Revenue']
            net_income = financial_data[company]['FY2025']['Net_Income']
            npm = (net_income / revenue) * 100
            companies[company] = {'net_income': net_income, 'npm': npm}
        
        sorted_companies = sorted(companies.items(), key=lambda x: x[1]['net_income'], reverse=True)
        
        response = "Profitability Ranking for FY2025 (by Net Income):\n\n"
        for rank, (company, metrics) in enumerate(sorted_companies, 1):
            response += (
                f"{rank}. {company}: ${metrics['net_income']:,.0f}M net income "
                f"(Net Profit Margin: {metrics['npm']:.1f}%)\n"
            )
        
        return response
    
    def get_company_performance(self, company_name):
        """Query 4: Detailed performance metrics for a specific company"""
        if company_name not in financial_data:
            return f"Sorry, I don't have data for {company_name}. Available companies: Microsoft, Apple, Tesla."
        
        company = financial_data[company_name]
        fy2025 = company['FY2025']
        fy2023 = company['FY2023']
        
        revenue_growth = ((fy2025['Revenue'] - fy2023['Revenue']) / fy2023['Revenue']) * 100
        ni_growth = ((fy2025['Net_Income'] - fy2023['Net_Income']) / fy2023['Net_Income']) * 100
        npm = (fy2025['Net_Income'] / fy2025['Revenue']) * 100
        roa = (fy2025['Net_Income'] / fy2025['Total_Assets']) * 100
        
        return (
            f"{company_name} Financial Summary (FY2025):\n"
            f"• Revenue: ${fy2025['Revenue']:,.0f}M (3-year growth: {revenue_growth:+.1f}%)\n"
            f"• Net Income: ${fy2025['Net_Income']:,.0f}M (3-year growth: {ni_growth:+.1f}%)\n"
            f"• Total Assets: ${fy2025['Total_Assets']:,.0f}M\n"
            f"• Operating Cash Flow: ${fy2025['OCF']:,.0f}M\n"
            f"• Net Profit Margin: {npm:.1f}%\n"
            f"• Return on Assets (ROA): {roa:.1f}%"
        )
    
    def get_operating_cash_flow(self):
        """Query 5: Operating cash flow analysis"""
        response = "Operating Cash Flow (OCF) for FY2025:\n\n"
        
        ocf_data = []
        for company in financial_data:
            ocf = financial_data[company]['FY2025']['OCF']
            ocf_data.append((company, ocf))
        
        ocf_data.sort(key=lambda x: x[1], reverse=True)
        total_ocf = sum([ocf for _, ocf in ocf_data])
        
        for company, ocf in ocf_data:
            pct = (ocf / total_ocf) * 100
            response += f"• {company}: ${ocf:,.0f}M ({pct:.1f}% of total)\n"
        
        response += f"\nTotal OCF: ${total_ocf:,.0f}M"
        return response
    
    def match_query(self, user_query):
        """Match user input to predefined queries using fuzzy matching"""
        query_lower = user_query.lower()
        
        # Query mapping with multiple keywords for each
        query_map = {
            'total_revenue': ['total revenue', 'combined revenue', 'all companies revenue', 'overall revenue'],
            'net_income_change': ['net income changed', 'income change', 'how has income', 'income trend'],
            'profitability': ['most profitable', 'profitability', 'highest profit', 'best performing', 'which company profitable'],
            'company_performance': ['microsoft', 'tesla', 'apple', 'company performance', 'detailed performance'],
            'ocf': ['operating cash flow', 'cash flow', 'ocf', 'cash flow analysis']
        }
        
        for query_type, keywords in query_map.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return query_type
        
        return None
    
    def respond(self, user_query):
        """Generate response to user query"""
        self.query_count += 1
        
        # Clean input
        user_query = user_query.strip()
        
        # Match query type
        query_type = self.match_query(user_query)
        
        if query_type == 'total_revenue':
            response = self.get_total_revenue()
        elif query_type == 'net_income_change':
            response = self.get_net_income_change()
        elif query_type == 'profitability':
            response = self.get_profitability_comparison()
        elif query_type == 'company_performance':
            # Extract company name
            company_name = None
            for company in financial_data:
                if company.lower() in user_query.lower():
                    company_name = company
                    break
            if company_name:
                response = self.get_company_performance(company_name)
            else:
                response = "Please specify which company (Microsoft, Apple, or Tesla) you'd like to know about."
        elif query_type == 'ocf':
            response = self.get_operating_cash_flow()
        else:
            response = (
                "Sorry, I can only respond to the following predefined queries:\n"
                "1. What is the total revenue?\n"
                "2. How has net income changed over the last few years?\n"
                "3. Which company is most profitable?\n"
                "4. Tell me about [Company] performance\n"
                "5. What is the operating cash flow?\n\n"
                "Please rephrase your question using these topics."
            )
        
        # Log conversation
        self.conversation_log.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'query': user_query,
            'query_type': query_type,
            'response': response
        })
        
        return response
    
    def get_conversation_log(self):
        """Return conversation log for testing/documentation"""
        return self.conversation_log


def run_interactive_chatbot():
    """Run the chatbot in interactive mode"""
    chatbot = FinancialChatbot()
    
    print("=" * 70)
    print("FINANCIAL ANALYSIS CHATBOT PROTOTYPE")
    print("=" * 70)
    print("\nHello! I'm a financial analysis chatbot. I can provide information")
    print("about Microsoft, Tesla, and Apple's financial data from FY2023-2025.")
    print("\nType 'exit' to quit or 'help' for available queries.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'exit':
            print("\nThank you for using the Financial Chatbot. Goodbye!")
            break
        
        if user_input.lower() == 'help':
            print("\nAvailable queries:")
            print("1. 'What is the total revenue?'")
            print("2. 'How has net income changed?'")
            print("3. 'Which company is most profitable?'")
            print("4. 'Tell me about [Microsoft/Apple/Tesla] performance'")
            print("5. 'What is the operating cash flow?'\n")
            continue
        
        if not user_input:
            continue
        
        response = chatbot.respond(user_input)
        print(f"\nBot: {response}\n")


def run_test_mode():
    """Run predefined test queries for demonstration"""
    chatbot = FinancialChatbot()
    
    test_queries = [
        "What is the total revenue?",
        "How has net income changed over the last year?",
        "Which company is most profitable?",
        "Tell me about Microsoft performance",
        "What is the operating cash flow?",
        "Can you predict tomorrow's stock price?"  # Test unrecognized query
    ]
    
    print("=" * 70)
    print("FINANCIAL CHATBOT - TEST MODE")
    print("=" * 70)
    print(f"\nRunning {len(test_queries)} predefined test queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {query}")
        print(f"{'='*70}")
        response = chatbot.respond(query)
        print(f"Response:\n{response}")
    
    return chatbot


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        chatbot = run_test_mode()
    else:
        run_interactive_chatbot()
