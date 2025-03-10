from __future__ import annotations
from typing import List
import sys
import multiprocessing
import pytesseract
import cv2
import copy

from . import constants
from . import utils
from .models import PredictedFrame, PredictedSubtitle
from .opencv_adapter import Capture


class Frame:
    left_x: int
    top_y: int
    right_x: int
    bottom_y: int

class Video:
    path: str
    lang: str
    box: (int, int, int, int)
    num_frames: int
    fps: float
    height: int
    width: int
    verbose: bool
    num_frames_to_process: int

    pred_frames: List[PredictedFrame]
    pred_subs: List[PredictedSubtitle]

    def __init__(self, path: str):
        self.path = path
        with Capture(path) as v:
            self.num_frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = v.get(cv2.CAP_PROP_FPS)
            self.height = int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.width = int(v.get(cv2.CAP_PROP_FRAME_WIDTH))

    def run_ocr(self, lang: str, time_start: str, time_end: str,
                conf_threshold: int, box = 2, frame_skip: int = 0, 
                brightness_threshold = None,
                verbose: bool = False) -> None:
        self.lang = lang
        self.box = box
        self.verbose = verbose
        self.frame_skip = frame_skip
        self.brightness_threshold = brightness_threshold
        if verbose:
            print("starting OCR")

        start_frame = utils.get_frame_index(time_start, self.fps) if time_start else 0
        end_frame = utils.get_frame_index(time_end, self.fps) if time_end else self.num_frames

        if end_frame < start_frame:
            raise ValueError('time_start is later than time_end')
        self.num_frames_to_process = end_frame - start_frame

        # get frames from start_frame to end_frame
        with Capture(self.path) as v, multiprocessing.Pool() as pool:
            v.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            frames = (v.read()[1] for x in range(self.num_frames_to_process))
            frames_plus_index = zip(range(1, self.num_frames_to_process + 1), frames)

            # perform ocr to frames in parallel
            it_ocr = pool.imap(self._image_to_data, frames_plus_index, chunksize=10)
            self.pred_frames = [
                None if data is None else PredictedFrame(i + start_frame, data, conf_threshold)
                for i, data in enumerate(it_ocr)
            ]
            

            # we simulate the skipped frames by simply multiplicating the ones we did not skip
            for i in range(1, len(self.pred_frames)):
                if self.pred_frames[i] == None:
                    cp = copy.copy(self.pred_frames[i - 1])
                    cp.index = i
                    self.pred_frames[i] = cp


    def _image_to_data(self, zipped) -> str:
        num = zipped[0]
        img = zipped[1]
        if img is None:
            print(f"no image data given for frame {num} of {self.num_frames_to_process}")
            return None
        if self.frame_skip > 0 and (num % self.frame_skip) != 1:
            print(f"skipping frame {num} of {self.num_frames_to_process} (frameskip {self.frame_skip} modulo: {num % self.frame_skip})")
            return None

        if self.verbose:
            print(f"processing frame {num} of {self.num_frames_to_process}")
        if isinstance(self.box, Frame):
            img = img[self.box.top_y:self.box.bottom_y, self.box.left_x:self.box.right_x]
        else:
            img = img[self.height // self.box:, :]

        if self.brightness_threshold:
            img = cv2.bitwise_and(img, img, mask=cv2.inRange(img, (self.brightness_threshold, self.brightness_threshold, self.brightness_threshold), (255, 255, 255)))

        config = '--tessdata-dir "{}"'.format(constants.TESSDATA_DIR)
        r = None
        try:
            r = pytesseract.image_to_data(img, lang=self.lang, config=config)
        except Exception as e:
            sys.exit('{}: {}'.format(e.__class__.__name__, e))
        if self.verbose:
            print(r)
        return r

    def get_subtitles(self, sim_threshold: int) -> str:
        self._generate_subtitles(sim_threshold)
        return ''.join(
            '{}\n{} --> {}\n{}\n\n'.format(
                i,
                utils.get_srt_timestamp(sub.index_start, self.fps),
                utils.get_srt_timestamp(sub.index_end, self.fps),
                sub.text)
            for i, sub in enumerate(self.pred_subs))

    def _generate_subtitles(self, sim_threshold: int) -> None:
        self.pred_subs = []

        if self.pred_frames is None:
            raise AttributeError(
                'Please call self.run_ocr() first to perform ocr on frames')

        # divide ocr of frames into subtitle paragraphs using sliding window
        WIN_BOUND = int(self.fps // 2)  # 1/2 sec sliding window boundary
        bound = WIN_BOUND
        i = 0
        j = 1
        while j < len(self.pred_frames):
            fi, fj = self.pred_frames[i], self.pred_frames[j]

            if fi.is_similar_to(fj):
                bound = WIN_BOUND
            elif bound > 0:
                bound -= 1
            else:
                # divide subtitle paragraphs
                para_new = j - WIN_BOUND
                self._append_sub(PredictedSubtitle(
                    self.pred_frames[i:para_new], sim_threshold))
                i = para_new
                j = i
                bound = WIN_BOUND

            j += 1

        # also handle the last remaining frames
        if i < len(self.pred_frames) - 1:
            self._append_sub(PredictedSubtitle(
                self.pred_frames[i:], sim_threshold))

    def _append_sub(self, sub: PredictedSubtitle) -> None:
        if len(sub.text) == 0:
            return
        if self.verbose:
            print(f"predicted subtitle: {sub.text}")

        # merge new sub to the last subs if they are similar
        while self.pred_subs and sub.is_similar_to(self.pred_subs[-1]):
            ls = self.pred_subs[-1]
            del self.pred_subs[-1]
            sub = PredictedSubtitle(ls.frames + sub.frames, sub.sim_threshold)

        self.pred_subs.append(sub)
