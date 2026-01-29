from checklist.application.use_cases import (
    AddItem,
    CreateItemInput,
    DeleteItem,
    GetChecklist,
    IndentItem,
    MoveItemDown,
    MoveItemUp,
    OutdentItem,
    UpdateItem,
    UpdateItemInput,
)
from checklist.domain.models import Sheet
from checklist.infrastructure.gateways import SmartsheetGateway
from checklist.infrastructure.serializers import (
    ChecklistItemSerializer,
    CreateItemSerializer,
    CreateSheetSerializer,
    SheetSerializer,
    UpdateItemSerializer,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class SheetListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sheets = Sheet.objects.filter(user=request.user)
        serializer = SheetSerializer(sheets, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.smartsheet_token:
            return Response(
                {"error": "Smartsheet token not configured"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CreateSheetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        smartsheet_id = SmartsheetGateway.create_sheet(
            token=request.user.smartsheet_token,
            name=serializer.validated_data["name"],
        )

        sheet = Sheet.objects.create(
            user=request.user,
            smartsheet_id=smartsheet_id,
            name=serializer.validated_data["name"],
        )

        return Response(
            SheetSerializer(sheet).data, status=status.HTTP_201_CREATED
        )


class SheetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_sheet(self, request, sheet_uuid):
        return Sheet.objects.get(user=request.user, uuid=sheet_uuid)

    def delete(self, request, sheet_uuid):
        sheet = self.get_sheet(request, sheet_uuid)
        sheet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChecklistView(APIView):
    permission_classes = [IsAuthenticated]

    def get_gateway(self, request, sheet_uuid):
        sheet = Sheet.objects.get(user=request.user, uuid=sheet_uuid)
        return SmartsheetGateway(
            token=request.user.smartsheet_token,
            sheet_id=sheet.smartsheet_id,
        )

    def get(self, request, sheet_uuid):
        gateway = self.get_gateway(request, sheet_uuid)
        tree = GetChecklist(gateway).execute()
        serializer = ChecklistItemSerializer(tree, many=True)
        return Response(serializer.data)


class ItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_gateway(self, request, sheet_uuid):
        sheet = Sheet.objects.get(user=request.user, uuid=sheet_uuid)
        return SmartsheetGateway(
            token=request.user.smartsheet_token,
            sheet_id=sheet.smartsheet_id,
        )

    def post(self, request, sheet_uuid):
        gateway = self.get_gateway(request, sheet_uuid)
        serializer = CreateItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tree = AddItem(gateway).execute(
            CreateItemInput(**serializer.validated_data)
        )
        return Response(
            ChecklistItemSerializer(tree, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class ItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_gateway(self, request, sheet_uuid):
        sheet = Sheet.objects.get(user=request.user, uuid=sheet_uuid)
        return SmartsheetGateway(
            token=request.user.smartsheet_token,
            sheet_id=sheet.smartsheet_id,
        )

    def put(self, request, sheet_uuid, row_id):
        gateway = self.get_gateway(request, sheet_uuid)
        serializer = UpdateItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tree = UpdateItem(gateway).execute(
            row_id, UpdateItemInput(**serializer.validated_data)
        )
        return Response(ChecklistItemSerializer(tree, many=True).data)

    def delete(self, request, sheet_uuid, row_id):
        gateway = self.get_gateway(request, sheet_uuid)
        tree = DeleteItem(gateway).execute(row_id)
        return Response(ChecklistItemSerializer(tree, many=True).data)


class ItemIndentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_gateway(self, request, sheet_uuid):
        sheet = Sheet.objects.get(user=request.user, uuid=sheet_uuid)
        return SmartsheetGateway(
            token=request.user.smartsheet_token,
            sheet_id=sheet.smartsheet_id,
        )

    def post(self, request, sheet_uuid, row_id):
        gateway = self.get_gateway(request, sheet_uuid)
        tree = IndentItem(gateway).execute(row_id)
        return Response(ChecklistItemSerializer(tree, many=True).data)


class ItemOutdentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_gateway(self, request, sheet_uuid):
        sheet = Sheet.objects.get(user=request.user, uuid=sheet_uuid)
        return SmartsheetGateway(
            token=request.user.smartsheet_token,
            sheet_id=sheet.smartsheet_id,
        )

    def post(self, request, sheet_uuid, row_id):
        gateway = self.get_gateway(request, sheet_uuid)
        tree = OutdentItem(gateway).execute(row_id)
        return Response(ChecklistItemSerializer(tree, many=True).data)


class ItemMoveUpView(APIView):
    permission_classes = [IsAuthenticated]

    def get_gateway(self, request, sheet_uuid):
        sheet = Sheet.objects.get(user=request.user, uuid=sheet_uuid)
        return SmartsheetGateway(
            token=request.user.smartsheet_token,
            sheet_id=sheet.smartsheet_id,
        )

    def post(self, request, sheet_uuid, row_id):
        gateway = self.get_gateway(request, sheet_uuid)
        tree = MoveItemUp(gateway).execute(row_id)
        return Response(ChecklistItemSerializer(tree, many=True).data)


class ItemMoveDownView(APIView):
    permission_classes = [IsAuthenticated]

    def get_gateway(self, request, sheet_uuid):
        sheet = Sheet.objects.get(user=request.user, uuid=sheet_uuid)
        return SmartsheetGateway(
            token=request.user.smartsheet_token,
            sheet_id=sheet.smartsheet_id,
        )

    def post(self, request, sheet_uuid, row_id):
        gateway = self.get_gateway(request, sheet_uuid)
        tree = MoveItemDown(gateway).execute(row_id)
        return Response(ChecklistItemSerializer(tree, many=True).data)
