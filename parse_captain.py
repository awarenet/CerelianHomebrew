
import json
import re

def parse_captain():
    source_file = "RoS.txt"
    output_file = "class/Awarenet; Ruins of Symbaroum (Class).json"
    
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Extract Captain Text
    start_line = 4730
    end_line = 4875 
    class_lines = lines[start_line:end_line]
    
    def clean_text(text_lines):
        clean = []
        for line in text_lines:
            if "\x0c" in line:
                clean.append(line)
                continue
            s = line.strip()
            if re.match(r'^\d+$', s): continue
            if "Classes & Feats" in s: continue
            if "Captain" in s and len(s) < 20 and not s.startswith("Feature"): 
                continue 
            if "Ruins of Symbaroum" in s: continue
            clean.append(line)
        return clean

    def decolumnize(lines):
        linearized = []
        page_left = []
        page_right = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped: continue
            if "\x0c" in line:
                 linearized.extend(page_left)
                 linearized.extend(page_right)
                 page_left = []
                 page_right = []
                 continue
            if len(line) > 50:
                match = re.search(r'\s{3,}', line[45:85])
                if match:
                    split_idx = 45 + match.start()
                    left = line[:split_idx].strip()
                    right = line[split_idx:].strip()
                    if left: page_left.append(left)
                    if right: page_right.append(right)
                else:
                    if line.startswith(" " * 40):
                        page_right.append(stripped)
                    else:
                        page_left.append(stripped)
            else:
                page_left.append(stripped)
                
        linearized.extend(page_left)
        linearized.extend(page_right)
        return linearized

    cleaned_lines = decolumnize(clean_text(class_lines))
    
    class_json = {
        "name": "Captain",
        "source": "RuinsOfSymbaroumC",
        "page": 96,
        "hd": { "number": 1, "faces": 8 },
        "proficiency": ["con", "cha"],
        "startingProficiencies": {
            "armor": ["light", "medium", "shields"],
            "weapons": ["simple", "martial"],
            "skills": [ { "choose": { "from": ["animal handling", "athletics", "deception", "history", "insight", "intimidation", "perception", "persuasion", "survival"], "count": 4 } } ]
        },
        "startingEquipment": {
            "additionalFromBackground": True,
            "default": [
                "(a) chain shirt or (b) studded leather armor, longbow, and 20 arrows",
                "(a) a martial weapon and a shield or (b) two martial weapons",
                "(a) a light crossbow and 20 bolts or (b) two handaxes",
                "(a) a dungeoneer’s pack or (b) an explorer’s pack"
            ]
        },
        "classTableGroups": [
            { "colLabels": ["Features"], "rows": [] }
        ],
        "classFeatures": []
    }
    
    # Table Rows
    table_rows = []
    table_pattern = re.compile(r'^\s*(\d+)(?:st|nd|rd|th)\s+\+(\d+)\s+(.*)$')
    for line in cleaned_lines:
        m = table_pattern.match(line.strip())
        if m:
            table_rows.append([m.group(3).strip()])
    class_json["classTableGroups"][0]["rows"] = table_rows

    # Parse Features
    features_list = [
        "Fighting Style", "Tactical Acumen", "Field Dressings", "Bid to Action", 
        "Ability Score Improvement", "Extra Attack", "War Stories", "Unending Conflict", 
        "Assessment", "Captain Approaches", "Merchant Master", "Officer", "Outlaw", "Poet Warrior",
        "Polearm Fighting", "Shield Fighting", "Snare Fighting", "Two-Weapon Fighting"
    ]
    
    base_features = {}
    current_feature = None
    feature_text = []
    
    for line in cleaned_lines:
        line_s = line.strip().replace("\u00ad", "")
        found_key = None
        for k in features_list:
            if k == "Ability Score Improvement" and "Ability Score Improvement" in line_s and len(line_s) < 40:
                found_key = k
                break
            if line_s == k:
                found_key = k
                break
        
        if found_key:
            if current_feature:
                base_features[current_feature] = " ".join(feature_text).strip()
            current_feature = found_key
            feature_text = []
        else:
            if current_feature:
                feature_text.append(line_s)
    
    if current_feature:
        base_features[current_feature] = " ".join(feature_text).strip()

    # Construct JSON
    json_features = []
    optional_features = []
    
    def create_feature(name, level, text):
        return {
            "name": name,
            "source": "RuinsOfSymbaroumC",
            "page": 96,
            "className": "Captain",
            "classSource": "RuinsOfSymbaroumC",
            "level": level,
            "entries": [text]
        }

    # Fighting Style (Level 1)
    if "Fighting Style" in base_features:
        # Create base feature
        base_entries = [
            "You adopt a particular style of fighting as your specialty. Choose one of the following options. You can\u2019t take a Fighting Style option more than once, even if you later get to choose again."
        ]
        
        # Styles
        styles = {
            "Polearm Fighting": base_features.get("Polearm Fighting", ""),
            "Shield Fighting": base_features.get("Shield Fighting", ""),
            "Snare Fighting": base_features.get("Snare Fighting", ""),
            "Two-Weapon Fighting": base_features.get("Two-Weapon Fighting", "")
        }
        
        # Extract Standard 5e Styles from the main text block if present?
        # The main text for Fighting Style contains: "Archery ... Defense ... Dueling ... Great Weapon Fighting ..."
        # I need to parse them out.
        
        raw_fs = base_features["Fighting Style"]
        # Primitive splitter for standard styles
        std_styles_names = ["Archery", "Defense", "Dueling", "Great Weapon Fighting"]
        
        for sname in std_styles_names:
            if sname in raw_fs:
                # Try to extract description.
                # It's mashed in there. "Archery You gain... Defense While you..."
                # Regex split?
                pass

        # For now, let's create Optional Features for the *new* ones, and standard references for old ones?
        # Or just create Optional Features for ALL of them.
        
        # Let's add all knowns to the styles dict by scraping text
        full_fs_text = raw_fs + " " + " ".join([k + " " + v for k,v in styles.items()]) # Re-assemble mostly
        
        # Clean splitter
        all_styles_list = std_styles_names + list(styles.keys())
        
        # We can iterate and find start indices
        style_indices = []
        for s in all_styles_list:
            idx = full_fs_text.find(s + " ") # Space after name to ensure whole word
            if idx != -1:
                style_indices.append((idx, s))
        style_indices.sort()
        
        for i, (idx, name) in enumerate(style_indices):
            start = idx + len(name)
            end = style_indices[i+1][0] if i+1 < len(style_indices) else len(full_fs_text)
            desc = full_fs_text[start:end].strip()
            
            # Create Optional Feature
            opt_feat = {
                "name": name,
                "source": "RuinsOfSymbaroumC",
                "page": 96,
                "featureType": ["FS:C"], # Fighting Style: Captain
                "entries": [desc]
            }
            optional_features.append(opt_feat)
            
        json_features.append(create_feature("Fighting Style", 1, "Choose a Fighting Style from the options."))

    # Other Features
    for k, lvl in [("Tactical Acumen", 1), ("Field Dressings", 2), ("Bid to Action", 3), ("Extra Attack", 5), ("War Stories", 7), ("Unending Conflict", 20)]:
        if k in base_features:
            json_features.append(create_feature(k, lvl, base_features[k]))

    # ASI
    json_features.append(create_feature("Ability Score Improvement", 4, "When you reach 4th level..."))

    # Link everything
    for feat in json_features:
        class_json["classFeatures"].append(f"{feat['name']}|Captain|RuinsOfSymbaroumC|{feat['level']}")

    # Final Output
    output_data = {
        "_meta": {
            "sources": [
                {
                    "json": "RuinsOfSymbaroumC",
                    "full": "Ruins of Symbaroum Classes",
                    "abbreviation": "RoS:C",
                    "authors": ["Free League Publishing"],
                    "version": "1.0.0",
                    "url": "https://freeleaguepublishing.com"
                }
            ],
            "dateAdded": 1705220000,
            "dateLastModified": 1705220000
        },
        "class": [class_json],
        "classFeature": json_features,
        "optionalfeature": optional_features
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent='\t')

if __name__ == "__main__":
    parse_captain()
