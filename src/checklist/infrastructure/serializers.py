from rest_framework import serializers


class CreateItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    status = serializers.ChoiceField(
        choices=["Not Started", "In Progress", "Complete"]
    )
    assignee = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    parent_id = serializers.IntegerField(
        required=False, allow_null=True, default=None
    )


class UpdateItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    status = serializers.ChoiceField(
        choices=["Not Started", "In Progress", "Complete"],
        required=False,
    )
    assignee = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    notes = serializers.CharField(required=False, allow_blank=True)


class ChecklistItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.CharField()
    assignee = serializers.CharField()
    notes = serializers.CharField()
    parent_id = serializers.IntegerField(allow_null=True)
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return ChecklistItemSerializer(obj.children, many=True).data


class SheetSerializer(serializers.Serializer):
    id = serializers.UUIDField(source="uuid")
    name = serializers.CharField()


class CreateSheetSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
