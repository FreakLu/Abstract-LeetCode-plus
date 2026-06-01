from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import LeetCodeProblem
from .serializers import LeetCodeProblemSerializer
from pipeline.llm_client import LeetCodeAgent, create_llm_client, resolve_llm_model, resolve_llm_provider
from pipeline.parse_response_to_csv import extract_table, parse_table_to_xlsx
from django.http import FileResponse, HttpResponseNotFound
import os
from django.conf import settings
from openai import OpenAIError


def download_excel(request):
    file_path = "./data/leetcode_solutions.xlsx"

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, "rb"), as_attachment=True, filename="./data/leetcode_solutions.xlsx")
        return response
    else:
        return HttpResponseNotFound("File not found.")


@api_view(["POST"])
def solve_question_api(request):
    user_input = request.data.get("question")
    response = None

    provider = resolve_llm_provider()
    model_name = resolve_llm_model(provider)

    try:
        llm_client = create_llm_client(provider=provider)
        sys_language = (request.data.get("language") or os.getenv("APP_LANGUAGE", "zh")).lower()
        agent = LeetCodeAgent(client=llm_client, model=model_name, language=sys_language)
        response = agent.generate_solution(user_input)
    except ValueError as e:
        return Response({"error": f"{str(e)}"}, status=400)
    
    except OpenAIError as e:
        error_msg = f"API FAIL[{model_name}]\ndetails: {str(e)}"
        print(f"❌ {error_msg}")
        return Response({"error": error_msg}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": f"service error: {str(e)}"}, status=500)

    print("\nResponse:\n", response)
       
    # if user_input.lower() == "exit":
    #     break
    if response:
        # Extract table and convert to Excel with Cambria font and Markdown conversion
        table_data = extract_table(response)
        if table_data:
            parse_table_to_xlsx(table_data)
        else:
            print("❌ No table found in response!")

        # while True:
        #     followup = input("\nAsk a follow-up (or type 'new' for another problem, 'exit' to quit): ")
        #     if followup.lower() == "new":
        #         break
        #     elif followup.lower() == "exit":
        #         exit()
        #     followup_response = agent.handle_followup(followup)
        #     print("\nAssistant:", followup_response)
        #     if followup_response:
        #         # Extract table and convert to Excel with Cambria font and Markdown conversion
        #         table_data = extract_table(followup_response)
        #         if table_data:
        #             parse_table_to_xlsx(table_data)
        #         else:
        #             print("❌ No table found in response!")

    return Response({"question": user_input, "response": response})
