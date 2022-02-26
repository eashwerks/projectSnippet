from rest_framework import serializers

from snippet_app.models import Snippet, Tag


class SnippetSerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedIdentityField(view_name='snippet-detail', format='html')

    class Meta:
        model = Snippet
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
