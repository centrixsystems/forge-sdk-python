# forge-sdk

Python SDK for the [Forge](https://github.com/centrixsystems/forge) rendering engine. Converts HTML/CSS to PDF, PNG, and other formats via a running Forge server.

## Installation

```sh
pip install forge-sdk
```

## Quick Start

```python
import asyncio
from forge_sdk import ForgeClient, OutputFormat

async def main():
    client = ForgeClient("http://localhost:3000")

    pdf = await client.render_html("<h1>Invoice #1234</h1>") \
        .format(OutputFormat.PDF) \
        .paper("a4") \
        .send()

    with open("invoice.pdf", "wb") as f:
        f.write(pdf)

asyncio.run(main())
```

## Sync Usage

```python
from forge_sdk import ForgeClient, OutputFormat

client = ForgeClient("http://localhost:3000")

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
    .send()
```

### Color Quantization

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

### Health Check

```python
healthy = await client.health()
# or sync:
healthy = client.health_sync()
```

## API Reference

### `ForgeClient(base_url, *, timeout=120.0)`

| Method | Description |
|--------|-------------|
| `render_html(html)` | Start a render request from an HTML string |
| `render_url(url)` | Start a render request from a URL |
| `health()` | Check server health (async) |
| `health_sync()` | Check server health (sync) |

### `RenderRequestBuilder`

All methods return `self` for chaining. Call `.send()` (async) or `.send_sync()` (sync) to execute.

| Method | Type | Description |
|--------|------|-------------|
| `format` | `OutputFormat` | Output format (default: PDF) |
| `width` | `int` | Viewport width in CSS pixels |
| `height` | `int` | Viewport height in CSS pixels |
| `paper` | `str` | Paper size: a3, a4, a5, b4, b5, letter, legal, ledger |
| `orientation` | `Orientation` | PORTRAIT or LANDSCAPE |
| `margins` | `str` | Preset (default, none, narrow) or "T,R,B,L" in mm |
| `flow` | `Flow` | AUTO, PAGINATE, or CONTINUOUS |
| `density` | `float` | Output DPI (default: 96) |
| `background` | `str` | CSS background color |
| `timeout` | `int` | Page load timeout in seconds |
| `colors` | `int` | Quantization color count (2-256) |
| `palette` | `Palette \| list[str]` | Color palette preset or custom hex colors |
| `dither` | `DitherMethod` | Dithering algorithm |

### Enums

- **`OutputFormat`**: PDF, PNG, JPEG, BMP, TGA, QOI, SVG
- **`Orientation`**: PORTRAIT, LANDSCAPE
- **`Flow`**: AUTO, PAGINATE, CONTINUOUS
- **`Palette`**: AUTO, BLACK_WHITE, GRAYSCALE, EINK
- **`DitherMethod`**: NONE, FLOYD_STEINBERG, ATKINSON, ORDERED

### Errors

- **`ForgeError`** — base exception
- **`ForgeServerError(status, message)`** — 4xx/5xx server responses
- **`ForgeConnectionError(cause)`** — network/connection failures

## License

MIT
