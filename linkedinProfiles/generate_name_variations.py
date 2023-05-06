from nameparser import HumanName

def generate_name_variations(name_str):
    # Full name variation
    variations = []
    variations.append(f"{name_str}") # full name

    # Remove specified words from name string
    name_str = name_str.replace(" de ", " ").replace(" do ", " ").replace(" da ", " ").replace(" dos ", " ").replace(" das ", " ")
    
    name = HumanName(name_str)

    # Extract individual name components
    first_name = name.first
    middle_name = name.middle
    last_name = name.last

    # Generate name variations
    variations.append(f"{first_name} {last_name.split()[-1]}") # first and last name
    variations.append(f"{first_name} {middle_name.split()[0]}")# first and second name
    
    variation = f"{first_name} {middle_name.split()[0]} {last_name.split()[-1]}" # first, second and last name
    if variation not in variations:
        variations.append(variation)

    if len(middle_name.split()) > 1:
        variations.append(f"{first_name} {middle_name.split()[1]} {last_name}") # all names except the second


    # if len(middle_name) > 1:
    #     variations.append(f"{first_name} {'. '.join([n[0] for n in middle_name.split()])}. {last_name}")

    # if len(last_name) > 1:
    #     variations.append(f"{first_name} {middle_name} {'. '.join([n[0] for n in last_name.split()])}.")

    # if len(middle_name) > 1 and len(last_name) > 1:
    #     variations.append(f"{first_name} {'. '.join([n[0] for n in middle_name.split()])}. {'. '.join([n[0] for n in last_name.split()])}.")

    return variations