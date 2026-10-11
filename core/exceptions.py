"""
APEX_JARVIS Typed Exceptions Hierarchy.
"""

class JarvisException(Exception):
    """Base exception for all APEX_JARVIS faults."""
    pass

class AudioBufferOverflow(JarvisException):
    """Raised when audio ingestion exceeds buffer capacity."""
    pass

class VoiceRecognitionFault(JarvisException):
    """Raised when speech transcription fails or produces unparseable tokens."""
    pass

class ActionContractViolation(JarvisException):
    """Raised when desktop pre or post condition assertions fail."""
    pass

class RollbackExecutionFault(JarvisException):
    """Raised when an inverse compensating action fails during rollback."""
    pass
