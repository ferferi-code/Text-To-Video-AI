import os
from moviepy.editor import TextClip, ColorClip

def get_caption_clips(text, t1, t2, config):
    """
    Generates MoviePy clips for captions based on 2026 trending styles.
    Returns a list of clips (e.g., [background_clip, text_clip]) to be composited.
    """
    style = os.getenv('CAPTION_STYLE', 'hormozi').lower()
    
    font_face = config.get_caption_font_face()
    font_size = config.get_caption_font_size()
    base_color = config.get_caption_font_color()
    stroke_width = config.get_caption_stroke_width()
    stroke_color = config.get_caption_stroke_color()
    position = config.get_caption_position()
    
    # Map position to MoviePy coordinates (optimized for 1080p height)
    pos_map = {
        'bottom_center': ('center', 900),
        'bottom_left': ('left', 900),
        'bottom_right': ('right', 900),
        'top': ('center', 150),
        'center': ('center', 540),
        'bottom': ('center', 950)
    }
    pos = pos_map.get(position, ('center', 900))
    clips = []

    # ==========================================
    # 2026 TRENDING CAPTION STYLES
    # ==========================================
    
    if style == 'hormozi':
        # قانون طلایی: کنتراست فوق‌العاده بالا، فونت بولد، حاشیه ضخیم
        color = 'yellow' if base_color == 'yellow' else 'white'
        sw = max(stroke_width, 5)
        sc = 'black'
        txt_clip = TextClip(txt=text, font=font_face, fontsize=font_size, color=color, 
                            stroke_width=sw, stroke_color=sc, method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    elif style == 'card':
        # قانون طلایی: خوانایی ۱۰۰٪ روی هر پس‌زمینه‌ای با باکس نیمه‌شفاف
        txt_clip = TextClip(txt=text, font=font_face, fontsize=font_size, color='white', 
                            stroke_width=0, stroke_color='transparent', method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        
        w, h = txt_clip.size
        padding = 15
        # ساخت باکس پس‌زمینه مشکی با شفافیت ۶۰٪
        bg_clip = ColorClip(size=(int(w + padding*2), int(h + padding)), color=(0, 0, 0))
        bg_clip = bg_clip.set_start(t1).set_end(t2).set_opacity(0.6).set_position((pos[0], pos[1] - 5))
        clips.append(bg_clip)
        clips.append(txt_clip)

    elif style == 'neon':
        # قانون طلایی: جذابیت بصری برای Gen-Z با رنگ‌های درخشان
        color = base_color if base_color in ['cyan', 'magenta', 'green', 'blue'] else 'cyan'
        txt_clip = TextClip(txt=text, font=font_face, fontsize=font_size, color=color, 
                            stroke_width=3, stroke_color='white', method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    elif style == 'minimal':
        # قانون طلایی: حرفه‌ای، تمیز، بدون حواس‌پرتی
        txt_clip = TextClip(txt=text, font='Arial-Bold', fontsize=font_size, color='white', 
                            stroke_width=2, stroke_color='black', method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    elif style == 'karaoke':
        # قانون طلایی: هایلایت کلمات برای افزایش Retention Rate
        color = 'yellow' if base_color == 'yellow' else 'green'
        txt_clip = TextClip(txt=text, font=font_face, fontsize=font_size, color=color, 
                            stroke_width=4, stroke_color='black', method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    elif style == 'comic':
        # قانون طلایی: صمیمیت و انرژی برای محتوای سرگرمی
        txt_clip = TextClip(txt=text, font='Comic-Sans-MS', fontsize=int(font_size * 1.1), color='white', 
                            stroke_width=4, stroke_color='black', method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    else: # Default / Custom fallback
        txt_clip = TextClip(txt=text, font=font_face, fontsize=font_size, color=base_color, 
                            stroke_width=stroke_width, stroke_color=stroke_color, method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    return clips
