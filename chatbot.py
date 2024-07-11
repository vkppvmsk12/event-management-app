from openai import OpenAI

openai = OpenAI(api_key='sk-proj-t6Jy7pX6uIrSrj5kjeWBT3BlbkFJmfYsITsKF6Rbi7E2LEy1')

def get_response(prompt):
    message={'role':'user','content':prompt}
    response=openai.chat.completions.create(
        messages=[message],
        model='gpt-3.5-turbo',
        temperature=0.7
    )

    return response.choices[0].message.content

if __name__ == '__main__':
    while True:
        user_input=input('User: ')
        if user_input in ['exit','quit']: print('Bye.'); break
        response=get_response(user_input)
        print('Chatbot:', response)