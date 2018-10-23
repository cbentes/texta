import json
from task_manager.models import Task
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from account.api_auth import api_auth

from utils.datasets import Datasets
from permission_admin.models import Dataset
from searcher.models import Search
from utils.es_manager import ES_Manager

from task_manager.task_manager import create_task
from task_manager.task_manager import get_fields
from task_manager.tasks.workers.tag_model_worker import TagModelWorker
from task_manager.tools import MassHelper
from task_manager.tools import get_pipeline_builder
from task_manager.models import TagFeedback


API_VERSION = "1.0"


def api_info(request):
    """ Get basic API info
    """
    data = {'name': 'TEXTA Task Manager API',
            'version': API_VERSION}
    data_json = json.dumps(data)
    return HttpResponse(data_json, content_type='application/json')


@csrf_exempt
@api_auth
def api_get_task_list(request, user, params):
    """ Get list of tasks
    """
    tasks = Task.objects.all()
    data = []
    # Build task list
    for task in tasks:
        t = {
            'task_id': task.id,
            'task_type': task.task_type,
            'status': task.status,
            'user': task.user.username
        }
        data.append(t)
    data_json = json.dumps(data)
    return HttpResponse(data_json, content_type='application/json')


@csrf_exempt
@api_auth
def api_get_task_status(request, user, params):
    """ Get task status for a given task id
    """
    task_id = params.get('task_id', None)
    try:
        task = Task.get_by_id(task_id)
        data = task.to_json()
        data_json = json.dumps(data)
        return HttpResponse(data_json, status=200, content_type='application/json')
    except Task.DoesNotExist as e:
        error = {'error': 'task id is not valid'}
        data_json = json.dumps(error)
        return HttpResponse(data_json, status=400, content_type='application/json')


@csrf_exempt
@api_auth
def api_train_model(request, user, params):
    """ Create task for train model
    """
    task_type = "train_model"
    description = params['description']
    # Create execution task
    task_id = create_task(task_type, description, params, user)
    # Add task to queue
    task = Task.get_by_id(task_id)
    task.update_status(Task.STATUS_QUEUED)
    # Return reference to task
    data = {
        'task_id': task_id,
        'task_type': task_type,
        'status': task.status,
        'user': task.user.username
    }
    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_train_tagger(request, user, params):
    """ Create task for train tagger
    """
    task_type = "train_tagger"
    description = params['description']
    # Create execution task
    task_id = create_task(task_type, description, params, user)
    # Add task to queue
    task = Task.get_by_id(task_id)
    task.update_status(Task.STATUS_QUEUED)
    # Return reference to task
    data = {
        'task_id': task_id,
        'task_type': task_type,
        'status': task.status,
        'user': task.user.username
    }
    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_apply(request, user, params):
    """ Create task for apply processor
    """
    task_type = "apply_preprocessor"
    description = params['description']
    # Create execution task
    task_id = create_task(task_type, description, params, user)
    # Add task to queue
    task = Task.get_by_id(task_id)
    task.update_status(Task.STATUS_QUEUED)
    # Return reference to task
    data = {
        'task_id': task_id,
        'task_type': task_type,
        'status': task.status,
        'user': task.user.username
    }
    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_dataset_list(request, user, params):
    """ Get list of available datasets for API user (via auth_token)
    """
    datasets = Datasets()
    dataset_mapping = datasets.get_allowed_datasets(user)
    data = []
    for d in dataset_mapping:
        # Build response structure
        row = {
            'dataset': d['id'],
            'index': d['index'],
            'mapping': d['mapping']
        }
        data.append(row)

    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_search_list(request, user, params):
    """ Get list of available searches for API user (via auth_token)
    """

    # Read all params
    dataset_id = int(params['dataset'])

    ds = Datasets()
    ds.activate_dataset_by_id(dataset_id, use_default=False)
    # Check if dataset_id is valid
    if not ds.is_active():
            error = {'error': 'invalid dataset parameter'}
            data_json = json.dumps(error)
            return HttpResponse(data_json, status=400, content_type='application/json')

    # Build response structure
    data = []
    dataset = Dataset(pk=dataset_id)
    search_list = list(Search.objects.filter(dataset=dataset))
    for search in search_list:
        row = {
            'dataset': dataset_id,
            'search': search.id,
            'description': search.description
        }
        data.append(row)

    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_normalizer_list(request, user, params):
    """ Get list of available normalizers for API user (via auth_token)
    """
    pipe_builder = get_pipeline_builder()

    data = []
    for opt in pipe_builder.get_normalizer_options():
        doc = {'normalizer_opt': opt['index'], 'label': opt['label']}
        data.append(doc)

    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_classifier_list(request, user, params):
    """ Get list of available classifiers for API user (via auth_token)
    """
    pipe_builder = get_pipeline_builder()

    data = []
    for opt in pipe_builder.get_classifier_options():
        doc = {'classifier_opt': opt['index'], 'label': opt['label']}
        data.append(doc)

    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_reductor_list(request, user, params):
    """ Get list of available reductors for API user (via auth_token)
    """
    pipe_builder = get_pipeline_builder()

    data = []
    for opt in pipe_builder.get_reductor_options():
        doc = {'reductor_opt': opt['index'], 'label': opt['label']}
        data.append(doc)

    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_extractor_list(request, user, params):
    """ Get list of available extractor for API user (via auth_token)
    """
    pipe_builder = get_pipeline_builder()

    data = []
    for opt in pipe_builder.get_extractor_options():
        doc = {'extractor_opt': opt['index'], 'label': opt['label']}
        data.append(doc)

    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_tagger_list(request, user, params):
    """ Get list of available tagger for API user (via auth_token)
    """
    all_taggers = Task.objects.filter(task_type="train_tagger", status=Task.STATUS_COMPLETED)
    data = []
    for tagger in all_taggers:
        doc = {'tagger': tagger.id, 'description': tagger.description}
        data.append(doc)

    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_tag_list(request, user, params):
    """ Get list of available tags for API user (via auth_token)
    """
    dataset_id = params['dataset']
    ds = Datasets()
    ds.activate_dataset_by_id(dataset_id, use_default=False)
    # Check if dataset_id is valid
    if not ds.is_active():
            error = {'error': 'invalid dataset parameter'}
            data_json = json.dumps(error)
            return HttpResponse(data_json, status=400, content_type='application/json')

    es_m = ds.build_manager(ES_Manager)
    mass_helper = MassHelper(es_m)
    tag_set = mass_helper.get_unique_tags()
    tag_frequency = mass_helper.get_tag_frequency(tag_set)
    tag_models = set([tagger.description for tagger in Task.objects.filter(task_type='train_tagger')])

    data = []
    for tag in sorted(tag_frequency.keys()):
        count = tag_frequency[tag]
        has_model = tag in tag_models
        doc = {'description': tag,
               'count': count,
               'has_model': has_model}
        data.append(doc)
    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_field_list(request, user, params):
    """ Get list of available fields for API user (via auth_token)
    """
    dataset_id = params['dataset']
    ds = Datasets()
    ds.activate_dataset_by_id(dataset_id, use_default=False)
    # Check if dataset_id is valid
    if not ds.is_active():
            error = {'error': 'invalid dataset parameter'}
            data_json = json.dumps(error)
            return HttpResponse(data_json, status=400, content_type='application/json')

    es_m = ds.build_manager(ES_Manager)
    fields = get_fields(es_m)
    data = sorted([x['path'] for x in fields])
    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_mass_train_tagger(request, user, params):
    """ Apply mass train tagger (via auth_token)
    """
    # Read all params
    dataset_id = params.get('dataset', None)
    selected_tags = set(params.get('tags', []))
    field = params.get("field", None)
    normalizer_opt = params.get("normalizer_opt", "0")
    classifier_opt = params.get("classifier_opt", "0")
    reductor_opt = params.get("reductor_opt", "0")
    extractor_opt = params.get("extractor_opt", "0")
    retrain_only = params.get("retrain_only", False)

    ds = Datasets()
    ds.activate_dataset_by_id(dataset_id, use_default=False)
    # Check if dataset_id is valid
    if not ds.is_active():
            error = {'error': 'invalid dataset parameter'}
            data_json = json.dumps(error)
            return HttpResponse(data_json, status=400, content_type='application/json')

    es_m = ds.build_manager(ES_Manager)
    mass_helper = MassHelper(es_m)
    
    data = mass_helper.schedule_tasks(selected_tags, normalizer_opt, classifier_opt, reductor_opt, extractor_opt, field, dataset_id, user)
    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_mass_tagger(request, user, params):
    """ Apply mass tagger (via auth_token)
    """
    # Get parameters with default values
    if 'search' not in params:
        params['search'] = 'all_docs'
    if 'description' not in params:
        params['description'] = "via API call"
    # Paramater projection for preprocessor task
    task_type = "apply_preprocessor"
    params["preprocessor_key"] = "text_tagger"
    params["text_tagger_feature_names"] = params['field']
    # Select taggers
    taggers = params.get('taggers', None)
    if taggers is None:
        taggers = [tagger.id for tagger in Task.objects.filter(task_type='train_tagger').filter(status=Task.STATUS_COMPLETED)]
    params['text_tagger_taggers'] = taggers
    # Prepare description
    description = params['description']
    # Create execution task
    task_id = create_task(task_type, description, params, user)
    # Add task to queue
    task = Task.get_by_id(task_id)
    task.update_status(Task.STATUS_QUEUED)
    # Return reference to task
    data = {
        'task_id': task_id,
        'task_type': task_type,
        'status': task.status,
        'user': task.user.username
    }
    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_hybrid_tagger(request, user, params):
    """ Apply hybrid tagger (via auth_token)
    """
    DEFAULT_TAGS_THRESHOLD = 50
    DEFAULT_MAX_TAGGERS = 20

    dataset_id = params['dataset']
    search = params['search']
    field = params['field']
    max_taggers = int(params.get('max_taggers', DEFAULT_MAX_TAGGERS))
    min_count_threshold = int(params.get('min_count_threshold', DEFAULT_TAGS_THRESHOLD))

    if 'description' not in params:
        params['description'] = "via API call"
    # Paramater projection for preprocessor task
    task_type = "apply_preprocessor"
    params["preprocessor_key"] = "text_tagger"
    params["text_tagger_feature_names"] = params['field']

    ds = Datasets()
    ds.activate_dataset_by_id(dataset_id, use_default=False)
    # Check if dataset_id is valid
    if not ds.is_active():
        error = {'error': 'invalid dataset parameter'}
        data_json = json.dumps(error)
        return HttpResponse(data_json, status=400, content_type='application/json')

    param_query = json.loads(Search.objects.get(pk=int(search)).query)
    es_m = ds.build_manager(ES_Manager)    
    es_m.load_combined_query(param_query)
    # Get similar documents in a neighborhood of size 1000
    response = es_m.more_like_this_search([field], search_size=1000)
    docs = response['hits']['hits']
    # Build Tag frequency
    tag_freq = {}
    for doc in docs:
        for f in doc['_source'].get('texta_facts', []):
            if f['fact'] == 'TEXTA_TAG' and f['doc_path'] == field:
                doc_tag = f['str_val']
                if doc_tag not in tag_freq:
                    tag_freq[doc_tag] = 0
                tag_freq[doc_tag] += 1

    # Top Tags to limit the number of taggers
    top_tags = [t[0] for t in sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)]
    top_tags = set(top_tags[:max_taggers])
    # Perform tag selection
    data = {'task': {}, 'explain': []}
    candidate_tags = set()
    for tag in tag_freq:
        selected = 0
        count = tag_freq[tag]
        if count >= min_count_threshold and tag in top_tags:
            selected = 1
            candidate_tags.add(tag)
        data['explain'].append({'tag': tag, 
                                'selected': selected, 
                                'count': count })
    # Filter tags
    tagger_search = Task.objects.filter(task_type='train_tagger').filter(status=Task.STATUS_COMPLETED)
    taggers = [tagger.id for tagger in tagger_search if tagger.description in candidate_tags]
    # Create Task if taggers is not zero
    if len(taggers) > 0:
        description = params['description']
        params['text_tagger_taggers'] = taggers
        # Create execution task
        task_id = create_task(task_type, description, params, user)
        # Add task to queue
        task = Task.get_by_id(task_id)
        task.update_status(Task.STATUS_QUEUED)
        # Return reference to task
        data['task'] = {
            'task_id': task_id,
            'task_type': task_type,
            'status': task.status,
            'user': task.user.username
        }
    else:
        # If here, no taggers were selected
        data['task'] = {"error": "no similar documents have tags count above threshold"}
    # Generate response
    data['min_count_threshold'] = min_count_threshold
    data['max_taggers'] = max_taggers
    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_tag_text(request, user, params):
    """ Apply tag to text (via auth_token)
    """
     # Get parameters with default values
    text = params.get('text', "").strip()
    taggers = params.get('taggers', None)
    # Check if text input is valid
    if len(text) == 0:
        error = {'error': 'text parameter cannot be empty'}
        data_json = json.dumps(error)
        return HttpResponse(data_json, status=400, content_type='application/json')
    # Select taggers
    tagger_ids_list = [tagger.id for tagger in Task.objects.filter(task_type='train_tagger').filter(status=Task.STATUS_COMPLETED)]
    data = {'tags': [], 'explain': []}
    # Apply
    for tagger_id in tagger_ids_list:
        is_tagger_selected = taggers is None or tagger_id in taggers
        if is_tagger_selected:
            tagger = TagModelWorker()
            tagger.load(tagger_id)
            p = int(tagger.model.predict([text])[0])
        else:
            p = None
        # Add explanation
        data['explain'].append({'tag': tagger.description, 
                                'prediction': p,
                                'selected': is_tagger_selected })
        # Add prediction as tag
        if p == 1:
            data['tags'].append(tagger.description)
    # Prepare response
    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


@csrf_exempt
@api_auth
def api_tag_feedback(request, user, params):
    """ Apply tag feedback (via auth_token)
    """
    dataset_id = params.get('dataset', None)
    document_ids = params.get('document_ids', None)
    tag = params.get('tag', None)
    field = params.get('field', None)
    value = int(params.get('value', 1))

    ds = Datasets()
    ds.activate_dataset_by_id(dataset_id, use_default=False)
    # Check if dataset_id is valid
    if not ds.is_active():
        error = {'error': 'invalid dataset parameter'}
        data_json = json.dumps(error)
        return HttpResponse(data_json, status=400, content_type='application/json')

    es_m = ds.build_manager(ES_Manager)
    mass_helper = MassHelper(es_m)
    resp = mass_helper.get_document_by_ids(document_ids)

    docs_to_update = []

    for hit in resp['hits']['hits']:
        doc = hit['_source']
        if value == 1:
            doc = _add_tag_to_document(doc, field, tag)
        else:
            doc = _remove_tag_from_document(doc, field, tag)
        docs_to_update.append(doc)
    
    es_m.update_documents(docs_to_update, document_ids)
    data = []
    for doc_id in document_ids:
        tag_feedback = TagFeedback.log(user, dataset_id, doc_id, field, tag, value)
        data.append(tag_feedback.to_json())
    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')


def _add_tag_to_document(doc, field, tag):
    """ Add tag from Texta facts field into document

    Parameters
    ----------
    doc: dict
        The elasticsearch document
    field: string
        The reference path inside the document
    tag: string
        The tag to be add in the document

    Returns
    -------
    dict
        The processed document
    """
    decoded_text = doc
    for k in field.split('.'):
        if k in decoded_text:
            decoded_text = decoded_text[k]
        else:
            decoded_text = ''
            break
    if 'texta_facts' not in doc:
        doc['texta_facts'] = []

    new_fact = {
        'fact': 'TEXTA_TAG',
        'str_val': tag,
        'doc_path': field,
        'spans': json.dumps([[0, len(decoded_text)]])
    }
    doc['texta_facts'].append(new_fact)
    return doc


def _remove_tag_from_document(doc, field, tag):
    """ Remove tag from Texta facts field in document

    Parameters
    ----------
    doc: dict
        The elasticsearch document
    field: string
        The reference path inside the document
    tag: string
        The tag to be removed from document

    Returns
    -------
    dict
        The processed document
    """
    if 'texta_facts' not in doc:
        # Nothing to remove
        return doc

    filtered_facts = []
    for fact in doc['texta_facts']:
        cond_1 = fact['fact'] == 'TEXTA_TAG'
        cond_2 = fact['str_val'] == tag
        cond_3 = fact['doc_path'] == field
        if cond_1 and cond_2 and cond_3:
            # Conditions to remove fact was met
            continue
        filtered_facts.append(fact)
    # Replace facts 
    doc['texta_facts'] = filtered_facts
    return doc


@csrf_exempt
@api_auth
def api_document_tags_list(request, user, params):
    """ Get document tags (via auth_token)
    """
    dataset_id = params.get('dataset', None)
    document_ids = params.get('document_ids', None)

    ds = Datasets()
    ds.activate_dataset_by_id(dataset_id, use_default=False)
    # Check if dataset_id is valid
    if not ds.is_active():
        error = {'error': 'invalid dataset parameter'}
        data_json = json.dumps(error)
        return HttpResponse(data_json, status=400, content_type='application/json')

    es_m = ds.build_manager(ES_Manager)
    mass_helper = MassHelper(es_m)
    resp = mass_helper.get_document_by_ids(document_ids)

    data = []
    for doc in resp['hits']['hits']:
        for f in doc['_source'].get('texta_facts', []):
            if f['fact'] == 'TEXTA_TAG':
                doc_id = doc['_id']
                doc_path = f['doc_path']
                doc_tag = f['str_val']
                data.append({ 'document_id': doc_id, 'field': doc_path, 'tag': doc_tag})

    data_json = json.dumps(data)
    return HttpResponse(data_json, status=200, content_type='application/json')