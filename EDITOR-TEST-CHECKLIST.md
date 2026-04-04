# Editor Test Checklist

## 🔤 Font Rendering
- [ ] Fonts load on page init (check console for "✅ Fonts loaded successfully")
- [ ] Playfair Display renders correctly on canvas
- [ ] Poppins renders correctly on canvas
- [ ] Fonts maintained when switching slides
- [ ] Fonts correct in exported PNG
- [ ] All font weights (400-800) work

## 📐 Templates (11 total)
- [ ] Cover template loads
- [ ] Myth Buster template loads
- [ ] Checklist template loads
- [ ] VS Compare template loads
- [ ] Grid Cards template loads
- [ ] CTA template loads
- [ ] Stats template loads
- [ ] Quote template loads
- [ ] Content Box template loads (NEW)
- [ ] Tip Cards template loads (NEW)
- [ ] Sign Cards template loads (NEW)

## 🏷️ Categories
- [ ] Category dropdown populates
- [ ] Selecting category shows preview
- [ ] Categories work with templates

## ✏️ Text Editing
- [ ] Double-click to edit inline
- [ ] Change font family
- [ ] Change font size (8-300 range)
- [ ] Change font weight
- [ ] Change text color
- [ ] Quick color swatches work
- [ ] Position X/Y inputs work
- [ ] Multi-line text works
- [ ] Emoji in text works
- [ ] Special characters work (quotes, apostrophes)

## 🔷 Shape Editing
- [ ] Add rectangle
- [ ] Add circle
- [ ] Change fill color
- [ ] Change opacity
- [ ] Change border radius (rect only)
- [ ] Position X/Y inputs work

## ➕ Add Elements
- [ ] Add Text button
- [ ] Add Heading button
- [ ] Add Badge button (group object)
- [ ] Add Rectangle button
- [ ] Add Circle button
- [ ] Add Emoji button (prompt works)

## 🖱️ Interactions
- [ ] Click to select element
- [ ] Drag to reposition
- [ ] Corner handles resize
- [ ] Rotation handle works
- [ ] Delete key removes selected
- [ ] Backspace removes selected
- [ ] Can't delete background/decoration
- [ ] Ctrl+C copies
- [ ] Ctrl+V pastes (offset by 20px)

## 📑 Slides
- [ ] Default slide shows
- [ ] Add Slide button works
- [ ] Switch between slides
- [ ] Slide content persists when switching
- [ ] Slide tabs update correctly

## 📅 Day Loader
- [ ] Day list renders (60 days)
- [ ] Search filter works
- [ ] Clicking day loads content
- [ ] Day active state updates

## 📏 Canvas Sizes
- [ ] 4:5 (1080×1350) - default
- [ ] 9:16 (1080×1920)
- [ ] 1:1 (1080×1080)
- [ ] Size buttons show active state
- [ ] Canvas scales to fit viewport

## 📥 Export
- [ ] Export PNG (single slide)
- [ ] Export All Slides
- [ ] Correct dimensions (not scaled)
- [ ] Fonts render in export
- [ ] Background gradient exports
- [ ] Save Project (JSON)

## 🌐 Browser Compatibility
- [ ] Chrome
- [ ] Safari
- [ ] Firefox
- [ ] Mobile responsive (sidebars collapse?)

## 🔴 Edge Cases
- [ ] Very long text (overflow handling)
- [ ] Empty slides export
- [ ] Rapid slide switching
- [ ] No selection → properties panel shows placeholder
- [ ] Group objects (badge) selection
- [ ] Undo/Redo (not implemented - document this!)
- [ ] Page refresh loses work (no auto-save - document!)
- [ ] Unicode/emoji rendering

## 🐛 Known Issues to Check
1. Font not loaded before export → FIXED
2. Missing slide in Day 37 → FIXED
3. Load project feature → Not implemented?
