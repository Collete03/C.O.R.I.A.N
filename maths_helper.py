import openai
import os

if not os.getenv("OPENAI_API_KEY"):
    print("API key not found environment!")
    print("API key loaded successfully.")
def calculate_with_llm(math_question):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a calculator. Only give the number."},
            {"role": "user", "content": f"Calculate: {math_question}"}
        ]
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    with open("questions.txt", "r") as f:
        questions = f.readlines()

    for q in questions:
        q = q.strip()
        if q:
            print(f"Question: {q}")
            answer = calculate_with_llm(q)
            print(f"Answer: {answer}")
            print("-" * 30)