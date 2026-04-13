language = 'pt'

# 1. Gravação de Áudio com Python e JS
from IPython.display import Audio, display, Javascript
from google.colab import output
from base64 import b64decode

RECORD = """
const sleep = time => new Promise(resolve => setTimeout(resolve,time))
const b2text = blob => new Promise(resolve => {
  const reader = new FileReader()
  reader.onloadend = e => resolve(e.srcElement.result)
  reader.readAsDataURL(blob)
})
var record = time => new Promise(async resolve => {
  stream = await navigator.mediaDevices.getUserMedia({audio:true})
  recorder = new MediaRecorder(stream)
  chunks = []
  recorder.ondataavailable = e => chunks.push(e.data)
  recorder.start()
  await sleep(time)
  recorder.onstop = async () => {
    blob = new Blob(chunks)
    text = await b2text(blob)
    resolve(text)
  }
  recorder.stop()
})
"""

def record(sec=5):
  js_code = f"""
(function() {{
  {RECORD}
  return record({sec * 1000});
}})();
"""
  js_result = output.eval_js(js_code)
  audio = b64decode(js_result.split(',')[1])
  file_name = 'request_audio.wav'
  with open(file_name, 'wb') as f:
    f.write(audio)
  return f'/content/{file_name}'


record_file = record()
display(Audio(record_file, autoplay=True))

# 2. Reconhecimento de Fala com Whisper(OpenAI)

!pip install git+https://github.com/openai/whisper.git -q

import whisper

model = whisper.load_model('small')
result = model.transcribe(record_file, fp16 = False, language=language)
transcription = result
print(transcription)

# 3. Integração com API do ChatGPT

!pip install openai

import openai

# Initialize the OpenAI client with the API key
client = openai.OpenAI(api_key="api_key")

response = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [{"role":"user","content":transcription['text']}]
)

chatgpt_response = response.choices[0].message.content
print(chatgpt_response)

# 4. Sintetizando a Resposta do ChatGPT com Voz(gTTS)

from gtts import gTTS

gtts_object = gTTS(text=chatgpt_response, lang=language, slow=False)
response_audio = "content/response_audio.wav"
gtts_object;save(response_audio)
display(Audio(response_audio, autoplay=True))

