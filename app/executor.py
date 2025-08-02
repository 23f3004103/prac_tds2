import io
import base64
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from .utils import fig_to_base64_uri

def convert_np_types(obj):
    if isinstance(obj, dict):
        return {k: convert_np_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_np_types(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_np_types(i) for i in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    elif isinstance(obj, plt.Figure):
        return fig_to_base64_uri(obj)
    else:
        return obj

def safe_execute(code: str) -> dict:
    try:
        local_vars = {}
        exec(code, {
            "__builtins__": __builtins__,
            "plt": plt,
            "io": io,
            "base64": base64,
            "np": np,
            "pd": pd
        }, local_vars)
        if "result" not in local_vars:
            return {"error": "Code did not assign a variable `result`."}
        return convert_np_types(local_vars["result"])
    except Exception as e:
        return {"error": str(e)}
