def add_image_path(instance_id: int | str, filename: str) -> str:
    """
    Creates a path for an image in the format: instance_id/filename
    Example: 123/avatar.jpg
    """
    file_name = filename.split("/")[-1]  # Get only filename without path
    return f"{instance_id}/{file_name}"
