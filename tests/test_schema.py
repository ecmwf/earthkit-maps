from magpye import schema


def test_default_schema():
    schema.use("default")


def test_set():
    font = "verdana"
    schema.set(font=font)
    assert schema.font == font


def test_set_context_manager():
    font = "verdana"
    schema.set(font=font)

    tmp_font = "comic sans"
    with schema.set(font=tmp_font):
        assert schema.font == tmp_font

    assert schema.font == font
