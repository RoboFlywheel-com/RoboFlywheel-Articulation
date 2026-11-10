# SPDX-License-Identifier: Apache-2.0

class SDKError(Exception):
    """Base error for the articulated object SDK."""


class ValidationError(SDKError):
    """Raised when an articulated object definition is invalid."""
