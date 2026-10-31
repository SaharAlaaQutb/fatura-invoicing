"""Domain error hierarchy for the Fatura bounded context.

All domain errors carry a stable machine ``code`` used by the
presentation layer to map to HTTP responses and localized messages.
"""

from typing import Optional


class DomainError(Exception):
    """Base class for all domain errors.

    Attributes:
        code: Stable machine-readable error code.
        message: Human-readable message template.
        context: Optional structured context for the error.
    """

    code: str = "domain.error"
    message: str = "A domain error occurred."

    def __init__(self, message: Optional[str] = None, context: Optional[dict] = None):
        self.message = message or self.message
        self.context = context or {}
        super().__init__(self.message)


class ValidationError(DomainError):
    """Raised when input fails domain validation."""


class StateError(DomainError):
    """Raised when an operation is invalid for the current state."""


class InventoryError(DomainError):
    """Raised when a stock operation violates inventory rules."""


class PaymentError(DomainError):
    """Raised when a payment operation fails."""


# --- Validation errors ---

class InvalidMoney(ValidationError):
    code = "money.invalid"
    message = "Invalid monetary amount."


class InvalidTaxRate(ValidationError):
    code = "tax.invalid_rate"
    message = "Tax rate must be between 0 and 10000 basis points."


class VoidReasonRequired(ValidationError):
    code = "void.reason_required"
    message = "A reason is required to void an invoice."


# --- State errors ---

class InvalidInvoiceState(StateError):
    code = "invoice.invalid_state"
    message = "Cannot transition invoice from {current} to {target}."

    def __init__(self, current, target, context: Optional[dict] = None):
        self.current = current
        self.target = target
        super().__init__(
            message=self.message.format(current=current, target=target),
            context=context,
        )


class InvoiceNotEditable(StateError):
    code = "invoice.not_editable"
    message = "Only draft invoices can be edited."


class InvoiceNotPayable(StateError):
    code = "invoice.not_payable"
    message = "Cannot record payments on a {status} invoice."

    def __init__(self, status, context: Optional[dict] = None):
        self.status = status
        super().__init__(message=self.message.format(status=status), context=context)


class EmptyInvoice(StateError):
    code = "invoice.empty"
    message = "An invoice must have at least one line before issuing."


# --- Inventory errors ---

class InsufficientStock(InventoryError):
    code = "stock.insufficient"
    message = "Not enough stock for product {product_id}. Available: {available}, requested: {requested}."

    def __init__(self, product_id, available, requested, context: Optional[dict] = None):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        super().__init__(
            message=self.message.format(
                product_id=product_id, available=available, requested=requested
            ),
            context=context,
        )


# --- Payment errors ---

class Overpayment(PaymentError):
    code = "payment.overpayment"
    message = "Payment amount {amount} exceeds outstanding balance {balance}."

    def __init__(self, amount, balance, context: Optional[dict] = None):
        self.amount = amount
        self.balance = balance
        super().__init__(
            message=self.message.format(amount=amount, balance=balance),
            context=context,
        )


class CannotVoidPaidInvoice(PaymentError):
    code = "payment.cannot_void_paid"
    message = "A paid invoice cannot be voided."
