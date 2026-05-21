# Chess Teeth — Pixel Art Sprite Sheet Prompt Log

## Version 1

### Prompt

Create a set of pixel art chess pieces as humanized cartoon characters. Style: chunky 16-bit pixel art, ~128×128 pixels each, transparent background.

The six pieces are: Pawn (small foot soldier), Knight (warrior on foot with a horse-head helmet), Bishop (robed cleric), Rook (armored castle guardian), Queen (regal warrior queen), King (armored king).

Produce two color variants:
- White set — warm golden/cream tones with brown outlines
- Black set — cool grey/slate tones with dark outlines

For each piece, produce two poses:
- Normal — neutral standing pose, personality visible
- Chomp — same character but mouth wide open showing teeth, aggressive expression, as if about to bite

Output as individual images, one per piece per variant per pose (24 images total). Keep the art style consistent across all pieces — same pixel density, same proportions, same level of detail.

### Result

Generated `Gemini_Generated_chessmen_v1.png`.

### Feedback

| Piece | Issue |
|---|---|
| **Pawn** | A little too small; no open mouth in chomp pose |
| **Knight** | Decent, but a lance in the other hand would be nicer |
| **Bishop (col 3)** | Good overall, but row 1 white bishop holds the staff in the wrong hand — inconsistent with other rows; black open-mouth variant's hand is slightly blurry |
| **Bishop/Rook hybrid (col 4)** | Spurious mixed column — can be deleted entirely |
| **Rook (col 5)** | Row 1 color is wrong; row 4 black Rook is missing the open mouth that row 2 white has |
| **Queen (cols 6 & 7)** | Two columns generated instead of one. Preferred picks: row 1 → col 7, row 2 → col 7 (mouth opens wider), row 3 → neither is ideal (col 7 wrong sword + no chomp; col 6 also no chomp), row 4 → col 7 sword inconsistent + skin tone mismatch with row 3 |
| **King (col 8)** | Row 4 skin tone inconsistent with row 3; hand gesture in col 7 row 3 doesn't match row 1; watermark overlaps character — needs a white border added |

**Overall:** Consistency is a major issue throughout — pose, weapon hand, and skin tone drift between rows.

---

## Version 2

### Prompt

Create a set of pixel art chess pieces as humanized cartoon characters.
Style: chunky 16-bit pixel art, ~128×128 pixels each, transparent background.

The six pieces are: Pawn (small foot soldier), Knight (warrior on foot with a horse-head helmet), Bishop (robed cleric), Rook (armored castle guardian), Queen (regal warrior queen), King (armored king).

Produce two color variants:
- White set — warm golden/cream tones with brown outlines
- Black set — cool grey/slate tones with dark outlines

For each piece, produce two poses:
- Normal — neutral standing pose, personality visible
- Chomp — same character but mouth dramatically wide open showing teeth, aggressive expression, as if about to bite. This applies to ALL six pieces including Pawn and Bishop.

Output as a single sprite sheet: 6 columns (one per piece) × 4 rows (White Normal, White Chomp, Black Normal, Black Chomp). Keep art style, proportions, skin tone, and weapon hands consistent across all rows for each piece.

### Result

Generated `Gemini_Generated_chessmen_v2.png`.

### Feedback

| Piece | Issue |
|---|---|
| **Pawn** | Actually not bad — acceptable |
| **Knight** | Should have a lance and shield; the horse-head helmet had more charm in v1 |
| **Bishop** | v1 had more soul — prefer v1's design with the inconsistencies fixed rather than v2's cleaner but blander version |
| **Rook** | v1 design was nicer overall; rows 2 and 3 in v1 were perfect |
| **Queen & King** | Character design and personality noticeably weaker than v1 |

**Overall:** v2 fixed the most important structural issue (6 columns instead of 8) but lost the aesthetic soul that made v1 special. v1 has better character design throughout — the goal is to recover that quality with v2's structural improvements.

---

## Version 3

### Prompt

Generate a single pixel art sprite sheet with a strict 4x6 grid layout.
Style: Chunky 16-bit fantasy RPG aesthetic. Clean pixels, expressive faces, cohesive palette.
Background: Transparent.
Aspect Ratio: Wide (3:2).
Borders: Thin white grid lines between cells; solid white outer border to clear watermarks.

**CRITICAL GRID RULE:** Exactly 4 Rows and 6 Columns. No extra rows. No duplicate rows.

**COLOR PALETTE:**
White Set (Rows 1 & 2): Golden/Cream armor tones, brown outlines.
Black Set (Rows 3 & 4): Grey/Slate armor tones, dark outlines.
Universal Skin Tone: Light Tan. Apply to ALL characters. Do not darken skin for the Black Set; only armor colors change.

**POSE DEFINITIONS:**
Normal: Neutral standing pose, personality visible, mouth closed.
Chomp: Same character, same pose, same weapon placement — ONLY change facial expression to mouth wide open, aggressive, teeth visible. Do not alter body stance or weapon angle.

**CHARACTER COLUMNS (Left to Right):**
1. **PAWN** — Small, compact foot soldier. Light armor, simple helmet. Personality: eager, grounded. Weapon: Spear in RIGHT hand.
2. **KNIGHT** — Human warrior wearing a full horse-head helmet. Personality: valiant, ready for charge. Weapon: Lance in RIGHT hand, Shield in LEFT hand.
3. **BISHOP** — Robed cleric with tall mitre hat. Personality: serene, wise. Weapon: Staff in LEFT hand. Right hand in blessing gesture.
4. **ROOK** — Armored castle guardian. Heavy plate armor with crenellated shoulders/helmet. Personality: stoic, immovable. Weapon: Battleaxe in RIGHT hand.
5. **QUEEN** — Regal warrior queen. Full armor, pointed crown, flowing cape. Personality: commanding, fierce. Weapon: Sword in RIGHT hand.
6. **KING** — Armored king. Broad flat crown, commanding stance. Personality: regal, authoritative. Weapon: Short royal sceptre in RIGHT hand.

**ROW SPECIFICATIONS:**
Row 1: White Set — Normal Pose
Row 2: White Set — Chomp Pose
Row 3: Black Set — Normal Pose
Row 4: Black Set — Chomp Pose

**CONSISTENCY RULES:**
- Weapon hand assignment is locked per character across all 4 rows.
- Chomp pose only changes facial expression; body, armor, and weapon placement remain identical.
- Maintain consistent pixel density, line weight, and shading across all 24 sprites.
- Give each character distinct personality and posture while keeping the set cohesive.

### Result

Generated `Gemini_Generated_chessmen_v3.png`.

### Feedback

Two persistent issues:
1. **Hand swapping:** The AI swaps hands between White and Black sets (e.g., Bishop's staff moves from one hand to another).
2. **Bishop chomp:** The Bishop occasionally fails to open its mouth in the Chomp rows.

---

## Version 4

### Prompt

Generate a single pixel art sprite sheet with a strict 4x6 grid layout.
Style: Chunky 16-bit fantasy RPG aesthetic. Clean pixels, expressive faces, cohesive palette.
Background: Transparent.
Aspect Ratio: Wide (3:2).
Borders: Thin white grid lines between cells; solid white outer border to clear watermarks.

**CRITICAL GRID RULE:** Exactly 4 Rows and 6 Columns. No extra rows. No duplicate rows.

**COLOR PALETTE:**
White Set (Rows 1 & 2): Golden/Cream armor tones, brown outlines.
Black Set (Rows 3 & 4): Grey/Slate armor tones, dark outlines.
Universal Skin Tone: Light Tan. Apply to ALL characters. Do not darken skin for the Black Set; only armor colors change.
Never apply black color palette to white set, never apply white color palette to black set.
Exactly same color palette between the normal and chomp versions in the same set.

**POSE DEFINITIONS:**
Normal: Neutral standing pose, personality visible, mouth closed.
Chomp: Same character, same pose, same weapon placement — ONLY change facial expression to mouth wide open, aggressive, teeth visible. Do not alter body stance or weapon angle.

**CHARACTER COLUMNS (Left to Right):**
*NOTE: Hand positions are anchored to the Viewer's Perspective to ensure consistency with V3.*
1. **PAWN** — Small, compact foot soldier. Light armor, simple helmet. Personality: eager, grounded. Weapon: Spear held on **Viewer's Right**.
2. **KNIGHT** — Human warrior wearing a horse-head helmet with open face. Personality: valiant, ready for charge. Weapon: Lance (not spear) held on **Viewer's Left** pointing up, Shield held on **Viewer's Right**.
3. **BISHOP** — Robed cleric with tall mitre hat. Personality: serene, wise. Weapon: Staff held on **Viewer's Left**. Right hand (Viewer's Right) in blessing gesture.
4. **ROOK** — Armored castle guardian. Heavy plate armor with crenellated shoulders, and crenellated helmet with open face. Personality: stoic, immovable. Weapon: Battleaxe held in one hand on **Viewer's Right**.
5. **QUEEN** — Regal warrior queen. Full armor, pointed crown, flowing cape. Personality: commanding, fierce. Weapon: Sword held on **Viewer's Left** pointing down.
6. **KING** — Armored king. Broad flat crown, commanding stance. Personality: regal, authoritative. Weapon: Short royal sceptre held on **Viewer's Right**.

**ROW SPECIFICATIONS:**
Row 1: White Set — Normal Pose, no chomp.
Row 2: White Set — **MANDATORY CHOMP POSE** (Mouth Wide Open, Teeth Visible). **Ensure ALL characters chomp**.
Row 3: Black Set — Normal Pose, no chomp.
Row 4: Black Set — **MANDATORY CHOMP POSE** (Mouth Wide Open, Teeth Visible). **Ensure ALL characters chomp**.

**CONSISTENCY RULES:**
- Weapon hand assignment is **LOCKED** per character across all 4 rows. Do not mirror or swap hands between White and Black sets.
- Chomp pose only changes facial expression; body, armor, and weapon placement remain identical (unless they're blocking the facial expression).
- Maintain consistent pixel density, line weight, and shading across all 24 sprites.
- Give each character distinct personality and posture while keeping the set cohesive.

### Result

Final version — sprites extracted and used as `game/assets/`.

---

## Sprite Extraction

Getting clean individual sprites from the AI-generated sheet turned out to be the hardest part of the pipeline. Two problems stood out.

### Background removal

The sprite sheets came with a white background, so extraction required removing it to get transparent PNGs. A simple global threshold (delete all near-white pixels) doesn't work — it also wipes out interior white areas like teeth, sword blades, and armor highlights that are essential to the art.

The solution was a **flood-fill from the sheet edges**: only pixels reachable from the border are treated as background and removed. This correctly preserves enclosed white areas inside each character.

One exception: the **black bishop**. Its crozier (staff) curves close to the robe, creating an enclosed gap that the flood-fill couldn't reach from the outside. That trapped background patch had to be removed with a targeted global threshold pass applied only to that cell.

Near-white was defined as: `r > 190 and g > 190 and b > 190 and max(r,g,b) − min(r,g,b) < 50` — bright and low-saturation, to avoid clipping warm skin tones or light armor.

### Positioning within the cell

After background removal, each extracted sprite needs to be centered in its final canvas. Two axes, two strategies:

- **Horizontal** — center on the sprite's **center of mass** (weighted average of non-transparent pixel positions). This handles asymmetric poses (a character leaning left, a weapon extending right) better than a simple bounding-box midpoint.
- **Vertical** — center on the **bounding box midpoint**. The vertical center of mass is pulled down by heavy armor and feet, which made characters float too high; bounding-box centering gives a more grounded, visually stable result.
