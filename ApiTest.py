# python——通过电脑摄像头采集图像实现利用百度api实现人脸检测
# https://blog.csdn.net/Cell_KEY/article/details/88669353
import base64
import cv2
import requests
import time
import json
import os
import math
import matplotlib.pyplot as plt

APP_ID = ''  # 百度人脸的appID,下面的参数同
API_KEY = ''
SECRET_KEY = ''


apiURL = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
accesstokenURL = "https://aip.baidubce.com/oauth/2.0/token"

apikey = ""
secretkey = ""

imge_path = os.path.dirname(os.path.abspath(__file__)) + '\\img.jpg'
avi_path = os.path.dirname(os.path.abspath(__file__)) + '\\output.avi'
faceinfo_type = ['face_type', 'face_shape', 'gender',
                 'emotion', 'age', 'glasses', 'beauty', 'location']


def camer_open():
    cap = cv2.VideoCapture(0)  # 默认的摄像头
    return cap


def camer_close(fun_cap):
    fun_cap.release()
    cv2.destroyAllWindows()


fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(avi_path, fourcc, 20.0, (640, 480))


def make_photo(capp):
    """使用opencv拍照"""
    access_token = get_AcessToken(apikey, secretkey)
    while True:

        ret_cap, frame = capp.read()
        time.sleep(0.2)
        if ret_cap:
            print("read ok")
            color = (0, 0, 0)
            img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            cv2.imwrite(imge_path, img_gray)
            image_base64 = imgeTobase64()
            ret, info_list = get_face_response(access_token, image_base64)
            print
            ret
            if ret == 0:

                w = int(info_list[faceinfo_type.index('location')]) + 100
                h = int(info_list[faceinfo_type.index('location') + 1]) + 100
                y = int(info_list[faceinfo_type.index('location') + 2]) - 80
                x = int(info_list[faceinfo_type.index('location') + 3]) - 50
                fun_str = []

                fun_str.append(
                    'age:' + str(info_list[faceinfo_type.index('age')]))
                fun_str.append(
                    'emotion:' + info_list[faceinfo_type.index('emotion')])
                fun_str.append(
                    'beauty:' + str(info_list[faceinfo_type.index('beauty')]))
                fun_str.append(
                    'gender:' + info_list[faceinfo_type.index('gender')])

                y1 = int(y + (h / 2))
                dy = 20
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                for i in range(len(fun_str)):
                    y2 = y1 + i * dy
                    cv2.putText(
                        frame, fun_str[i], (x + w + 20, y2), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)
            # draw_0 = cv2.rectangle(image, (2*w, 2*h), (3*w, 3*h), (255, 0, 0), 2)

            # frame = cv2.flip(frame,0)
            # write the flipped frame
            out.write(frame)
            cv2.imshow("capture", frame)  # 弹窗口
            if cv2.waitKey(1) & 0xFF == ord('q'):
                camer_close(capp)
                break
        else:
            break


def get_AcessToken(fun_apikey, fun_secretkey):
    # print fun_apikey,fun_secretkey
    data = {
        "grant_type": "client_credentials",
        "client_id": fun_apikey,
        "client_secret": fun_secretkey
    }
    r = requests.post(accesstokenURL, data)
    # print (r.text)
    t = json.loads(r.text)

    # print t['access_token']
    at = t['access_token']
    return at


def response_parse(result_res):
    r = json.loads(result_res)
    print
    r
    ret = r['error_msg']
    if r['error_code'] != 0:
        print
        ret
        return r['error_code'], 0

    result_parse = []
    face_list = r['result']['face_list'][0]
    # print face_list
    print
    len(face_list)
    for i in range(len(faceinfo_type)):
        if (faceinfo_type[i] == 'age') or (faceinfo_type[i] == 'beauty'):
            result_parse.append(face_list[faceinfo_type[i]])
        elif faceinfo_type[i] == 'location':
            result_parse.append(face_list[faceinfo_type[i]]['width'])
            result_parse.append(face_list[faceinfo_type[i]]['height'])
            result_parse.append(face_list[faceinfo_type[i]]['top'])
            result_parse.append(face_list[faceinfo_type[i]]['left'])

        else:
            result_parse.append(face_list[faceinfo_type[i]]['type'])

    print("result:%s \nface_type:%s\nface_shape:%s\ngender:%s\nemotion:%s\nglasses:%s\nage:%d\nbeauty:%d\n\
	       " % (ret, result_parse[faceinfo_type.index('face_type')], result_parse[faceinfo_type.index('face_shape')],
             result_parse[faceinfo_type.index(
                 'gender')], result_parse[faceinfo_type.index('emotion')],
             result_parse[faceinfo_type.index(
                 'glasses')], result_parse[faceinfo_type.index('age')],
             result_parse[faceinfo_type.index('beauty')]))
    return 0, result_parse


def get_face_response(fun_access_token, base64_imge):
    header = {
        "Content-Type": "application/json"
    }
    data = {
        "image": base64_imge,
        "image_type": "BASE64",
        "face_field": "faceshape,facetype,age,gender,glasses,eye_status,emotion,race,beauty"
    }
    url = apiURL + "?access_token=" + fun_access_token
    r = requests.post(url, json.dumps(data), header)
    # print (r.url)
    # print (r.text)
    ret = response_parse(r.text)
    return ret


def imgeTobase64():
    with open(imge_path, 'rb') as f:
        base64_data = base64.b64encode(f.read())
    s = base64_data.decode()
    # print("data:imge/jpeg;base64,%s"%s)
    s = s[s.find(',') + 1:]
    # print s
    return s


def main():
    print('face identification starting')
    # print access_token
    cap = camer_open()
    make_photo(cap)


if __name__ == '__main__':
    main()
