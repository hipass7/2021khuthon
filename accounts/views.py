from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from accounts.forms import SignupForm, ProfileForm
from django.contrib.auth.views import LoginView, logout_then_login
from django.contrib.auth import login as auth_login
import pyaudio
import wave
import time
import requests
from backend import settings

login = LoginView.as_view(template_name="accounts/login_form.html")

# def login(request):
#     if request.method == 'POST':
#         form = LoginForm (request.POST)

def logout(request):
    messages.success(request, '로그아웃되었습니다.')
    return logout_then_login(request)


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            signed_user = form.save()
            auth_login(request, signed_user)
            messages.success(request, "회원가입 성공")
            next_url = request.GET.get('next', '/')
            return redirect(next_url)

    else:
        form = SignupForm()

    return render(request, 'accounts/signup_form.html', {
        'form': form,
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "프로필을 수정/저장했습니다.")
            return redirect("profile_edit")

    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile_edit_form.html", {
        "form": form,
    })


@login_required
def start(request):
    messages.success(request, "녹음을 시작했습니다.")
    redirect_url = request.META.get("HTTP_REFERER", "root")
    user = request.user
    user.check = True
    user.save()


    return redirect(redirect_url)



@login_required
def end(request):
    messages.success(request, "녹음을 끝냅니다.")
    redirect_url = request.META.get("HTTP_REFERER", "root")
    user = request.user
    user.check = False
    user.save()

    return redirect(redirect_url)


def check(request):
    user = request.user
    requirements = dict()
    requirements['check'] = user.check
    return JsonResponse(requirements)


def test():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 10
    WAVE_OUTPUT_FILENAME = "file.wav"
    audio = pyaudio.PyAudio()

    # start Recording

    stream = audio.open(format=pyaudio.paInt16,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=2,
                        frames_per_buffer=CHUNK)

    print("recording...")

    frames = []

    while (1):
        data = stream.read(CHUNK)
        frames.append(data)

        result = requests.get("https:localhost:8000/accounts/check/")

        yield data


    print("finished recording")

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

