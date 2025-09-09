#!/usr/bin/env python3
"""
🔧 Fix Upload Headers in uploader_robust.py
Remove problematic Content-Type header
"""

import re

# Read the file
with open('lib/uploader_robust.py', 'r') as f:
    content = f.read()

# Fix 1: Remove Content-Type from session headers
content = re.sub(
    r"'Content-Type': 'application/json'",
    "# Content-Type removed for multipart compatibility",
    content
)

# Fix 2: Simplify upload method - don't mess with headers
upload_section = '''            # Upload with proper multipart handling
            response = self.session.post(
                url, 
                files=files, 
                data=data, 
                timeout=60
            )'''

content = re.sub(
    r'# Remove Content-Type header for multipart upload.*?timeout=60,  # Longer timeout for upload\s+headers=headers\s+\)',
    upload_section,
    content,
    flags=re.DOTALL
)

# Fix 3: Simplify set_active_event method
set_event_section = '''            response = self.session.post(url, json=data, timeout=self.timeout)'''

content = re.sub(
    r'# Remove Content-Type header for this request.*?response = self\.session\.post\(url, json=data, timeout=self\.timeout, headers=headers\)',
    set_event_section,
    content,
    flags=re.DOTALL
)

# Write the fixed file
with open('lib/uploader_robust.py', 'w') as f:
    f.write(content)

print("✅ Fixed upload headers in uploader_robust.py")
print("✅ Removed problematic Content-Type header")
print("✅ Simplified multipart upload handling")
