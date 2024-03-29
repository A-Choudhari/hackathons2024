import easyocr
import cv2
import numpy as np
import time
import crim as CommonRegex
import moviepy.editor as mpe

# from google.colab.patches import cv2_imshow


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


def ocr_frame(frame, downscale_fhd=False):
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

    return (pii_list, np.array(pii_coord), non_pii_list, np.array(non_pii_coord))


def find_faces(frame, face_cascade, profile_cascade):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_coord = face_cascade.detectMultiScale(gray, 1.3, 5)
    profiles_coord = profile_cascade.detectMultiScale(gray, 1.3)
    return (faces_coord, profiles_coord)


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

        ROI = frame[y1:y2, x1:x2]

        blur = cv2.GaussianBlur(ROI, (299, 299), 0)
        frame[y1:y2, x1:x2] = blur

    return frame


def call_func(file_name):

    start_time = time.time()
    reader = easyocr.Reader(['en'])

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
    cap = mpe.VideoFileClip(file_name)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output = cv2.VideoWriter(file_name, fourcc, 30, (cap.w, cap.h))

    display = False

    frame_count = 0

    for vid_frame in cap.iter_frames():

        frame_count += 1
        vid_frame =  cv2.cvtColor(vid_frame, cv2.COLOR_BGR2RGB)
        print(f"\nProcessing frame {frame_count} out of")

        faces_list = find_faces(vid_frame, face_cascade, profile_cascade)
        blurred = blur_faces(vid_frame, faces_list)


        output.write(blurred)

        #print("Processed in", time.time() - current_time, "seconds")

    end_time = time.time()
    print(end_time - start_time, "seconds")

    #cap.release()
    output.release()

    print("Done")

