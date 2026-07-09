"""A small 2-D line-plot helper for drawing spectra on a tkinter Canvas.

Keeps the blackbody topics free of repetitive axis / mapping code. Curves are
drawn as plain segment polylines (no smoothing) and clamped to the plot box so
a divergent curve simply runs along the top edge instead of shooting off.
"""


class Plot:
    def __init__(self, canvas, box, xrange, yrange, colors, font_small):
        self.c = canvas
        self.x0, self.y0, self.x1, self.y1 = box       # pixel box (top-left, bottom-right)
        self.xmin, self.xmax = xrange
        self.ymin, self.ymax = yrange
        self.colors = colors
        self.font = font_small

    # coordinate mapping ---------------------------------------------------
    def X(self, x):
        return self.x0 + (x - self.xmin) / (self.xmax - self.xmin) * (self.x1 - self.x0)

    def Y(self, y):
        y = max(self.ymin, min(self.ymax, y))
        return self.y1 - (y - self.ymin) / (self.ymax - self.ymin) * (self.y1 - self.y0)

    # framework ------------------------------------------------------------
    def axes(self, xlabel, ylabel, xticks=(), xtick_fmt="{:.0f}"):
        c = self.colors
        self.c.create_rectangle(self.x0, self.y0, self.x1, self.y1, outline="#334155")
        for xv in xticks:
            px = self.X(xv)
            self.c.create_line(px, self.y1, px, self.y1 + 4, fill="#334155")
            self.c.create_text(px, self.y1 + 12, text=xtick_fmt.format(xv),
                               fill=c["canvas_text"], font=self.font)
        self.c.create_text((self.x0 + self.x1) / 2, self.y1 + 28, text=xlabel,
                           fill=c["canvas_text"], font=self.font)
        self.c.create_text(self.x0 - 44, self.y0 - 14, text=ylabel, anchor="w",
                           fill=c["canvas_text"], font=self.font)

    def curve(self, xs, ys, color, width=2, dash=None):
        pts = []
        for x, y in zip(xs, ys):
            pts.append(self.X(x))
            pts.append(self.Y(y))
        if len(pts) >= 4:
            kw = {"fill": color, "width": width}
            if dash:
                kw["dash"] = dash
            self.c.create_line(*pts, **kw)

    def vline(self, x, color, label=None, dash=(3, 3)):
        px = self.X(x)
        self.c.create_line(px, self.y0, px, self.y1, fill=color, dash=dash)
        if label:
            self.c.create_text(px + 4, self.y0 + 8, text=label, anchor="w",
                               fill=color, font=self.font)

    def band(self, xa, xb, color):
        self.c.create_rectangle(self.X(xa), self.y0, self.X(xb), self.y1,
                                fill=color, outline="")

    def label(self, x, y, text, color, anchor="w"):
        self.c.create_text(self.X(x), self.Y(y), text=text, anchor=anchor,
                           fill=color, font=self.font)
