from google.cloud import texttospeech
import playsound
client = texttospeech.TextToSpeechClient()

voice_eng = texttospeech.VoiceSelectionParams(
    language_code='en-US',
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
voice_kor = texttospeech.VoiceSelectionParams(
    language_code='ko-KR',
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16)

def exchange_eng(input_text):
    synthesis_input = texttospeech.SynthesisInput(text=input_text)
    response = client.synthesize_speech(input=synthesis_input,voice=voice_eng,audio_config=audio_config)
    return response.audio_content

def exchange_kor(input_text):
    synthesis_input = texttospeech.SynthesisInput(text=input_text)
    response = client.synthesize_speech(input=synthesis_input,voice=voice_kor,audio_config=audio_config)
    return response.audio_content

def makeFile(textList, *adder):
    if len(adder) == 0: adder = 'output'
    else : adder = adder[0]

    for i, text in enumerate(textList):
        if type(text) == type(list()):
            #with open('tts_output/'+str(adder)+str(i)+'_eng.mp3','wb') as out:
            #    out.write(exchange_kor(text[0]))
            with open('tts_output/'+str(adder)+str(i)+'_kor.wav','wb') as out:
                out.write(exchange_kor(text[0]))
        else:
            with open('tts_output/' + str(adder) + str(i) + '.wav', 'wb') as out:
                out.write(exchange_kor(text))

#location = ['안녕','in a clothing store','at a construction site']
#makeFile(location,'location')
behavior = [['텅텅 빈 인생에 몸서리친 어제의 나는 오늘의 나와 동명이인',]]
makeFile(behavior,'test')