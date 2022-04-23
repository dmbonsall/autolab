#!/usr/bin/python

import json
import re
import os.path
import os

from ansible.module_utils import basic
import requests


IMAGE_URL_RE = re.compile(r"^(https://.+)/(.+?\.(?:img|qcow2))$")
CHUNK_SIZE = 1024


def create_cache_dir(cache_dir_path):
    if os.path.isdir(cache_dir_path):
        return

    os.mkdir(cache_dir_path)


def read_metadata_from_cache(cache_path):
    """Gets the latest date and etag from the cache."""
    if not os.path.exists(cache_path):
        return {"images": {}}

    with open(cache_path) as f:
        data = json.load(f)

    return data


def write_metadata_to_cache(cache_path, image_name, etag):
    data = read_metadata_from_cache(cache_path)

    if not image_name in data["images"]:
        data["images"][image_name] = {}

    data["images"][image_name]["etag"] = etag

    with open(cache_path, "w") as f:
        json.dump(data, f, indent=2)


def get_image_etag(sess, image_url):
    """Gets metadata about the cloud image."""
    res = sess.head(image_url)
    res.raise_for_status()

    return res.headers["ETag"]


def download_image(sess, image_url, output_file_path):
    """Gets the latest version and adds it to cache."""
    # ===== Place the request to download the image =====
    r = sess.get(image_url, stream=True)
    r.raise_for_status()
    content_length = int(r.headers.get('Content-Length'))

    # ===== Download the image and write to disk =====
    with open(output_file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)

    return content_length


def split_image_url(image_url):
    match = IMAGE_URL_RE.match(image_url)

    if not match:
        raise ValueError("Invalid url '{image_url}'".format(image_url=image_url))

    return match.group(1), match.group(2)


def main():
    """Program entry point."""
    module = basic.AnsibleModule(argument_spec={
        "image_url": {
            "required": True,
            "type": "str",
        },
        "cache_dir": {
            "required": False,
            "type": "path",
            "default": "~/image_cache/"
        }
    })

    # ===== Validate and split the url =====
    _, image_name = split_image_url(module.params["image_url"])

    # ===== Create the cache directory if needed =====
    create_cache_dir(module.params["cache_dir"])
    cache_path = os.path.join(module.params["cache_dir"], "cache.json")

    # ===== Get cached data about our image =====
    cached_data = read_metadata_from_cache(cache_path)
    cached_image_data = cached_data["images"].get(image_name, {})
    cached_image_etag = cached_image_data.get("etag", "")

    # ===== Build the output file path =====
    output_file_path = os.path.join(module.params["cache_dir"], image_name)

    # ===== Query the image and download if needed =====
    with requests.Session() as sess:
        etag = get_image_etag(sess, module.params["image_url"])
        if etag != cached_image_etag or not os.path.exists(output_file_path):
            download_image(sess, module.params["image_url"], output_file_path)
            write_metadata_to_cache(cache_path, image_name, etag)
            changed = True
        else:
            changed = False

    module.exit_json(changed=changed, image_path=output_file_path)


if __name__ == "__main__":
    main()
