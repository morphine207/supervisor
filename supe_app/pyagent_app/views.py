from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# Include the ChatGPT class definition as previously provided

import openai

class ChatGPT:
    def __init__(self, api_key, chatbot):
        self.api_key = api_key  # Set the API key
        self.chatbot = chatbot  # Set the chatbot prompt
        self.conversation = []  # Initialize the conversation history

    def chat(self, user_input):
        # Add the user's input to the conversation history
        self.conversation.append({"role": "user", "content": user_input})

        # Get the chatbot's response
        response = self.chatgpt_with_retry(self.conversation, self.chatbot, user_input)

        # Add the chatbot's response to the conversation history
        self.conversation.append({"role": "assistant", "content": response})
        return response

    def chatgpt(self, conversation, chatbot, user_input, temperature=0.75, frequency_penalty=0.2, presence_penalty=0):
        # Set the API key for OpenAI
        openai.api_key = self.api_key

        # Prepare the input messages for the API call
        messages_input = conversation.copy()
        prompt = [{"role": "system", "content": chatbot}]
        messages_input.insert(0, prompt[0])

        # Call the OpenAI API to get a response
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the GPT-3.5-turbo model
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            messages=messages_input)

        # Extract the chat response from the API response
        chat_response = completion['choices'][0]['message']['content']
        return chat_response

    def chatgpt_with_retry(self, conversation, chatbot, user_input, temperature=0.75, frequency_penalty=0.2, presence_penalty=0, retries=3):
        # Retry the chatgpt function if there's an exception
        for i in range(retries):
            try:
                return self.chatgpt(conversation, chatbot, user_input, temperature, frequency_penalty, presence_penalty)
            except Exception as e:
                if i < retries - 1:
                    print(f"Error in chatgpt attempt {i + 1}: {e}. Retrying...")
                else:
                    print(f"Error in chatgpt attempt {i + 1}: {e}. No more retries.")
        return None



def index(request):
    return render(request, "index.html")

@csrf_exempt
def chat(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        api_key = request.POST.get("api_key")
        chatbot1_prompt = request.POST.get("chatbot1_prompt")
        chatbot2_prompt = request.POST.get("chatbot2_prompt")
        
        if not all([user_input, api_key, chatbot1_prompt, chatbot2_prompt]):
            return JsonResponse({"error": "Missing input parameters"}, status=400)

        chatbot1 = ChatGPT(api_key, chatbot1_prompt)
        chatbot2 = ChatGPT(api_key, chatbot2_prompt)

        chatbot1_response = chatbot1.chat(user_input)
        chatbot2_response = chatbot2.chat(chatbot1_response)

        return JsonResponse({"response1": chatbot1_response, "response2": chatbot2_response})

    return render(request, "index.html")
