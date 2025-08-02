import base64
from io import BytesIO
import matplotlib.pyplot as plt

def fig_to_base64_uri(fig, format="png", max_bytes=100_000):
    """Render a Matplotlib figure, encode as data URI (PNG/WebP)."""
    buf = BytesIO()
    fig.savefig(buf, format=format, bbox_inches="tight")
    buf.seek(0)
    data = buf.getvalue()
    if len(data) > max_bytes:
        # Try WebP if too large, else error.
        try:
            import PIL.Image
            import numpy as np
            img = PIL.Image.open(BytesIO(data))
            buf = BytesIO()
            img.save(buf, format="webp")
            data = buf.getvalue()
            if len(data) > max_bytes:
                raise Exception("Base64 image exceeds size limit")
            return "data:image/webp;base64," + base64.b64encode(data).decode()
        except Exception:
            raise Exception("Image too large and WebP conversion failed")
    return f"data:image/{format};base64," + base64.b64encode(data).decode()
