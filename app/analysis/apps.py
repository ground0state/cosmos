from django.apps import AppConfig
import os
from .const import DATA_DIR, MODEL_DIR


class AnalysisConfig(AppConfig):
    name = 'analysis'

    def ready(self):

        if not os.path.isdir(DATA_DIR):
            os.mkdir(DATA_DIR)

        if not os.path.isdir(MODEL_DIR):
            os.mkdir(MODEL_DIR)
