def write_markdown_file(content, filename):
    """Writes the given content as a markdown file to the local directory.

    Args:
        content: The string content to write to the file.
        filename: The filename to save the file as.
    """
    if type(content) == dict:
        content = '\n'.join(f"{key}: {value}" for key, value in content.items())
    if type(content) == list:
        content = '\n'.join(content)
    with open(f"{filename}.md", "w") as f:
        f.write(content)