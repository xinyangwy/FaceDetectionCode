# 百度api实现实时摄像头人脸识别
# https://blog.csdn.net/cjava_python/article/details/118964372
import cv2
from aip import AipFace
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import threading
import numpy as np


def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype("simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def frame2base64(frame):
    img = Image.fromarray(frame)  # 将每一帧转为Image
    output_buffer = BytesIO()  # 创建一个BytesIO
    img.save(output_buffer, format='JPEG')  # 写入output_buffer
    byte_data = output_buffer.getvalue()  # 在内存中读取
    base64_data = base64.b64encode(byte_data)  # 转为BASE64
    return base64_data  # 转码成功 返回base64编码


def process(image, ls):
    """ 调用人脸检测 """
    """ 如果有可选参数 """

    # 换成自己的appid
    APP_ID = ''
    API_KEY = ''
    SECRET_KEY = ''
    groupIdList = 'admin'
    imageType = 'BASE64'
    base64 = frame2base64(image)
    # base64 = str(base64)
    base64 = str(base64, 'UTF-8')
    options = {}
    options["face_field"] = "age,gender,emotion"
    options["max_face_num"] = 10
    options["face_type"] = "LIVE"
    options["match_threshold"] = 0
    # options["liveness_control"] = "NORMAL"
    client = AipFace(APP_ID, API_KEY, SECRET_KEY)
    face_data = client.detect(base64, imageType, options)
    print(face_data)
    user_result = {}
    user_attribute = {}
    user_type = '访客'
    is_user = False
    if face_data['error_msg'] == 'SUCCESS':
        i = face_data['result']['face_list'][0]
        if i['face_probability'] > 0.8:
            is_user = True
            age = str(i['age'])
            gender = str('男' if i['gender']['type'] == 'male' else '女')
            emotion = str(i['emotion']['type'])
            if emotion == 'disgust':
                emotion = 'angry'
            elif emotion == 'pouty':
                emotion = 'sad'
            elif emotion == 'grimace':
                emotion = 'happy'
            else:
                emotion = 'neutral'
            # shibie
            # groupIdList = 'group_1'
            """ 如果有可选参数 """
            options = {}
            options["max_face_num"] = 10
            options["match_threshold"] = 0
            options["quality_control"] = "LOW"
            options["liveness_control"] = "LOW"
            options["max_user_num"] = 7
            # json1 = client.multiSearch(base64, imageType, groupIdList, options)
            json1 = client.multiSearch(base64, imageType, groupIdList, options)
            print(json1)
            face_num = face_data['result']['face_num']
            for i in range(face_num):
                x = max(int(face_data['result']
                        ['face_list'][i]['location']['left']), 0)
                y = max(int(face_data['result']
                        ['face_list'][i]['location']['top']), 0)
                width = int(face_data['result']
                            ['face_list'][i]['location']['width'])
                height = int(face_data['result']
                             ['face_list'][i]['location']['height'])
                cv2.rectangle(image, (x, y), (x + width,
                              y + height), (0, 0, 255), 2)
                if json1['error_msg'] == 'SUCCESS':
                    user_attribute = []
                    user_type = '员工'
                    user_result = {
                        'is_user': is_user, 'user_type': user_type, 'user_attribute': user_attribute}

                    if json1['result']['face_list'][0]['user_list'][i]['score'] > 70:
                        print(json1['result']['face_list']
                              [0]['user_list'][i]['user_id'])
                        image = cv2ImgAddText(image, json1['result']['face_list'][0]['user_list'][i]['user_id'],
                                              max(x - 20, 0), max(y - 20, 0), (255, 255, 255), 20)
                    else:

                        cv2.putText(image,
                                    f"{str(face_data['result']['face_list'][i]['age'])} {face_data['result']['face_list'][i]['gender']['type']}",
                                    (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
                    ls.append(image)

        else:
            user_result = {'is_user': is_user}
            print(user_result)
            # return user_result
    else:
        user_result = {'is_user': is_user}
        print(user_result)
        # return user_result
    # return user_result


def main():
    video_capture = cv2.VideoCapture(0)
    # video_capture = cv2.VideoCapture('1.avi')
    # video_capture.set(30, 30)
    # video_capture.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
    # video_capture.set(3, 640)  # Width of the frames in the video stream.
    # video_capture.set(4, 480)  # Height of the frames in the video stream.
    # video_capture.set(5, 30) # Frame rate.
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 宽度
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 高度
    video_capture.set(cv2.CAP_PROP_FPS, 30)  # 帧数
    video_capture.set(cv2.CAP_PROP_BRIGHTNESS, 1)  # 亮度 1
    video_capture.set(cv2.CAP_PROP_CONTRAST, 40)  # 对比度 40
    video_capture.set(cv2.CAP_PROP_SATURATION, 50)  # 饱和度 50
    video_capture.set(cv2.CAP_PROP_HUE, 50)  # 色调 50
    video_capture.set(cv2.CAP_PROP_EXPOSURE, 50)  # 曝光 50

    while True:
        ls = []
        ret, frame = video_capture.read()
        t = threading.Thread(target=process, args=(frame, ls))
        t.start()
        t.join()
        frame = ls[0] if ls else frame
        cv2.imshow('wx', frame)
        if cv2.waitKey(1) & 0xFF == ord('Q'):
            cv2.destroyAllWindows()
            video_capture.release()
            break


if __name__ == "__main__":
    main()
