"""Type definitions for the Forge SDK."""

from enum import Enum


class OutputFormat(str, Enum):
    """Output format for rendered content."""

    PDF = "pdf"
    PNG = "png"
    JPEG = "jpeg"
    BMP = "bmp"
    TGA = "tga"
    QOI = "qoi"
    SVG = "svg"


class Orientation(str, Enum):
    """Page orientation."""

    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class Flow(str, Enum):
    """Document flow mode."""

    AUTO = "auto"
    PAGINATE = "paginate"
    CONTINUOUS = "continuous"


class DitherMethod(str, Enum):
    """Dithering algorithm for color quantization."""

    NONE = "none"
    FLOYD_STEINBERG = "floyd-steinberg"
    ATKINSON = "atkinson"
    ORDERED = "ordered"


class Palette(str, Enum):
    """Built-in color palette presets."""

    AUTO = "auto"
    BLACK_WHITE = "bw"
    GRAYSCALE = "grayscale"
    EINK = "eink"


class WatermarkLayer(str, Enum):
    """Watermark layer position."""

    OVER = "over"
    UNDER = "under"


class PdfStandard(str, Enum):
    """PDF standard compliance level."""

    NONE = "none"
    A2B = "pdf/a-2b"
    A3B = "pdf/a-3b"


class EmbedRelationship(str, Enum):
    """Relationship of embedded file to the PDF document."""

    ALTERNATIVE = "alternative"
    SUPPLEMENT = "supplement"
    DATA = "data"
    SOURCE = "source"
    UNSPECIFIED = "unspecified"


class PdfMode(str, Enum):
    """PDF rendering mode."""

    AUTO = "auto"
    VECTOR = "vector"
    RASTER = "raster"


class AccessibilityLevel(str, Enum):
    """PDF accessibility compliance level."""

    NONE = "none"
    BASIC = "basic"
    PDF_UA_1 = "pdf/ua-1"


class BarcodeType(str, Enum):
    """Barcode type for PDF barcode overlays."""

    QR = "qr"
    CODE128 = "code128"
    EAN13 = "ean13"
    UPCA = "upca"
    CODE39 = "code39"


class BarcodeAnchor(str, Enum):
    """Anchor position for barcode placement."""

    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
