from nameparser import HumanName

def generate_name_variations(name_str):
    name = HumanName(name_str)

    # Extract individual name components
    first_name = name.first
    middle_name = name.middle
    last_name = name.last

    # Generate name variations
    variations = []
    variations.append(f"{first_name} {middle_name} {last_name}") # full name
    variations.append(f"{first_name} {last_name.split()[-1]}") # first and last name

    if len(middle_name) > 1:
        variations.append(f"{first_name} {'. '.join([n[0] for n in middle_name.split()])}. {last_name}")

    if len(last_name) > 1:
        variations.append(f"{first_name} {middle_name} {'. '.join([n[0] for n in last_name.split()])}.")

    if len(middle_name) > 1 and len(last_name) > 1:
        variations.append(f"{first_name} {'. '.join([n[0] for n in middle_name.split()])}. {'. '.join([n[0] for n in last_name.split()])}.")

    return variations