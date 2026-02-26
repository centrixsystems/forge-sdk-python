"""Unit tests for the Forge SDK client."""

from forge_sdk import (
    DitherMethod,
    Flow,
    ForgeClient,
    Orientation,
    OutputFormat,
    Palette,
)


def test_minimal_html_payload():
    client = ForgeClient("http://localhost:3000")
    builder = client.render_html("<h1>Hi</h1>")
    payload = builder._build_payload()

    assert payload["html"] == "<h1>Hi</h1>"
    assert payload["format"] == "pdf"
    assert "url" not in payload
    assert "width" not in payload
    assert "quantize" not in payload


def test_url_payload_with_options():
    client = ForgeClient("http://localhost:3000")
    builder = (
        client.render_url("https://example.com")
        .format(OutputFormat.PNG)
        .width(1280)
        .height(800)
        .paper("letter")
        .orientation(Orientation.LANDSCAPE)
        .margins("10,20,10,20")
        .flow(Flow.PAGINATE)
        .density(300.0)
        .background("#ffffff")
        .timeout(60)
    )
    payload = builder._build_payload()

    assert "html" not in payload
    assert payload["url"] == "https://example.com"
    assert payload["format"] == "png"
    assert payload["width"] == 1280
    assert payload["height"] == 800
    assert payload["paper"] == "letter"
    assert payload["orientation"] == "landscape"
    assert payload["margins"] == "10,20,10,20"
    assert payload["flow"] == "paginate"
    assert payload["density"] == 300.0
    assert payload["background"] == "#ffffff"
    assert payload["timeout"] == 60
    assert "quantize" not in payload


def test_quantize_payload():
    client = ForgeClient("http://localhost:3000")
    builder = (
        client.render_html("<p>test</p>")
        .format(OutputFormat.PNG)
        .colors(16)
        .palette(Palette.AUTO)
        .dither(DitherMethod.FLOYD_STEINBERG)
    )
    payload = builder._build_payload()

    q = payload["quantize"]
    assert q["colors"] == 16
    assert q["palette"] == "auto"
    assert q["dither"] == "floyd-steinberg"


def test_quantize_custom_palette():
    client = ForgeClient("http://localhost:3000")
    builder = (
        client.render_html("<p>test</p>")
        .palette(["#000000", "#ffffff", "#ff0000"])
        .dither(DitherMethod.ATKINSON)
    )
    payload = builder._build_payload()

    q = payload["quantize"]
    assert q["palette"] == ["#000000", "#ffffff", "#ff0000"]
    assert q["dither"] == "atkinson"


def test_no_quantize_when_unset():
    client = ForgeClient("http://localhost:3000")
    builder = client.render_html("<p>test</p>").format(OutputFormat.PNG)
    payload = builder._build_payload()
    assert "quantize" not in payload


def test_enum_values():
    assert OutputFormat.PDF.value == "pdf"
    assert OutputFormat.PNG.value == "png"
    assert OutputFormat.JPEG.value == "jpeg"
    assert Orientation.PORTRAIT.value == "portrait"
    assert Orientation.LANDSCAPE.value == "landscape"
    assert Flow.AUTO.value == "auto"
    assert Flow.PAGINATE.value == "paginate"
    assert Flow.CONTINUOUS.value == "continuous"
    assert DitherMethod.NONE.value == "none"
    assert DitherMethod.FLOYD_STEINBERG.value == "floyd-steinberg"
    assert DitherMethod.ATKINSON.value == "atkinson"
    assert DitherMethod.ORDERED.value == "ordered"
    assert Palette.AUTO.value == "auto"
    assert Palette.BLACK_WHITE.value == "bw"
    assert Palette.GRAYSCALE.value == "grayscale"
    assert Palette.EINK.value == "eink"
