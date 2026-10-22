# scripts/extreureValors.py
import argparse
from pathlib import Path
import textwrap

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2, norm


var_labels = {
    "speech_rate": "Speech rate",
    "vdist_cent_mean": "Mean V-to-V",
    "vdist_cent_sd": "SD V-to-V",
    "delta_v": "ΔV (ms)",
    "delta_c": "ΔC (ms)",
    "percentage_v": "%V",
    "varco_v": "VarcoV",
    "varco_c": "VarcoC",
    "rpvi_v": "rPVI-V",
    "rpvi_c": "rPVI-C",
    "npvi_v": "nPVI-V",
    "npvi_c": "nPVI-C",
}

order_vars = [
    "Speech rate",
    "%V",
    "ΔV (ms)",
    "ΔC (ms)",
    "VarcoV",
    "VarcoC",
    "rPVI-V",
    "rPVI-C",
    "nPVI-V",
    "nPVI-C",
    "Mean V-to-V",
    "SD V-to-V",
]


def wrap(s, width=14):
    return "\n".join(textwrap.wrap(str(s), width=width))


def build_plot(df_audio: pd.DataFrame, robust_params: pd.DataFrame, out_png: Path):
    common_vars = sorted(set(robust_params["variable"]).intersection(df_audio.columns))
    if not common_vars:
        raise ValueError(
            "No common variables between robust_params['variable'] and the audio CSV columns."
        )

    rp = robust_params[robust_params["variable"].isin(common_vars)].copy()

    # assume 1 row
    rp["new"] = [df_audio[var].iloc[0] for var in rp["variable"]]
    rp["center"] = rp["center_robust"]
    rp["sd"] = rp["sd_robust"]
    rp["z"] = (rp["new"] - rp["center"]) / rp["sd"]

    df_w_summary = rp[["variable", "new", "z", "center", "sd"]].copy()
    df_w_summary["variable_label"] = df_w_summary["variable"].map(var_labels).fillna(df_w_summary["variable"])

    z_vals = df_w_summary["z"].to_numpy()
    mask = ~np.isnan(z_vals)
    k = int(mask.sum())
    mahal2_approx = float(np.nansum(z_vals[mask] ** 2))
    global_percentile = float(chi2.cdf(mahal2_approx, df=k) * 100) if k > 0 else float("nan")

    mean_abs_z = float(np.nanmean(np.abs(z_vals)))
    mean_percentile = float(np.nanmean(norm.cdf(z_vals[mask]) * 100)) if k > 0 else float("nan")

    order_present = [v for v in order_vars if v in df_w_summary["variable_label"].values]

    df_plot = df_w_summary.copy()
    df_plot["variable_label"] = pd.Categorical(
        df_plot["variable_label"], categories=order_present, ordered=True
    )
    df_plot = df_plot.sort_values("variable_label", ascending=False).reset_index(drop=True)
    df_plot["y"] = np.arange(len(df_plot))

    z_max = np.nanmax(np.abs(df_plot["z"].to_numpy()))
    lim = max(3.0, float(z_max) * 1.05)

    fig, ax = plt.subplots(figsize=(10, 7), dpi=140)

    # normality band [-2,2]
    for _, row in df_plot.iterrows():
        y = row["y"]
        ax.add_patch(
            plt.Rectangle((-2, y - 0.4), 4, 0.8, alpha=0.4, edgecolor="none", zorder=1)
        )

    ax.axvline(x=0, linestyle="--", linewidth=1, zorder=2)
    ax.scatter(df_plot["z"], df_plot["y"], s=30, zorder=3)

    ax.set_xlim(-lim, lim)
    ax.set_yticks(df_plot["y"])
    ax.set_yticklabels([wrap(v, 14) for v in df_plot["variable_label"]])
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.subplots_adjust(left=0.28)

    subtitle = "Observed value (z) ~ estimated normality (center ± 2 robust SD)"
    fig.suptitle("Normality per variable", fontsize=14, y=0.98)
    ax.set_title(subtitle, fontsize=10, pad=10)

    caption_text = (
        f"• Multivariate percentile (χ²): {global_percentile:.2f}% — global profile.\n"
        f"• Mean |z|: {mean_abs_z:.2f} — aggregated global deviation.\n"
        f"• Mean univariate percentile: {mean_percentile:.2f}% — average normality."
    )
    fig.text(0.01, 0.01, caption_text, ha="left", va="bottom", fontsize=9)

    plt.tight_layout(rect=(0, 0.14, 1, 0.92))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--df-audio", required=True, help="CSV with 1 row of metrics (R output)")
    parser.add_argument("--robust-xlsx", required=True, help="Excel with columns variable, center_robust, sd_robust")
    parser.add_argument("--out-png", required=True, help="Output PNG path")
    args = parser.parse_args()

    df_audio = pd.read_csv(args.df_audio, sep=None, engine="python")
    robust_params = pd.read_excel(args.robust_xlsx)

    build_plot(df_audio, robust_params, Path(args.out_png))


if __name__ == "__main__":
    main()
