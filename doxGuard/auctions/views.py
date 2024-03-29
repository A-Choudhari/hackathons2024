import os
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from django.views.decorators import gzip
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from .testing2 import call_func
import requests
#from playsound import playsound
#import io
import easyocr
#import matplotlib.pyplot as plt
#import pydub
import wave
#from pydub.utils import mediainfo
import pyaudio
import speech_recognition as sr
#from better_profanity import profanity
#from google.cloud import speech
import scrubadub
from pydub import AudioSegment, generators
import tempfile
import numpy as np
import cv2
import time
import crim as CommonRegex
from .models import User, Image, Video
from .form import ImageUploadForm, VideoUploadForm
from .camera import VideoRecorder
from moviepy.editor import *
import assemblyai as aai
aai.settings.api_key = "1df1807395744e1fa6282daf48dad05e"


def index(request):
    try:
        video_list = Video.objects.filter(user=request.user)
        video_list = video_list[::-1]
    except:
        video_list = None

    try:
        image_list = Image.objects.filter(user=request.user)
        image_list = image_list[::-1]
    except:
        image_list = None
    return render(request, "auctions/index.html", {"image": image_list, "video": video_list})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def resize_frame(frame, resolution=720, allow_upscale=False):
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    scale_ratio = 1

    if frame_height >= frame_width:
        scale_ratio = resolution / frame_height
    elif frame_width > frame_height:
        scale_ratio = resolution / frame_width

    if scale_ratio > 1 and allow_upscale == False:
        return frame
    elif scale_ratio > 1:
        interpolation_type = cv2.INTER_LINEAR
    elif scale_ratio == 1:
        return frame
    else:
        interpolation_type = cv2.INTER_AREA

    adjusted_width = round(frame_width * scale_ratio)
    adjusted_height = round(frame_height * scale_ratio)

    resized = cv2.resize(frame, (adjusted_width, adjusted_height), interpolation=interpolation_type)
    return resized


def ocr_frame(frame, reader, downscale_fhd=False):
    if downscale_fhd:
        frame = resize_frame(frame, 1080)

    result = reader.readtext(frame)
    return result


def decode_ocr(ocr_result):
    text_list = []
    coordinates = []
    for text in ocr_result:
        top_left = text[0][0]
        bottom_right = text[0][2]

        text_list.append(text[1])
        coordinates.append([top_left, bottom_right])
    return (text_list, np.array(coordinates).astype(int))


def find_pii(decoded_ocr):
    pii_list = []
    pii_coord = []

    non_pii_list = []
    non_pii_coord = []
    for i in range(len(decoded_ocr[0])):
        text, coord = decoded_ocr[0][i], decoded_ocr[1][i]
        print(coord)
        sensitive_data = [CommonRegex.phones(text), CommonRegex.phones_with_exts(text), CommonRegex.links(text),
                          CommonRegex.emails(text),
                          CommonRegex.ipv4s(text), CommonRegex.ipv6s(text), CommonRegex.ips(text),
                          CommonRegex.not_known_ports(text),
                          CommonRegex.credit_cards(text), CommonRegex.visa_cards(text), CommonRegex.master_cards(text),
                          CommonRegex.btc_address(text), CommonRegex.street_addresses(text),
                          CommonRegex.zip_codes(text),
                          CommonRegex.po_boxes(text), CommonRegex.ssn_numbers(text), CommonRegex.md5_hashes(text),
                          CommonRegex.sha1_hashes(text), CommonRegex.sha256_hashes(text), CommonRegex.isbn13s(text),
                          CommonRegex.isbn10s(text), CommonRegex.mac_addresses(text), CommonRegex.iban_numbers(text),
                          CommonRegex.git_repos(text)]

        alt_text = text.replace(" com", ".com")

        sensitive_data2 = [CommonRegex.phones(alt_text), CommonRegex.phones_with_exts(alt_text),
                           CommonRegex.links(alt_text),
                           CommonRegex.emails(alt_text), CommonRegex.ipv4s(alt_text), CommonRegex.ipv6s(alt_text),
                           CommonRegex.ips(alt_text), CommonRegex.not_known_ports(alt_text),
                           CommonRegex.credit_cards(alt_text),
                           CommonRegex.visa_cards(alt_text), CommonRegex.master_cards(alt_text),
                           CommonRegex.btc_address(alt_text),
                           CommonRegex.street_addresses(text), CommonRegex.zip_codes(alt_text),
                           CommonRegex.po_boxes(alt_text),
                           CommonRegex.ssn_numbers(alt_text), CommonRegex.md5_hashes(alt_text),
                           CommonRegex.sha1_hashes(alt_text),
                           CommonRegex.sha256_hashes(alt_text), CommonRegex.isbn13s(alt_text),
                           CommonRegex.isbn10s(alt_text),
                           CommonRegex.mac_addresses(alt_text), CommonRegex.iban_numbers(alt_text),
                           CommonRegex.git_repos(alt_text)]

        pii = False
        for item in sensitive_data:
            if len(item) > 0:
                pii = True
            if pii == True:
                break
        for item in sensitive_data2:
            if len(item) > 0:
                pii = True
            if pii == True:
                break

        if pii:
            pii_list.append(text)

            pii_coord.append(coord)
        elif pii == False:
            non_pii_list.append(text)
            non_pii_coord.append(coord)
    print(pii_coord)
    return (pii_list, np.array(pii_coord), non_pii_list, np.array(non_pii_coord))


def find_faces(frame, face_cascade, profile_cascade):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_coord = face_cascade.detectMultiScale(gray, 1.3)
    profiles_coord = profile_cascade.detectMultiScale(gray, 1.3)
    return faces_coord, profiles_coord


def blur_faces(frame, faces):
    for (x, y, w, h) in faces[0]:
        if y < 2:
            y = 2
        if x < 2:
            x = 2
        if y + h >= frame.shape[0] - 2:
            h = frame.shape[0] - y - 3
        if x + w >= frame.shape[1] - 2:
            w = frame.shape[1] - x - 3
        y -= 2
        h += 2
        x -= 2
        w += 2

        ROI = frame[y:y + h, x:x + w]

        blur = cv2.GaussianBlur(ROI, (299, 299), 0)
        frame[y:y + h, x:x + w] = blur

    for (x, y, w, h) in faces[1]:
        if y < 2:
            y = 2
        if x < 2:
            x = 2
        if y + h >= frame.shape[0] - 2:
            h = frame.shape[0] - y - 3
        if x + w >= frame.shape[1] - 2:
            w = frame.shape[1] - x - 3
        y -= 2
        h += 2
        x -= 2
        w += 2

        ROI = frame[y:y + h, x:x + w]

        blur = cv2.GaussianBlur(ROI, (299, 299), 0)
        frame[y:y + h, x:x + w] = blur
    return frame


def blur_areas(frame, coordinates):
    for top_left, bottom_right in coordinates:
        # print(top_left)
        y1, y2, x1, x2 = round(top_left[1]), round(bottom_right[1]), round(top_left[0]), round(bottom_right[0])

        if y2 - y1 <= 3:
            y1 -= 2
            y2 += 2
        if x2 - x1 <= 3:
            x1 -= 2
            x2 += 2

        if y1 < 0:
            y1 = 0
            y2 += 3
        if x1 < 0:
            x1 = 0
            x2 += 3

        h = y2 - y1
        w = x2 - x2

        ROI = frame[y1:y2, x1:x2]

        blur = cv2.GaussianBlur(ROI, (299, 299), 0)
        frame[y1:y2, x1:x2] = blur
        # frame[y1:y2, x1:x2] = cv2.resize(cv2.resize(ROI, (h//10, w//10), interpolation=cv2.INTER_LINEAR), (h, w), interpolation=cv2.INTER_NEAREST)
    return frame


def image_blur(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user

            image.save()
            image_url = image.image.url
            try:
                blur_face = request.POST["blurFace"]
            except:
                blur_face = ""
            try:
                blur_text = request.POST["blurText"]
            except:
                blur_text = ""
            original_img = cv2.imread("C:\Akshat\python\python projects\doxPrevent\commerce" + image_url)
            #rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
            rgb = original_img
            blurred = rgb
            width, height = rgb.shape[0], rgb.shape[1]
            print("Resolution:", width, height)
            # frame_count = 0
            if blur_text == "on":
                print("Blurring Text")
                reader = easyocr.Reader(['en'])
                ocr_results = ocr_frame(rgb, reader)
                decoded = decode_ocr(ocr_results)
                pii_lists = find_pii(decoded)
                blurred = blur_areas(blurred, pii_lists[1])
            if blur_face == "on":
                print("Blurring Face")
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces_list = find_faces(rgb, face_cascade)
                blurred = blur_faces(blurred, faces_list)
            cv2.imwrite("C:\Akshat\python\python projects\doxPrevent\commerce" + image_url, blurred)
            print("Done")
            time.sleep(10)
            return HttpResponseRedirect(reverse("index"))
        else:
            print(form.errors)
    else:
        form = ImageUploadForm()
        return render(request, 'auctions/image_blur.html', {'form': form})


def blur_audio(file_path, medical_process, medical_condition, blood_type, drug, injury, number_sequence, email_address, date_of_birth, phone_number, social_security, credit_card, date, nationality, event, language, money_amount, person_name, person_age, organization, political_affiliation, occupation, religion, drivers_license, banking_information, profanity):
    redaction_policy = [aai.PIIRedactionPolicy.date_of_birth]
    if medical_process == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.medical_process)
    if medical_condition == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.medical_condition)
    if blood_type == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.blood_type)
    if drug == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.drug)
    if injury == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.injury)
    if number_sequence == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.number_sequence)
    if email_address == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.email_address)
    if date_of_birth == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.date_of_birth)
    if phone_number == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.phone_number)
    if social_security == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.us_social_security_number)
    if credit_card == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.credit_card_cvv)
        redaction_policy.append(aai.PIIRedactionPolicy.credit_card_number)
        redaction_policy.append(aai.PIIRedactionPolicy.credit_card_expiration)
    if date == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.date)
    if nationality == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.nationality)
    if event == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.event)
    if language == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.language)
        redaction_policy.append(aai.PIIRedactionPolicy.money_amount)
    if person_name == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.person_name)
        print("Name")
    if person_age == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.person_age)
    if organization == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.organization)
    if political_affiliation == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.political_affiliation)
    if occupation == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.occupation)
    if religion == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.religion)
    if drivers_license == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.drivers_license)
    if banking_information == "on":
        redaction_policy.append(aai.PIIRedactionPolicy.banking_information)

    if profanity == "on":
        transcript = aai.Transcriber().transcribe(
            file_path,
            config=aai.TranscriptionConfig(
                redact_pii=True,
                redact_pii_audio=True,
                redact_pii_policies=redaction_policy,
                filter_profanity=True
            )
        )
    else:
        transcript = aai.Transcriber().transcribe(
            file_path,
            config=aai.TranscriptionConfig(
                redact_pii=True,
                redact_pii_audio=True,
                redact_pii_policies=redaction_policy,
            )
        )
    redacted_audio_url = transcript.get_redacted_audio_url()
    new_audio = AudioFileClip(redacted_audio_url)
    return new_audio
    # audio has been replaced with redaction
    #video_audio = video_audio.set_audio(new_audio)

    # Save the video with the new audio for the video2.mp4. This saves it locally
    #video_audio.write_videofile(file_path, codec='libx264', audio_codec='aac')
    #return "Transcribing Audio Was Success"


def video_blur(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_form = form.save(commit=False)
            video_form.user = request.user
            video_form.save()
            file_name = "C:\Akshat\python\python projects\doxPrevent\commerce" + video_form.video.url
            try:
                medical_process = request.POST["medical_process"]
            except:
                medical_process = ""
            try:
                medical_condition = request.POST["medical_condition"]
            except:
                medical_condition = ""
            try:
                blood_type = request.POST["blood_type"]
            except:
                blood_type = ""
            try:
                drug = request.POST["drug"]
            except:
                drug = ""
            try:
                injury = request.POST["injury"]
            except:
                injury = ""
            try:
                number_sequence = request.POST["number_sequence"]
            except:
                number_sequence = ""
            try:
                email_address = request.POST["email_address"]
            except:
                email_address = ""
            try:
                date_of_birth = request.POST["date_of_birth"]
            except:
                date_of_birth = ""
            try:
                phone_number = request.POST["phone_number"]
            except:
                phone_number = ""
            try:
                social_security = request.POST["social_security"]
            except:
                social_security = ""
            try:
                phone_number = request.POST["phone_number"]
            except:
                phone_number = ""
            try:
                credit_card = request.POST["credit_card"]
            except:
                credit_card = ""
            try:
                date = request.POST["date"]
            except:
                date = ""
            try:
                nationality = request.POST["nationality"]
            except:
                nationality = ""
            try:
                event = request.POST["event"]
            except:
                event = ""
            try:
                language = request.POST["language"]
            except:
                language = ""
            try:
                money_amount = request.POST["money_amount"]
            except:
                money_amount = ""
            try:
                person_name = request.POST["person_name"]
            except:
                person_name = ""
            try:
                person_age = request.POST["person_age"]
            except:
                person_age = ""
            try:
                organization = request.POST["organization"]
            except:
                organization = ""
            try:
                political_affiliation = request.POST["political_affiliation"]
            except:
                political_affiliation = ""
            try:
                occupation = request.POST["occupation"]
            except:
                occupation = ""
            try:
                religion = request.POST["religion"]
            except:
                religion = ""
            try:
                drivers_license = request.POST["drivers_license"]
            except:
                drivers_license = ""
            try:
                banking_information = request.POST["banking_information"]
            except:
                banking_information = ""
            try:
                profanity = request.POST["profanity"]
            except:
                profanity = ""
            try:
                blur_face = request.POST["blurFace"]
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
            except:
                blur_face = ""
            try:
                blur_text = request.POST["blurText"]
                reader = easyocr.Reader(['en'])
            except:
                blur_text = ""

            #blurred_audio = blur_audio(file_name, medical_process, medical_condition, blood_type, drug, injury, number_sequence, email_address, date_of_birth, phone_number, social_security, credit_card, date, nationality, event, language, money_amount, person_name, person_age, organization, political_affiliation, occupation, religion, drivers_license, banking_information, profanity)
            #
            file_name = file_name.replace("/", f"\\")
            print(file_name)
            #time.sleep(5)
            call_func(file_name)
            #cap = cv2.VideoCapture(file_name)

            #total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            #fps = round(cap.get(cv2.CAP_PROP_FPS))
            #video_width, video_height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            #video_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

            #print("Total Frames:", total_frames)
            #print("FPS:", fps)
            #print("Time (seconds):", video_time)
            #print("Resolution:", video_width, video_height)

            #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            #output = cv2.VideoWriter(file_name, fourcc, fps, (video_width, video_height))

            #frame_count = 0

            # #while cap.isOpened():
            # #    current_time = time.time()
            # #    ret, vid_frame = cap.read()
            # #    if not ret:
            #         print("Can't receive frame. End of video. Exiting...")
            #         break
            #
            #     frame_count += 1
            #     print(f"\nProcessing frame {frame_count} out of {total_frames}")
            #     blurred = vid_frame
            #     if blur_text == "on":
            #         print("Blurring Text")
            #         ocr_results = ocr_frame(vid_frame, reader)
            #         decoded = decode_ocr(ocr_results)
            #         pii_lists = find_pii(decoded)
            #         blurred = blur_areas(blurred, pii_lists[1])
            #     if blur_face == "on":
            #         print("Blurring Face")
            #         faces_list = find_faces(vid_frame, face_cascade, profile_cascade)
            #         blurred = blur_faces(blurred, faces_list)
            #
            #     output.write(blurred)
            #
            #     print("Processed in", time.time() - current_time, "seconds")
            # cap.release()
            # output.release()
            # cv2.destroyAllWindows()
            #final_video = VideoFileClip(file_name)
            #final_clip = final_video.set_audio(blurred_audio)
            #final_clip.write_videofile(file_name)
        return HttpResponseRedirect(reverse("index"))
    else:
        form = VideoUploadForm()
        return render(request, 'auctions/video_blur.html', {'form': form})


def liveCapture_blur(request):
    return render(request, "auctions/testing.html")


@gzip.gzip_page
def stream_capture(request):
    try:
        video_player = VideoRecorder()

        def generate():
            try:
                # Continuously yield frames and audio data
                while True:
                    video_frame = video_player.get_frame()
                    yield (b'--frame\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + video_frame + b'\r\n\r\n')
            except GeneratorExit:
                # Cleanup when generator is closed
                video_player.stop()


        # Return streaming response with frames and audio data
        return StreamingHttpResponse(generate(), content_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        print("Error:", e)
        return HttpResponse("An error occurred during streaming.")


def audio_capture(request):
    # Constants for audio capture
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    total_frames = int(RATE / CHUNK_SIZE * 5)
    # Create an instance of PyAudio
    audio = pyaudio.PyAudio()

    # Open a stream for audio capture
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK_SIZE)

    # Open a stream for audio playback
    output_stream = audio.open(format=FORMAT,
                               channels=CHANNELS,
                               rate=RATE,
                               output=True)
    #client = speech.SpeechClient.from_service_account_json('bellhacks-a402a0a74fbd.json')
    #config = speech.RecognitionConfig(
    #    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    #    sample_rate_hertz=RATE,
    #    language_code="en-us",
    #    profanity_filter=True)
    #streaming_config = speech.StreamingRecognitionConfig(
    #    config=config,
    #    interim_results=True)
    print("Recording and playback started. Press Ctrl+C to stop.")
    #r = sr.Recognizer()
    while True:
        #frames = []
        #if request.get_full_path() != "liveCapture_blur":
        #    break
        # Read audio data from the microphone
        #for i in range(0, int(RATE / CHUNK_SIZE * 3)):
        data = stream.read(CHUNK_SIZE)
            #frames.append(data)
        #audio_data = b''.join(frames)
        #final_audio_data = process_audio(audio_data)
        output_stream.write(data)
            #transcribed_text = transcribe_audio(audio_data, r)
        #print(transcribed_text)
        #if len(transcribed_text) == 0:
            #bleeped_audio_bytes = generate_bleeped_audio("That person is a *****", audio_data)
            #print(bleeped_audio_bytes)
            #output_stream.write(audio_data)
        #else:
        #    modified_text = bleep_sensitive_information(transcribed_text)
        #    bleeped_audio_bytes = generate_bleeped_audio(modified_text, audio_data)
        #    output_stream.write(bleeped_audio_bytes)

    print("Recording and playback stopped.")

    # Close the audio streams
    stream.stop_stream()
    stream.close()
    output_stream.stop_stream()
    output_stream.close()

    # Terminate PyAudio
    audio.terminate()
    return HttpResponse("Finished code")


def process_audio(audio_data):
    with wave.open("input.wav", 'wb') as wav_out:
        # Set the parameters for the output .wav file
        # Write the audio data to the output .wav file
        wav_out.setnchannels(1)
        wav_out.setsampwidth(2)
        wav_out.setframerate(44100)
        wav_out.writeframes(audio_data)
    try:
        transcript = aai.Transcriber().transcribe(
        "input.wav",
            config=aai.TranscriptionConfig(
                redact_pii=True,
                redact_pii_audio=True,
                redact_pii_policies=[aai.PIIRedactionPolicy.credit_card_cvv,
                                     aai.PIIRedactionPolicy.person_name,
                                     aai.PIIRedactionPolicy.credit_card_number,
                                     aai.PIIRedactionPolicy.credit_card_expiration,
                                     aai.PIIRedactionPolicy.us_social_security_number,
                                     aai.PIIRedactionPolicy.drug],
                filter_profanity=True
            )
        )
        redacted_audio_url = transcript.get_redacted_audio_url()
        # #print(redacted_audio_url)
        # print(redacted_audio_url)
        # #print(redacted_audio_url)
        # response = requests.get(redacted_audio_url)
        # redacted_audio_bytes = response.content
        transcript.save_redacted_audio("input.wav")
        with open('input.wav', 'rb') as f:
            wav_bytes = f.read()
        # Save the video with the new audio for the video2.mp4. This saves it locally
        return wav_bytes
    except Exception as e:
        print("Error processing audio:", e)
        return None


def transcribe_audio(audio_byte, r):
    text = ""
    with open('temp_audio.wav', 'wb') as f:
        f.write(audio_byte)
    with sr.AudioFile("temp_audio.wav") as source:
        audio = r.listen(source)

    # Recognize speech using Google Speech Recognition
    try:
        # Recognize speech using Google Speech Recognition
        text = r.recognize_google(audio)
        print(text)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    # Moderate PII in the text
    pii_types = ["NAME", "ADDRESS", "PHONE_NUMBER", "EMAIL_ADDRESS"]
    for pii_type in pii_types:
        text = text.replace(pii_type, "***")
    print(f"beta:{text}")
    return text


def bleep_sensitive_information(transcribed_text):
    # Implement logic to identify and bleep out sensitive information
    # For example, replace sensitive words with beep sounds or silence
    modified_text = scrubadub.clean(transcribed_text)
    return modified_text


def generate_bleeped_audio(transcribed_text, original_audio_segments):
    # Define the duration of silence to represent censored words
    silence_duration = 500  # Duration of silence in milliseconds

    # Create an empty audio segment
    bleeped_audio = AudioSegment.empty()
    beep_duration = silence_duration // 10
    beep = generators.Sine(freq=1000)
    # Iterate through each word in the transcribed text
    for i, word in enumerate(transcribed_text.split()):
        # Replace sensitive words with a bleep sound
        if word == "*":
            # Generate a beep sound
            # Add the bleep sound to the bleeped audio
            bleeped_audio += beep
        else:
            # Add the original audio segment corresponding to the non-sensitive word
            bleeped_audio += original_audio_segments[i]

            # Add silence between words (except for the last word)
            if i < len(transcribed_text.split()) - 1:
                bleeped_audio += AudioSegment.silent(duration=silence_duration)

    # Export the bleeped audio as raw audio data
    return bleeped_audio.raw_data


# ----------------------------------------------------------------------------------------

@csrf_exempt
def stream_data(request):
    if request.method == 'PUT':
        video_hex = request.body
        #final_audio = async_to_sync(stream_audio_blur)(video_hex)
        #print(final_audio)
        #video_string = video_hex.decode('utf-8')
        return JsonResponse({"video": "testing"})
    else:
        return render(request, "auctions/liveCapture_blur.html")


async def stream_audio_blur(video_mp4):
    redaction_policy = [aai.PIIRedactionPolicy.name,aai.PIIRedactionPolicy.banking_information, aai.PIIRedactionPolicy.us_social_security_number, aai.PIIRedactionPolicy.credit_card_expiration, aai.PIIRedactionPolicy.drug, aai.PIIRedactionPolicy.credit_card_number, aai.PIIRedactionPolicy.credit_card_cvv]
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp_file:
        temp_file.write(video_mp4)
        temp_file_path = temp_file.name
    transcript = aai.Transcriber().transcribe(
        temp_file_path,
        config=aai.TranscriptionConfig(
            redact_pii=True,
            redact_pii_audio=True,
            redact_pii_policies=redaction_policy,
            filter_profanity=True,
            )
        )
    redacted_audio_url = transcript.get_redacted_audio_url()
    new_audio = AudioFileClip(redacted_audio_url)
    # audio has been replaced with redaction
    video_audio = VideoFileClip(video_mp4)
    video_audio = video_audio.set_audio(new_audio)
    return video_audio
