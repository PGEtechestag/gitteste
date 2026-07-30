import platform

os_name = platform.system()

# Map system names to user-friendly names
friendly_names = {
    "Darwin": "macOS",
    "Windows": "Windows",
    "Linux": "Linux",
    "Java": "Java",
}

friendly_name = friendly_names.get(os_name, os_name)
print(f"You're using this {friendly_name} OS")