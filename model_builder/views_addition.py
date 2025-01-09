import json
import re
import uuid

from django.shortcuts import render

from model_builder.model_web import ModelWeb
from model_builder.object_creation_and_edition_utils import create_efootprint_obj_from_post_data, \
    add_new_efootprint_object_to_system, add_new_object_to_system_from_builder
from model_builder.views_edition import edit_object


def open_create_object_panel(request, object_type):
    model_web = ModelWeb(request.session)
    new_object_structure = model_web.get_object_structure(object_type)
    template_name = f'{new_object_structure.template_name}_add.html'
    context_data = {"object_structure": new_object_structure,
                    "header_name": "Create " +  new_object_structure.template_name.replace("_", " "),
                    "new_object_name": "New " + new_object_structure.template_name.replace("_", " ")}
    if request.GET.get('efootprint_id_of_parent_to_link_to'):
        context_data['efootprint_id_of_parent_to_link_to'] = request.GET['efootprint_id_of_parent_to_link_to']
    if request.GET.get("name"):
        context_data["new_object_name"] = request.GET["name"]
    if request.GET.get("efootprint_id_of_empty_object_origin"):
        context_data["efootprint_id_of_empty_object_origin"] = request.GET["efootprint_id_of_empty_object_origin"]

    return render(request, f"model_builder/side_panels/{template_name}", context=context_data)


def open_create_server_panel(request, object_type):
    template_name = f"{re.sub(r'(?<!^)(?=[A-Z])', '_', object_type).lower()}_add.html"
    structure_dict = {
        'str_attributes': ['name'],
        'server_items': [
            {'category':'server_type_helper','header': 'Server type','class': '','fields': [
                    {'input_type':'select', 'id':'server_type', 'name' : 'Server type', 'required':True, 'options': [
                        'Autoscaling', 'OnPremise', 'Serverless']}]},
            {'category':'cloud_creation_helper','header': 'Server creation helper','class': '','fields': [
                    {'input_type': 'select', 'id': 'provider', 'name': 'Provider', 'required':True, 'options': [
                        'aws', 'Azure', 'GCP', 'IBM', 'Oracle', 'Other']},
                    {'input_type': 'select', 'id': 'configuration', 'name': 'Server configuration', 'required':True,
                     'options': [
                        'a1.4xlarge', 'a1.2xlarge', 'a1.large', 'a1.medium', 'a1.xlarge',
                        'm6g.12xlarge', 'm6g.16xlarge', 'm6g.2xlarge', 'm6g.4xlarge', 'm6g.8xlarge', 'm6g.large',
                        'm6g.medium', 'm6g.xlarge', 'm5.12xlarge', 'm5.16xlarge', 'm5.24xlarge',
                        'm5.2xlarge', 'm5.4xlarge', 'm5.8xlarge', 'm5.large', 'm5.metal', 'm5.xlarge',
                        'm5a.12xlarge', 'm5a.16xlarge', 'm5a.24xlarge', 'm5a.2xlarge', 'm5a.4xlarge',
                        'm5a.8xlarge', 'm5a.large', 'm5a.xlarge', 'm5ad.12xlarge', 'm5ad.16xlarge',
                        'm5ad.24xlarge', 'm5ad.2xlarge', 'm5ad.4xlarge', 'm5ad.8xlarge', 'm5ad.large',
                        'm5ad.xlarge', 'm5d.12xlarge', 'm5d.16xlarge', 'm5d.24xlarge', 'm5d.2xlarge',
                        'm5d.4xlarge', 'm5d.8xlarge', 'm5d.large', 'm5d.metal', 'm5d.xlarge', 'm5dn.12xlarge',
                        'm5dn.16xlarge', 'm5dn.24xlarge', 'm5dn.2xlarge', 'm5dn.4xlarge', 'm5dn.8xlarge',
                        'm5dn.large', 'm5dn.xlarge', 'm5n.12xlarge', 'm5n.16xlarge', 'm5n.24xlarge',
                        'm5n.2xlarge', 'm5n.4xlarge', 'm5n.8xlarge', 'm5n.large', 'm5n.xlarge', 't3.2']
                    },
                    {'input_type': 'input', 'id': 'average_carbon_intensity', 'name': 'Average carbon intensity',
                     'unit': 'g/KWh', 'default': '100'}
                ]
            },
            {'category':'on_premise_creation_helper','header': 'Server creation helper','class': 'd-none','fields': [
                    {'input_type':'input', 'id': 'nb_of_cpu_units', 'name': 'Number of CPU units', 'unit': '',
                     'default': '2'},
                    {'input_type':'input', 'id': 'nb_of_cores_per_cpu_unit', 'name': 'Number of CPU Cores',
                     'unit': 'core', 'default': '24'},
                    {'input_type':'input', 'id': 'nb_of_ram_units', 'name': 'RAM unit', 'unit': 'GB', 'default': '12'},
                    {'input_type':'input', 'id': 'ram_quantity_per_unit_in_gb', 'name': 'RAM per unit', 'unit': '',
                     'default': '32'},
                    {'input_type': 'input', 'id': 'average_carbon_intensity', 'name': 'Average carbon intensity',
                     'unit': 'g/KWh', 'default': '100'}]}]}
    return render(request, f"model_builder/side_panels/{template_name}",
                  context={'structure_dict': structure_dict})


def add_new_user_journey(request):
    model_web = ModelWeb(request.session)
    if request.POST.getlist("form_add_uj_steps"):
        new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, 'UserJourney')
        added_obj = add_new_efootprint_object_to_system(request, model_web, new_efootprint_obj)
        response = render(
            request, "model_builder/object_cards/user_journey_card.html", {"user_journey": added_obj})
        response["HX-Trigger-After-Swap"] = json.dumps({
            "updateTopParentLines": {"topParentIds": [added_obj.web_id]},
            "setAccordionListeners": {"accordionIds": [added_obj.web_id]}})
    else:
        if not request.POST.get("efootprint_id_of_empty_object_origin"):
            empty_uj_id = f"new-uj-{str(uuid.uuid4())[:6]}"
        else:
            empty_uj_id = request.POST["efootprint_id_of_empty_object_origin"]
        added_obj = {
            "name": request.POST["form_add_name"],
            "web_id": empty_uj_id,
            "efootprint_id": empty_uj_id,
            "links_to": "",
            "data_line_opt": "",
            "uj_steps": [],
            "list_attributes": [{"attr_name": "uj_steps", "existing_objects": []}]
        }

        if "empty_objects" not in request.session:
            request.session["empty_objects"] = {"UserJourney": {empty_uj_id: added_obj}}
        else:
            if "UserJourney" not in request.session["empty_objects"]:
                request.session["empty_objects"]["UserJourney"] = {empty_uj_id: added_obj}
            else:
                request.session["empty_objects"]["UserJourney"][empty_uj_id] = added_obj
            request.session.modified = True

        response = render(request, "model_builder/object_cards/user_journey_empty.html",
                  context={"user_journey": added_obj})

    return response


def add_new_user_journey_step(request, user_journey_efootprint_id):
    model_web = ModelWeb(request.session)
    new_efootprint_obj = create_efootprint_obj_from_post_data(request, model_web, 'UserJourneyStep')
    added_obj = add_new_efootprint_object_to_system(request, model_web, new_efootprint_obj)
    user_journey_to_edit = model_web.get_web_object_from_efootprint_id(user_journey_efootprint_id)
    mutable_post = request.POST.copy()
    for key in list(mutable_post.keys()):
        if key.startswith('form_add'):
            del mutable_post[key]
    mutable_post['form_edit_name'] = user_journey_to_edit.name
    user_journey_step_ids = []
    for uj_step in user_journey_to_edit.uj_steps:
        user_journey_step_ids.append(uj_step.efootprint_id)
    user_journey_step_ids.append(added_obj.efootprint_id)
    mutable_post.setlist('form_edit_uj_steps', user_journey_step_ids)
    request.POST = mutable_post
    return edit_object(request, user_journey_efootprint_id, model_web)


def add_new_server(request):
    model_web = ModelWeb(request.session)
    server_type = request.POST.get('form_add_server_type')
    server_added = add_new_object_to_system_from_builder(request, model_web, server_type)
    response = render(
        request, "model_builder/object_cards/server_card.html", {"server": server_added})

    return response
