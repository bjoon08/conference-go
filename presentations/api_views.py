from django.http import JsonResponse
from .models import Presentation, Status
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json
from events.models import Conference


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
        "presenter_name",
    ]

    def get_extra_data(self, o):
        return {"status": o.status.name}


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
    ]


@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    """
    Lists the presentation titles and the link to the
    presentation for the specified conference id.

    Returns a dictionary with a single key "presentations"
    which is a list of presentation titles and URLS. Each
    entry in the list is a dictionary that contains the
    title of the presentation, the name of its status, and
    the link to the presentation's information.

    {
        "presentations": [
            {
                "title": presentation's title,
                "status": presentation's status name
                "href": URL to the presentation,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        presentations = Presentation.objects.filter(conference=conference_id)
        return JsonResponse(
            {"presentations": presentations},
            encoder=PresentationListEncoder,
        )
    elif request.method == "POST":
        try:
            content = json.loads(request.body)
            status = Status.objects.get(id=content["status"])
            conference = Conference.objects.get(id=conference_id)
            content["status"] = status
            content["conference"] = conference
            presentation = Presentation.objects.create(**content)
            return JsonResponse(
                presentation,
                encoder=PresentationDetailEncoder,
                safe=False,
            )
        # except KeyError:
        #     return JsonResponse(
        #         {"message": "status is missing in the request body"},
        #         status=400,
        #     )
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference ID"},
                status=400,
            )
        except Status.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid status"},
                status=400,
            )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_presentation(request, id):
    """
    Returns the details for the Presentation model specified
    by the id parameter.

    This should return a dictionary with the presenter's name,
    their company name, the presenter's email, the title of
    the presentation, the synopsis of the presentation, when
    the presentation record was created, its status name, and
    a dictionary that has the conference name and its URL

    {
        "presenter_name": the name of the presenter,
        "company_name": the name of the presenter's company,
        "presenter_email": the email address of the presenter,
        "title": the title of the presentation,
        "synopsis": the synopsis for the presentation,
        "created": the date/time when the record was created,
        "status": the name of the status for the presentation,
        "conference": {
            "name": the name of the conference,
            "href": the URL to the conference,
        }
    }
    """
    if request.method == "GET":
        presentation = Presentation.objects.get(id=id)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "status" in content:
                status = Status.objects.get(id=content["status"])
                content["status"] = status
        except Status.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid status"},
                status=400,
            )

        Presentation.objects.filter(id=id).update(**content)
        presentation = Presentation.objects.get(id=id)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
