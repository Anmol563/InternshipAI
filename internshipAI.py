import os
import requests
import textwrap

 from colorama import init, Fore, Style
  init(autoreset=True)

   class Fore:
        CYAN = ''
        GREEN = ''
        WHITE = ''

    class Style:
        BRIGHT = ''


def call_gemini_api(prompt):

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(Fore.RED + "Error: GEMINI_API_KEY environment variable not set.")
        return None

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(api_url, json=payload, headers={
                                 'Content-Type': 'application/json'})
        response.raise_for_status()
        result = response.json()
        return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error calling the API: {e}")
        return None


def display_recommendations(text):

    print("\n" + Fore.CYAN + "="*60)
    print(Style.BRIGHT + Fore.CYAN + "        YOUR PERSONALIZED RECOMMENDATIONS")
    print("="*60 + "\n")

    if not text:
        print(Fore.RED + "Could not retrieve recommendations.")
        return

    recommendations = text.split('---')

    for rec in recommendations:
        rec = rec.strip()
        if not rec:
            continue

        try:
            title_part, reason_part = rec.split('REASON:')
            title = title_part.replace('TITLE:', '').strip()
            reason = reason_part.strip()

            print(Style.BRIGHT + Fore.WHITE + f"=> {title}")

            wrapped_reason = textwrap.fill(
                reason, width=80, initial_indent='   ', subsequent_indent='   ')
            print(Fore.GREEN + wrapped_reason)
            print(Fore.CYAN + "-" * 30 + "\n")
        except ValueError:

            print(Style.BRIGHT + Fore.WHITE + rec)


def display_follow_up(answer):

    print("\n" + Style.BRIGHT + Fore.CYAN + "=> AI Assistant:")
    wrapped_answer = textwrap.fill(answer, width=80)
    print(Fore.WHITE + wrapped_answer)


def main():

    print(Style.BRIGHT + Fore.CYAN + "--- AI Internship Recommender ---")
    skills = input(
        Fore.WHITE + "=> Enter Your Skills (e.g., Python, Data Analysis): ")
    interests = input(
        Fore.WHITE + "=> Enter Your Interests (e.g., Healthcare, AI/ML): ")

    if not skills or not interests:
        print(Fore.RED + "\nPlease enter both skills and interests.")
        return

    initial_prompt = f"""
        Based on an intern with skills in '{skills}' and interests in '{interests}', recommend 3 suitable projects.
        For each recommendation, provide:
        1. A title starting with 'TITLE:'.
        2. A detailed reason starting with 'REASON:'.
        Separate each full recommendation with '---'.
    """

    print("\n" + Fore.CYAN + "=> Getting initial recommendations...")
    recommendations_text = call_gemini_api(initial_prompt)

    if recommendations_text:
        display_recommendations(recommendations_text)

    # Conversational Loop
    while True:
        print("\n" + Fore.CYAN + "-"*60)
        question = input(
            Fore.WHITE + "Do you have any follow-up questions? (Type 'exit' to quit)\n▶ You: ")

        if question.lower() in ['exit', 'quit', 'no']:
            print(Fore.CYAN + "\nHappy to help. Good luck!")
            break

        follow_up_prompt = f"""
            Context: An intern has skills in '{skills}' and interests in '{interests}'. You already provided some recommendations.
            Based on this, answer the following question concisely: "{question}"
        """

        print("\n" + Fore.CYAN + "=> Thinking...")
        answer = call_gemini_api(follow_up_prompt)

        if answer:
            display_follow_up(answer)


if __name__ == "__main__":
    main()
