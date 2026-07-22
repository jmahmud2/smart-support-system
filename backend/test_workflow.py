"""
Test script for the customer support workflow.
Runs sample messages through the AI pipeline.
"""

from app.workflow.workflow import process_message

# Test messages covering different intents and sentiments
test_messages = [
    "I ordered a MacBook Pro and it arrived with a scratched screen. I need a replacement immediately.",
    "When will my iPhone be delivered? It's been 3 days without shipping updates.",
    "Do you have student discounts? I'm a college student looking to buy a laptop.",
    "I love the Le Creuset Dutch oven. Do you offer gift wrapping?"
]

def main():
    """Run the workflow tests and display results."""
    print("\n" + "=" * 70)
    print("CUSTOMER SUPPORT WORKFLOW TEST")
    print("=" * 70)

    for idx, message in enumerate(test_messages, 1):
        print(f"\n[{idx}] MESSAGE:")
        print(f"    {message}")
        print("-" * 70)

        # Process through the workflow
        result = process_message(message)

        # Display results
        print(f"    Intent:     {result.get('intent')}")
        print(f"    Sentiment:  {result.get('sentiment')}")
        print(f"    Priority:   {result.get('priority')}")
        print(f"    Escalate:   {result.get('escalate')}")
        print(f"    Reasoning:  {result.get('reasoning')}")
        print(f"\n    Response:")
        print(f"    {result.get('response')}")
        print("-" * 70)

if __name__ == "__main__":
    main()