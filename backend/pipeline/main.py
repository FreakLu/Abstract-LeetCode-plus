from pipeline.llm_client import LeetCodeAgent
from pipeline.parse_response_to_csv import extract_table, parse_table_to_xlsx

def solve_questions():
    agent = LeetCodeAgent(model="gpt-4")

    while True:
        user_input = input("\nAsk a question about a LeetCode problem (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        response = agent.stream_solution(user_input)
        print("\nResponse:\n", response)
        if response:
            # Extract table and convert to Excel with Cambria font and Markdown conversion
            table_data = extract_table(response)
            if table_data:
                parse_table_to_xlsx(table_data)
            else:
                print("❌ No table found in response!")

        while True:
            followup = input("\nAsk a follow-up (or type 'new' for another problem, 'exit' to quit): ")
            if followup.lower() == "new":
                break
            elif followup.lower() == "exit":
                exit()
            followup_response = agent.handle_followup(followup)
            print("\nAssistant:", followup_response)
            if followup_response:
                # Extract table and convert to Excel with Cambria font and Markdown conversion
                table_data = extract_table(followup_response)
                if table_data:
                    parse_table_to_xlsx(table_data)
                else:
                    print("❌ No table found in response!")


solve_questions()