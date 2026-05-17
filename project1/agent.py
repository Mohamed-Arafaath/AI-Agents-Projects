import os
from datetime import datetime

class SimpleWeatherAgent:
    def __init__(self):
        self.name = "Weather Assistant"
        self.created_at = datetime.now()

    def get_response(self, query):
        """Generate a response based on the user query"""
        responses = {
            "weather": "It's sunny today with a high of 25°C",
            "temperature": "The current temperature is 25°C",
            "forecast": "Expect sunny weather with clear skies",
            "default": "I'm your weather assistant. Ask me about weather, temperature, or forecast."
        }

        # Simple keyword matching for responses
        query_lower = query.lower()
        for key in responses:
            if key in query_lower:
                return responses[key]
        return responses["default"]

def main():
    agent = SimpleWeatherAgent()
    print(f"Hello! I'm {agent.name}")
    while True:
        user_input = input("Ask me about weather: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        response = agent.get_response(user_input)
        print(response)

if __name__ == "__main__":
    main()