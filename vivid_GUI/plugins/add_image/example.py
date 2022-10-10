def before(data, img_con):
    return {**data, "name": f"{data['name']} is present"}


description = "Adds ' is present' to image name"

title = "Example Plugin"
