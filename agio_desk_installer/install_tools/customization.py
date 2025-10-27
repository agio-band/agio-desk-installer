import base64
import re


def parse_custom_code(src_data: str) -> dict:
    try:
        src_data = base64.b64decode(src_data).decode()
    except Exception as e:
        pass
    result = {}
    for line in src_data.strip().splitlines():
        pkg_name, data = parse_line(line)
        if pkg_name:
            if pkg_name in result:
                raise RuntimeError(f"Duplicate package name '{pkg_name}'")
            result[pkg_name] = data
    return result


def parse_args(version_args: list[str]) -> dict:
    versions = {}
    for pkg_line in version_args:
        pkg, data = parse_line(pkg_line)
        if pkg:
            versions[pkg] = data
    return versions


def parse_line(line: str) -> (str, dict):
    match = re.match(r"([\w\-_]+):(\w+)=(.+)", line.strip())
    if match:
        pkg, ref_type, value = match.groups()
        return pkg, {'ref_type': ref_type, 'value': value, 'raw': line.strip()}
    else:
        return None, None


if __name__ == '__main__':
    # example
    src = """
        agio-core:branch=dev
        agio-pipe:tag=0.0.1
        agio-desk:commit=d947745
    """
    src = '\n'.join([line.strip() for line in src.split()])
    code = base64.b64encode(src.strip().encode()).decode()
    print(parse_custom_code(code))
