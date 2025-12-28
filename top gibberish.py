from PIL import Image, ImageDraw, ImageFont
import random
import subprocess
import time
from io import BytesIO

WIDTH = 854
HEIGHT = 480
SLIDES = 2000
SECONDS_PER_SLIDE = 5
FPS = 30

stream_key = #PUT YOUR STREAM KEY HERE OR ELSE I'LL EAT YOU

VIDEO_OUT = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
MUSIC_PATH = r"music.mp3"
FONT_PATH = "arial.ttf"

TOP_FONT_SIZE = 48
CENTER_FONT_SIZE = 120
BG_COLOR = (0, 102, 204)

ffmpeg = None
stream_dead = False

top_font = ImageFont.truetype(FONT_PATH, TOP_FONT_SIZE)
center_font = ImageFont.truetype(FONT_PATH, CENTER_FONT_SIZE)

vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"

def random_word():
    length = 5
    chance = 1
    firstc = ""
    while random.randint(0,1) == 0:
        length += 1
        chance *= 2
    if random.randint(1,26) == 1:
        chance *= 26
        if random.randint(0,1) == 0:
            firstc = "ch"
        else:
            firstc = "sh"
    else:
        firstc = random.choice(consonants)
    for wor in range(length-1):
        if wor % 2 == 0:
            random_vol = random.choice(vowels)
            if random_vol == "e":
                if random.randint(1,4) == 1:
                    firstc += "ee"
                    chance *= 8
                else:
                    firstc += "e"
            elif random_vol == "o":
                if random.randint(1,4) == 1:
                    firstc += "oo"
                    chance *= 8
                else:
                    firstc += "o"
            else:
                firstc += random_vol
        else:
            firstc += random.choice(consonants)
    return firstc, chance

def launch_ffmpeg():
    cmd = [
        "ffmpeg",
        "-re",
        "-f", "image2pipe",
        "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-framerate", str(FPS),
        "-i", "-",
        "-stream_loop", "-1",
        "-i", MUSIC_PATH,

        "-c:v", "libx264",
        "-b:v", "4000k",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "16k",
        "-shortest",
        "-f", "flv", VIDEO_OUT
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)

def restart_stream(e):
    global ffmpeg, stream_dead
    try:
        ffmpeg.stdin.close()
        ffmpeg.wait()
    except:
        pass
    ffmpeg = launch_ffmpeg()
    open("stream_crash.log", "a").write(f"[{time.ctime()}]: {e}\n")
    stream_dead = False

def fit_font(draw, text):
    global FONT_PATH, CENTER_FONT_SIZE, HEIGHT, WIDTH
    size = CENTER_FONT_SIZE
    while size > 10:
        font = ImageFont.truetype(FONT_PATH, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= WIDTH and h <= 200:
            return font, bbox
        size -= 2

    return font, bbox

def send_frame(img, durr):
    global stream_dead, ffmpeg
    if stream_dead:
        restart_stream("idk loll")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    for _ in range(round(durr * FPS)):
        try:
            ffmpeg.stdin.write(buffer.getvalue())
        except(BrokenPipeError, OSError) as e:
            stream_dead = True
            restart_stream(e)
            break

def art(word, chance, rank, durr):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img) 
    center_text = word
    top_font = ImageFont.truetype(FONT_PATH, TOP_FONT_SIZE)

    if rank > 0:
        top_text = f"top {rank} gibberish"
        top_bbox = draw.textbbox((0, 0), top_text, font=top_font)
        top_x = (WIDTH - (top_bbox[2] - top_bbox[0])) // 2
        draw.text((top_x, 20), top_text, fill="white", font=top_font)

    if chance >= 1:
        bottom_text = f"chance: 1 in {chance}"
        bottom_bbox = draw.textbbox((0, 0), bottom_text, font=top_font) #AAAAA code so messy :e
        bottom_x = (WIDTH - (bottom_bbox[2] - bottom_bbox[0])) // 2
        color = ""
        if chance <= 10:
            color = "white"
        elif chance <= 50:
            color = "yellow"
        else:
            color = "purple"
        draw.text((bottom_x, HEIGHT - 20 - (bottom_bbox[3] - bottom_bbox[1])), bottom_text, fill=color, font=top_font)
    
    center_font, center_bbox = fit_font(draw, center_text)
    print(center_bbox[0], center_bbox[1], center_bbox[2], center_bbox[3])
    center_x = (WIDTH - (center_bbox[2] - center_bbox[0])) // 2
    center_y = (HEIGHT - (center_bbox[3] - center_bbox[1])) // 2
    draw.text((center_x, center_y), center_text, fill="white", font=center_font)

    send_frame(img, durr)



ffmpeg = launch_ffmpeg()

art(f"top {SLIDES} gibberish:", 0, 0, SECONDS_PER_SLIDE+10)

for slide in range(SLIDES):
    le_word, chance = random_word()
    art(le_word, chance, SLIDES-slide, SECONDS_PER_SLIDE)

art("thanks for watching", 0, 0, SECONDS_PER_SLIDE+10)
ffmpeg.stdin.close()
ffmpeg.wait()

print("DONE:", VIDEO_OUT)
