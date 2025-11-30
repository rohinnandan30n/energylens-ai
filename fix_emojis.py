#!/usr/bin/env python3
"""Replace emojis in main.py with ASCII equivalents for Windows console compatibility"""

import re

# Read the file
with open('src/cli/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Process each line
output_lines = []
for line in lines:
    # Replace only outside of docstrings/comments context
    # Only replace in print statements, not in docstrings
    if '"""' not in line and "'''" not in line:
        line = line.replace('⚡', '[POWER]')
        line = line.replace('✔', '[OK]')
        line = line.replace('📂', '[INFO]')
        line = line.replace('✅', '[YES]')
        line = line.replace('❌', '[NO]')
        line = line.replace('⚠️', '[WARN]')
        line = line.replace('🔧', '[FIX]')
        line = line.replace('🤖', '[AI]')
        line = line.replace('📊', '[CHART]')
        line = line.replace('🏆', '[TROPHY]')
        line = line.replace('🟢', '[GREEN]')
        line = line.replace('🔴', '[RED]')
        line = line.replace('🟡', '[YEL]')
        line = line.replace('⚫', '[BLK]')
        line = line.replace('💾', '[SAVE]')
        line = line.replace('💡', '[IDEA]')
        line = line.replace('🚨', '[ALERT]')
    
    output_lines.append(line)

# Write back
with open('src/cli/main.py', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("✓ Emojis replaced successfully!")
