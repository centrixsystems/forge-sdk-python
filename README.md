# forge-sdk

Python SDK for the [Forge](https://github.com/centrixsystems/forge) rendering engine. Converts HTML/CSS to PDF, PNG, and other formats via a running Forge server.

Uses [`httpx`](https://www.python-httpx.org/) for both async and sync HTTP. Supports Python 3.9+.

## Installation

```sh
pip install forge-sdk
```

## Quick Start

### Async

```python
import asyncio
from forge_sdk import ForgeClient, OutputFormat

async def main():
    async with ForgeClient("http://localhost:3000") as client:
        pdf = await client.render_html("<h1>Invoice #1234</h1>") \
            .format(OutputFormat.PDF) \
            .paper("a4") \
            .send()

        with open("invoice.pdf", "wb") as f:
            f.write(pdf)

asyncio.run(main())
```

### Sync

```python
from forge_sdk import ForgeClient, OutputFormat

with ForgeClient("http://localhost:3000") as client:
    pdf = client.render_html("<h1>Invoice #1234</h1>") \
        .format(OutputFormat.PDF) \
        .paper("a4") \
        .send_sync()

    with open("invoice.pdf", "wb") as f:
        f.write(pdf)
```

## Usage

### Render HTML to PDF

```python
from forge_sdk import Orientation, Flow

pdf = await client.render_html("<h1>Hello</h1>") \
    .format(OutputFormat.PDF) \
    .paper("a4") \
    .orientation(Orientation.PORTRAIT) \
    .margins("25.4,25.4,25.4,25.4") \
    .flow(Flow.PAGINATE) \
    .send()
```

### Render URL to PNG

```python
png = await client.render_url("https://example.com") \
    .format(OutputFormat.PNG) \
    .width(1280) \
    .height(800) \
    .density(2.0) \
    .send()
```

### Color Quantization

Reduce colors for e-ink displays or limited-palette output.

```python
from forge_sdk import Palette, DitherMethod

eink = await client.render_html("<h1>Dashboard</h1>") \
    .format(OutputFormat.PNG) \
    .palette(Palette.EINK) \
    .dither(DitherMethod.FLOYD_STEINBERG) \
    .send()
```

### Custom Palette

```python
img = await client.render_html("<h1>Brand</h1>") \
    .format(OutputFormat.PNG) \
    .palette(["#000000", "#ffffff", "#ff0000"]) \
    .dither(DitherMethod.ATKINSON) \
    .send()
```

### PDF Metadata

Embed document metadata and enable bookmark/outline generation in PDF output.

```python
pdf = await client.render_html("<h1>Invoice #1234</h1>") \
    .format(OutputFormat.PDF) \
    .paper("a4") \
    .pdf_title("Invoice #1234") \
    .pdf_author("Centrix ERP") \
    .pdf_subject("Monthly billing") \
    .pdf_keywords("invoice,billing,2026") \
    .pdf_creator("forge-sdk-python") \
    .pdf_bookmarks(True) \
    .send()
```

### Health Check

```python
# Async
healthy = await client.health()

# Sync
healthy = client.health_sync()
```

### Resource Management

`ForgeClient` maintains connection pools internally. Use it as a context manager for automatic cleanup:

```python
# Async context manager
async with ForgeClient("http://localhost:3000") as client:
    pdf = await client.render_html("<h1>Hi</h1>").send()

# Sync context manager
with ForgeClient("http://localhost:3000") as client:
    pdf = client.render_html("<h1>Hi</h1>").send_sync()

# Manual cleanup
client = ForgeClient("http://localhost:3000")
try:
    pdf = client.render_html("<h1>Hi</h1>").send_sync()
finally:
    client.close()
```

## API Reference

### `ForgeClient(base_url, *, timeout=120.0)`

| Method | Description |
|--------|-------------|
| `render_html(html)` | Start a render request from an HTML string |
| `render_url(url)` | Start a render request from a URL |
| `health()` | Check server health (async) |
| `health_sync()` | Check server health (sync) |
| `close()` | Close underlying HTTP connections (sync) |
| `aclose()` | Close underlying HTTP connections (async) |

Implements both sync (`with`) and async (`async with`) context manager protocols.

### `RenderRequestBuilder`

All methods return `self` for chaining. Call `.send()` (async) or `.send_sync()` to execute.

| Method | Type | Description |
|--------|------|-------------|
| `format` | `OutputFormat` | Output format (default: `PDF`) |
| `width` | `int` | Viewport width in CSS pixels |
| `height` | `int` | Viewport height in CSS pixels |
| `paper` | `str` | Paper size: a3, a4, a5, b4, b5, letter, legal, ledger |
| `orientation` | `Orientation` | `PORTRAIT` or `LANDSCAPE` |
| `margins` | `str` | Preset (`default`, `none`, `narrow`) or `"T,R,B,L"` in mm |
| `flow` | `Flow` | `AUTO`, `PAGINATE`, or `CONTINUOUS` |
| `density` | `float` | Output DPI (default: 96) |
| `background` | `str` | CSS background color (e.g. `"#ffffff"`) |
| `timeout` | `int` | Page load timeout in seconds |
| `colors` | `int` | Quantization color count (2-256) |
| `palette` | `Palette \| list[str]` | Color palette preset or list of hex strings |
| `dither` | `DitherMethod` | Dithering algorithm |
| `pdf_title` | `str` | PDF document title metadata |
| `pdf_author` | `str` | PDF document author metadata |
| `pdf_subject` | `str` | PDF document subject metadata |
| `pdf_keywords` | `str` | PDF keywords (comma-separated) |
| `pdf_creator` | `str` | PDF creator tool metadata |
| `pdf_bookmarks` | `bool` | Enable PDF bookmarks/outline generation |

### Enums

| Enum | Values |
|------|--------|
| `OutputFormat` | `PDF`, `PNG`, `JPEG`, `BMP`, `TGA`, `QOI`, `SVG` |
| `Orientation` | `PORTRAIT`, `LANDSCAPE` |
| `Flow` | `AUTO`, `PAGINATE`, `CONTINUOUS` |
| `Palette` | `AUTO`, `BLACK_WHITE`, `GRAYSCALE`, `EINK` |
| `DitherMethod` | `NONE`, `FLOYD_STEINBERG`, `ATKINSON`, `ORDERED` |

### Errors

| Exception | Description |
|-----------|-------------|
| `ForgeError` | Base exception for all SDK errors |
| `ForgeServerError` | Server returned 4xx/5xx (has `.status` and `.message`) |
| `ForgeConnectionError` | Network failure (has `.cause`) |

## Requirements

- Python 3.9+
- `httpx >= 0.24`
- A running [Forge](https://github.com/centrixsystems/forge) server

## License

MIT
