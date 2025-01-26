import json
from argparse import ArgumentParser
import os
from base64 import b64encode
from fastkml import kml
import requests
from pathlib import Path
from bs4 import BeautifulSoup


def parse_gme_geometry(gme_geometry):
    return gme_geometry[6][0]


def parse_feature_order(feature_order):
    return feature_order[4]


def parse_place_ref(place_ref):
    return place_ref[4]


def parse_gx_metafeatureid(gx_metafeatureid):
    return gx_metafeatureid[4]


def parse_name(name):
    return name[4]


def parse_description(description):
    return description[4]


def parse_record_content(record_content):
    coordinates = parse_gme_geometry(record_content[0])
    feature_order = parse_feature_order(record_content[1])
    place_ref = parse_place_ref(record_content[2])
    gx_metafeatureid = parse_gx_metafeatureid(record_content[3])
    name = parse_name(record_content[4])
    description = parse_description(record_content[5])

    return {
        "coordinates": coordinates,
        "feature_order": feature_order,
        "place_ref": place_ref,
        "gx_metafeatureid": gx_metafeatureid,
        "name": name,
        "description": description,
    }


def parse_record_images(record_images, convert_images_to_base64=False):
    images = []
    for record_image in record_images:
        image_code = record_image[0]
        image_url = record_image[3]

        if convert_images_to_base64:
            image_content = requests.get(image_url).content
            image_url = f"data:image/jpeg;base64,{b64encode(image_content).decode()}"

        images.append(
            {
                "image_code": image_code,
                "image_url": image_url,
            }
        )
    return images


def parse_map_folder(map_folder, convert_images_to_base64=False):
    map_folder_name = map_folder[1]
    map_records = map_folder[17]

    records = []
    for record in map_records:
        record_content = parse_record_content(record[11])
        try:
            images = parse_record_images(record[14], convert_images_to_base64)
        except IndexError:
            images = []

        records.append(
            {
                **record_content,
                "images": images,
            }
        )

    # with open("test.json", "w") as f:
    #     json.dump(map_data[1][0][17], f, indent=4)

    return {
        "map_folder_name": map_folder_name,
        "records": records,
    }


def parse_page_data(page_data_file_path, convert_images_to_base64=False):
    with open(page_data_file_path) as f:
        page_data = json.load(f)

    map_data = page_data["mapdataJson"]

    map_folders = []
    for map_folder in map_data[1]:
        map_folders.append(
            parse_map_folder(
                map_folder, convert_images_to_base64=convert_images_to_base64
            )
        )

    return map_folders


def generate_description_with_images(record, description=None):
    if description is None:
        description = record["description"]

    # Try to parse description as HTML and return the text content
    try:
        description = BeautifulSoup(description, "html.parser").get_text()
    except Exception as e:
        pass

    images = record["images"]

    image_tags = "".join("{{" + image["image_url"] + "}}<br>" for image in images)
    return f"{image_tags}{description}"


def merge_kml_and_page_data(input_km_path: str, page_data: dict, output_kml_path: str):
    k = kml.KML.parse(input_km_path)

    assert len(k.features) == 1

    document = k.features[0]
    folders = document.features

    # print(folders)
    print(len(folders))
    print(len(page_data))
    # print(folders[0])

    for folder, page_folder in zip(folders, page_data):
        assert folder.name == page_folder["map_folder_name"]
        assert len(folder.features) == len(page_folder["records"])

        for placemark, page_record in zip(folder.features, page_folder["records"]):
            # print(f"Record Name: {placemark.name}")
            # print(f"Placemark Name: {placemark.name}")
            # assert placemark.name == page_record["name"]
            # print(f"Processing {page_record['name']}...")

            # if str(placemark.description).strip() != page_record["description"].strip():
            #     print(f"Record Description: {page_record['description']}")
            #     print(f"Placemark Description: {placemark.description}")

            #     # Print the characters that are different
            #     for i, (a, b) in enumerate(
            #         zip(str(placemark.description), page_record["description"])
            #     ):
            #         if a != b:
            #             print(f"Index: {i}, Placemark: {a}, Page Record: {b}")

            # assert (
            #     str(placemark.description).strip() == page_record["description"].strip()
            # )

            placemark.description = generate_description_with_images(
                page_record, placemark.description
            )

    k.write(Path(output_kml_path))


def main():
    parser = ArgumentParser()
    # Create three arguments: page_data, input_kml, output_kml with default values of page_data.json, input.kml, output.kml
    parser.add_argument("--page_data", default=os.path.join("exports", "pageData.json"))
    parser.add_argument("--input_kml", default=os.path.join("exports", "input.kml"))
    parser.add_argument("--output_kml", default=os.path.join("exports", "output.kml"))
    args = parser.parse_args()

    page_data = parse_page_data(args.page_data, convert_images_to_base64=True)

    merge_kml_and_page_data(args.input_kml, page_data, args.output_kml)


if __name__ == "__main__":
    main()
