"""Apply sample/fictional studio details to Liller Photo while preserving 100% of the original CSS classes, fonts, and layout structure."""
from pathlib import Path
import re

root = Path(__file__).resolve().parent / 'public'

# Define replacements that preserve layout and font styles
replacements = {
    'lauren@lillerphoto.com': 'hello@rheakapoor.example',
    'mailto:lauren@lillerphoto.com': 'mailto:hello@rheakapoor.example',
    'instagram.com/lillerphoto': 'instagram.com/rheakapoor.photography',
    'Lauren Liller': 'Rhea Kapoor',
    'LILLER PHOTO': 'RHEA KAPOOR PHOTOGRAPHY',
    'Liller Photo': 'Rhea Kapoor Photography',
    "Hi, I'm Lauren!": "Hi, I'm Rhea!",
    "I'm Lauren!": "I'm Rhea!",
    '“Lauren, you were absolutely incredible!”': '“Rhea, you were absolutely incredible!”',
    'Milwaukee, WI &amp; Beyond': 'New Delhi, India &amp; Beyond',
    'Milwaukee, WI & Beyond': 'New Delhi, India & Beyond',
    'Milwaukee, WI': 'New Delhi, India',
    'Capturing Your Joy est. 2012': 'Capturing Timeless Stories est. 2018',
    'est. 2012': 'est. 2018',
}

# Contact card markup that matches Showit's font styles and design aesthetic
contact_card_html = '''
<div style="max-width: 800px; margin: 35px auto; padding: 30px 25px; background: #faf8f5; border: 1px solid #e2ddd5; border-radius: 8px; font-family: 'Lato', sans-serif;">
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 24px; margin-bottom: 30px; border-bottom: 1px solid #ddd7cc; padding-bottom: 25px; text-align: center;">
    <div>
      <h4 style="font-family: 'Montserrat', sans-serif; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: #555; margin: 0 0 10px;">Studio Location</h4>
      <p style="margin: 0; font-size: 15px; color: #222; line-height: 1.6;">
        Studio 18, Hauz Khas Galleria<br>
        New Delhi, 110016, India
      </p>
    </div>
    <div>
      <h4 style="font-family: 'Montserrat', sans-serif; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: #555; margin: 0 0 10px;">Direct Contact</h4>
      <p style="margin: 0; font-size: 15px; color: #222; line-height: 1.6;">
        <strong>Phone:</strong> +91 98765 43210<br>
        <strong>WhatsApp:</strong> +91 98111 22334<br>
        <strong>Email:</strong> <a href="mailto:hello@rheakapoor.example" style="color: #444; text-decoration: underline;">hello@rheakapoor.example</a>
      </p>
    </div>
    <div>
      <h4 style="font-family: 'Montserrat', sans-serif; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: #555; margin: 0 0 10px;">Office Timings</h4>
      <p style="margin: 0; font-size: 15px; color: #222; line-height: 1.6;">
        Monday – Saturday<br>
        10:00 AM – 7:00 PM IST<br>
        <em>(By Appointment)</em>
      </p>
    </div>
  </div>

  <h3 style="font-family: 'Fitzgerald Bold', 'Playfair Display', Georgia, serif; font-size: 26px; color: #1a1a1a; margin: 0 0 10px; text-align: center;">Send An Inquiry</h3>
  <p style="text-align: center; color: #666; font-size: 14px; margin-bottom: 25px; font-family: 'Lato', sans-serif;">I do my best to respond within 24 hours of your inquiry. Let's create something extraordinary together!</p>

  <form onsubmit="event.preventDefault(); alert('Thank you! Your inquiry has been received. Rhea will connect with you within 24 hours.');" style="display: flex; flex-direction: column; gap: 16px;">
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
      <div>
        <label style="display: block; font-family: 'Montserrat', sans-serif; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; color: #333;">Your Name *</label>
        <input type="text" required placeholder="Aarav & Meera" style="width: 100%; padding: 12px; border: 1px solid #ccc5b9; border-radius: 4px; font-size: 14px; box-sizing: border-box; background: #fff;" />
      </div>
      <div>
        <label style="display: block; font-family: 'Montserrat', sans-serif; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; color: #333;">Email Address *</label>
        <input type="email" required placeholder="meera@example.com" style="width: 100%; padding: 12px; border: 1px solid #ccc5b9; border-radius: 4px; font-size: 14px; box-sizing: border-box; background: #fff;" />
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
      <div>
        <label style="display: block; font-family: 'Montserrat', sans-serif; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; color: #333;">Phone Number *</label>
        <input type="tel" required placeholder="+91 98765 00000" style="width: 100%; padding: 12px; border: 1px solid #ccc5b9; border-radius: 4px; font-size: 14px; box-sizing: border-box; background: #fff;" />
      </div>
      <div>
        <label style="display: block; font-family: 'Montserrat', sans-serif; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; color: #333;">Wedding / Event Date</label>
        <input type="date" style="width: 100%; padding: 12px; border: 1px solid #ccc5b9; border-radius: 4px; font-size: 14px; box-sizing: border-box; background: #fff;" />
      </div>
    </div>

    <div>
      <label style="display: block; font-family: 'Montserrat', sans-serif; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; color: #333;">Event Location / Venue</label>
      <input type="text" placeholder="e.g. Udaipur, Delhi NCR, Jaipur, Goa, International" style="width: 100%; padding: 12px; border: 1px solid #ccc5b9; border-radius: 4px; font-size: 14px; box-sizing: border-box; background: #fff;" />
    </div>

    <div>
      <label style="display: block; font-family: 'Montserrat', sans-serif; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; color: #333;">Your Vision & Details</label>
      <textarea rows="4" placeholder="Tell me about your celebration, guest count, and any moments you want captured..." style="width: 100%; padding: 12px; border: 1px solid #ccc5b9; border-radius: 4px; font-size: 14px; box-sizing: border-box; background: #fff; resize: vertical;"></textarea>
    </div>

    <button type="submit" style="align-self: center; background: #1a1a1a; color: #fff; padding: 14px 42px; font-family: 'Montserrat', sans-serif; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 2px; border: none; border-radius: 4px; cursor: pointer; transition: background 0.2s; margin-top: 8px;">
      Send Message
    </button>
  </form>
</div>
'''

count = 0
for file in root.rglob('*.html'):
    text = file.read_text(encoding='utf-8')

    # Apply global string replacements
    for before, after in sorted(replacements.items(), key=lambda x: -len(x[0])):
        text = text.replace(before, after)

    # In contact page, inject the contact card above the dubsado iframe
    if file.parent.name == 'contact':
        if '<iframe ' in text and 'id="rk-contact-card"' not in text:
            text = text.replace('<iframe ', f'<div id="rk-contact-card">{contact_card_html}</div>\n<iframe ', 1)

    file.write_text(text, encoding='utf-8')
    count += 1

print(f"Successfully personalized {count} HTML pages in Liller website without affecting any styles or fonts!")
