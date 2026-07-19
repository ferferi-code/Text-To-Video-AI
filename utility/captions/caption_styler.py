import os
from moviepy.editor import TextClip, ColorClip

def get_caption_clips(text, t1, t2, config):
    """
    Generates MoviePy clips for captions based on 2026 trending styles.
    Returns a list of clips (e.g., [background_clip, text_clip]) to be composited.
    """
    style = config.get_caption_style()
    
    font_face = config.get_caption_font_face()
    font_size = config.get_caption_font_size()
    base_color = config.get_caption_font_color()
    stroke_width = config.get_caption_stroke_width()
    stroke_color = config.get_caption_stroke_color()
    position = config.get_caption_position()
    
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

    if style == 'hormozi':
        color = 'yellow' if base_color == 'yellow' else 'white'
        sw = max(stroke_width, 5)
        sc = 'black'
        txt_clip = TextClip(txt=text, font=font_face, fontsize=font_size, color=color, 
                            stroke_width=sw, stroke_color=sc, method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    elif style == 'card':
        txt_clip = TextClip(txt=text, font=font_face, fontsize=font_size, color='white', 
                            stroke_width=0, stroke_color='transparent', method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        
        w, h = txt_clip.size
        padding = 15
        bg_clip = ColorClip(size=(int(w + padding*2), int(h + padding)), color=(0, 0, 0))
        bg_clip = bg_clip.set_start(t1).set_end(t2).set_opacity(0.6).set_position((pos[0], pos[1] - 5))
        clips.append(bg_clip)
        clips.append(txt_clip)

    elif style == 'neon':
        color = base_color if base_color in ['cyan', 'magenta', 'green', 'blue'] else 'cyan'
        txt_clip = TextClip(txt=text, font=font_face, fontsize=font_size, color=color, 
                            stroke_width=3, stroke_color='white', method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    elif style == 'minimal':
        txt_clip = TextClip(txt=text, font='Arial-Bold', fontsize=font_size, color='white', 
                            stroke_width=2, stroke_color='black', method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    elif style == 'karaoke':
        color = 'yellow' if base_color == 'yellow' else 'green'
        txt_clip = TextClip(txt=text, font=font_face, fontsize=font_size, color=color, 
                            stroke_width=4, stroke_color='black', method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    elif style == 'comic':
        txt_clip = TextClip(txt=text, font='Comic-Sans-MS', fontsize=int(font_size * 1.1), color='white', 
                            stroke_width=4, stroke_color='black', method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    else:
        txt_clip = TextClip(txt=text, font=font_face, fontsize=font_size, color=base_color, 
                            stroke_width=stroke_width, stroke_color=stroke_color, method='label')
        txt_clip = txt_clip.set_start(t1).set_end(t2).set_position(pos)
        clips.append(txt_clip)

    return clips
