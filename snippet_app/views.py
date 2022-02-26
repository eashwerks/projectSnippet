from django.db import transaction
from django.shortcuts import redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse

from snippet_app.models import Snippet, Tag
from snippet_app.serializers import SnippetSerializer, TagSerializer


class SnippetViewSet(viewsets.ModelViewSet):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        previous_serializer_fields = self.serializer_class.Meta.fields
        self.serializer_class.Meta.fields = ('id', 'title', 'detail')
        serializer = self.get_serializer(queryset, many=True)
        data = {'count': queryset.count(),
                'results': serializer.data}
        self.serializer_class.Meta.fields = previous_serializer_fields
        return Response(data)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        self._set_tag(data)
        self._set_user(data, request.user)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        self._set_tag(data)
        self._set_user(data, request.user, instance)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(methods=('delete',), detail=False, url_path='delete-bulk')
    def delete_bulk(self, request):
        # The ids of the objects to delete are passed as /?ids=1,2,4
        ids = request.GET.get('ids')
        if not ids:
            raise ValidationError(detail='parameter ?id= is required.')
        queryset = self.get_queryset().filter(id__in=ids.split(','))
        queryset.delete()
        return redirect(reverse('snippet-list'))

    def _set_tag(self, data):
        tag, created = Tag.objects.get_or_create(title=data.get('title').upper())
        data['tag'] = str(tag.id)
        self.is_tag_set = True

    def _set_user(self, data, user, instance=None):
        if not instance:
            data['created_by'] = user.id
        else:
            data['created_by'] = instance.created_by_id
        self.is_user_set = True


class TagViewSet(viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        snippets = Snippet.objects.filter(tag=instance.id)
        snippets_serializer = SnippetSerializer
        snippets_serializer.Meta.fields = ('id', 'title', 'detail')
        serializer = self.get_serializer(instance)
        snippets_data = snippets_serializer(snippets, many=True, context={'request': request})
        data = serializer.data
        data['snippets'] = snippets_data.data
        return Response(data)
