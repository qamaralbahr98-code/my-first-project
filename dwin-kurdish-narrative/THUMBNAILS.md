# THUMBNAILS.md: create these AFTER the video is finished (Claude Code)

Make 6 files in `thumbnails/`, one for each language in each format:
`thumb_ar_16x9.png`, `thumb_ckb_16x9.png`, `thumb_kmr_16x9.png` (1280×720, under 2 MB) and
`thumb_ar_9x16.png`, `thumb_ckb_9x16.png`, `thumb_kmr_9x16.png` (1080×1920).

Build them with Playwright (HTML + brand fonts), place the logo top-left, and preview them at 160 px wide; the big words must still be readable.

## Main design: "Text behind the mountain person"
- Background: A03 (a person seen from behind on a ridge at sunrise). The person is on the side opposite the text.
- Giant title BEHIND the person (rembg matte over the letters):
  - ar: «من يملك الحكاية؟»
  - ckb: «چیرۆکەکە هی کێیە؟»
  - kmr: «ÇÎROK YA KÊ YE?»
- Small saffron tag above the title (#E8A33D, dark text):
  - ar: «السردية الكردية»
  - ckb: «گێڕانەوەی کوردی»
  - kmr: «Vegotina Kurdî»
- A faint "1923" (12% opacity) in the sky, as a curiosity hook.
- Text sits on the reading side: right for ar/ckb, left for kmr. Colours: cream #EFE8DC with a soft dark shadow; slight warm grade.

## 9:16 version
The person is centred in the lower half. The title sits in the upper third, behind the head, with the tag above it. Keep 250 px clear at the bottom.

## Alternative for A/B testing
A dark slide (#111418) with the mountains (A01) at 40% opacity. Use the quote in two lines:
- ar: «ليس للكرد أصدقاء… إلا الجبال؟»
- ckb: «کورد هیچ دۆستێکی نییە… جگە لە چیاکان؟»
- kmr: «Hevalên Kurdan tune ne… ji bilî çiyan?»

The question mark is in saffron.

## Rules
- At most 4 big words. No flags, no party symbols, no faces of real people, and no red arrows or shocked faces.
- Use the same layout in all three languages so the channels look like one brand.
