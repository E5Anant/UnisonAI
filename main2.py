import datetime
from unisonai import Agent
from unisonai import Clan
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType
from unisonai.tools.websearch import WebSearchTool
from unisonai.llms import Gemini
from unisonai import config

config.set_api_key("gemini", "Your API Key")

# Enhanced Custom Tool 1: Time Tool with validation
class TimeTool(BaseTool):
    """Enhanced time tool with proper field validation."""
    
    def __init__(self):
        self.name = "time_tool"
        self.description = "Get current date and time in specified format with timezone support."
        self.params = [
            Field(
                name="format",
                description="DateTime format string (e.g., '%Y-%m-%d %H:%M:%S')",
                field_type=ToolParameterType.STRING,
                default_value="%Y-%m-%d %H:%M:%S",
                required=False
            )
        ]
        super().__init__()

    def _run(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get current time in specified format."""
        return datetime.datetime.now().strftime(format)

# Enhanced Custom Tool 2: Weather Tool with proper validation
class WeatherTool(BaseTool):
    """Enhanced weather tool with type validation."""
    
    def __init__(self):
        self.name = "weather_tool"
        self.description = "Get simulated weather information for Indian cities."
        self.params = [
            Field(
                name="city",
                description="Name of the Indian city to check weather for",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="include_forecast",
                description="Include 3-day forecast",
                field_type=ToolParameterType.BOOLEAN,
                default_value=False,
                required=False
            )
        ]
        super().__init__()

    def _run(self, city: str, include_forecast: bool = False) -> str:
        """Get weather information for the specified city."""
        # Simulated weather data for major Indian cities
        weather_data = {
            "delhi": {"temp": 32, "condition": "Hot and sunny", "humidity": 65},
            "mumbai": {"temp": 28, "condition": "Humid and cloudy", "humidity": 80},
            "bangalore": {"temp": 24, "condition": "Pleasant and cool", "humidity": 60},
            "kolkata": {"temp": 30, "condition": "Warm and humid", "humidity": 75},
            "chennai": {"temp": 35, "condition": "Hot and humid", "humidity": 85},
            "jaipur": {"temp": 38, "condition": "Very hot and dry", "humidity": 40},
            "agra": {"temp": 36, "condition": "Hot and dry", "humidity": 45},
            "varanasi": {"temp": 34, "condition": "Hot and humid", "humidity": 70},
            "goa": {"temp": 26, "condition": "Warm and breezy", "humidity": 75}
        }
        
        city_lower = city.lower()
        if city_lower in weather_data:
            data = weather_data[city_lower]
            result = f"Current weather in {city.title()}: {data['temp']}°C, {data['condition']}, Humidity: {data['humidity']}%"
            
            if include_forecast:
                result += f"\n3-Day Forecast: Similar conditions expected with temperatures ranging {data['temp']-2}°C to {data['temp']+3}°C"
        else:
            result = f"Weather data not available for {city}. Estimated: 30°C, partly cloudy (simulated)."
        
        return result

# Enhanced Custom Tool 3: Budget Tracker with comprehensive validation
class BudgetTrackerTool(BaseTool):
    """Enhanced budget tracking with detailed expense categorization."""
    
    def __init__(self):
        self.name = "budget_tracker"
        self.description = "Track expenses and manage trip budget with detailed reporting."
        self.params = [
            Field(
                name="action",
                description="Action to perform: 'initialize', 'add_expense', 'get_balance', 'get_report'",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="amount",
                description="Amount in INR (required for initialize/add_expense)",
                field_type=ToolParameterType.FLOAT,
                default_value=0.0,
                required=False
            ),
            Field(
                name="category",
                description="Expense category: food, transport, accommodation, activities, miscellaneous",
                field_type=ToolParameterType.STRING,
                default_value="miscellaneous",
                required=False
            ),
            Field(
                name="description",
                description="Detailed description of the expense",
                field_type=ToolParameterType.STRING,
                default_value="",
                required=False
            )
        ]
        self.total_budget = 0
        self.expenses = []
        super().__init__()

    def _run(self, action: str, amount: float = 0.0, category: str = "miscellaneous", description: str = "") -> str:
        """Execute budget management actions with enhanced reporting."""
        if action == "initialize":
            self.total_budget = amount
            self.expenses = []
            return f"Budget initialized with ₹{amount:,.2f}"
        
        elif action == "add_expense":
            if amount <= 0:
                return "Error: Expense amount must be positive"
            
            expense = {
                "amount": amount,
                "category": category,
                "description": description,
                "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.expenses.append(expense)
            spent = sum(exp["amount"] for exp in self.expenses)
            remaining = self.total_budget - spent
            
            status = "✅ Within budget" if remaining >= 0 else "⚠️ Over budget"
            return f"Added expense: ₹{amount:,.2f} for {category}\nRemaining budget: ₹{remaining:,.2f} ({status})"
        
        elif action == "get_balance":
            spent = sum(exp["amount"] for exp in self.expenses)
            remaining = self.total_budget - spent
            percentage_used = (spent / self.total_budget * 100) if self.total_budget > 0 else 0
            
            return f"Budget Balance:\nTotal: ₹{self.total_budget:,.2f}\nSpent: ₹{spent:,.2f} ({percentage_used:.1f}%)\nRemaining: ₹{remaining:,.2f}"
        
        elif action == "get_report":
            spent = sum(exp["amount"] for exp in self.expenses)
            remaining = self.total_budget - spent
            
            # Category breakdown
            breakdown = {}
            for exp in self.expenses:
                cat = exp["category"]
                breakdown[cat] = breakdown.get(cat, 0) + exp["amount"]
            
            report = f"📊 Detailed Budget Report\n"
            report += f"Total Budget: ₹{self.total_budget:,.2f}\n"
            report += f"Total Spent: ₹{spent:,.2f}\n"
            report += f"Remaining: ₹{remaining:,.2f}\n\n"
            report += "📈 Category Breakdown:\n"
            
            for cat, amt in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
                percentage = (amt / spent * 100) if spent > 0 else 0
                report += f"  • {cat.title()}: ₹{amt:,.2f} ({percentage:.1f}%)\n"
            
            report += f"\n📝 Recent Transactions ({len(self.expenses)} total):\n"
            for exp in self.expenses[-5:]:  # Show last 5 transactions
                report += f"  • {exp['timestamp']}: ₹{exp['amount']:,.2f} - {exp['category']} ({exp['description']})\n"
            
            return report
        
        else:
            return f"Error: Invalid action '{action}'. Valid actions: initialize, add_expense, get_balance, get_report"

# Enhanced Transport Cost Tool with detailed validation
class TransportCostTool(BaseTool):
    """Enhanced transport cost estimation with detailed route planning."""
    
    def __init__(self):
        self.name = "transport_cost_estimator"
        self.description = "Estimate transportation costs between Indian cities with multiple transport options."
        self.params = [
            Field(
                name="from_city",
                description="Starting city name",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="to_city",
                description="Destination city name",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="transport_mode",
                description="Mode of transport: train, bus, flight, taxi",
                field_type=ToolParameterType.STRING,
                default_value="train",
                required=False
            ),
            Field(
                name="get_all_options",
                description="Get costs for all transport modes",
                field_type=ToolParameterType.BOOLEAN,
                default_value=False,
                required=False
            )
        ]
        super().__init__()

    def _run(self, from_city: str, to_city: str, transport_mode: str = "train", get_all_options: bool = False) -> str:
        """Calculate transport costs with enhanced route information."""
        # Simulated cost matrix (base costs in INR)
        base_costs = {
            "train": {"base": 150, "per_km": 0.5},
            "bus": {"base": 100, "per_km": 0.8},
            "flight": {"base": 3000, "per_km": 2.0},
            "taxi": {"base": 500, "per_km": 12.0}
        }
        
        # Simulated distances between major cities (in km)
        distances = {
            ("delhi", "agra"): 230,
            ("delhi", "jaipur"): 280,
            ("agra", "jaipur"): 240,
            ("delhi", "mumbai"): 1150,
            ("mumbai", "goa"): 460,
            ("delhi", "varanasi"): 750,
            ("mumbai", "bangalore"): 840,
            ("bangalore", "chennai"): 290
        }
        
        from_lower = from_city.lower()
        to_lower = to_city.lower()
        
        # Find distance (check both directions)
        distance = distances.get((from_lower, to_lower)) or distances.get((to_lower, from_lower)) or 500
        
        if get_all_options:
            result = f"🚗 Transport Options from {from_city.title()} to {to_city.title()} ({distance} km):\n\n"
            for mode, cost_data in base_costs.items():
                total_cost = cost_data["base"] + (distance * cost_data["per_km"])
                duration = self._estimate_duration(distance, mode)
                result += f"• {mode.title()}: ₹{total_cost:,.0f} (~{duration})\n"
        else:
            if transport_mode not in base_costs:
                return f"Error: Invalid transport mode '{transport_mode}'. Valid options: train, bus, flight, taxi"
            
            cost_data = base_costs[transport_mode]
            total_cost = cost_data["base"] + (distance * cost_data["per_km"])
            duration = self._estimate_duration(distance, transport_mode)
            
            result = f"🚗 {transport_mode.title()} from {from_city.title()} to {to_city.title()}:\n"
            result += f"Distance: {distance} km\n"
            result += f"Estimated Cost: ₹{total_cost:,.0f}\n"
            result += f"Duration: ~{duration}"
        
        return result
    
    def _estimate_duration(self, distance: int, mode: str) -> str:
        """Estimate travel duration based on distance and transport mode."""
        speeds = {"train": 60, "bus": 45, "flight": 600, "taxi": 50}  # km/h
        hours = distance / speeds.get(mode, 50)
        
        if hours < 1:
            return f"{int(hours * 60)} minutes"
        elif hours < 24:
            return f"{hours:.1f} hours"
        else:
            days = int(hours // 24)
            remaining_hours = int(hours % 24)
            return f"{days} day(s) {remaining_hours} hours"

# Enhanced Agents with improved tools and descriptions
time_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Time Keeper",
    description="Advanced time management specialist with flexible formatting capabilities",
    task="Provide accurate time information and scheduling support for the trip",
    tools=[TimeTool()]
)

web_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Specialist",
    description="Expert web researcher for travel information and real-time data",
    task="Gather comprehensive travel information, cultural activities, and current pricing",
    tools=[WebSearchTool()]
)

weather_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Weather Forecaster",
    description="Weather specialist providing detailed forecasts and travel advisories",
    task="Provide accurate weather information and recommendations for each destination",
    tools=[WeatherTool()]
)

budget_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Financial Manager",
    description="Expert budget tracker with detailed expense categorization and reporting",
    task="Monitor all expenses, provide detailed budget reports, and ensure financial goals are met",
    tools=[BudgetTrackerTool()]
)

transport_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Transport Coordinator",
    description="Transportation expert with comprehensive route planning and cost analysis",
    task="Plan optimal transportation routes with detailed cost comparisons and timing",
    tools=[TransportCostTool()]
)

food_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Culinary Guide",
    description="Food specialist focusing on local cuisine and budget-friendly dining options",
    task="Recommend authentic local foods, restaurants, and budget-friendly meal planning",
    tools=[WebSearchTool()]
)

planner_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Master Trip Planner",
    description="Expert trip coordinator specializing in comprehensive itinerary planning and team management",
    task="Orchestrate all agents to create detailed, cohesive trip plans with precise budget management",
    tools=[BudgetTrackerTool()]  # Planner also has budget oversight
)

# Create the Enhanced Clan with improved coordination
clan = Clan(
    manager=planner_agent,
    members=[time_agent, web_agent, weather_agent, budget_agent, transport_agent, food_agent, planner_agent],
    shared_instruction="""You are part of an elite Trip Planning team with enhanced tools and capabilities. 

IMPORTANT INSTRUCTIONS:
- Use the enhanced tool system with proper parameter validation
- Budget tracking: Initialize with ₹10,000 and track all expenses by category
- Weather: Check weather conditions for each destination with forecast options
- Transport: Compare multiple transport options and get detailed cost breakdowns
- Research: Use web search for real-time information about destinations, costs, and activities
- Time: Use flexible time formatting for scheduling and planning

Work collaboratively to create a comprehensive, detailed 7-day trip plan. Each agent should:
1. Use their specialized tools effectively with proper parameter validation
2. Provide detailed, actionable recommendations
3. Coordinate with other agents to ensure consistency
4. Focus on budget optimization while maintaining quality experiences
5. Include specific venue names, addresses, and contact information where possible""",
    goal="Create a detailed 7-day trip itinerary across India (Delhi → Agra → Jaipur → Varanasi → Mumbai → Goa → Delhi) with a strict budget of ₹10,000. Include day-by-day breakdowns with: transportation costs and options, accommodation recommendations, food options with specific restaurant names, weather considerations, cultural activities with timings and costs, and real-time budget tracking.",
    history_folder="enhanced_trip_history",
    clan_name="Enhanced Ultimate Trip Expert Clan",
    output_file="enhanced_trip_plan.txt"
)

# Unleash the Enhanced Clan
print("🚀 Launching Enhanced Trip Planning Clan with advanced tools...")
print("📊 Enhanced features: Type validation, detailed budget tracking, weather forecasts, transport comparisons")
clan.unleash()