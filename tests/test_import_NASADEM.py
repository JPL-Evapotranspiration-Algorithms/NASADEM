def test_import_NASADEM():
    import NASADEM

    assert hasattr(NASADEM, "__version__")