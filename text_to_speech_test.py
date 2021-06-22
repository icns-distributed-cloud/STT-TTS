from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()

voice_eng = texttospeech.VoiceSelectionParams(
    language_code='en-US',
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
voice_kor = texttospeech.VoiceSelectionParams(
    language_code='ko-KR',
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3)

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
            with open('tts_output/'+str(adder)+str(i)+'_eng.mp3','wb') as out:
                out.write(exchange_eng(text[0]))
            with open('tts_output/'+str(adder)+str(i)+'_kor.mp3','wb') as out:
                out.write(exchange_eng(text[1]))
        else:
            with open('tts_output/' + str(adder) + str(i) + '.mp3', 'wb') as out:
                out.write(exchange_eng(text))

location = ['안녕','in a clothing store','at a construction site']
makeFile(location,'location')
behavior = [['he is sitting arm in arm','안녕하세요 안녕 안녕']]
makeFile(behavior,'behavior')