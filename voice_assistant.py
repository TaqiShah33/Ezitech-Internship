import os
import time
import speech_recognition as sr
from gtts import gTTS
from groq import Groq

# 1. Configuration & Setup (Using Free Groq API)
os.getenv("GROQ_API_KEY")


def capture_voice_input():
  """Capture audio input via microphone and convert to text using STT"""
  recognizer = sr.Recognizer()
  recognizer.energy_threshold = 300
  recognizer.dynamic_energy_threshold = True

  with sr.Microphone() as source:
    print("\n[LISTENING...] Speak clearly into your microphone.")
    recognizer.adjust_for_ambient_noise(source, duration=2)
    try:
      audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)
      print("[PROCESSING STT] Converting speech to text...")
      text = recognizer.recognize_google(audio)
      print(f'User Said: "{text}"')
      return text
    except sr.WaitTimeoutError:
      print("[ERROR] No speech detected within timeout.")
      return None
    except sr.UnknownValueError:
      print("[ERROR] Could not understand the audio clearly. Speak louder.")
      return None
    except sr.RequestError as e:
      print(f"[ERROR] Could not request results from STT service; {e}")
      return None


def get_llm_response(prompt_text):
  """Send processed text to the free Groq LLM API and retrieve the response"""
  if not prompt_text:
    return "I didn't catch that. Could you please repeat?"

  try:
    print("[PROCESSING LLM] Generating intelligent response...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful, concise AI voice assistant. Keep"
                    " responses short and conversational."
                ),
            },
            {"role": "user", "content": prompt_text},
        ],
        max_tokens=150,
    )
    reply = response.choices[0].message.content.strip()
    print(f'AI Response: "{reply}"')
    return reply
  except Exception as e:
    print(f"[API ERROR] Failed to connect to Groq LLM: {e}")
    return "Sorry, please check your Groq API key and network connection."


def text_to_speech_output(text_response):
  """Convert AI text response into speech and play it back"""
  try:
    print("[PROCESSING TTS] Converting response to speech...")
    tts = gTTS(text=text_response, lang="en", slow=False)
    audio_file = "response.mp3"
    tts.save(audio_file)

    if os.name == "nt":  # Windows
      os.system(f"start {audio_file}")
    elif os.name == "posix":  # macOS / Linux
      os.system(
          f"afplay {audio_file}"
          if "darwin" in os.sys.platform
          else f"mpg123 {audio_file}"
      )
  except Exception as e:
    print(f"[TTS ERROR] Could not play audio: {e}")


# --- System Integration & Continuous Interaction Loop ---
if __name__ == "__main__":
  print("==================================================")
  print("   AI VOICE ASSISTANT SYSTEM INITIALIZED (FREE)")
  print("==================================================")
  print("Say 'exit', 'quit', or 'stop' anytime to end the conversation.\n")

  while True:
    user_text = capture_voice_input()

    if user_text:
      if user_text.lower() in ["exit", "stop", "quit"]:
        farewell = "Goodbye! Have a great day."
        print(farewell)
        text_to_speech_output(farewell)
        break

      ai_reply = get_llm_response(user_text)
      text_to_speech_output(ai_reply)

    print("-" * 50)
    time.sleep(1)