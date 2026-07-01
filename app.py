import os
import re
import yt_dlp
import google.generativeai as genai
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, TextClip
import moviepy.video.fx.all as vfx

# ==========================================
# ၁။ CONFIGURATION (ဒီနေရာမှာ သင့် API Key ထည့်ပါ)
# ==========================================
GEMINI_API_KEY = "YOUR_FREE_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)

def download_video_auto(link, output_name="raw_downloaded.mp4"):
    """YouTube သို့မဟုတ် TikTok Link ကို Auto ခွဲခြားပြီး အကောင်းဆုံး Quality နဲ့ ဒေါင်းပေးမယ့်စနစ်"""
    print(f"🚀 [အဆင့် ၁] ဗီဒီယိုကို စတင်ဒေါင်းလုဒ်ဆွဲနေပါပြီ: {link}")
    
    # TikTok နဲ့ YouTube အတွက် yt-dlp Options ပြင်ဆင်ခြင်း
    ydl_opts = {
        'format': 'bestvideo[height<=1024]+bestaudio/best' if 'youtube' in link or 'youtu.be' in link else 'best',
        'outtmpl': 'temp_file.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': False
    }
    
    # ဒေါင်းလုဒ်ဆွဲခြင်း
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
        
    # ဒေါင်းလို့ရလာတဲ့ ဖိုင်အမှန်ကို ရှာပြီး နာမည်ပြောင်းခြင်း
    for file in os.listdir('.'):
        if file.startswith('temp_file.'):
            os.rename(file, output_name)
            break
            
    print("✅ ဒေါင်းလုဒ်ဆွဲခြင်း အောင်မြင်ပါသည်။")
    return output_name

def ai_generate_script(link_type="movie"):
    """Gemini API သုံးပြီး 100% Copyright ကင်းလွတ်မယ့် ဇာတ်ညွှန်း (Script) ကို အော်တိုရေးခိုင်းခြင်း"""
    print("🧠 [အဆင့် ၂] Gemini AI သုံးပြီး ဇာတ်ညွှန်း ဖန်တီးနေပါပြီ...")
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = (
        "Write a 150-word highly engaging, energetic voiceover commentary for a short video recap. "
        "Make it storytelling style. Keep it original to avoid any copyright issues."
    )
    
    response = model.generate_content(prompt)
    return response.text

def generate_ai_voice(text, voice_lang='my', output_audio="ai_voice.mp3"):
    """ရလာတဲ့ ဇာတ်ညွှန်းကို မြန်မာသံ သို့မဟုတ် အင်္ဂလိပ်သံ အော်တိုပြောင်းပေးခြင်း"""
    print("🎤 [အဆင့် ၃] ဇာတ်ညွှန်းကို AI အသံဖိုင်အဖြစ် ပြောင်းလဲနေပါပြီ...")
    # voice_lang: 'my' (မြန်မာ) သို့မဟုတ် 'en' (အင်္ဂလိပ်)
    tts = gTTS(text=text, lang=voice_lang, slow=False)
    tts.save(output_audio)
    return output_audio

def render_final_video(video_path, audio_path, output_final="Finished_Video.mp4", logo_path="logo.png"):
    """ဗီဒီယိုကို ကာကွယ်ရေးစနစ်များထည့်ပြီး (Mirror, Audio Swap, Logo, Timer) အချောထည် Render ရိုက်ခြင်း"""
    print("🎬 [အဆင့် ၄] ဗီဒီယိုကို ကာကွယ်ရေးစနစ်များဖြင့် Render ရိုက်နေပါပြီ...")
    
    # ဗီဒီယိုနှင့် အသံကို သွင်းခြင်း
    clip = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # ၃ မိနစ် (စက္ကန့် ၁၈၀) ထက်ကျော်ရင် ဖြတ်ချမယ် (Copyright Safe ဖြစ်ရန်)
    final_duration = min(audio.duration, 180, clip.duration)
    
    # ဗီဒီယိုဖြတ်တောက်မှု ပြုလုပ်ခြင်း
    clip = clip.subclip(0, final_duration)
    
    # 🛡️ COPYRIGHT BREAKING (မူပိုင်ခွင့်စက်ရုပ်များ ကျော်ရန် ဗီဒီယိုကို ဘယ်ညာပြောင်းပြန်လှန်ခြင်း)
    clip = clip.fx(vfx.mirror_x)
    
    # မူရင်းအသံကို လုံးဝဖြုတ်ပစ်ပြီး AI ရဲ့ အသံအသစ်ကို ထည့်သွင်းခြင်း
    clip = clip.set_audio(audio)
    
    # 🏷️ Logo ရေစာ Overlay ထည့်ခြင်း (ရီပိုထဲမှာ logo.png ရှိရင် အော်တိုထည့်ပေးမယ်)
    layers = [clip]
    if os.path.exists(logo_path):
        logo = (ImageClip(logo_path)
                .set_duration(final_duration)
                .resize(height=50) # Logo အမြင့်
                .set_pos(("right", "top"))) # ညာဘက်အပေါ်ထောင့်
        layers.append(logo)
        
    # ⏱️ 3-Minute Timer Box (အောက်ခြေ ဘယ်ဘက်မှာ ကောင်တာပြခြင်း)
    timer_box = (TextClip("03:00 FIXED RECAP", fontsize=18, color='white', bg_color='black')
                 .set_duration(final_duration)
                 .set_pos(("left", "bottom")))
    layers.append(timer_box)
    
    # ဗီဒီယိုတစ်ခုလုံးကို ပေါင်းစပ်ပြီး အချောထည် ထုတ်ခြင်း
    final_video = CompositeVideoClip(layers)
    final_video.write_videofile(output_final, fps=24, codec="libx264", audio_codec="aac")
    
    # ပိတ်သိမ်းခြင်း
    final_video.close()
    clip.close()
    audio.close()
    print("✨ [ပြီးဆုံးပါပြီ] တန်းတင်လို့ရမယ့် ဗီဒီယို 'Finished_Video.mp4' အောင်မြင်စွာ ထွက်လာပါပြီ။")

# ==========================================
# 🚀 MAIN ONE-CLICK EXECUTION RUNNER
# ==========================================
if __name__ == "__main__":
    # ဤနေရာတွင် သင်အလိုရှိရာ TikTok သို့မဟုတ် YouTube Link ကို ထည့်ပေးရုံပါပဲ
    TARGET_LINK = "https://www.youtube.com/watch?v=020g-0hhCAU" 
    
    try:
        raw_video = download_video_auto(TARGET_LINK)
        script_text = ai_generate_script()
        ai_audio = generate_ai_voice(script_text, voice_lang='my') # မြန်မာသံအတွက် 'my', အင်္ဂလိပ်သံအတွက် 'en'
        
        # ဗီဒီယို ဖန်တီးမှု စတင်ပါပြီ
        render_final_video(raw_video, ai_audio)
        
    except Exception as e:
        print(f"❌ Error တစ်ခုခုတက်သွားပါသည်: {e}")
