#!/bin/bash
# Assemble raw text training data for LoRA fine-tuning
# Curriculum order: foundations → theory → applied → civilization

CORPUS_DIR="C:/data/devops.propercode.co.uk/propercode-toolbox.claude/EDIManager/Resources"
DICT_DIR="C:/data/devops.propercode.co.uk/ultimatelaw/dictionary"
DIALOGUE_DIR="C:/data/devops.propercode.co.uk/ultimatelaw/dialogues"
CASES_DIR="C:/data/devops.propercode.co.uk/ultimatelaw/prosecution-framework/cases"
OUTPUT="C:/data/devops.propercode.co.uk/ultimatelaw/training/ul_raw_text.txt"

echo "Assembling Ultimate Law training corpus..."
> "$OUTPUT"

# === LAYER 0: Constitutional Foundation ===
echo "=== Layer 0: Constitutional Foundation ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cat "$DICT_DIR/coherent-dictionary-of-simple-english.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_ultimatelaw.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"

# === LAYER 1: Logic and Reasoning ===
echo "=== Layer 1: Logic and Reasoning ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_logic.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_maths.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_maths_advanced.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"

# === LAYER 2: Natural Sciences ===
echo "=== Layer 2: Natural Sciences ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_physics.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_chemistry.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_chemistry_practical.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_biology.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_biology_advanced.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_science.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"

# === LAYER 3: Human Sciences ===
echo "=== Layer 3: Human Sciences ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_economics.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_history.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"

# === LAYER 4: Survival and Practical ===
echo "=== Layer 4: Survival and Practical Knowledge ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_survival.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_agriculture.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_materials.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_medicine_practical.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_tools.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"

# === LAYER 5: Technology and Infrastructure ===
echo "=== Layer 5: Technology and Infrastructure ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_infrastructure.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_electronics.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_transportation.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_communication.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_navigation.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_organization.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"

# === LAYER 6: Advanced Technology ===
echo "=== Layer 6: Advanced Technology ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_technology_engineering.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_technology_computing.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_technology_ai.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_technology_health.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"

# === LAYER 7: Extended Dictionary ===
echo "=== Layer 7: Extended Vocabulary ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cat "$DICT_DIR/coherent-dictionary-extended.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"

# === LAYER 8: Stories and Narrative ===
echo "=== Layer 8: Narrative and Applied Reasoning ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cat "$CORPUS_DIR/corpus_stories.txt" >> "$OUTPUT"
echo -e "\n\n" >> "$OUTPUT"

# === LAYER 9: AI Dialogues (stress-testing) ===
echo "=== Layer 9: Cross-Model Dialogue Transcripts ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
for f in "$DIALOGUE_DIR"/2026-02-12-*.md "$DIALOGUE_DIR"/2026-02-13-*.md; do
    if [ -f "$f" ]; then
        echo "--- $(basename "$f") ---" >> "$OUTPUT"
        cat "$f" >> "$OUTPUT"
        echo -e "\n\n" >> "$OUTPUT"
    fi
done

# === LAYER 10: Prosecution Cases ===
echo "=== Layer 10: Prosecution Framework (Applied Ethics) ===" >> "$OUTPUT"
echo "" >> "$OUTPUT"
for f in "$CASES_DIR"/*.md; do
    if [ -f "$f" ]; then
        echo "--- $(basename "$f") ---" >> "$OUTPUT"
        cat "$f" >> "$OUTPUT"
        echo -e "\n\n" >> "$OUTPUT"
    fi
done

# Report
LINES=$(wc -l < "$OUTPUT")
SIZE=$(wc -c < "$OUTPUT")
echo ""
echo "=== Assembly Complete ==="
echo "Output: $OUTPUT"
echo "Lines: $LINES"
echo "Size: $SIZE bytes ($(echo "scale=1; $SIZE/1048576" | bc) MB)"
echo "Estimated tokens: ~$(echo "scale=0; $SIZE/4" | bc)"
