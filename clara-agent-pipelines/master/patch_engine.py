def apply_patch(original, patch):

    updated = original.copy()

    for key, value in patch.items():

        if value:
            updated[key] = value

    return updated
