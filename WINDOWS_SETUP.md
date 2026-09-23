# AURA setup note

The original requirements file contained a very large general-purpose environment including TensorFlow, Streamlit, Supabase, OpenCV, librosa and other packages that this Django storefront does not import. On Windows this can trigger MAX_PATH/Long Path failures during TensorFlow installation.

`requirements.txt` has therefore been reduced to the dependency actually required by this Django project: Django.

The original environment list is preserved as `requirements-full.txt`.

Use `START_AURA_IN_EDGE.bat` to create the virtual environment, install the lightweight dependencies, migrate the SQLite database, seed the existing AURA catalog, start Django, and open Microsoft Edge.
