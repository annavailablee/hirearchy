"""Build a minimal valid PDF in memory for tests. Avoids committing binary fixtures."""


def make_minimal_pdf(text: str = "Hello world") -> bytes:
    """
    Hand-roll a tiny single-page PDF containing `text`.
    This is the smallest valid PDF structure we can produce without a library.
    """
    objects: list[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)

    # Object 1: Catalog
    catalog_num = add(b"<< /Type /Catalog /Pages 2 0 R >>")
    # Object 2: Pages
    pages_num = add(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")

    # Object 3: Page. Content stream is object 4.
    page_num = add(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
    )

    # Object 4: Content stream
    stream_body = f"BT /F1 24 Tf 72 700 Td ({text}) Tj ET".encode("latin-1")
    content_num = add(
        b"<< /Length " + str(len(stream_body)).encode() + b" >>\nstream\n"
        + stream_body + b"\nendstream"
    )

    # Object 5: Font
    add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    # Assemble the PDF
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]  # index 0 unused; offsets[i] is offset for object i
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode()
        out += obj
        out += b"\nendobj\n"

    xref_offset = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()

    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    ).encode()

    return bytes(out)