import pyttsx3
import speech_recognition as SR


#Text To Speech
def System_Speak(Text) : 

 
 #Initialization
 Engine = pyttsx3.init(driverName = "sapi5" , debug = False)

 #Voice
 Voices = Engine.getProperty("voices")
 Engine.setProperty("Voice" , Voices[0].id)
 #Volume
 Engine.setProperty("volume" , 1)
 #Rate
 Engine.setProperty("rate" , 200)
 
 #Set & Speak
 Engine.say(Text)
 Engine.runAndWait()

#Speech To Text
def System_Recognize() : 
 

 #MicroPhone(Activate) >> Recognizer(InPut) > Text(OutPut)

 print("Listening , Sir")
 System_Speak("Listening , Sir")
 #MicroPhone(Activate)
 with SR.Microphone() as Source : 
  SR.Recognizer().adjust_for_ambient_noise(Source)
  SR.Recognizer.energy_threshold = 700
  SR.Recognizer.dynamic_energy_threshold = True
  
  try : 
   #Recognize(InPut)
   Audio = SR.Recognizer().listen(Source , timeout = 10)
   #Text(OutPut)
   Text = SR.Recognizer().recognize_google(Audio , language = "en-IN")
  except Exception as E :  
   print(f"Audio Error : {E}")
   System_Speak(f"Audio Error : {E}")
  else : 
   print(f"Sir , You Said : {Text.title()}")
   System_Speak(f"Sir , You Said : {Text.title()}")
   

while True : 
 System_Recognize()