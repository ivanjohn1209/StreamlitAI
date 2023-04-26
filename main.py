# import streamlit as st
# import websockets
# import asyncio
# import base64
# import json
# from configure import auth_key
# import openai
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore
# import pyaudio
#
# # Initialize Firebase app with a unique app name
# if not firebase_admin._apps:
#     cred = credentials.Certificate("./python-c83ba-firebase-adminsdk-ukztc-fd2c6c28a1.json")
#     firebase_admin.initialize_app(cred)  # Provide a unique app name here
#
# # Get Firestore client
# db = firestore.client()
#
# # Set OpenAI API key
# openai.api_key = "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"
#
# # Firebase config
# config = {
#     "apiKey": "YOUR_API_KEY",
#     "authDomain": "python-c83ba.firebaseapp.com",
#     "projectId": "python-c83ba",
#     "storageBucket": "python-c83ba.appspot.com",
#     "messagingSenderId": "894337970722",
#     "appId": "1:894337970722:web:d2905089db8a13d9a1907b",
#     "measurementId": "G-SJ2MR1K3N1"
# }
#
# if 'text' not in st.session_state:
# 	st.session_state['text'] = 'Listening...'
# 	st.session_state['run'] = False
# 	st.session_state['show'] = False
# 	st.session_state['responses'] = []
#
# FRAMES_PER_BUFFER = 3200
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 16000
# p = pyaudio.PyAudio()
#
# # starts recording
# stream = p.open(
#    format=FORMAT,
#    channels=CHANNELS,
#    rate=RATE,
#    input=True,
#    frames_per_buffer=FRAMES_PER_BUFFER
# )
#
# def start_listening():
# 	st.session_state['run'] = True
#
# def stop_listening():
# 	st.session_state['run'] = False
#
# def addMSG():
# 	st.session_state['responses'].append("trt")
#
# st.title('Get real-time transcription')
#
# start, stop = st.columns(2)
# start.button('Start listening', on_click=start_listening)
#
# stop.button('Stop listening', on_click=stop_listening)
# stop.button('Add MSG', on_click=addMSG)
#
# URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"
#
# st.write('Here are the responses:')
# for response in st.session_state['responses']:
# 	st.write(response)
# async def send_receive():
#
# 	print(f'Connecting websocket to url {URL}')
#
# 	async with websockets.connect(
# 		URL,
# 		extra_headers=(("Authorization", auth_key),),
# 		ping_interval=5,
# 		ping_timeout=20
# 	) as _ws:
#
# 		r = await asyncio.sleep(0.1)
# 		print("Receiving SessionBegins ...")
#
# 		session_begins = await _ws.recv()
# 		print(session_begins)
# 		print("Sending messages ...")
#
#
# 		async def send():
# 			while st.session_state['run']:
# 				try:
# 					data = stream.read(FRAMES_PER_BUFFER)
# 					data = base64.b64encode(data).decode("utf-8")
# 					json_data = json.dumps({"audio_data":str(data)})
# 					r = await _ws.send(json_data)
#
# 				except websockets.exceptions.ConnectionClosedError as e:
# 					print(e)
# 					assert e.code == 4008
# 					break
#
# 				except Exception as e:
# 					print(e)
# 					assert False, "Not a websocket 4008 error"
#
# 				r = await asyncio.sleep(0.01)
#
#
# 		async def receive():
# 			while st.session_state['run']:
# 				try:
# 					result_str = await _ws.recv()
# 					result = json.loads(result_str)['text']
#
# 					if json.loads(result_str)['message_type'] == 'FinalTranscript':
# 						response = openai.Completion.create(
# 							engine="text-davinci-003",
# 							prompt=result,
# 							max_tokens=1024,
#                             n=1,
#                             stop=None,
#                             temperature=0.7,
# 						)
# 						data = {
# 							"question":  result,
# 							"aiMessage": response.choices[0].text
# 						}
# 						db.collection("chats").add(data)
# 						addMSG()
# 						st.session_state['text'] = response.choices[0].text
# 						st.write(response.choices[0].text)
#
# 				except websockets.exceptions.ConnectionClosedError as e:
# 					print(e)
# 					assert e.code == 4008
# 					break
#
# 				except Exception as e:
# 					print(e)
# 					assert False, "Not a websocket 4008 error"
#
# 		send_result, receive_result = await asyncio.gather(send(), receive())
#
# asyncio.run(send_receive())

import streamlit as st
import websockets
import asyncio
import base64
import json
from configure import auth_key,open_ai_key
import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pyaudio
import pandas as pd

if not firebase_admin._apps:
    cred = credentials.Certificate("./python-c83ba-firebase-adminsdk-ukztc-fd2c6c28a1.json")
    firebase_admin.initialize_app(cred)  # Provide a unique app name here

# Get Firestore client
db = firestore.client()

# Set OpenAI API key
openai.api_key = open_ai_key;

if 'text' not in st.session_state:
    st.session_state['text'] = 'Listening...'
    st.session_state['run'] = False
    st.session_state['responses'] = [];

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

# starts recording
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
)


def start_listening():
    st.session_state['run'] = True


def stop_listening():
    st.session_state['run'] = False

st.title('Get real-time transcription')

start, stop = st.columns(2)
start.button('Start listening', on_click=start_listening)

stop_btn=stop.button('Stop listening', on_click=stop_listening)
st.write('Here are the responses:')
chat_ref = db.collection("chats")
query = chat_ref.order_by('created_date', direction=firestore.Query.DESCENDING)
docs = query.get()

data = []
for doc in docs:
    doc_data = doc.to_dict()
    aiMessage = doc_data.get("aiMessage")
    question = doc_data.get("question")
    data.append({ "Question": question, "Message": aiMessage})

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(data)

# Display the DataFrame as a table in Streamlit
st.table(df)

URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

async def send_receive():
    print(f'Connecting websocket to url ${URL}')

    async with websockets.connect(
            URL,
            extra_headers=(("Authorization", auth_key),),
            ping_interval=5,
            ping_timeout=20
    ) as _ws:

        r = await asyncio.sleep(0.1)
        print("Receiving SessionBegins ...")

        session_begins = await _ws.recv()
        print(session_begins)
        print("Sending messages ...")

        async def send():
            while st.session_state['run']:
                try:
                    data = stream.read(FRAMES_PER_BUFFER)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data": str(data)})
                    r = await _ws.send(json_data)

                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break

                except Exception as e:
                    print(e)
                    assert False, "Not a websocket 4008 error"

                r = await asyncio.sleep(0.01)

        async def receive():
            while st.session_state['run']:
                try:
                    result_str = await _ws.recv()
                    result = json.loads(result_str)['text']

                    if json.loads(result_str)['message_type'] == 'FinalTranscript':
                        print(result)
                        st.session_state['text'] = result
                        st.markdown("Transcription: " + st.session_state['text'])
                        if(result):
                            response = openai.Completion.create(
								engine="text-davinci-003",
								prompt=result,
								max_tokens=1024,
								n=1,
								stop=None,
								temperature=0.7,
                        	)
                            data = {
                            	"question":  result,
                            	"aiMessage": response.choices[0].text,
								"created_date": firestore.SERVER_TIMESTAMP
                        	}
                            db.collection("chats").add(data)
                            stop_listening()

                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break

                except Exception as e:
                    print(e)
                    assert False, "Not a websocket 4008 error"

        send_result, receive_result = await asyncio.gather(send(), receive())


asyncio.run(send_receive())
