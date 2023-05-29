from nameparser import HumanName

def generate_name_variations(name_str):
    # Remove specified words from name string
    name_str = name_str.replace(" de ", " ").replace(" do ", " ").replace(" da ", " ").replace(" dos ", " ").replace(" das ", " ")

    def append_variation(variation, variations):

        if variation not in variations:
            variations.append(variation)
        
        return variations

    # Full name variation
    variations = []
    variations.append(f"{name_str}") # full name

    # Extract individual name components
    name = HumanName(name_str)
    first_name = name.first
    middle_name = name.middle
    last_name = name.last

    ### Generate name variations ###
    ################################
    variation = f"{first_name} {last_name.split()[-1]}" # first and last name
    variations = append_variation(variation, variations)

    if len(middle_name.split()) > 0:
        variation = f"{first_name} {middle_name.split()[0]}" # first and second name
        variations = append_variation(variation, variations)

        variation = f"{first_name} {middle_name.split()[0]} {last_name.split()[-1]}" # first, second and last name
        variations = append_variation(variation, variations)

    if len(middle_name.split()) > 1:
        variation = f"{first_name} {middle_name.split()[1]} {last_name}" # all names except the second
        variations = append_variation(variation, variations)

    print(variations)

    return variations