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
