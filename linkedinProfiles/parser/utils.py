def generate_new_id(df, id_column):
    if df.empty:
        return 0
    else:
        return df[id_column].max() + 1

def get_or_add_id(entity, df, name_column, id_column):
    # check if entity already exists in the DataFrame
    existing_entity = df.loc[df[name_column] == entity[name_column]]

    if not existing_entity.empty:
        # if entity exists, return its ID
        return existing_entity.iloc[0][id_column], df
    else:
        # if entity doesn't exist, generate a new ID, add them to DataFrame, and return the ID
        new_id = generate_new_id(df, id_column)  # function to generate new unique id
        entity[id_column] = new_id
        df = df.append(entity, ignore_index=True)
        return new_id, df