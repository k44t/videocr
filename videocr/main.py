from .api import save_subtitles_to_file
from .video import Frame

import argparse
import sys



# compiled from https://github.com/tesseract-ocr/tessdata_fast/tree/main/script and https://tesseract-ocr.github.io/tessdoc/Data-Files
langs = {
    "afr": "Afrikaans",
    "amh": "Amharic",
    "ara": "Arabic",
    "asm": "Assamese",
    "aze": "Azerbaijani",
    "aze_cyrl": "Azerbaijani - Cyrillic",
    "bel": "Belarusian",
    "ben": "Bengali",
    "bod": "Tibetan",
    "bos": "Bosnian",
    "bul": "Bulgarian",
    "cat": "Catalan; Valencian",
    "ceb": "Cebuano",
    "ces": "Czech",
    "chi_sim": "Chinese - Simplified",
    "chi_tra": "Chinese - Traditional",
    "chr": "Cherokee",
    "cym": "Welsh",
    "dan": "Danish",
    "deu": "German",
    "dzo": "Dzongkha",
    "ell": "Greek, Modern (1453-)",
    "eng": "English",
    "enm": "English, Middle (1100-1500)",
    "epo": "Esperanto",
    "est": "Estonian",
    "eus": "Basque",
    "fas": "Persian",
    "fin": "Finnish",
    "fra": "French",
    "frk": "German Fraktur",
    "frm": "French, Middle (ca. 1400-1600)",
    "gle": "Irish",
    "glg": "Galician",
    "grc": "Greek, Ancient (-1453)",
    "guj": "Gujarati",
    "hat": "Haitian; Haitian Creole",
    "heb": "Hebrew",
    "hin": "Hindi",
    "hrv": "Croatian",
    "hun": "Hungarian",
    "iku": "Inuktitut",
    "ind": "Indonesian",
    "isl": "Icelandic",
    "ita": "Italian",
    "ita_old": "Italian - Old",
    "jav": "Javanese",
    "jpn": "Japanese",
    "kan": "Kannada",
    "kat": "Georgian",
    "kat_old": "Georgian - Old",
    "kaz": "Kazakh",
    "khm": "Central Khmer",
    "kir": "Kirghiz; Kyrgyz",
    "kor": "Korean",
    "kur": "Kurdish",
    "lao": "Lao",
    "lat": "Latin",
    "lav": "Latvian",
    "lit": "Lithuanian",
    "mal": "Malayalam",
    "mar": "Marathi",
    "mkd": "Macedonian",
    "mlt": "Maltese",
    "msa": "Malay",
    "mya": "Burmese",
    "nep": "Nepali",
    "nld": "Dutch; Flemish",
    "nor": "Norwegian",
    "ori": "Oriya",
    "pan": "Panjabi; Punjabi",
    "pol": "Polish",
    "por": "Portuguese",
    "pus": "Pushto; Pashto",
    "ron": "Romanian; Moldavian; Moldovan",
    "rus": "Russian",
    "san": "Sanskrit",
    "sin": "Sinhala; Sinhalese",
    "slk": "Slovak",
    "slv": "Slovenian",
    "spa": "Spanish; Castilian",
    "spa_old": "Spanish; Castilian - Old",
    "sqi": "Albanian",
    "srp": "Serbian",
    "srp_latn": "Serbian - Latin",
    "swa": "Swahili",
    "swe": "Swedish",
    "syr": "Syriac",
    "tam": "Tamil",
    "tel": "Telugu",
    "tgk": "Tajik",
    "tgl": "Tagalog",
    "tha": "Thai",
    "tir": "Tigrinya",
    "tur": "Turkish",
    "uig": "Uighur; Uyghur",
    "ukr": "Ukrainian",
    "urd": "Urdu",
    "uzb": "Uzbek",
    "uzb_cyrl": "Uzbek - Cyrillic",
    "vie": "Vietnamese",
    "yid": "Yiddish",
    "Arabic": None,
    "Armenian": None,
    "Bengali": None,
    "Canadian_Aboriginal": "Canadian Aboriginal",
    "Cherokee": None,
    "Cyrillic": None,
    "Devanagari": None,
    "Ethiopic": None,
    "Fraktur": None,
    "Georgian": None,
    "Greek": None,
    "Gujarati": None,
    "Gurmukhi": None,
    "HanS": "Modern Chinese Han Script",
    "HanS_vert": "Vertical Modern Chinese Han Script",
    "HanT": "Traditional Chinese Han Script",
    "HanT_vert": "Vertical Traditional Chinese Han Script",
    "Hangul": None,
    "Hangul_vert": "Vertical Hangul Script",
    "Hebrew": None,
    "Japanese": None,
    "Japanese_vert": "Vertical Japanese Script",
    "Kannada": None,
    "Khmer": None,
    "Lao": None,
    "Latin": None,
    "Malayalam": None,
    "Myanmar": None,
    "Oriya": None,
    "Sinhala": None,
    "Syriac": None,
    "Tamil": None,
    "Telugu": None,
    "Thaana": None,
    "Thai": None,
    "Tibetan": None,
    "Vietnamese": None
}


class CustomHelpFormatter(argparse.HelpFormatter):                                       
    def _format_action(self, action):
        if action.dest == "lang":
            header = f"  --lang  {action.help}\n"  
            choices = []
            for k in sorted(langs.keys(), key=lambda s: s.lower()):
                v = langs[k]
                line = [f"    {k}"]
                
                if v is not None:
                    line.append(": ")
                    line.append(v)
                choices.append("".join(line))
            
            return header + "\n".join(choices) + "\n"
        else:
            return super()._format_action(action)





def parse_frame(s):
    try:                                                                                             
        return int(s)
    except ValueError:
        try:
            ab = s.split(",")
            assert (len(ab) == 2)
            print(ab)
            a = ab[0]
            b = ab[1]
            a = a.split(":")
            print(a)
            assert(len(a) == 2)
            b = b.split(":")
            print(b)
            assert(len(b) == 2)
            f = Frame()
            f.left_x = int(a[0])
            f.top_y = int(a[1])
            f.right_x = int(b[0])
            f.bottom_y = int(b[1])
            return f
        except:
            raise argparse.ArgumentTypeError(f"Not a valid frame specification.")




parser = argparse.ArgumentParser(description="OCR subtitle extractor (based on Tesseract)", formatter_class=CustomHelpFormatter)
parser.add_argument("video", type=str, help="the video file to extract subtitles from")
parser.add_argument("output", type=str, help="the path to the SRT file in which the subtitles will be written")
parser.add_argument("--lang", choices=langs.keys(), default="eng", help="the language and/or script of the subtitiles")
parser.add_argument("--start-time", default="0:00", type=str, help="timestamp of the format H:MM[:SS[.SSS]]")
parser.add_argument("--end-time", default="", type=str, help="timestamp of the format H:MM[:SS[.SSS]]")
parser.add_argument("--confidence-threshold", default=65, type=int, help='''Confidence threshold for word predictions. Words with lower confidence than this value will be discarded. The default value 65 is fine for most cases.
Make it closer to 0 if you get too few words in each line, or make it closer to 100 if there are too many excess words in each line.''')
parser.add_argument("--similarity-threshold", default=90, type=int, help='''Similarity threshold for subtitle lines. Subtitle lines with larger Levenshtein ratios than this threshold will be merged together. The default value 90 is fine for most cases.
Make it closer to 0 if you get too many duplicated subtitle lines, or make it closer to 100 if you get too few subtitle lines.''')
parser.add_argument("--box", type=parse_frame, default=2, help='''the box (part of the image) on which subtitles are located.
An integer would be interpreted as a fraction of the image's lower part. I.e. 4 would mean that the lower quarter of the image contains the subtitles.
A box in pixels can be specified as: <x-left>:<y-top>,<x-right>:<y-bottom> (e.g. 10:10,20:20). 
If unspecified the lower half of the image will be used.''')
parser.add_argument("--frame-skip", type=int, default=0, help="if n > 0 then only every n-th frame will be processed. This of course will make timestamps less accurate the greater the number of skipped frames is, but it will dramatically reduce processing time.")




def run(args):
    save_subtitles_to_file(
        video_path = args.video,
        file_path = args.output,
        lang = args.lang,
        time_start=args.start_time,
        time_end=args.end_time,
        conf_threshold=args.confidence_threshold, 
        sim_threshold=args.similarity_threshold,
        box=args.box,
        frame_skip=args.frame_skip,
        verbose=True
    )



parser.set_defaults(func=run)



if __name__ == '__main__':  # This check is mandatory for Windows.
    print(sys.argv)
    args = parser.parse_args()
    args.func(args)

