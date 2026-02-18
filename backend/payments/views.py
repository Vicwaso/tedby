import re
from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from requests_app.models import KraRequest, RequestStatus
from .models import Payment, PaymentMethod, PaymentStatus

RECEIPT_PATTERN = re.compile(r"^[A-Z0-9]{10}$")

@api_view(["POST"])
def manual_verify(request):
    """
    Manual payment verification (TEDBY):
    - Early rejection: receipt must match ^[A-Z0-9]{10}$
    - Finalization uses DB lock (first payment wins)
    """
    request_id = request.data.get("requestId")
    receipt = (request.data.get("mpesaReceipt") or "").strip().upper()

    if not request_id:
        return Response({"message": "requestId is required"}, status=status.HTTP_400_BAD_REQUEST)

    if not RECEIPT_PATTERN.match(receipt):
        return Response({"message": "Invalid transaction code format."}, status=status.HTTP_400_BAD_REQUEST)

    # TODO: Stage 2 (year/month/day plausibility) + Stage 3 (authoritative validation)
    # For now, we accept any correctly formatted code so you can test end-to-end.

    with transaction.atomic():
        # Lock request row to prevent race conditions
        try:
            kra_req = KraRequest.objects.select_for_update().get(id=request_id)
        except KraRequest.DoesNotExist:
            return Response({"message": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        if kra_req.status not in [RequestStatus.CONFIRMED, RequestStatus.PAYMENT_PENDING]:
            return Response({"message": "Invalid state for payment"}, status=status.HTTP_400_BAD_REQUEST)

        # If already paid, reject (first payment wins)
        if kra_req.status in [RequestStatus.PAID, RequestStatus.RELEASED]:
            return Response({"message": "Already paid"}, status=status.HTTP_409_CONFLICT)

        # Create payment record (mpesa_receipt is UNIQUE)
        try:
            Payment.objects.create(
                request=kra_req,
                method=PaymentMethod.MANUAL,
                status=PaymentStatus.SUCCESS,
                amount=100,
                till="8993804",
                mpesa_receipt=receipt,
            )
        except IntegrityError:
            return Response({"message": "Transaction code already used."}, status=status.HTTP_409_CONFLICT)

        # Mark request as PAID
        kra_req.status = RequestStatus.PAID
        kra_req.paid_at = timezone.now()
        kra_req.save(update_fields=["status", "paid_at", "updated_at"])

    return Response({"requestId": kra_req.id, "status": kra_req.status, "receipt": receipt})
import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

PHONE_RE = re.compile(r"^(?:2547\d{8}|07\d{8})$")

@api_view(["POST"])
def stk_push(request):
    """
    STK Push (stub for now).
    Later we’ll call Daraja API here.
    """
    request_id = request.data.get("requestId")
    phone = (request.data.get("phone") or "").strip()

    if not request_id:
        return Response({"message": "requestId is required"}, status=status.HTTP_400_BAD_REQUEST)

    if not PHONE_RE.match(phone):
        return Response({"message": "Phone must be like 07XXXXXXXX or 2547XXXXXXXX"}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        try:
            kra_req = KraRequest.objects.select_for_update().get(id=request_id)
        except KraRequest.DoesNotExist:
            return Response({"message": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        if kra_req.status not in [RequestStatus.CONFIRMED, RequestStatus.PAYMENT_PENDING]:
            return Response({"message": "Invalid state for payment"}, status=status.HTTP_400_BAD_REQUEST)

        # Mark as pending (UI can poll)
        kra_req.status = RequestStatus.PAYMENT_PENDING
        kra_req.save(update_fields=["status", "updated_at"])

    # Stub response: in real implementation this would return CheckoutRequestID
    return Response({
        "requestId": request_id,
        "status": "PAYMENT_PENDING",
        "message": "STK prompt requested (stub). Integrate Daraja to send real prompt."
    })



@api_view(["POST"])
def simulate_paid(request, request_id: int):
    """
    DEV ONLY: simulate STK callback success.
    Sets request to PAID (or RELEASED if you prefer).
    """
    try:
        kra_req = KraRequest.objects.get(id=request_id)
    except KraRequest.DoesNotExist:
        return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    kra_req.status = RequestStatus.PAID
    kra_req.save(update_fields=["status", "updated_at"])
    return Response({"requestId": kra_req.id, "status": kra_req.status})

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from requests_app.models import KraRequest

@api_view(["GET"])
def payment_status(request, request_id: int):
    try:
        kra_req = KraRequest.objects.get(id=request_id)
    except KraRequest.DoesNotExist:
        return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response({"requestId": kra_req.id, "status": kra_req.status})



