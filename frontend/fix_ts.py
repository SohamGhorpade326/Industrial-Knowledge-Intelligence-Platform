import os
import re

def fix_imports_and_font_weight(root_dir):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if not file.endswith(('.ts', '.tsx')):
                continue
            
            filepath = os.path.join(subdir, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix imports
            content = re.sub(r"import \{([^}]+)\} from '(\.\./)+types';", r"import type {\1} from '\2types';", content)
            
            # Fix unused imports by just removing the ts-check or letting it slide?
            # Unused imports are better fixed manually or by just turning off the strict unused-imports check.
            
            # Fix fontWeight={X} in Typography
            # Let's find all instances of <Typography ... fontWeight={X} ... >
            # We can just replace fontWeight={X} with sx={{ fontWeight: X }} if there is no sx=
            # Or if there is sx={{ ... }}, we inject fontWeight: X, into it.
            
            def replace_font_weight(match):
                before_fw = match.group(1)
                fw_val = match.group(2)
                after_fw = match.group(3)
                
                # Check if there is an sx={{ in before_fw or after_fw (within the same tag)
                tag_content = before_fw + after_fw
                
                if 'sx={{' in tag_content:
                    # Inject fontWeight into existing sx
                    new_after = re.sub(r'sx=\{\{\s*', f'sx={{{{ fontWeight: {fw_val}, ', after_fw)
                    if new_after == after_fw:
                        new_before = re.sub(r'sx=\{\{\s*', f'sx={{{{ fontWeight: {fw_val}, ', before_fw)
                        return f"<Typography {new_before}{new_after}"
                    return f"<Typography {before_fw}{new_after}"
                else:
                    return f"<Typography {before_fw}sx={{{{ fontWeight: {fw_val} }}}} {after_fw}"

            
            content = re.sub(r"<Typography([^>]*)fontWeight=\{([^}]+)\}([^>]*)", replace_font_weight, content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

fix_imports_and_font_weight(r'c:\Users\Amol G\Documents\ET-2.0\frontend\src')
