# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from tornado.escape import json_encode

from qiita_db.handlers.oauth2 import authenticate_oauth
from .rest_handler import RESTHandler


class StudySamplesHandler(RESTHandler):

    @authenticate_oauth
    def get(self, study_id):
        study = self.safe_get_study(study_id)
        if study is None:
            return

        if study.sample_template is None:
            samples = []
        else:
            samples = list(study.sample_template.keys())

        self.write(json_encode(samples))
        self.finish()


class StudySamplesCategoriesHandler(RESTHandler):

    @authenticate_oauth
    def get(self, study_id, categories):
        if not categories:
            self.fail('No categories specified', 405)
            return

        study = self.safe_get_study(study_id)
        if study is None:
            return

        categories = categories.split(',')

        if study.sample_template is None:
            self.fail('Study does not have sample information', 404)
            return

        available_categories = set(study.sample_template.categories())
        not_found = set(categories) - available_categories
        if not_found:
            self.fail('Category not found', 404,
                      categories_not_found=sorted(not_found))
            return

        blob = {'header': categories,
                'samples': {}}
        df = study.sample_template.to_dataframe()
        for idx, row in df[categories].iterrows():
            blob['samples'][idx] = list(row)

        self.write(json_encode(blob))
        self.finish()


class StudySamplesInfoHandler(RESTHandler):

    @authenticate_oauth
    def get(self, study_id):
        study = self.safe_get_study(study_id)
        if study is None:
            return

        st = study.sample_template
        if st is None:
            info = {'number-of-samples': 0,
                    'categories': []}
        else:
            info = {'number-of-samples': len(st),
                    'categories': st.categories()}

        self.write(json_encode(info))
        self.finish()