from . import utils
from .video import Video


def get_subtitles(
        video_path: str, lang='eng', time_start='0:00', time_end='',
        conf_threshold=65, sim_threshold=90, box=2, frame_skip=0, verbose=False) -> str:
    utils.download_lang_data(lang, verbose)

    v = Video(video_path)
    v.run_ocr(lang, time_start, time_end, conf_threshold, box, frame_skip, verbose)
    return v.get_subtitles(sim_threshold)


def save_subtitles_to_file(
        video_path: str, file_path='subtitle.srt', lang='eng',
        time_start='0:00', time_end='', conf_threshold=65, sim_threshold=90,
        box=2, frame_skip=0, verbose=False) -> None:
    with open(file_path, 'w+', encoding='utf-8') as f:
        f.write(get_subtitles(
            video_path, lang, time_start, time_end, conf_threshold,
            sim_threshold, box, frame_skip, verbose))
