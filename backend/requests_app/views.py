from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
import base64
import os

from .models import KraRequest, RequestStatus
from .serializers import InitRequestSerializer
from .utils import mask_full_name

from django.http import HttpResponse
from requests_app.utils import generated_email
from certificates.pdf import build_pin_certificate_pdf


def get_kra_token():
    consumer_key = os.environ.get("GAVA_CONSUMER_KEY")
    consumer_secret = os.environ.get("GAVA_CONSUMER_SECRET")

    credentials = f"{consumer_key}:{consumer_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()

    response = requests.get(
        "https://sbx.kra.go.ke/v1/token/generate?grant_type=client_credentials",
        headers={"Authorization": f"Basic {encoded}"},
        timeout=10
    )
    response.raise_for_status()
    return response.json()["access_token"]


def kra_lookup(id_number: str) -> dict:
    token = get_kra_token()

    response = requests.post(
        "https://sbx.kra.go.ke/checker/v1/pin",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={
            "TaxpayerType": "KE",
            "TaxpayerID": id_number
        },
        timeout=10
    )

    data = response.json()

    if "ErrorCode" in data or "errorCode" in data:
        error = data.get("ErrorMessage") or data.get("errorMessage", "ID not found")
        raise ValueError(error)

    return {
        "full_name": data["TaxpayerName"].upper(),
        "pin": data["TaxpayerPIN"]
    }


@api_view(["POST"])
def init_request(request):
    ser = InitRequestSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    id_number = ser.validated_data["idNumber"].strip()
    first_name = ser.validated_data["firstName"].strip().upper()

    if not id_number.isdigit() or len(id_number) > 10:
        return Response({"message": "Invalid ID format"}, status=status.HTTP_400_BAD_REQUEST)
    '''
    try:
        kra = kra_lookup(id_number)
    except ValueError as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"message": "KRA lookup failed. Please try again."}, status=status.HTTP_502_BAD_GATEWAY)

    full_name = kra["full_name"]

    if not full_name.startswith(first_name):
        return Response({"message": "First name does not match our records."}, status=status.HTTP_400_BAD_REQUEST)

    masked = mask_full_name(full_name)
    '''
    try:
    kra = kra_lookup(id_number)
except ValueError as e:
    return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
except Exception as e:
    return Response({"message": f"KRA lookup failed: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

full_name = kra["full_name"]
# Temporarily return the name so we can see it
return Response({"debug_name": full_name})
    obj = KraRequest.objects.create(
        id_number=id_number,
        first_name_input=first_name,
        kra_full_name=full_name,
        masked_name=masked,
        kra_pin=kra["pin"],
        status=RequestStatus.LOOKUP_OK,
        ip_address=request.META.get("REMOTE_ADDR"),
        session_key=getattr(request.session, "session_key", "") or "",
    )

    return Response({
        "requestId": obj.id,
        "maskedName": obj.masked_name,
        "status": obj.status
    })


@api_view(["POST"])
def confirm_request(request, request_id: int):
    try:
        obj = KraRequest.objects.get(id=request_id)
    except KraRequest.DoesNotExist:
        return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if obj.status != RequestStatus.LOOKUP_OK:
        return Response({"message": "Invalid state"}, status=status.HTTP_400_BAD_REQUEST)

    obj.status = RequestStatus.CONFIRMED
    obj.save(update_fields=["status", "updated_at"])

    return Response({"requestId": obj.id, "status": obj.status})


@api_view(["GET"])
def request_result(request, request_id: int):
    try:
        obj = KraRequest.objects.get(id=request_id)
    except KraRequest.DoesNotExist:
        return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if obj.status not in [RequestStatus.PAID, RequestStatus.RELEASED]:
        return Response({"message": "Payment not confirmed"}, status=status.HTTP_402_PAYMENT_REQUIRED)

    gen_email = generated_email(obj.kra_full_name)

    return Response({
        "requestId": obj.id,
        "status": obj.status,
        "fullName": obj.kra_full_name,
        "pin": obj.kra_pin,
        "generatedEmail": gen_email,
        "certificateUrl": f"/api/requests/{obj.id}/certificate.pdf"
    })


@api_view(["GET"])
def certificate_pdf(request, request_id: int):
    try:
        obj = KraRequest.objects.get(id=request_id)
    except KraRequest.DoesNotExist:
        return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if obj.status not in [RequestStatus.PAID, RequestStatus.RELEASED]:
        return Response({"message": "Payment not confirmed"}, status=status.HTTP_402_PAYMENT_REQUIRED)

    gen_email = generated_email(obj.kra_full_name)
    pdf_bytes = build_pin_certificate_pdf(obj.kra_full_name, obj.kra_pin, gen_email)

    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="PIN_Certificate_{obj.id}.pdf"'
    return resp
