import matplotlib.pyplot as plt
from io import BytesIO
from itertools import accumulate


def build_progress_plot(values, goal, title, ylabel):
    cumulative = list(accumulate(values))

    plt.figure(figsize=(6, 4))

    plt.plot(
        cumulative,
        marker="o",
        label="Накоплено"
    )

    plt.axhline(
        y=goal,
        linestyle="--",
        color="red",
        label="Цель"
    )

    plt.title(title)
    plt.xlabel("запись")
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.legend()

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()

    buffer.seek(0)
    return buffer
