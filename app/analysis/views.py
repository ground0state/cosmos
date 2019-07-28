import os
import pickle
import uuid

import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View
from pandas.api.types import is_numeric_dtype
from django.http import HttpResponse

from .apps import AnalysisConfig
from .const import DATA_DIR, MODEL_DIR

from .reg_model import RegressionModel
from .clf_model import ClassifierModel


def error_handler_400(request, message):
    context = {'message': message}
    return render(request, 'analysis/home.html', context=context, status=400)


def error_handler_500(request):
    return render(request, '500.html', status=500)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'analysis/home.html'


home = HomeView.as_view()


class UploadView(LoginRequiredMixin, View):
    '''upload train and test file.'''

    def handle_uploaded_file(self, f, filename):
        path = os.path.join(DATA_DIR, filename)
        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    def post(self, request, *args, **kwargs):
        try:
            if ('train_data' in request.FILES) and ('test_data' in request.FILES):
                pass
            else:
                return error_handler_400(request, 'File not set.')

            # ファイルを保存
            train_uuid = str(uuid.uuid4())
            self.handle_uploaded_file(
                request.FILES['train_data'], train_uuid+'.csv')

            test_uuid = str(uuid.uuid4())
            self.handle_uploaded_file(
                request.FILES['test_data'], test_uuid+'.csv')

            # targetが数値であることを確認
            df_train = pd.read_csv(DATA_DIR+train_uuid+'.csv')
            df_test = pd.read_csv(DATA_DIR+test_uuid+'.csv')
            if not is_numeric_dtype(df_train.iloc[:, 0]):
                return error_handler(request, 400, 'Target is not number.')
            col_train = df_train.columns.tolist()
            col_train.pop(0)
            col_test = df_test.columns.tolist()
            if not (col_train == col_test):
                return error_handler_400(request, 'Columns does not match.')

            # セッションにファイル情報を格納
            request.session['train_uuid'] = train_uuid
            request.session['train_file_name'] = request.FILES['train_data'].name
            request.session['test_uuid'] = test_uuid
            request.session['test_file_name'] = request.FILES['test_data'].name

            return redirect('analysis:home')
        except:
            return error_handler_500(request)


upload = UploadView.as_view()


class TrainView(LoginRequiredMixin, TemplateView):

    def post(self, request, *args, **kwargs):
        try:
            if 'train_uuid' not in request.session:
                return error_handler_400(request, 'Train data missing.')

            train_uuid = request.session.get('train_uuid')
            df_train = pd.read_csv(DATA_DIR + train_uuid + ".csv")

            if request.POST.get('kind') == 'regression':
                model = RegressionModel()
            else:
                model = ClassifierModel()

            model.fit(df_train)

            model_uuid = str(uuid.uuid4())
            request.session['model_uuid'] = model_uuid

            with open(MODEL_DIR+model_uuid+'.pickle', mode='wb') as f:
                pickle.dump(model, f)

            return redirect('analysis:home')
        except:
            return error_handler_500(request)


train = TrainView.as_view()


class PredictView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            if 'test_uuid' not in request.session:
                return error_handler_400(request, 'Test data missing.')

            if 'model_uuid' not in request.session:
                return error_handler_400(request, 'Not trained.')

            test_uuid = request.session.get('test_uuid')
            df = pd.read_csv(DATA_DIR + test_uuid + ".csv", header=0)
            model_uuid = request.session['model_uuid']

            with open(MODEL_DIR + model_uuid+'.pickle', mode='rb') as f:
                model = pickle.load(f)

            df_pred = model.predict(df)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=prediction.csv'
            df_pred.to_csv(path_or_buf=response, sep=';',
                           float_format='%.2f', index=False, decimal=",")

            return response
        except:
            return error_handler_500(request)


predict = PredictView.as_view()
