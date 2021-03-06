import json
import importlib


def save_model(model, filepath=None, params_mask={}, json_params={}):
    filepath = filepath or 'model.json'
    params = model.get_params(deep=False, **params_mask)
    params = model._serialize(params)
    with open(filepath, 'w') as f:
        json.dump(params, f, **json_params)


def load_model(filepath=None):
    filepath = filepath or 'model.json'
    with open(filepath) as f:
        params = json.load(f)

    # get rid of ugly unicode
    to_str = lambda x: str(x) if isinstance(x, unicode) else x
    params = dict(zip(params.keys(), map(to_str, params.values())))

    if not 'model' in params:
        raise ValueError("missed required field: 'model'")
    model_path = params['model']

    module_path, model_name = model_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    model_class = getattr(module, model_name, None)

    if model_class:
        model = model_class()
        params = model._deserialize(params)
        model.set_params(**params)
        return model

    raise ValueError("cannot find model '{0}'".format(model_path))