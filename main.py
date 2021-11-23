from __future__ import division

import re
import sys

from google.cloud import speech

import pyaudio
from six.moves import queue

import requests
import json

RATE = 44100
CHUNK = int(RATE / 10)

words = []

class MicrophoneStream(object):
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

def listen_print_loop(responses):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            num_chars_printed = 0
            continue

        res = requests.get("http://localhost:8000/accounts/check/")
        check = json.loads(res.text)
        if check['check'] == False:
            break

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)

            line = transcript + overwrite_chars
            line = line.split(' ')
            words.append(line)

            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0


def main():
    language_code = "ko-KR"

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)
        
        listen_print_loop(responses)
        

if __name__ == "__main__":
    res = requests.get("http://localhost:8000/accounts/check/")
    check = json.loads(res.text)
    while not check['check']:
        res = requests.get("http://localhost:8000/accounts/check/")
        check = json.loads(res.text)
        
    while check['check']:
        main()
        res = requests.get("http://localhost:8000/accounts/check/")
        check = json.loads(res.text)

    result = sum(words, [])
    print(result)

    yok = []
    f = open('TEST.txt','r',encoding='utf-8') # txt파일은 욕설 단어 종류가 담긴 데이터 오픈소스
    for line in f:
        line = line.split(',')
    
    for i in line:
        if i in result:
            yok.append(
                i
            )

    print(yok)
    print(len(yok), "번 욕을 하셨습니다.")
