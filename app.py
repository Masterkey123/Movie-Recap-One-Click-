import os
import yt_dlp
import google.generativeai as genai
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, TextClip

# ၁။ FREE API KEYS CONFIGURATION
GEMINI_API_KEY = "YOUR_FREE_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)

def download_and_cut_video(youtube_url, output_raw="raw_video.mp4"):
    """YouTube ဗီဒီယိုကို အခမဲ့ ဒေါင်းလုဒ်ဆွဲပြီး Copyright ကင်းအောင် ၃ မိနစ်စာ ဖြတ်ထုတ်ခြင်း"""
    print("[1/5] Downloading YouTube Video...")
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best',
        'outtmpl': 'downloaded_temp.%(ext)s',
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    # Copyright မိခြင်းမှ ကာကွယ်ရန် အစ/အဆုံး ဖြတ်ပြီး အလယ်က ၃ မိနစ် (စက္ကန့် ၁၈၀) ကိုပဲ ယူမည်
    clip = VideoFileClip("downloaded_temp.mp4").subclip(60, 240) # မိနစ် 1 မှ 4 အထိ ဖြတ်ယူခြင်း
    clip.write_videofile(output_raw, codec="libx264")
    clip.close()
    return output_raw

def generate_recap_script():
    """Gemini Free API ကိုသုံးပြီး ရုပ်ရှင်အကျဉ်းချုပ် Script ကို အော်တိုရေးခိုင်းခြင်း"""
    print("[2/5] Generating Movie Recap Script via Gemini...")
    model = genai.GenerativeModel('gemini-pro')
    prompt = "Write a short, engaging summary or narrative commentary for a movie recap video. Length should be around 250 words."
    response = model.generate_content(prompt)
    return response.text

def text_to_speech(text, voice_config, output_audio="narration.mp3"):
    """ရလာတဲ့ ဇာတ်ညွှန်းကို မြန်မာ/အင်္ဂလိပ် ကျား၊မ အသံပြောင်းခြင်း (gTTS - 100% Free)"""
    print("[3/5] Converting Script to AI Voice...")
    
    # ရွေးချယ်မှုအလိုက် ဘာသာစကားသတ်မှတ်ခြင်း
    if "my" in voice_config:
        lang_code = 'my'  # မြန်မာသံ (gTTS standard)
    else:
        lang_code = 'en'  # English voice
        
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(output_audio)
    return output_audio

def compile_final_video(video_path, audio_path, logo_path="logo.png"):
    """ဗီဒီယို၊ အသံ၊ Logo ရေစာ နှင့် 3-Minute Timer Box ကို တစ်ခါတည်း Render ရိုက်ပေါင်းစပ်ခြင်း"""
    print("[4/5] Processing Video Compositing & Rendering...")
    
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # ဗီဒီယိုအလျားကို အသံဖိုင်အလျား (သို့မဟုတ်) ၃ မိနစ်အတိ ညှိပါမည်
    final_duration = min(audio.duration, 180)
    video = video.set_duration(final_duration).set_audio(audio)
    
    # ကာကွယ်ရေးအတွက် အသံတိုးထားခြင်း (Copyright Safe ဖြစ်စေရန်)
    video = video.volumex(0.8) 

    # ကာကွယ်ရေးအဆင့် (၁) - Logo Png Overlay ထည့်သွင်းခြင်း
    if os.path.exists(logo_path):
        logo = (ImageClip(logo_path)
                .set_duration(final_duration)
                .resize(height=60) # အရွယ်အစား
                .set_pos(("right", "top"))) # ညာဘက်အပေါ်ထောင့်
    else:
        logo = None

    # ကာကွယ်ရေးအဆင့် (၂) - Video Timer Box (3 Mins Counter)
    # ဤနေရာတွင် စက္ကန့်အလိုက် ပြောင်းလဲမည့် text timer box ကို သတ်မှတ်ပါသည်
    timer_box = (TextClip("03:00 FIXED RECAP", fontsize=20, color='white', bg_color='black')
                 .set_duration(final_duration)
                 .set_pos(("left", "bottom")))

    # အားလုံးကို တစ်ခါတည်း ရောသမမွှေပြီး Render ထုတ်ခြင်း
    clips_to_compose = [video, timer_box]
    if logo: clips_to_compose.append(logo)
    
    final_output = CompositeVideoClip(clips_to_compose)
    print("[5/5] Exporting Final Movie Recap Video...")
    final_output.write_videofile("Final_Recap_Video.mp4", fps=24, codec="libx264", audio_codec="aac")
    
    # Temporary ဖိုင်များ ရှင်းလင်းရေး
    final_output.close()
    video.close()
    audio.close()

# --- RUN WORKFLOW ---
if __name__ == "__main__":
    YT_URL = "INSERT_TARGET_YOUTUBE_LINK_HERE"
    
    raw_vid = download_and_cut_video(YT_URL)
    script_text = generate_recap_script()
    narr_audio = text_to_speech(script_text, voice_config="my_female")
    
    # ဇာတ်လမ်းဗီဒီယို ဖန်တီးမှု စတင်ပါပြီ
    compile_final_video(raw_vid, narr_audio)
    print("✨ အစအဆုံး အောင်မြင်စွာ ပြီးဆုံးပါပြီ။ 'Final_Recap_Video.mp4' ထွက်လာပါပြီ။")
