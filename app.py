</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(
            HTML_TEMPLATE,
            results=None,
            last_run_path=None,
            interval_value=50,
            embed_mode=False,
        )

    file = request.files.get("textfile")
    if not file:
        return render_template_string(
            HTML_TEMPLATE,
            results=None,
            last_run_path=None,
            interval_value=50,
            embed_mode=False,
        )