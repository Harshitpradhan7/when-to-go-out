def label_windows(windows: list):
    scores = [w["exposure"] for w in windows]
    scores_sorted = sorted(scores)

    def percentile(score):
        return scores_sorted.index(score) / len(scores_sorted)

    for w in windows:
        p = percentile(w["exposure"])
        if p <= 0.2:
            w["label"] = "Best"
        elif p <= 0.5:
            w["label"] = "Acceptable"
        else:
            w["label"] = "Avoid"

    return windows
