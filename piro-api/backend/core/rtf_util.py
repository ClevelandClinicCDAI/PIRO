import io

import mammoth
from mammoth import transforms

# with open(input_filename, "rb") as docx_file:
#     result = mammoth.extract_raw_text(docx_file)
#     text = result.value # The raw text
#     with open('output.txt', 'w') as text_file:
#         text_file.write(text)


def process_file(file: str | bytes, type_name: str = "html"):
    if isinstance(file, str):
        with open(file, "rb+") as f:
            bytes_stream = f.read()
    else:
        bytes_stream = file
    html_payload = file_html_conversion(bytes_stream, type_name=type_name)
    return str(html_payload)


def _file_type_conv(
    file_stream: bytes, trans_ele=None, type_name: str = "html"
):
    stream = io.BytesIO(file_stream)
    transform_document = transforms.paragraph(trans_ele) if trans_ele else None
    func_name = f"convert_to_{type_name}"
    result = getattr(mammoth, func_name)(
        stream, transform_document=transform_document
    )
    content = result.value
    if result.messages:
        print(result.messages)
    if type_name == "html":
        split_content = [f"<h1>{ele}" for ele in content.split("<h1>") if ele]
    else:
        split_content = content.split("\\")
    return split_content


def file_html_conversion(stream: bytes, type_name: str = "html"):
    content_parts = _file_type_conv(stream, type_name=type_name)
    join_str = "," if type_name == "html" else ""
    payload = join_str.join(content_parts)
    return payload
