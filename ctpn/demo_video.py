from __future__ import print_function

import glob
import os
import shutil
import sys

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.python.platform import gfile

sys.path.append(os.getcwd())
from lib.fast_rcnn.config import cfg, cfg_from_file
from lib.fast_rcnn.test import _get_blobs
from lib.text_connector.detectors import TextDetector
from lib.text_connector.text_connect_cfg import Config as TextLineCfg
from lib.rpn_msr.proposal_layer_tf import proposal_layer


def resize_im(im, scale, max_scale=None):
    f = float(scale) / min(im.shape[0], im.shape[1])
    if max_scale != None and f * max(im.shape[0], im.shape[1]) > max_scale:
        f = float(max_scale) / max(im.shape[0], im.shape[1])
    return cv2.resize(im, None, None, fx=f, fy=f, interpolation=cv2.INTER_LINEAR), f


def draw_boxes(img, video_name, frameNum, boxes, scale):
    base_name = video_name.split('/')[-1]
    with open('data/results/' + 'res_{0}_{1}.txt'.format(base_name.split('.')[0], frameNum), 'w') as f:
        for box in boxes:
            if np.linalg.norm(box[0] - box[1]) < 5 or np.linalg.norm(box[3] - box[0]) < 5:
                continue
            if box[8] >= 0.9:
                color = (0, 255, 0)
            elif box[8] >= 0.8:
                color = (255, 0, 0)
            cv2.line(img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), color, 2)
            cv2.line(img, (int(box[0]), int(box[1])), (int(box[4]), int(box[5])), color, 2)
            cv2.line(img, (int(box[6]), int(box[7])), (int(box[2]), int(box[3])), color, 2)
            cv2.line(img, (int(box[4]), int(box[5])), (int(box[6]), int(box[7])), color, 2)

            min_x = min(int(box[0] / scale), int(box[2] / scale), int(box[4] / scale), int(box[6] / scale))
            min_y = min(int(box[1] / scale), int(box[3] / scale), int(box[5] / scale), int(box[7] / scale))
            max_x = max(int(box[0] / scale), int(box[2] / scale), int(box[4] / scale), int(box[6] / scale))
            max_y = max(int(box[1] / scale), int(box[3] / scale), int(box[5] / scale), int(box[7] / scale))

            line = ','.join([str(min_x), str(min_y), str(max_x), str(max_y)]) + '\r\n'
            f.write(line)

    img = cv2.resize(img, None, None, fx=1.0 / scale, fy=1.0 / scale, interpolation=cv2.INTER_LINEAR)
    cv2.imwrite(os.path.join("data/results", "{0}_{1}.jpg".format(base_name.split('.')[0], frameNum)), img)
    return img


###
# 切割出含有文字的图片区域
###
def cropped_pic(img, video_name, frameNum):
    base_name = video_name.split('/')[-1]

    # 对每一帧分别创建一个文件夹存放截取出的字幕
    if os.path.exists("data/results/cropped_pic_{0}_{1}".format(base_name.split('.')[0], frameNum)):
        shutil.rmtree("data/results/cropped_pic_{0}_{1}".format(base_name.split('.')[0], frameNum))
    os.makedirs("data/results/cropped_pic_{0}_{1}".format(base_name.split('.')[0], frameNum))

    file = open('data/results/' + 'res_{0}_{1}.txt'.format(base_name.split('.')[0], frameNum), 'r')
    file_name = base_name.split('.')[0]
    i = 0
    for line in file:
        point = line.split(',')
        cropped = img[int(point[1]):int(point[3]), int(point[0]):int(point[2])]
        cv2.imwrite(os.path.join("data/results/cropped_pic_{0}_{1}".format(base_name.split('.')[0], frameNum),
                                 "{0}_{1}_{2}.jpg".format(file_name, frameNum, str(i))), cropped)
        i = i + 1


if __name__ == '__main__':

    if os.path.exists("data/results/"):
        shutil.rmtree("data/results/")
    os.makedirs("data/results/")

    cfg_from_file('text.yml')

    # init session
    config = tf.ConfigProto(allow_soft_placement=True)
    sess = tf.Session(config=config)
    with gfile.FastGFile('data/ctpn.pb', 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        sess.graph.as_default()
        tf.import_graph_def(graph_def, name='')
    sess.run(tf.global_variables_initializer())

    input_img = sess.graph.get_tensor_by_name('Placeholder:0')
    output_cls_prob = sess.graph.get_tensor_by_name('Reshape_2:0')
    output_box_pred = sess.graph.get_tensor_by_name('rpn_bbox_pred/Reshape_1:0')

    vd_names = glob.glob(os.path.join(cfg.DATA_DIR, 'video', '*.mp4')) + \
               glob.glob(os.path.join(cfg.DATA_DIR, 'video', '*.flv')) + \
               glob.glob(os.path.join(cfg.DATA_DIR, 'video', '*.avi'))

    for vd_name in vd_names:
        videoCapture = cv2.VideoCapture(vd_name)
        success, frame = videoCapture.read()
        frameNum = 0

        # 创建视频容器
        videoWriter = cv2.VideoWriter("data/results/{}_drawnBoxes.mp4".format(vd_name.split('/')[-1].split('.')[0]),
                                      cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                      videoCapture.get(cv2.CAP_PROP_FPS),
                                      (int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                       int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        while (success):
            frameNum = frameNum + 1
            # cv2.imshow('', frame)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            tmp = frame
            img, scale = resize_im(frame, scale=TextLineCfg.SCALE, max_scale=TextLineCfg.MAX_SCALE)
            blobs, im_scales = _get_blobs(img, None)
            if cfg.TEST.HAS_RPN:
                im_blob = blobs['data']
                blobs['im_info'] = np.array(
                    [[im_blob.shape[1], im_blob.shape[2], im_scales[0]]],
                    dtype=np.float32)
            cls_prob, box_pred = sess.run([output_cls_prob, output_box_pred], feed_dict={input_img: blobs['data']})
            rois, _ = proposal_layer(cls_prob, box_pred, blobs['im_info'], 'TEST', anchor_scales=cfg.ANCHOR_SCALES)

            scores = rois[:, 0]
            boxes = rois[:, 1:5] / im_scales[0]
            textdetector = TextDetector()
            boxes = textdetector.detect(boxes, scores[:, np.newaxis], img.shape[:2])  ###TODO：可选择感兴趣区域
            drawn = draw_boxes(img, vd_name, frameNum, boxes, scale)

            # 将加框后图片拼接成视频
            videoWriter.write(drawn)

            cropped_pic(tmp, vd_name, frameNum)
            success, frame = videoCapture.read()
