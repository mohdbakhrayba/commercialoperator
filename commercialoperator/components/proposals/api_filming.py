import traceback
import os
import base64
import geojson
import json
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
from django.db.models import Q, Min
from django.db import transaction, connection
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route, renderer_classes, parser_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import Country
from datetime import datetime, timedelta, date
from commercialoperator.components.proposals.utils import save_proponent_data,save_assessor_data, proposal_submit
from commercialoperator.components.proposals.models import searchKeyWords, search_reference, ProposalUserAction
from commercialoperator.utils import missing_required_fields
from commercialoperator.components.main.utils import check_db_connection

from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from commercialoperator.components.main.models import Document, Region, District, Tenure, ApplicationType, RequiredDocument
from commercialoperator.components.proposals.models import (
	ProposalFilmingActivity,
	ProposalFilmingAccess,
	ProposalFilmingParks,
    Proposal,
)
from commercialoperator.components.proposals.serializers_filming import (
    ProposalFilmingActivitySerializer,
    ProposalFilmingAccessSerializer,
    ProposalFilmingParksSerializer,
    ProposalFilmingSerializer,
    SaveProposalFilmingParksSerializer
)

from commercialoperator.helpers import is_customer, is_internal
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer
from rest_framework.filters import BaseFilterBackend
import reversion
from reversion.models import Version

import logging
logger = logging.getLogger(__name__)


class ProposalFilmingViewSet(viewsets.ModelViewSet):
    """
    Similar to ProposalViewSet, except get_queryset include migrated_licences
    """
    queryset = Proposal.objects.none()
    serializer_class = ProposalFilmingSerializer
    lookup_field = 'id'

    @property
    def excluded_type(self):
        try:
            return ApplicationType.objects.get(name='E Class')
        except:
            return ApplicationType.objects.none()

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request): #user.is_authenticated():
            qs= Proposal.objects.all().exclude(application_type=self.excluded_type)
            return qs.exclude(migrated=True)
            #return Proposal.objects.filter(region__isnull=False)
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            queryset =  Proposal.objects.filter( Q(org_applicant_id__in = user_orgs) | Q(submitter = user) ).exclude(migrated=True)
            #queryset =  Proposal.objects.filter(region__isnull=False).filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) )
            return queryset.exclude(application_type=self.excluded_type)
        logger.warn("User is neither customer nor internal user: {} <{}>".format(user.get_full_name(), user.email))
        return Proposal.objects.none()

    def get_object(self):

        check_db_connection()
        try:
            obj = super(ProposalViewSet, self).get_object()
        except Exception, e:
            # because current queryset excludes migrated licences
            obj = get_object_or_404(Proposal, id=self.kwargs['id'])
        return obj



class ProposalFilmingParksViewSet(viewsets.ModelViewSet):
    queryset = ProposalFilmingParks.objects.all().order_by('id')
    serializer_class = ProposalFilmingParksSerializer

    @detail_route(methods=['post'])
    def edit_park(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SaveProposalFilmingParksSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instance.proposal.log_user_action(ProposalUserAction.ACTION_EDIT_VEHICLE.format(instance.id),request)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        try:
            #instance = self.get_object()
            serializer = SaveProposalFilmingParksSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            instance.proposal.log_user_action(ProposalUserAction.ACTION_CREATE_VEHICLE.format(instance.id),request)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))